from pathlib import Path

import pandas as pd
import biom


DATA_RAW = Path("data/raw/emp/release1")
DATA_PROCESSED = Path("data/processed")

MAPPING_PATH = DATA_RAW / "mapping_files" / "emp_qiime_mapping_subset_2k.tsv"
BIOM_PATH = DATA_RAW / "otu_tables" / "deblur" / \
    "emp_deblur_90bp.subset_2k.rare_5000.biom"


def load_mapping() -> pd.DataFrame:
    missing_values = [
        "not applicable",
        "not provided",
        "unknown",
        "Unknown",
        "NA",
        "N/A",
        "",
    ]

    return pd.read_csv(
        MAPPING_PATH,
        sep="\t",
        dtype=str,
        na_values=missing_values,
        keep_default_na=True,
    )


def main() -> None:
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

    mapping = load_mapping()


if __name__ == "__main__":
    main()
