import pandas as pd
from pathlib import Path

MASTER_PATH = Path(__file__).parent.parent / "data" / "price_master.csv"


def load() -> pd.DataFrame:
    return pd.read_csv(MASTER_PATH, encoding="utf-8-sig")


def lookup(category: str, item: str) -> int | None:
    df = load()
    row = df[(df["工種"] == category) & (df["品目"] == item)]
    if row.empty:
        return None
    return int(row.iloc[0]["単価"])


def all_items() -> pd.DataFrame:
    return load()
