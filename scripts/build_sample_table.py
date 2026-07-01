
"""
build_sample_table.py
 
Construye la tabla base de muestras para EMPKG-lite cruzando:
  - El mapping file TSV (metadatos ambientales por muestra).
  - El fichero BIOM (IDs válidos + estadísticas de abundancia).
 
La tabla resultante tiene una fila por muestra y no incluye relaciones
muestra-ASV. Esas relaciones se generarán en un script posterior
(build_abundance_table.py).
 
Conceptos clave:
  - sample_id: identificador único de una muestra concreta. Es el índice
    de la tabla y será el futuro nodo empkg:Sample en el KG.
  - study_id: identificador del estudio EMP al que pertenece la muestra.
    Muchas muestras comparten el mismo study_id. Será la futura relación
    Sample -> partOfStudy -> Study en el KG.
 
Output:
    data/processed/sample_table.csv
 
Uso:
    python scripts/build_sample_table.py
"""


from pathlib import Path

import pandas as pd
import biom

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------

DATA_RAW = Path("data/raw/emp/release1")
MAPPING_PATH = DATA_RAW / "mapping_files" / "emp_qiime_mapping_subset_2k.tsv"
BIOM_PATH = DATA_RAW / "otu_tables" / "deblur" / \
    "emp_deblur_90bp.subset_2k.rare_5000.biom"
OUTPUT_PATH = Path("data/processed") / "sample_table.csv"

# ---------------------------------------------------------------------------
# Marcadores de valores ausentes en el mapping file del EMP.
# Se detectaron y validaron con inspect_missing_values.py.
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Grupos de columnas del mapping file relevantes para el KG.
# Separados por categoría para facilitar añadir o quitar campos en el futuro.
#
# ---------------------------------------------------------------------------

# Identificador del estudio de origen (futuro nodo empkg:Study).
FIELDS_IDENTITY = ["study_id"]

# Clasificación jerárquica EMPO (EMP Ontology) del entorno de la muestra.
# empo_0 no se incluye porque en este dataset es constante ("EMP sample").
FIELDS_EMPO = ["empo_1", "empo_2", "empo_3"]

# Descripción ambiental de la muestra.
# Los tres primeros campos (env_*) son texto libre.
# Los envo_biome_* son términos jerarquizados del EMP pre-mapeados (no son URIs ENVO oficiales
FIELDS_ENVIRONMENT = [
    "env_biome",    # texto libre, p.ej. "temperate grassland biome"
    "env_feature",  # texto libre, p.ej. "rhizosphere soil"
    "env_material",  # texto libre, p.ej. "soil"
    "envo_biome_0",  # nivel ENVO más grueso (cobertura 100%)
    "envo_biome_1",  # nivel ENVO nivel 1 (cobertura 100%)
    "envo_biome_2",  # nivel ENVO nivel 2 (cobertura ~98%)
    "envo_biome_3",  # nivel ENVO nivel 3 (cobertura ~72%)
]

# Campos geográficos (futuro nodo empkg:Location).
FIELDS_LOCATION = [
    "country",
    "latitude_deg",
    "longitude_deg",
    "depth_m",
    "altitude_m",
    "elevation_m",
]

# Mediciones físico-químicas de la muestra (propiedades de empkg:Sample).
FIELDS_MEASUREMENTS = [
    "temperature_deg_c",
    "ph",
    "salinity_psu",
    "oxygen_mg_per_l",
]

# Métricas derivadas del BIOM (se añaden en build_sample_stats).
FIELDS_BIOM_STATS = [
    "biom_total_reads",
    "biom_observed_asvs",
]

