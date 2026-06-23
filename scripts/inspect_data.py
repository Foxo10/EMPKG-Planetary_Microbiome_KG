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
import biom
import h5py

# --- Rutas ---
DATA_RAW = Path("data/raw/emp/release1")
MAPPING_PATH = DATA_RAW / "mapping_files" / "emp_qiime_mapping_subset_2k.tsv"
BIOM_PATH = DATA_RAW / "otu_tables" / "deblur" / \
    "emp_deblur_90bp.subset_2k.rare_5000.biom"
OUTPUT_PATH = Path("data/processed") / "sample_summary.csv"


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


def inspect_mapping_file(mapping_path: Path) -> pd.DataFrame:
    """Lee e inspecciona el mapping file de EMP."""

    print("\n" + "=" * 40)
    print("MAPPING FILE")
    print("=" * 40)

    mapping = pd.read_csv(mapping_path, sep="\t", dtype=str)

    print(f"Filas: {mapping.shape[0]:,}  |  Columnas: {mapping.shape[1]:,}")

    print("\nPrimeras columnas:")
    print(mapping.columns[:15].to_list())

    print("\nÚltimas columnas:")
    print(mapping.columns[-15:].to_list())

    print(f"\nTodas las columnas ({mapping.shape[1]}):")
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
                "empo_1",
                "empo_2",
                "empo_3",
            ]
        ].head()
    )

    print("\nDistribución EMPO nivel 1:")
    print(mapping["empo_1"].value_counts())

    print("\nDistribución EMPO nivel 2:")
    print(mapping["empo_2"].value_counts())

    print("\nDistribución EMPO nivel 3:")
    print(mapping["empo_3"].value_counts())

    return mapping


def inspect_biom_file():
    """
    Carga el fichero BIOM con biom-format y muestra estadísticas básicas.
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

    return table


def check_sample_ids(mapping: pd.DataFrame, table: biom.Table) -> None:
    """Comprueba que los IDs de muestra coinciden entre mapping y BIOM."""
    print("\n" + "=" * 40)
    print("COMPROBACIÓN DE IDS")
    print("=" * 40)

    mapping_ids = set(mapping["#SampleID"])
    biom_ids = set(table.ids(axis="sample"))

    common_ids = mapping_ids.intersection(biom_ids)
    only_mapping = mapping_ids.difference(biom_ids)
    only_biom = biom_ids.difference(mapping_ids)

    print(f"Muestras en mapping file: {len(mapping_ids)}")
    print(f"Muestras en BIOM: {len(biom_ids)}")
    print(f"Muestras comunes: {len(common_ids)}")
    print(f"Solo en mapping: {len(only_mapping)}")
    print(f"Solo en BIOM: {len(only_biom)}")

    if len(common_ids) == len(mapping_ids) == len(biom_ids):
        print("\nOK: todos los IDs de muestra coinciden.")
    else:
        print("\nAVISO: hay IDs que no coinciden.")


def main() -> None:
    inspect_hdf5_structure(BIOM_PATH)
    mapping = inspect_mapping_file(MAPPING_PATH)
    table = inspect_biom_file()
    check_sample_ids(mapping, table)


if __name__ == "__main__":
    main()
