"""
build_sample_table.py

Construye la tabla base de muestras para EMPKG-lite cruzando:
- El mapping file TSV (metadatos ambientales de muestra)
- El fichero BIOM (IDs válidos + estadísticas de abundancia)

Output:
    data/processed/sample_table.csv

Uso:
    python scripts/build_sample_table.py
"""


from pathlib import Path

import pandas as pd
import numpy as np
import biom

# --- Rutas ---
DATA_RAW = Path("data/raw/emp/release1")
MAPPING_PATH = DATA_RAW / "mapping_files" / "emp_qiime_mapping_subset_2k.tsv"
BIOM_PATH = DATA_RAW / "otu_tables" / "deblur" / \
    "emp_deblur_90bp.subset_2k.rare_5000.biom"
OUTPUT_PATH = Path("data/processed") / "sample_table.csv"

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

# Campos del mapping file que nos interesan para el KG.
# Los dividimos por categoría para que sea fácil añadir o quitar campos.
FIELDS_IDENTITY = ["study_id"]

FIELDS_EMPO = ["empo_1", "empo_2", "empo_3"]

FIELDS_ENVO = [
    "env_biome",    # texto libre, p.ej. "temperate grassland biome"
    "env_feature",  # texto libre, p.ej. "rhizosphere soil"
    "env_material",  # texto libre, p.ej. "soil"
    "envo_biome_0",  # término ENVO más grueso (siempre presente)
    "envo_biome_1",  # término ENVO nivel 1 (siempre presente)
    "envo_biome_2",  # término ENVO nivel 2 (1,65% de nulos)
    "envo_biome_3",  # término ENVO nivel 3 (27,85% de nulos)
]

FIELDS_GEO = [
    "country",
    "latitude_deg",
    "longitude_deg",
    "depth_m",
    "altitude_m",
    "elevation_m",
]

FIELDS_PHYSICOCHEMICAL = [
    "temperature_deg_c",
    "ph",
    "salinity_psu",
    "oxygen_mg_per_l",
]

ALL_FIELDS = (
    FIELDS_IDENTITY
    + FIELDS_EMPO
    + FIELDS_ENVO
    + FIELDS_GEO
    + FIELDS_PHYSICOCHEMICAL
)

REQUIRED_COLUMNS = [
    "study_id",
    "env_biome",
    "env_feature",
    "env_material",
    "empo_0",
    "empo_1",
    "empo_2",
    "empo_3",
]

NUMERIC_COLUMNS = [
    "read_length_bp",
    "sequences_split_libraries",
    "observations_closed_ref_greengenes",
    "observations_closed_ref_silva",
    "observations_open_ref_greengenes",
    "observations_deblur_90bp",
    "observations_deblur_100bp",
    "observations_deblur_150bp",
    "sample_taxid",
    "host_taxid",
    "latitude_deg",
    "longitude_deg",
    "depth_m",
    "altitude_m",
    "elevation_m",
    "adiv_observed_otus",
    "adiv_chao1",
    "adiv_shannon",
    "adiv_faith_pd",
    "temperature_deg_c",
    "ph",
    "salinity_psu",
    "oxygen_mg_per_l",
    "phosphate_umol_per_l",
    "ammonium_umol_per_l",
    "nitrate_umol_per_l",
    "sulfate_umol_per_l",
]


def load_mapping(mapping_path: Path) -> pd.DataFrame:
    """
    Carga el mapping file, normaliza valores ausentes y lo indexa por sample_id.

    Pasos:
    1. Carga el TSV en crudo (sin que pandas interprete nada).
    2. Reemplaza los marcadores de ausencia de la lista MISSING_VALUES por NaN.
    3. Renombra '#SampleID' a 'sample_id' y lo establece como índice.

    Returns:
        DataFrame indexado por sample_id con todos los campos del mapping file.
        Los valores ausentes están normalizados a NaN (float).
    """
    print("=" * 40)
    print("LOADING MAPPING FILE")
    print("=" * 40)

    # Paso 1: carga en crudo.
    # keep_default_na=False y na_filter=False evitan que pandas convierta
    # automáticamente "", "nan", "NA", etc. antes de que podamos inspeccionarlos.

    # Así controlamos nosotros qué se trata como ausente, no pandas.
    df = pd.read_csv(
        mapping_path,
        sep="\t",
        dtype=str,
        keep_default_na=False,
        na_filter=False,
    )

    print(f"  Filas cargadas:  {df.shape[0]:,}")
    print(f"  Columnas:        {df.shape[1]:,}")

    # Paso 2: normalizar valores ausentes.
    # replace() sobre un DataFrame aplica la sustitución célula a célula.
    # Convertimos la lista a un dict {valor: NaN} para ser explícitos.
    n_missing_markers = int(df.isin(MISSING_VALUES).sum().sum())

    na_map = {value: pd.NA for value in MISSING_VALUES}
    df = df.replace(na_map)

    print(f"  Valores normalizados a NA: {n_missing_markers:,}")

    df = df.rename(columns={"#SampleID": "sample_id"})

    if df["sample_id"].isna().any():
        raise ValueError("Hay muestras sin sample_id después de normalizar nulos.")

    if df["sample_id"].duplicated().any():
        n_duplicates = df["sample_id"].duplicated().sum()
        raise ValueError(f"Hay sample_id duplicados: {n_duplicates}")

    df = df.set_index("sample_id")

    print(f"  Índice: sample_id ({df.index.nunique():,} valores únicos)")

    return df