# ---------------------------------------------------------------------------
# Columnas cuya presencia es obligatoria en el mapping file.
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Columnas numéricas del mapping file.
# Se convierten con pd.to_numeric(errors="coerce") para que los valores
# no convertibles queden como NA en lugar de romper el pipeline.
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Funciones
# ---------------------------------------------------------------------------


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

    Raises:
        ValueError: si algún sample_id es nulo o hay sample_ids duplicados.
    """
    print("=" * 40)
    print("LOADING MAPPING FILE")
    print("=" * 40)

    # keep_default_na=False y na_filter=False evitan que pandas convierta
    # automáticamente "", "nan", "NA", etc. antes de que podamos inspeccionarlos.
    df = pd.read_csv(
        mapping_path,
        sep="\t",
        dtype=str,
        keep_default_na=False,
        na_filter=False,
    )

    print(f"  Filas cargadas:  {df.shape[0]:,}")
    print(f"  Columnas:        {df.shape[1]:,}")

    n_missing_markers = int(df.isin(MISSING_VALUES).sum().sum())
    na_map = {value: pd.NA for value in MISSING_VALUES}
    df = df.replace(na_map)

    print(f"  Valores normalizados a NA: {n_missing_markers:,}")

    df = df.rename(columns={"#SampleID": "sample_id"})

    if df["sample_id"].isna().any():
        raise ValueError("Hay muestras sin sample_id después de normalizar nulos.")

    if df["sample_id"].duplicated().any():
        n_duplicates = int(df["sample_id"].duplicated().sum())
        raise ValueError(f"Hay {n_duplicates} sample_id duplicados en el mapping file.")

    df = df.set_index("sample_id")

    print(f"  Índice: sample_id ({df.index.nunique():,} valores únicos)")

    return df


def validate_required_columns(df: pd.DataFrame) -> None:
    """
    Comprueba que el mapping file contiene las columnas mínimas necesarias.

    Como sample_id ya es el índice, aquí solo se comprueban columnas normales.

    Raises:
        ValueError: si falta alguna columna de REQUIRED_COLUMNS.
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

    Los valores que no puedan convertirse quedan como NA (no rompen el pipeline).
    Si aparecen valores no convertibles en una columna, se imprime un aviso con
    ejemplos para facilitar la depuración.

    Returns:
        Copia del DataFrame con las columnas numéricas convertidas.
    """

    print("\n" + "=" * 40)
    print("CONVERTING NUMERIC COLUMNS")
    print("=" * 40)

    df = df.copy()

    for column in NUMERIC_COLUMNS:
        if column not in df.columns:
            continue

        before_na = df[column].isna().sum()
        original_non_null = df[column].dropna()
        converted = pd.to_numeric(df[column], errors="coerce")
        new_na = int(converted.isna().sum() - before_na)

        df[column] = converted

        if new_na > 0:
            invalid = original_non_null[
                pd.to_numeric(original_non_null, errors="coerce").isna()
            ].unique()
            print(
                f"  AVISO {column}: {new_na} valor(es) no convertible(s). "
                f"Ejemplos: {list(invalid[:3])}"
            )

    print("  Conversión completada.")

    return df


def load_biom_table(biom_path: Path) -> biom.Table:
    """
    Carga el fichero BIOM con biom-format.

    La matriz de abundancias no se convierte a formato denso: todas las
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
    file y el BIOM (ambos indexados por sample_id).

    Se usa ValueError en lugar de assert porque assert puede desactivarse
    con `python -O` y no es adecuado en un pipeline reproducible.

    Raises:
        ValueError: si hay IDs exclusivos de un lado o discrepancia en el total.
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

    if len(common_ids) != len(mapping_ids):
        raise ValueError(
            f"El número de IDs comunes ({len(common_ids):,}) no coincide "
            f"con el total de mapping ({len(mapping_ids):,}) ni de BIOM "
            f"({len(biom_ids):,})."
        )

    print(f"  OK: los {len(common_ids):,} sample_id coinciden exactamente.")


