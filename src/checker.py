import anthropic
import base64
import json
from pathlib import Path


CHECK_PROMPT = """あなたは建築図面のチェック専門家です。
提示された建築図面を詳細に確認し、以下の観点でチェックしてください。

## チェック観点

1. **基本情報**
   - 図面名称の記入
   - 縮尺の記入
   - 作成日・改訂日の記入
   - 設計者・会社名の記入

2. **寸法**
   - 通り芯寸法の記入漏れ
   - 開口部（窓・ドア）の寸法記入
   - 室の内法寸法・面積
   - 階高・軒高（断面図の場合）

3. **室名・用途**
   - 全室の室名記入
   - 用途（居室/非居室）の判別可否

4. **建具**
   - 建具記号の記入
   - 開き方向・引き方向の表示
   - 建具の種別表示

5. **法規関連**
   - 採光計算に必要な開口部の明示
   - 換気開口の記入

## 出力形式

必ずJSON形式で出力してください。

{
  "drawing_type": "図面種別（平面図/立面図/断面図/配置図/不明）",
  "overall_score": 0〜100の数値（完成度のスコア）,
  "check_items": [
    {
      "category": "カテゴリ名",
      "item": "チェック項目",
      "status": "OK" または "NG" または "要確認",
      "severity": "高" または "中" または "低",
      "comment": "詳細コメント（NGの場合は改善内容も記載）"
    }
  ],
  "quantities": {
    "floor_area": 床面積（m2、読み取れる場合）または null,
    "building_area": 建築面積（m2、読み取れる場合）または null,
    "stories": 階数（読み取れる場合）または null,
    "window_count": 窓の数（読み取れる場合）または null,
    "door_count": ドアの数（読み取れる場合）または null,
    "outer_wall_length": 外壁周長（m、読み取れる場合）または null
  },
  "summary": "総合所見（3〜5行）"
}

読み取れない情報はnullとしてください。JSONのみ出力し、前後に説明文は不要です。"""


def encode_image(image_bytes: bytes, media_type: str) -> str:
    return base64.standard_b64encode(image_bytes).decode("utf-8")


def check_drawing(image_bytes: bytes, media_type: str, api_key: str) -> dict:
    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": encode_image(image_bytes, media_type),
                        },
                    },
                    {
                        "type": "text",
                        "text": CHECK_PROMPT,
                    },
                ],
            }
        ],
    )

    raw = message.content[0].text.strip()
    # JSONブロックが```json ... ```で囲まれている場合も対応
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw)
