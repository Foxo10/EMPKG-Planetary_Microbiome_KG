"""
inspect_data.py

Inspecciona los datos iniciales descargados de EMP Release 1:

- Mapping file: metadatos de muestras.
- BIOM file: matriz de abundancias y taxonomía.

Además de imprimir los resultados por pantalla, exporta CSVs de diagnóstico
en data/inspection/:
 
    mapping_field_coverage.csv    — cobertura (nulos y %) de cada campo del mapping
    mapping_empo_distribution.csv — distribución de muestras por categoría EMPO (niveles 1-3)
    biom_summary.csv              — métricas generales del BIOM (dimensiones, densidad…)
    biom_taxonomy_sample.csv      — primeros N ASVs con su taxonomía desglosada por nivel
    id_validation.csv             — resultado de la validación de IDs entre BIOM y mapping
 
Uso:
    python scripts/inspect_data.py
"""

from pathlib import Path

import pandas as pd
import biom
import h5py

# --- Rutas ---
DATA_RAW = Path("data/raw/emp/release1")
MAPPING_PATH = DATA_RAW / "mapping_files" / "emp_qiime_mapping_subset_2k.tsv"
BIOM_PATH = DATA_RAW / "otu_tables" / "deblur" / \
    "emp_deblur_90bp.subset_2k.rare_5000.biom"

# Carpeta de salida para los CSVs de diagnóstico.
INSPECTION_DIR = Path("data/inspection")


def inspect_hdf5_structure(biom_path: Path) -> None:
    """Recorre la estructura jerárquica del HDF5 e imprime grupos y datasets."""
    def _visitor(name, obj):
        indent = "  " * name.count("/")
        kind = "GROUP" if isinstance(obj, h5py.Group) else "DATASET"
        shape = getattr(obj, "shape", "")
        print(f"{indent}{kind}: /{name}  {shape}")

    print("=" * 40)
    print("HDF5 STRUCTURE")
    print("=" * 40 + "\n")

    with h5py.File(biom_path, 'r') as f:
        # file_attr_names = list(f.attrs.keys())
        print(f"File attributes:")

        for k in f.attrs.keys():
            print("  " + f"{k} => {f.attrs[k]}")
        print("")

        f.visititems(_visitor)


def inspect_mapping_file(mapping_path: Path, output_dir: Path | None = None) -> pd.DataFrame:
    """
    Lee e inspecciona el mapping file de EMP.

    Si se especifica output_dir, exporta:
    - mapping_field_coverage.csv: cobertura (nulos y %) de cada campo.
    - mapping_empo_distribution.csv: distribución de muestras por categoría EMPO.
    """

    print("\n" + "=" * 40)
    print("MAPPING FILE")
    print("=" * 40)

    mapping = pd.read_csv(mapping_path, sep="\t", dtype=str)
    n_rows, n_cols = mapping.shape

    print(f"Filas: {n_rows:,}  |  Columnas: {n_cols:,}")

    print("\nPrimeras columnas:")
    print(mapping.columns[:15].to_list())

    print("\nÚltimas columnas:")
    print(mapping.columns[-15:].to_list())

    print(f"\nTodas las columnas ({n_cols}):")
    for i, col in enumerate(mapping.columns):
        n_nulls = mapping[col].isna().sum()
        print(f"  {i:3d}. {col:<40}  nulos/NA: {n_nulls}")

    print("\nPrimeras muestras:")
    print(
        mapping[
            [
                "#SampleID",
                "Description",
                "study_id",
                "empo_0",
                "empo_1",
                "empo_2",
                "empo_3",
            ]
        ].head()
    )

    print("\nPrimeras muestras:")
    print(
        mapping[["#SampleID", "Description", "study_id", "empo_0",
                 "empo_1", "empo_2", "empo_3"]].head()
    )

    print("\nDistribución EMPO nivel 0:")
    print(mapping["empo_0"].value_counts())

    print("\nDistribución EMPO nivel 1:")
    print(mapping["empo_1"].value_counts())

    print("\nDistribución EMPO nivel 2:")
    print(mapping["empo_2"].value_counts())

    print("\nDistribución EMPO nivel 3:")
    print(mapping["empo_3"].value_counts())

    # --- Exportación ---
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)

        # CSV 1: cobertura de campos
        # Cada fila es un campo del mapping file con su número y porcentaje de nulos.

        coverage = pd.DataFrame({
            "field": mapping.columns,
            "null_count": [mapping[col].isna().sum() for col in mapping.columns],
            "total": n_rows,
        })
        coverage["null_pct"] = (coverage["null_count"] / n_rows * 100).round(1)
        coverage["filled_count"] = n_rows - coverage["null_count"]
        coverage["filled_pct"] = (100 - coverage["null_pct"]).round(1)

        path_coverage = output_dir / "mapping_field_coverage.csv"
        coverage.to_csv(path_coverage, index=False)
        print(f"\n[CSV] Cobertura de campos → {path_coverage}")

        # CSV 2: distribución EMPO
        # Concatena los value_counts de los cuatro niveles en una sola tabla.
        empo_rows = []
        for level in ["empo_0", "empo_1", "empo_2", "empo_3"]:
            counts = mapping[level].value_counts().reset_index()
            counts.columns = ["category", "count"]
            counts.insert(0, "empo_level", level)
            counts["pct"] = (counts["count"] / n_rows * 100).round(1)
            empo_rows.append(counts)

        empo_dist = pd.concat(empo_rows, ignore_index=True)

        path_empo = output_dir / "mapping_empo_distribution.csv"
        empo_dist.to_csv(path_empo, index=False)
        print(f"[CSV] Distribución EMPO       → {path_empo}")

    return mapping