def build_sample_stats(table: biom.Table) -> pd.DataFrame:
    """
    Extrae del BIOM dos métricas agregadas por muestra:

      - biom_total_reads: suma de lecturas de la muestra. En el fichero
        rare_5000, este valor debería ser constante = 5000 para todas las
        muestras (efecto de la rarefacción).
      - biom_observed_asvs: número de ASVs distintos detectados en la muestra
        (celdas no nulas). Es una medida básica de riqueza microbiana.

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
    }).set_index("sample_id").astype({
        "biom_total_reads": "int64",
        "biom_observed_asvs": "int64",
    })

    reads_min = sample_stats["biom_total_reads"].min()
    reads_max = sample_stats["biom_total_reads"].max()
    asvs_med = sample_stats["biom_observed_asvs"].median()
    asvs_min = sample_stats["biom_observed_asvs"].min()
    asvs_max = sample_stats["biom_observed_asvs"].max()

    print(f"  Muestras procesadas:   {sample_stats.shape[0]:,}")
    print(f"  biom_total_reads:      min={reads_min}, max={reads_max}")
    print(
        f"  biom_observed_asvs:    min={asvs_min}, max={asvs_max}, mediana={asvs_med:.0f}")
    print(sample_stats.head())

    return sample_stats


def join_mapping_with_biom(
        mapping: pd.DataFrame,
        sample_stats: pd.DataFrame,
) -> pd.DataFrame:
    """
    Cruza el mapping file con sample_stats mediante un join por sample_id.

    Se asume que validate_sample_ids() ya se ejecutó sin errores. El inner
    join no debería perder filas, pero se verifica explícitamente como
    salvaguarda.

    Returns:
        DataFrame indexado por sample_id con todas las columnas del mapping
        más 'biom_total_reads' y 'biom_observed_asvs'.

    Raises:
        ValueError: si el número de filas resultante no es el esperado.
    """
    print("\n" + "=" * 40)
    print("JOINING MAPPING + BIOM SAMPLE STATS")
    print("=" * 40)

    expected_rows = len(set(mapping.index) & set(sample_stats.index))
    sample_table = mapping.join(sample_stats, how="inner")

    if sample_table.shape[0] != expected_rows:
        raise ValueError(
            f"El join produjo {sample_table.shape[0]:,} filas; "
            f"se esperaban {expected_rows:,}."
        )

    print(f"  Filas:    {sample_table.shape[0]:,}")
    print(f"  Columnas: {sample_table.shape[1]:,}")

    return sample_table


def select_output_columns(sample_table: pd.DataFrame) -> pd.DataFrame:
    """
    Selecciona y ordena las columnas relevantes para el KG.

    La tabla resultante contiene:
      - study_id (identificador del estudio de origen)
      - campos EMPO (clasificación jerárquica del entorno)
      - campos de entorno (texto libre + términos ENVO pre-mapeados)
      - campos de localización (coordenadas, profundidad, altitud)
      - mediciones físico-químicas
      - estadísticas del BIOM (biom_total_reads, biom_observed_asvs)

    El índice (sample_id) no se incluye como columna porque ya es el índice.

    Raises:
        ValueError: si alguna columna esperada no está en la tabla de entrada.
    """
    print("\n" + "=" * 40)
    print("SELECTING OUTPUT COLUMNS")
    print("=" * 40)

    output_columns = (
        FIELDS_IDENTITY
        + FIELDS_EMPO
        + FIELDS_ENVIRONMENT
        + FIELDS_LOCATION
        + FIELDS_MEASUREMENTS
        + FIELDS_BIOM_STATS
    )

    missing_columns = [
        col for col in output_columns
        if col not in sample_table.columns
    ]

    if missing_columns:
        raise ValueError(
            "Faltan columnas esperadas para la tabla final del KG: "
            + ", ".join(missing_columns)
        )

    selected = sample_table[output_columns].copy()

    print(f"  Columnas seleccionadas: {selected.shape[1]:,}")
    print("")
    print(selected.head())

    return selected


def validate_sample_table(sample_table: pd.DataFrame) -> None:
    """
    Valida la tabla final antes de exportarla.

    Comprobaciones críticas (lanzan ValueError si fallan):
      - El índice se llama 'sample_id'.
      - No hay índices duplicados.
      - Están todas las columnas esperadas de salida.
      - 'biom_total_reads' existe y todas las muestras tienen 5.000 lecturas
        (invariante del fichero rare_5000).
      - 'biom_observed_asvs' tiene valores positivos en todas las filas.

    Comprobaciones no críticas (imprimen AVISO si fallan):
      - 'latitude_deg' y 'longitude_deg' son numéricas.
      - 'ph', 'temperature_deg_c', 'salinity_psu', 'oxygen_mg_per_l' son
        numéricas o NA.

    Raises:
        ValueError: si alguna comprobación crítica falla.
    """
    print("\n" + "=" * 40)
    print("VALIDATING SAMPLE TABLE")
    print("=" * 40)

    # --- Comprobaciones críticas ---

    if sample_table.index.name != "sample_id":
        raise ValueError(
            f"El índice de la tabla debería llamarse 'sample_id', "
            f"pero se llama '{sample_table.index.name}'."
        )

    if sample_table.index.duplicated().any():
        n_dup = int(sample_table.index.duplicated().sum())
        raise ValueError(f"Hay {n_dup} sample_id duplicados en la tabla final.")

    output_columns = (
        FIELDS_IDENTITY
        + FIELDS_EMPO
        + FIELDS_ENVIRONMENT
        + FIELDS_LOCATION
        + FIELDS_MEASUREMENTS
        + FIELDS_BIOM_STATS
    )
    missing = [col for col in output_columns if col not in sample_table.columns]
    if missing:
        raise ValueError(
            "La tabla final no contiene todas las columnas esperadas. "
            "Faltan: " + ", ".join(missing)
        )

    if "biom_total_reads" in sample_table.columns:
        expected_reads = 5000
        wrong = sample_table["biom_total_reads"] != expected_reads
        if wrong.any():
            raise ValueError(
                f"Hay {wrong.sum()} muestra(s) con biom_total_reads ≠ {expected_reads}. "
                f"¿Es el fichero rare_{expected_reads} correcto?"
            )

    if "biom_observed_asvs" in sample_table.columns:
        non_positive = sample_table["biom_observed_asvs"] <= 0
        if non_positive.any():
            raise ValueError(
                f"Hay {non_positive.sum()} muestra(s) con biom_observed_asvs ≤ 0."
            )

    print("  OK: comprobaciones críticas superadas.")

    # --- Comprobaciones no críticas ---

    for col in ["latitude_deg", "longitude_deg"]:
        if col in sample_table.columns:
            if not pd.api.types.is_numeric_dtype(sample_table[col]):
                print(f"  AVISO: '{col}' no es de tipo numérico.")

    for col in ["ph", "temperature_deg_c", "salinity_psu", "oxygen_mg_per_l"]:
        if col in sample_table.columns:
            non_numeric_non_na = sample_table[col].dropna()
            if not pd.api.types.is_numeric_dtype(non_numeric_non_na):
                print(f"  AVISO: '{col}' contiene valores no numéricos y no NA.")

    print("  OK: comprobaciones no críticas superadas.")


def export_sample_table(sample_table: pd.DataFrame, output_path: Path) -> None:
    """
    Exporta la tabla final a CSV.

    Crea el directorio de salida si no existe. El índice (sample_id) se
    incluye en el CSV para que pueda usarse como clave al recargar el fichero.

    Args:
        sample_table: DataFrame indexado por sample_id listo para exportar.
        output_path: ruta del fichero CSV de salida.
    """
    print("\n" + "=" * 40)
    print("EXPORTING SAMPLE TABLE")
    print("=" * 40)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sample_table.to_csv(output_path, index=True)

    print(f"  Ruta:     {output_path}")
    print(f"  Filas:    {sample_table.shape[0]:,}")
    print(f"  Columnas: {sample_table.shape[1]:,}  (+ índice sample_id)")


def print_diagnostic_summary(sample_table: pd.DataFrame) -> None:
    """
    Imprime un resumen diagnóstico de la tabla final.

    Incluye:
      - Número de muestras y columnas.
      - Número de estudios únicos.
      - Distribución de empo_3 (tipo de entorno más específico).
      - Estadísticas de biom_total_reads y biom_observed_asvs.
      - Cobertura (% de valores no nulos) de los campos clave para el KG.
    """
    print("\n" + "=" * 40)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 40)

    n_samples = sample_table.shape[0]
    n_columns = sample_table.shape[1]
    n_studies = sample_table["study_id"].nunique()

    print(f"  Muestras:          {n_samples:,}")
    print(f"  Columnas:          {n_columns}")
    print(f"  Estudios únicos:   {n_studies}")

    print("\n  Distribución empo_3:")
    empo3_counts = sample_table["empo_3"].value_counts()
    for category, count in empo3_counts.items():
        pct = count / n_samples * 100
        print(f"    {category:<35} {count:>5}  ({pct:4.1f}%)")

    print("\n  biom_total_reads:")
    reads = sample_table["biom_total_reads"]
    print(f"    min={reads.min()}, max={reads.max()}, media={reads.mean():.0f}")

    print("\n  biom_observed_asvs:")
    asvs = sample_table["biom_observed_asvs"]
    print(
        f"    min={asvs.min()}, max={asvs.max()}, "
        f"mediana={asvs.median():.0f}, media={asvs.mean():.0f}"
    )

    key_fields = [
        "latitude_deg",
        "longitude_deg",
        "ph",
        "temperature_deg_c",
        "salinity_psu",
        "oxygen_mg_per_l",
    ]

    print("\n  Cobertura de campos clave (% no nulos):")
    for field in key_fields:
        if field in sample_table.columns:
            n_filled = sample_table[field].notna().sum()
            pct = n_filled / n_samples * 100
            print(f"    {field:<25}  {n_filled:>5,} / {n_samples:,}  ({pct:5.1f}%)")


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def main() -> None:

    # 1. Cargar y limpiar el mapping file.
    mapping = load_mapping(MAPPING_PATH)
    validate_required_columns(mapping)
    mapping = convert_numeric_columns(mapping)

    # 2. Cargar el BIOM y extraer estadísticas agregadas por muestra.
    table = load_biom_table(BIOM_PATH)
    sample_stats = build_sample_stats(table)

    # 3. Validar que los IDs de muestra coinciden entre mapping y BIOM.
    validate_sample_ids(mapping, sample_stats)

    # 4. Integrar mapping + estadísticas BIOM.
    sample_table = join_mapping_with_biom(mapping, sample_stats)

    # 5. Seleccionar las columnas relevantes para el KG.
    sample_table = select_output_columns(sample_table)

    # 6. Validar la tabla final antes de exportar.
    validate_sample_table(sample_table)

    # 7. Exportar a data/processed/sample_table.csv.
    export_sample_table(sample_table, OUTPUT_PATH)

    # 8. Resumen diagnóstico.
    print_diagnostic_summary(sample_table)


if __name__ == "__main__":
    main()