def validate_required_columns(df: pd.DataFrame) -> None:
    """
    Comprueba que el mapping file contiene las columnas mínimas necesarias
    para construir la tabla base de muestras.

    Como sample_id ya es el índice, aquí solo comprobamos columnas normales.
    """

    print("\n" + "=" * 40)
    print("VALIDATING REQUIRED COLUMNS")
    print("=" * 40)

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Faltan columnas obligatorias en el mapping file: "
            + ", ".join(missing_columns)
        )

    print("  OK: todas las columnas obligatorias están presentes.")


def convert_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte a tipo numérico las columnas que representan coordenadas,
    medidas ambientales, recuentos o métricas de diversidad.

    Los valores que no se puedan convertir se transforman en NA.
    """

    print("\n" + "=" * 40)
    print("CONVERTING NUMERIC COLUMNS")
    print("=" * 40)

    df = df.copy()

    for column in NUMERIC_COLUMNS:
        if column not in df.columns:
            print(f"  {column:<40} no existe, se ignora.")
            continue

        before_na = df[column].isna().sum()

        original_non_null = df[column].dropna()

        converted = pd.to_numeric(df[column], errors="coerce")

        after_na = converted.isna().sum()
        new_na = after_na - before_na

        df[column] = converted

        print(
            f"  {column:<40} "
            f"NA antes: {before_na:>4} | "
            f"NA después: {after_na:>4} | "
            f"nuevos NA: {new_na:>4}"
        )

        if new_na > 0:
            invalid_values = original_non_null[
                pd.to_numeric(original_non_null, errors="coerce").isna()
            ].unique()

            invalid_preview = list(invalid_values[:5])

            print(f"    Valores no convertibles detectados: {invalid_preview}")

    return df


def load_biom_table(biom_path: Path) -> biom.Table:
    """
    Carga el fichero BIOM con biom-format.

    No se convierte la matriz a denso en ningún momento: todas las
    operaciones posteriores (sum, nonzero_counts) trabajan sobre la
    representación dispersa interna de biom.Table.

    Returns:
        biom.Table con la matriz de abundancias ASV × muestra.
    """
    print("\n" + "=" * 40)
    print("LOADING BIOM FILE")
    print("=" * 40)

    table = biom.load_table(str(biom_path))
    n_obs, n_samples = table.shape

    print(f" ASVs (observaciones):  {n_obs:,}")
    print(f" Muestras:              {n_samples:,}")
    print(f" Valores no nulos:      {table.nnz:,}")
    print(f" Densidad de la matriz: {table.get_table_density():.4f}")

    return table


def validate_sample_ids(mapping: pd.DataFrame, sample_stats: pd.DataFrame) -> None:
    """
    Comprueba que los IDs de muestra coinciden exactamente entre el mapping
    file y el BIOM (ambos ya indexados por sample_id).

    A diferencia del notebook de exploración (que usa assert), aquí se lanza
    ValueError con un mensaje explícito: assert puede desactivarse en
    producción con `python -O` y no es la herramienta adecuada para
    validación de datos en un pipeline reproducible.

    Raises:
        ValueError: si hay IDs exclusivos de un lado o el recuento de IDs
            comunes no coincide con el total de ambos conjuntos.
    """

    print("\n" + "=" * 40)
    print("VALIDATING SAMPLE IDs")
    print("=" * 40)

    mapping_ids = set(mapping.index)
    biom_ids = set(sample_stats.index)

    common_ids = mapping_ids & biom_ids
    only_mapping = mapping_ids - biom_ids
    only_biom = biom_ids - mapping_ids

    print(f"  IDs en mapping: {len(mapping_ids):,}")
    print(f"  IDs en BIOM:    {len(biom_ids):,}")
    print(f"  IDs comunes:    {len(common_ids):,}")

    if only_mapping:
        raise ValueError(
            f"Hay {len(only_mapping)} sample_id en el mapping file que no "
            f"están en el BIOM. Ejemplos: {list(only_mapping)[:5]}"
        )

    if only_biom:
        raise ValueError(
            f"Hay {len(only_biom)} sample_id en el BIOM que no están en el "
            f"mapping file. Ejemplos: {list(only_biom)[:5]}"
        )

    if not (len(common_ids) == len(mapping_ids) == len(biom_ids)):
        raise ValueError(
            f"El número de IDs comunes ({len(common_ids):,}) no coincide "
            f"con el total de mapping ({len(mapping_ids):,}) o BIOM "
            f"({len(biom_ids):,})."
        )

    print(f"  OK: los {len(common_ids):,} sample_id coinciden exactamente.")


def build_sample_stats(table: biom.Table) -> pd.DataFrame:
    """
    Construye una tabla con una fila por muestra y dos métricas derivadas
    del BIOM:

    - biom_total_reads: lecturas totales de la muestra (suma de la columna).
      En el fichero rare_5000 debería ser constante = 5000 para todas las
      muestras, por la rarefacción.
    - biom_observed_asvs: número de ASVs distintos detectados en la muestra
      (cuenta de valores no nulos), una medida básica de riqueza/diversidad.

    Returns:
        DataFrame indexado por sample_id con columnas
        ['biom_total_reads', 'biom_observed_asvs'], ambas en int64.
    """

    print("\n" + "=" * 40)
    print("BUILDING SAMPLE STATS FROM BIOM")
    print("=" * 40)

    sample_stats = pd.DataFrame({
        "sample_id": table.ids(axis="sample"),
        "biom_total_reads": table.sum(axis="sample"),
        "biom_observed_asvs": table.nonzero_counts(axis="sample"),
    }).set_index("sample_id")

    sample_stats = sample_stats.astype({
        "biom_total_reads": "int64",
        "biom_observed_asvs": "int64",
    })

    print(f"  Muestras procesadas: {sample_stats.shape[0]:,}")
    print(
        "  biom_total_reads -> "
        f"min: {sample_stats['biom_total_reads'].min()}, "
        f"max: {sample_stats['biom_total_reads'].max()}"
    )
    print(
        "  biom_observed_asvs -> "
        f"min: {sample_stats['biom_observed_asvs'].min()}, "
        f"max: {sample_stats['biom_observed_asvs'].max()}, "
        f"mediana: {sample_stats['biom_observed_asvs'].median():.0f}"
    )
    print("")
    print(sample_stats)

    return sample_stats


def join_mapping_with_biom(
        mapping: pd.DataFrame,
        sample_stats: pd.DataFrame,
) -> pd.DataFrame:
    """
    Cruza el mapping file (metadatos ambientales) con sample_stats
    (estadísticas derivadas del BIOM) mediante un join por sample_id.

    Se asume que validate_sample_ids() ya se ha ejecutado sin errores antes
    de llamar a esta función, por lo que un inner join no debería perder
    ninguna fila. Aun así, se verifica explícitamente el número de filas
    resultante como salvaguarda.

    Returns:
        DataFrame indexado por sample_id con todas las columnas del mapping
        más 'biom_total_reads' y 'biom_observed_asvs'.
    """
    print("\n" + "=" * 40)
    print("JOINING MAPPING + BIOM SAMPLE STATS")
    print("=" * 40)

    expected_rows = len(set(mapping.index) & set(sample_stats.index))

    sample_table = mapping.join(sample_stats, how="inner")

    if sample_table.shape[0] != expected_rows:
        raise ValueError(
            f"El join perdió o duplicó filas: esperábamos {expected_rows:,}, "
            f"se obtuvieron {sample_table.shape[0]:,}."
        )

    print(f"  Filas resultantes: {sample_table.shape[0]:,}")
    print(f"  Columnas resultantes: {sample_table.shape[1]:,}")
    print("")
    print(sample_table)

    return sample_table


def select_output_columns(sample_table: pd.DataFrame) -> pd.DataFrame:
    """
    Selecciona y ordena las columnas principales de la tabla base de muestras.

    Mantiene:
    - campos ambientales relevantes para el KG
    - métricas físico-químicas principales
    - estadísticas derivadas del BIOM
    - algunas métricas de diversidad ya presentes en el mapping file
    """
    print("\n" + "=" * 40)
    print("SELECTING OUTPUT COLUMNS")
    print("=" * 40)

    biom_fields = [
        "biom_total_reads",
        "biom_observed_asvs",
    ]

    # diversity_fields = [
    #     "adiv_observed_otus",
    #     "adiv_chao1",
    #     "adiv_shannon",
    #     "adiv_faith_pd",
    # ]

    candidate_columns = (
        FIELDS_IDENTITY
        + FIELDS_EMPO
        + FIELDS_ENVO
        + FIELDS_GEO
        + FIELDS_PHYSICOCHEMICAL
        + biom_fields
    )

    missing_columns = [
        column for column in candidate_columns
        if column not in sample_table.columns
    ]

    if missing_columns:
        raise ValueError(
            "Faltan columnas esperadas para la tabla final del KG: "
            + ", ".join(missing_columns)
        )

    selected = sample_table[candidate_columns].copy()

    print(f"  Columnas seleccionadas: {selected.shape[1]:,}")
    print("")
    print(selected)

    return selected


def main() -> None:

    # --- Mapping file: carga, validación y limpieza ---
    mapping = load_mapping(MAPPING_PATH)
    validate_required_columns(mapping)
    mapping = convert_numeric_columns(mapping)

    # --- BIOM: carga y estadísticas por muestra ---
    table = load_biom_table(BIOM_PATH)
    sample_stats = build_sample_stats(table)

    # --- Validación cruzada e integración ---
    validate_sample_ids(mapping, sample_stats)
    sample_table = join_mapping_with_biom(mapping, sample_stats)

    # --- Selección de columnas relevantes para el KG ---
    sample_table = select_output_columns(sample_table)

    # --- Exportación ---

    # --- Resumen diagnóstico ---


if __name__ == "__main__":
    main()