def inspect_biom_file(
    biom_path: Path = BIOM_PATH,
    output_dir: Path | None = None,
    taxonomy_sample_size: int = 20,
) -> biom.Table:
    """
    Carga el fichero BIOM con biom-format y muestra estadísticas básicas.

    Si se especifica output_dir, exporta:
    - biom_summary.csv: métricas generales del BIOM.
    - biom_taxonomy_sample.csv: primeros N ASVs con su taxonomía desglosada.

    Args:
        biom_path: ruta al fichero BIOM.
        output_dir: carpeta de salida para los CSVs. Si es None, no exporta.
        taxonomy_sample_size: número de ASVs a incluir en el CSV de taxonomía.
    """

    print("\n" + "=" * 40)
    print("BIOM FILE")
    print("=" * 40 + "\n")

    table = biom.load_table(str(BIOM_PATH))
    n_obs, n_samples = table.shape

    print(f"ID tabla: {table.table_id}")
    print(f"Versión: {table.format_version}")
    # "ASU table" no está definido como tipo de tabla.
    print(f"Observaciones {table.type.split(' ')[0]}s : {n_obs:,}")
    print(f"Muestras:             {n_samples:,}")
    # La densidad indica qué fracción de celdas son no-cero.
    # En microbiomas es típicamente baja (0.01 - 0.05).
    print(f"Valores no nulos: {table.nnz}")
    print(
        f"Densidad de la matriz:             {table.get_table_density():.2%}")

    # IDs de muestras
    sample_ids = list(table.ids(axis="sample"))
    print(f"\nPrimeros 5 IDs de muestra: \n{sample_ids[:5]}")

    # IDs de observaciones
    obs_ids = list(table.ids(axis="observation"))
    print(
        f"Primeros 5 IDs de ASV/OTU (secuencias): \n{[s[:20] + '...' for s in obs_ids[:5]]}")

    # Metadatos de observaciones: taxonomia
    obs_meta = table.metadata(axis="observation")
    print(f"\nCampos en metadatos de observación: {list(obs_meta[0].keys())}")

    # Metadatos de muestras dentro del BIOM
    sample_meta = table.metadata(axis="sample")
    if sample_meta and len(sample_meta) > 0:
        print(
            f"\nCampos en metadatos de muestra (dentro del BIOM): {list(sample_meta[0].keys())}")
    else:
        print("\nLos metadatos de muestra no están en el BIOM.")
        print("(Están en el mapping file TSV — lo habitual en EMP.)")

    first_observation_id = obs_ids[0]
    first_observation_metadata = table.metadata(
        id=first_observation_id,
        axis="observation",
    )

    print("\nMetadatos de la primera observación:")
    print(first_observation_metadata)

    # --- Exportación ---
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)

        # CSV 1: métricas generales del BIOM
        # Una tabla de dos columnas (métrica, valor) que resume el fichero.
        # Útil para comparar entre distintos subsets o versiones del BIOM.
        summary = pd.DataFrame([
            {"metric": "n_asvs",          "value": n_obs},
            {"metric": "n_samples",        "value": n_samples},
            {"metric": "nnz",              "value": table.nnz},
            {"metric": "density",          "value": round(
                table.get_table_density(), 6)},
            {"metric": "table_id",         "value": table.table_id},
            {"metric": "format_version",   "value": str(table.format_version)},
            {"metric": "biom_path",        "value": str(biom_path)},
        ])

        path_summary = output_dir / "biom_summary.csv"
        summary.to_csv(path_summary, index=False)
        print(f"\n[CSV] Métricas BIOM           → {path_summary}")

        # CSV 2: muestra de taxonomía de los primeros N ASVs
        # Desglosa el campo taxonomy (lista de 7 niveles) en columnas separadas.
        # Los niveles siguen la notación Greengenes: k__, p__, c__, o__, f__, g__, s__
        tax_levels = ["kingdom", "phylum", "class",
                      "order", "family", "genus", "species"]
        tax_rows = []

        for asv_id in obs_ids[:taxonomy_sample_size]:
            meta = table.metadata(id=asv_id, axis="observation")
            tax_raw = meta.get("taxonomy", [])

            # Cada elemento tiene el formato "k__Bacteria", "p__Proteobacteria", etc.
            # Eliminamos el prefijo de dos caracteres (k__, p__…) para dejar solo el nombre.
            tax_clean = [t[3:] if len(t) > 3 else "" for t in tax_raw]

            # Si por algún motivo hay menos de 7 niveles, rellenamos con cadena vacía.
            tax_clean += [""] * (len(tax_levels) - len(tax_clean))

            row = {"asv_id": asv_id[:30] + "..."}
            row.update(dict(zip(tax_levels, tax_clean)))
            tax_rows.append(row)

        tax_df = pd.DataFrame(tax_rows)

        path_tax = output_dir / "biom_taxonomy_sample.csv"
        tax_df.to_csv(path_tax, index=False)
        print(
            f"[CSV] Muestra de taxonomía    → {path_tax}  ({taxonomy_sample_size} ASVs)")

    return table


