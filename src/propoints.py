"""デザインプロポイント スコア計算ロジック"""

# ==================== マスタテーブル ====================
# マスタシートの点数テーブルをそのまま定義

PRODUCTS = ['ORDER', 'SELECT', 'COCOQUMI', 'COCOCHIE']
BUILDING_TYPES = ['2階建て', '平屋建て']

PRODUCT_PT = {
    'ORDER'   : 2.0,
    'SELECT'  : 1.5,
    'COCOQUMI': 1.5,
    'COCOCHIE': 1.2,
}

# (閾値以上の精度 → このPt) ← VLOOKUP TRUE (近似一致 / 以下の最大値)
ACCURACY_TABLE = [
    (0,  1.0),
    (90, 1.1),
    (93, 1.2),
    (96, 1.3),
    (98, 1.5),
]

WORKLOAD_2F = [
    (0,  1.5),
    (50, 1.4),
    (60, 1.3),
    (65, 1.2),
    (70, 1.1),
    (80, 1.0),
]

WORKLOAD_HIRA = [
    (0,  1.5),
    (40, 1.5),
    (50, 1.3),
    (55, 1.2),
    (60, 1.1),
    (70, 1.0),
]

# STATUS判定は 精度Pt × 工数Pt（商品Ptは合計スコアに使うが判定には使わない）
STATUS_THRESHOLDS = [
    (1.9,  '👑 PERFECT!'),
    (1.5,  '✨ EXCELLENT!'),
    (1.25, '🔥 GREAT'),
    (0,    '✅ GOOD'),
]

STATUS_COLORS = {
    '👑 PERFECT!':   '#FFF9C4',
    '✨ EXCELLENT!': '#FFE0B2',
    '🔥 GREAT':      '#DCEDC8',
    '✅ GOOD':       '#E3F2FD',
}

STATUS_TEXT_COLORS = {
    '👑 PERFECT!':   '#F57F17',
    '✨ EXCELLENT!': '#E65100',
    '🔥 GREAT':      '#33691E',
    '✅ GOOD':       '#0D47A1',
}


def _vlookup_approx(table: list, value: float) -> float:
    """VLOOKUP TRUE（近似一致）と同等: value 以下の最大閾値のPtを返す"""
    result = table[0][1]
    for threshold, pt in table:
        if value >= threshold:
            result = pt
        else:
            break
    return result


def calculate(product: str, accuracy: float, hours: float, building_type: str) -> dict:
    """
    プロポイントを計算して結果辞書を返す

    Returns:
        {
            product_pt, accuracy_pt, workload_pt,
            total_score,   # 商品×精度×工数
            perf_score,    # 精度×工数（STATUS判定用）
            status,
        }
    """
    product_pt  = PRODUCT_PT.get(product, 0)
    accuracy_pt = _vlookup_approx(ACCURACY_TABLE, float(accuracy))
    table       = WORKLOAD_2F if building_type == '2階建て' else WORKLOAD_HIRA
    workload_pt = _vlookup_approx(table, float(hours))

    total_score = round(product_pt * accuracy_pt * workload_pt, 3)
    perf_score  = round(accuracy_pt * workload_pt, 3)  # STATUS判定は精度×工数のみ

    status = STATUS_THRESHOLDS[-1][1]
    for threshold, label in STATUS_THRESHOLDS:
        if perf_score >= threshold:
            status = label
            break

    return {
        'product_pt' : product_pt,
        'accuracy_pt': accuracy_pt,
        'workload_pt': workload_pt,
        'total_score': total_score,
        'perf_score' : perf_score,
        'status'     : status,
    }


def status_color(status: str) -> tuple[str, str]:
    """(背景色, 文字色)を返す"""
    return STATUS_COLORS.get(status, '#F5F5F5'), STATUS_TEXT_COLORS.get(status, '#212121')
