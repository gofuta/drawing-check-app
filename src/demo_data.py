def get_demo_result():
    return {
        "drawing_type": "平面図",
        "overall_score": 72,
        "check_items": [
            {"category": "基本情報", "item": "図面名称", "status": "OK", "severity": "低", "comment": "記入あり"},
            {"category": "基本情報", "item": "縮尺", "status": "NG", "severity": "高", "comment": "縮尺の記入がありません"},
            {"category": "寸法", "item": "通り芯寸法", "status": "OK", "severity": "低", "comment": "記入あり"},
            {"category": "寸法", "item": "開口部寸法", "status": "要確認", "severity": "中", "comment": "一部寸法が不鮮明"},
            {"category": "室名・用途", "item": "全室室名", "status": "OK", "severity": "低", "comment": "全室に室名あり"},
            {"category": "建具", "item": "建具記号", "status": "NG", "severity": "高", "comment": "建具記号の記入が一部不足"},
            {"category": "法規関連", "item": "採光開口", "status": "要確認", "severity": "中", "comment": "採光計算の根拠となる開口寸法の明示が必要"},
        ],
        "quantities": {
            "floor_area": 98.5,
            "building_area": 65.2,
            "stories": 2,
            "window_count": 12,
            "door_count": 8,
            "outer_wall_length": 42.0,
        },
        "summary": "全体的に図面の完成度は概ね良好ですが、縮尺の記入漏れと建具記号の不足が見られます。法規確認のための開口情報も補足が必要です。早急に修正対応してください。",
    }