def check_sample_ids(
        mapping: pd.DataFrame,
        table: biom.Table,
        output_dir: Path | None = None
) -> None:
    """
    Comprueba que los IDs de muestra coinciden entre mapping y BIOM.

    Si se especifica output_dir, exporta:
    - id_validation.csv: resumen del cruce de IDs con estado de validación.
    """

    print("\n" + "=" * 40)
    print("COMPROBACIÓN DE IDS")
    print("=" * 40)

    mapping_ids = set(mapping["#SampleID"])
    biom_ids = set(table.ids(axis="sample"))

    common_ids = mapping_ids.intersection(biom_ids)
    only_mapping = mapping_ids.difference(biom_ids)
    only_biom = biom_ids.difference(mapping_ids)
    all_match = len(common_ids) == len(mapping_ids) == len(biom_ids)

    print(f"Muestras en mapping file: {len(mapping_ids)}")
    print(f"Muestras en BIOM: {len(biom_ids)}")
    print(f"Muestras comunes: {len(common_ids)}")
    print(f"Solo en mapping: {len(only_mapping)}")
    print(f"Solo en BIOM: {len(only_biom)}")

    if all_match:
        print("\nOK: todos los IDs de muestra coinciden.")
    else:
        print("\nAVISO: hay IDs que no coinciden.")

    # --- Exportación ---
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)

        validation = pd.DataFrame([
            {"check": "mapping_ids",  "count": len(mapping_ids)},
            {"check": "biom_ids",     "count": len(biom_ids)},
            {"check": "common_ids",   "count": len(common_ids)},
            {"check": "only_mapping", "count": len(only_mapping)},
            {"check": "only_biom",    "count": len(only_biom)},
            {"check": "all_match",    "count": int(all_match)},
        ])

        path_val = output_dir / "id_validation.csv"
        validation.to_csv(path_val, index=False)
        print(f"\n[CSV] Validación de IDs       → {path_val}")


def main() -> None:
    inspect_hdf5_structure(BIOM_PATH)
    mapping = inspect_mapping_file(MAPPING_PATH, output_dir=INSPECTION_DIR)
    table = inspect_biom_file(BIOM_PATH, output_dir=INSPECTION_DIR)
    check_sample_ids(mapping, table, output_dir=INSPECTION_DIR)


if __name__ == "__main__":
    main()
