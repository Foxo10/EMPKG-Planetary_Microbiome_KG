"""
inspect_missing_values.py

Inspecciona el mapping file de EMP para detectar qué valores se usan
como posibles marcadores de datos ausentes.

Salida:
- data/inspection/missing_value_candidates.csv
- data/inspection/missing_value_candidates_by_column.csv

Uso:
    python scripts/inspect_missing_values.py
"""

from collections import Counter
from pathlib import Path

import pandas as pd


DATA_RAW = Path("data/raw/emp/release1")
INSPECTION_DIR = Path("data/inspection")

MAPPING_PATH = DATA_RAW / "mapping_files" / "emp_qiime_mapping_subset_2k.tsv"

OUTPUT_VALUES_PATH = INSPECTION_DIR / "missing_value_candidates.csv"
OUTPUT_COLUMNS_PATH = INSPECTION_DIR / "missing_value_candidates_by_column.csv"


# Valores que queremos detectar como posibles nulos.
# Se comparan de forma exacta tras aplicar strip() y lower().
MISSING_CANDIDATES = {
    "",
    "na",
    "n/a",
    "nan",
    "none",
    "null",
    "unknown",
    "missing",
    "not applicable",
    "not provided",
    "not collected",
    "not available",
    "unspecified",
    "no data",
}


def is_missing_candidate(value: str) -> bool:
    """
    Devuelve True si un valor parece representar ausencia de dato.

    La comparación principal es exacta, no por substring.
    Esto evita marcar como nulo textos válidos que contienen palabras como
    'not' o 'unknown' dentro de una descripción.
    """

    clean_value = value.strip()
    clean_lower = clean_value.lower()

    if clean_lower in MISSING_CANDIDATES:
        return True

    if clean_lower.startswith("missing:"):
        return True

    return False


def load_mapping_as_raw_text(mapping_path: Path) -> pd.DataFrame:
    """
    Carga el mapping file sin conversión automática de nulos.

    Es importante usar keep_default_na=False y na_filter=False para que pandas
    no convierta valores como '', 'nan' o 'NA' antes de que podamos inspeccionarlos.
    """

    mapping = pd.read_csv(
        mapping_path,
        sep="\t",
        dtype=str,
        keep_default_na=False,
        na_filter=False,
    )

    return mapping


def inspect_missing_values(mapping: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Inspecciona valores candidatos a nulo.

    Devuelve:
    - Tabla global de valores candidatos.
    - Tabla por columna y valor candidato.
    """

    global_counter: Counter[str] = Counter()
    column_rows = []

    for column in mapping.columns:
        column_counter: Counter[str] = Counter()

        for value in mapping[column]:
            if is_missing_candidate(value):
                clean_value = value.strip()
                column_counter[clean_value] += 1
                global_counter[clean_value] += 1

        for value, count in column_counter.items():
            column_rows.append({
                "column": column,
                "missing_value": value,
                "count": count,
                "total_rows": len(mapping),
                "pct": round(count / len(mapping) * 100, 2),
            })

    values_df = pd.DataFrame([
        {
            "missing_value": value,
            "count": count,
            "total_cells": mapping.shape[0] * mapping.shape[1],
            "pct_total_cells": round(
                count / (mapping.shape[0] * mapping.shape[1]) * 100,
                4,
            ),
        }
        for value, count in global_counter.most_common()
    ])

    columns_df = pd.DataFrame(column_rows)

    if not columns_df.empty:
        columns_df = columns_df.sort_values(
            by=["count", "column"],
            ascending=[False, True],
        )

    return values_df, columns_df


def export_results(values_df: pd.DataFrame, columns_df: pd.DataFrame) -> None:
    """Guarda los resultados de la inspección."""

    INSPECTION_DIR.mkdir(parents=True, exist_ok=True)

    values_df.to_csv(OUTPUT_VALUES_PATH, index=False)
    columns_df.to_csv(OUTPUT_COLUMNS_PATH, index=False)

    print(f"[CSV] Valores candidatos globales → {OUTPUT_VALUES_PATH}")
    print(f"[CSV] Valores candidatos por campo → {OUTPUT_COLUMNS_PATH}")


def main() -> None:
    print("=" * 40)
    print("INSPECTING MISSING VALUES")
    print("=" * 40)

    mapping = load_mapping_as_raw_text(MAPPING_PATH)

    print(
        f"Mapping cargado: {mapping.shape[0]:,} filas x {mapping.shape[1]:,} columnas")

    values_df, columns_df = inspect_missing_values(mapping)

    print("\nValores candidatos a nulo encontrados:")
    print(values_df)

    print("\nColumnas con valores candidatos a nulo:")
    print(columns_df.head(40))

    export_results(values_df, columns_df)


if __name__ == "__main__":
    main()
