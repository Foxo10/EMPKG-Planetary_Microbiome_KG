import pandas as pd

MISSING_VALUES = [
    "",
    "nan",
    "NaN",
    "NA",
    "N/A",
    "n/a",
    "null",
    "Null",
    "None",
    "none",
    "unknown",
    "Unknown",
    "UNKNOWN",
    "Missing: Not provided",
]


def normalize_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    na_map = {value: pd.NA for value in MISSING_VALUES}
    return df.replace(na_map)
