"""
inspect_data.py

Inspecciona los datos iniciales descargados de EMP Release 1:

- Mapping file: metadatos de muestras.
- BIOM file: matriz de abundancias y taxonomía.

Uso:
    python scripts/inspect_data.py
"""

from pathlib import Path

import pandas as pd
from biom import load_table

DATA_RAW = Path("data/raw/emp/release1")

MAPPING_PATH = DATA_RAW / "mapping_files" / "emp_qiime_mapping_subset_2k.tsv"
BIOM_PATH = (
    DATA_RAW
    / "otu_tables"
    / "deblur"
    / "emp_deblur_90bp.subset_2k.rare_5000.biom"
)


def inspect_mapping_file() -> pd.DataFrame:
    """Lee e inspecciona el mapping file de EMP."""

    print("=" * 40)
    print("MAPPING FILE")
    print("=" * 40)

    mapping = pd.read_csv(MAPPING_PATH, sep="\t", dtype=str)

    print(f"Ruta: {MAPPING_PATH}")
    print(f"Filas: {mapping.shape[0]}")
    print(f"Columnas: {mapping.shape[1]}")

    print("\nPrimeras columnas:")
    print(mapping.columns[:15].to_list())

    print("\nÚltimas columnas:")
    print(mapping.columns[-15:].to_list())

    return mapping


def inspect_biom_file():
    """Lee e inspecciona el archivo BIOM."""

    print("\n" + "=" * 40)
    print("BIOM FILE")
    print("=" * 40)


def main() -> None:
    mapping = inspect_mapping_file()
    table = inspect_biom_file()


if __name__ == "__main__":
    main()
