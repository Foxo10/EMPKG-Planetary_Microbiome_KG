from pathlib import Path

DATA_RAW = Path("data/raw/emp/release1")
INSPECTION_DIR = Path("data/inspection")
PROCESSED_DIR = Path("data/processed")

MAPPING_PATH = DATA_RAW / "mapping_files" / "emp_qiime_mapping_subset_2k.tsv"

BIOM_PATH = (
    DATA_RAW / "otu_tables" / "deblur" / "emp_deblur_90bp.subset_2k.rare_5000.biom"
)

SAMPLE_TABLE_PATH = PROCESSED_DIR / "sample_table.csv"
