"""
csv_to_rdf.py

Genera el RDF/Turtle v0 de EMPKG-lite a partir de un CSV de muestras.

Entrada por defecto:
    data/samples/kg_v0_test_samples.csv

Salida por defecto:
    data/processed/empkg_v0_test.ttl

Alcance v0:
    Sample, Study, Location, EMPOCategory, EnvironmentDescription

Uso:
    python scripts/csv_to_rdf.py
    python scripts/csv_to_rdf.py --input data/samples/kg_v0_test_samples.csv --output data/processed/empkg_v0_test.ttl
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import pandas as pd
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, XSD

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------

EXPECTED_COLUMNS = [
    "sample_id",
    "study_id",
    "empo_1",
    "empo_2",
    "empo_3",
    "env_biome",
    "env_feature",
    "env_material",
    "envo_biome_0",
    "envo_biome_1",
    "envo_biome_2",
    "envo_biome_3",
    "country",
    "latitude_deg",
    "longitude_deg",
    "depth_m",
    "altitude_m",
    "elevation_m",
    "temperature_deg_c",
    "ph",
    "salinity_psu",
    "oxygen_mg_per_l",
    "biom_total_reads",
    "biom_observed_asvs",
]

MISSING_STRINGS = {
    "",
    "nan",
    "none",
    "null",
    "na",
    "n/a",
    "unknown",
    "missing: not provided",
    "not applicable",
    "not provided",
}

CLASSES = {
    "Sample": "Sample",
    "Study": "Study",
    "Location": "Location",
    "EMPOCategory": "EMPO category",
    "EnvironmentDescription": "Environment description",
}

RELATIONS = {
    "belongsToStudy": {
        "domain": "Sample",
        "range": "Study",
        "label": "belongs to study",
    },
    "wasCollectedAt": {
        "domain": "Sample",
        "range": "Location",
        "label": "was collected at",
    },
    "hasEMPOCategory": {
        "domain": "Sample",
        "range": "EMPOCategory",
        "label": "has EMPO category",
    },
    "hasEnvironmentDescription": {
        "domain": "Sample",
        "range": "EnvironmentDescription",
        "label": "has environment description",
    },
}

SAMPLE_DECIMAL_PROPERTIES = {
    "temperature_deg_c": "temperatureDegC",
    "ph": "ph",
    "salinity_psu": "salinityPsu",
    "oxygen_mg_per_l": "oxygenMgPerL",
}

SAMPLE_INTEGER_PROPERTIES = {
    "biom_total_reads": "biomTotalReads",
    "biom_observed_asvs": "biomObservedASVs",
}

RELATION_PREDICATES = [
    "belongsToStudy",
    "wasCollectedAt",
    "hasEMPOCategory",
    "hasEnvironmentDescription",
]

BAD_LITERAL_VALUES = {"", "nan", "none", "null", "unknown"}

EMPKG = Namespace("https://w3id.org/empkg/ontology/")
SAMPLE = Namespace("https://w3id.org/empkg/resource/sample/")
STUDY = Namespace("https://w3id.org/empkg/resource/study/")
LOC = Namespace("https://w3id.org/empkg/resource/location/")
EMPO = Namespace("https://w3id.org/empkg/resource/empo-category/")
ENVDESC = Namespace("https://w3id.org/empkg/resource/environment-description/")
SCHEMA = Namespace("https://schema.org/")

PROJECT_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_NON_NULL_COLUMNS = [
    "sample_id",
    "study_id",
    "empo_1",
    "empo_2",
    "empo_3",
]


def default_input_path() -> Path:
    return PROJECT_ROOT / "data" / "samples" / "kg_v0_test_samples.csv"


def default_output_path() -> Path:
    return PROJECT_ROOT / "data" / "processed" / "empkg_v0_test.ttl"


# ---------------------------------------------------------------------------
# Limpieza y sanitización
# ---------------------------------------------------------------------------


def is_missing(value: Any) -> bool:
    """Devuelve True si el valor debe considerarse ausente."""
    if pd.isna(value):
        return True

    if isinstance(value, str):
        clean = value.strip().lower()
        return clean in MISSING_STRINGS

    return False


def sanitize_id_for_uri(value: Any) -> str:
    """Sanitiza identificadores técnicos conservando mayúsculas/minúsculas."""
    if is_missing(value):
        raise ValueError("No se puede sanitizar un valor ausente para URI.")

    text = str(value).strip()
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text)
    text = text.strip("_")
    text = re.sub(r"_+", "_", text)
    return text


def sanitize_label_for_uri(value: Any) -> str:
    """Sanitiza etiquetas textuales normalizadas a minúsculas."""
    if is_missing(value):
        raise ValueError("No se puede sanitizar un valor ausente para URI.")

    text = str(value).strip().lower()
    text = text.replace("(non-saline)", "non saline")
    text = text.replace("(saline)", "saline")
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text)
    text = text.strip("_")
    text = re.sub(r"_+", "_", text)
    return text


def canonical_decimal_for_location(value: Any) -> str | None:
    """Normaliza un número para construir una clave de Location estable."""
    if is_missing(value):
        return None

    try:
        number = Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"No se puede normalizar el valor espacial {value!r}") from exc

    if not number.is_finite():
        raise ValueError(f"El valor espacial no es finito: {value!r}")

    # Evita diferencias entre 0, 0.0 y -0.0.
    if number == 0:
        return "0"

    text = format(number.normalize(), "f")

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    return text


def canonical_country_for_location(value: Any) -> str | None:
    """Normaliza el país para la clave interna de Location."""
    if is_missing(value):
        return None

    text = str(value).strip()

    if text.startswith("GAZ:"):
        text = text.removeprefix("GAZ:")

    # Normaliza espacios y mayúsculas.
    return " ".join(text.split()).casefold()


# ---------------------------------------------------------------------------
# Constructores de URI
# ---------------------------------------------------------------------------


def make_sample_uri(sample_id: Any) -> URIRef:
    return SAMPLE[sanitize_id_for_uri(sample_id)]


def make_study_uri(study_id: Any) -> URIRef:
    return STUDY[sanitize_id_for_uri(study_id)]


def make_empo_uri(empo_3: Any) -> URIRef:
    return EMPO[sanitize_label_for_uri(empo_3)]


def make_environment_description_uri(sample_id: Any) -> URIRef:
    return ENVDESC[sanitize_id_for_uri(sample_id)]


def make_location_key(row: pd.Series) -> str:
    """
    Construye una representación canónica y determinista de la localización.
    """
    values = {
        "country": canonical_country_for_location(row["country"]),
        "latitude_deg": canonical_decimal_for_location(row["latitude_deg"]),
        "longitude_deg": canonical_decimal_for_location(row["longitude_deg"]),
        "depth_m": canonical_decimal_for_location(row["depth_m"]),
        "altitude_m": canonical_decimal_for_location(row["altitude_m"]),
        "elevation_m": canonical_decimal_for_location(row["elevation_m"]),
    }

    # Sin coordenadas no hay evidencia suficiente para afirmar que dos
    # muestras del mismo país proceden exactamente del mismo lugar.
    if values["latitude_deg"] is None or values["longitude_deg"] is None:
        values["sample_id_fallback"] = str(row["sample_id"]).strip()

    return json.dumps(
        values,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def make_location_uri(row: pd.Series) -> URIRef:
    location_key = make_location_key(row)

    location_hash = hashlib.sha256(location_key.encode("utf-8")).hexdigest()[:16]

    return LOC[location_hash]


def make_location_label(row: pd.Series) -> str:
    lat = row["latitude_deg"]
    lon = row["longitude_deg"]

    if not is_missing(lat) and not is_missing(lon):
        return f"Location {lat}, {lon}"

    country = row["country"]
    if not is_missing(country):
        return f"Location {country}"

    return "Location"


# ---------------------------------------------------------------------------
# Grafo RDF
# ---------------------------------------------------------------------------


def create_empty_graph() -> Graph:
    graph = Graph()
    graph.bind("empkg", EMPKG)
    graph.bind("sample", SAMPLE)
    graph.bind("study", STUDY)
    graph.bind("loc", LOC)
    graph.bind("empo", EMPO)
    graph.bind("envdesc", ENVDESC)
    graph.bind("rdf", RDF)
    graph.bind("rdfs", RDFS)
    graph.bind("xsd", XSD)
    graph.bind("schema", SCHEMA)
    return graph


def add_model_layer(graph: Graph) -> None:
    for class_name, label in CLASSES.items():
        class_uri = EMPKG[class_name]
        graph.add((class_uri, RDF.type, RDFS.Class))
        graph.add((class_uri, RDFS.label, Literal(label)))

    for property_name, info in RELATIONS.items():
        property_uri = EMPKG[property_name]
        domain_uri = EMPKG[info["domain"]]
        range_uri = EMPKG[info["range"]]
        graph.add((property_uri, RDF.type, RDF.Property))
        graph.add((property_uri, RDFS.domain, domain_uri))
        graph.add((property_uri, RDFS.range, range_uri))
        graph.add((property_uri, RDFS.label, Literal(info["label"])))


def add_text_literal_if_present(
    graph: Graph,
    subject: URIRef,
    predicate: URIRef,
    value: Any,
) -> None:
    if is_missing(value):
        return

    text = str(value).strip()
    if text == "":
        return

    graph.add((subject, predicate, Literal(text)))


def add_decimal_literal_if_present(
    graph: Graph,
    subject: URIRef,
    predicate: URIRef,
    value: Any,
) -> None:
    if is_missing(value):
        return

    try:
        decimal_value = Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(
            f"No se puede convertir a xsd:decimal: {value!r} para el predicado {predicate}"
        ) from exc

    graph.add((subject, predicate, Literal(decimal_value, datatype=XSD.decimal)))


def add_integer_literal_if_present(
    graph: Graph,
    subject: URIRef,
    predicate: URIRef,
    value: Any,
) -> None:
    if is_missing(value):
        return

    try:
        decimal_value = Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(
            f"No se puede convertir a xsd:integer: {value!r} para el predicado {predicate}"
        ) from exc

    if decimal_value != decimal_value.to_integral_value():
        raise ValueError(
            f"El valor no es entero: {value!r} para el predicado {predicate}"
        )

    graph.add((subject, predicate, Literal(int(decimal_value), datatype=XSD.integer)))


def add_study(graph: Graph, row: pd.Series) -> URIRef:
    study_id = row["study_id"]
    study_uri = make_study_uri(study_id)

    graph.add((study_uri, RDF.type, EMPKG.Study))
    add_text_literal_if_present(graph, study_uri, RDFS.label, f"Study {study_id}")
    add_text_literal_if_present(graph, study_uri, EMPKG.studyId, study_id)
    return study_uri


def add_empo_category(graph: Graph, row: pd.Series) -> URIRef:
    empo_uri = make_empo_uri(row["empo_3"])

    graph.add((empo_uri, RDF.type, EMPKG.EMPOCategory))
    add_text_literal_if_present(graph, empo_uri, RDFS.label, row["empo_3"])
    add_text_literal_if_present(graph, empo_uri, EMPKG.empo1, row["empo_1"])
    add_text_literal_if_present(graph, empo_uri, EMPKG.empo2, row["empo_2"])
    add_text_literal_if_present(graph, empo_uri, EMPKG.empo3, row["empo_3"])
    return empo_uri


def add_location(graph: Graph, row: pd.Series) -> URIRef:
    loc_uri = make_location_uri(row)

    graph.add((loc_uri, RDF.type, EMPKG.Location))
    add_text_literal_if_present(graph, loc_uri, RDFS.label, make_location_label(row))
    add_text_literal_if_present(graph, loc_uri, EMPKG.country, row["country"])
    add_decimal_literal_if_present(graph, loc_uri, SCHEMA.latitude, row["latitude_deg"])
    add_decimal_literal_if_present(
        graph, loc_uri, SCHEMA.longitude, row["longitude_deg"]
    )
    add_decimal_literal_if_present(graph, loc_uri, EMPKG.depthM, row["depth_m"])
    add_decimal_literal_if_present(graph, loc_uri, EMPKG.altitudeM, row["altitude_m"])
    add_decimal_literal_if_present(graph, loc_uri, EMPKG.elevationM, row["elevation_m"])
    return loc_uri


def add_environment_description(graph: Graph, row: pd.Series) -> URIRef:
    env_uri = make_environment_description_uri(row["sample_id"])

    graph.add((env_uri, RDF.type, EMPKG.EnvironmentDescription))
    add_text_literal_if_present(graph, env_uri, EMPKG.envBiome, row["env_biome"])
    add_text_literal_if_present(graph, env_uri, EMPKG.envFeature, row["env_feature"])
    add_text_literal_if_present(graph, env_uri, EMPKG.envMaterial, row["env_material"])
    add_text_literal_if_present(graph, env_uri, EMPKG.envoBiome0, row["envo_biome_0"])
    add_text_literal_if_present(graph, env_uri, EMPKG.envoBiome1, row["envo_biome_1"])
    add_text_literal_if_present(graph, env_uri, EMPKG.envoBiome2, row["envo_biome_2"])
    add_text_literal_if_present(graph, env_uri, EMPKG.envoBiome3, row["envo_biome_3"])
    return env_uri


def add_sample(graph: Graph, row: pd.Series) -> URIRef:
    sample_id = row["sample_id"]
    sample_uri = make_sample_uri(sample_id)

    study_uri = add_study(graph, row)
    empo_uri = add_empo_category(graph, row)
    loc_uri = add_location(graph, row)
    env_uri = add_environment_description(graph, row)

    graph.add((sample_uri, RDF.type, EMPKG.Sample))
    add_text_literal_if_present(graph, sample_uri, RDFS.label, f"Sample {sample_id}")
    add_text_literal_if_present(graph, sample_uri, EMPKG.sampleId, sample_id)

    graph.add((sample_uri, EMPKG.belongsToStudy, study_uri))
    graph.add((sample_uri, EMPKG.hasEMPOCategory, empo_uri))
    graph.add((sample_uri, EMPKG.wasCollectedAt, loc_uri))
    graph.add((sample_uri, EMPKG.hasEnvironmentDescription, env_uri))

    for csv_column, property_name in SAMPLE_DECIMAL_PROPERTIES.items():
        add_decimal_literal_if_present(
            graph, sample_uri, EMPKG[property_name], row[csv_column]
        )

    for csv_column, property_name in SAMPLE_INTEGER_PROPERTIES.items():
        add_integer_literal_if_present(
            graph, sample_uri, EMPKG[property_name], row[csv_column]
        )

    return sample_uri


# ---------------------------------------------------------------------------
# Validación y E/S
# ---------------------------------------------------------------------------


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No existe el CSV de entrada: {path}")

    df = pd.read_csv(path)

    missing_columns = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Faltan columnas esperadas: {missing_columns}")

    extra_columns = [col for col in df.columns if col not in EXPECTED_COLUMNS]
    if extra_columns:
        print(
            f"AVISO: hay columnas extra no esperadas: {extra_columns}", file=sys.stderr
        )

    if df["sample_id"].duplicated().any():
        duplicated = df.loc[df["sample_id"].duplicated(), "sample_id"].tolist()
        raise ValueError(f"Hay sample_id duplicados: {duplicated}")

    for column in REQUIRED_NON_NULL_COLUMNS:
        missing_mask = df[column].apply(is_missing)

        if missing_mask.any():
            raise ValueError(f"Hay {int(missing_mask.sum())} filas sin {column}")

    return df


def build_graph_from_dataframe(df: pd.DataFrame) -> Graph:
    graph = create_empty_graph()
    add_model_layer(graph)

    for _, row in df.iterrows():
        add_sample(graph, row)

    return graph


def count_subjects_of_type(graph: Graph, rdf_class: URIRef) -> int:
    return len(set(graph.subjects(RDF.type, rdf_class)))


def count_triples_with_predicate(graph: Graph, predicate: URIRef) -> int:
    return len(list(graph.triples((None, predicate, None))))


def find_bad_literals(graph: Graph) -> list[tuple[URIRef, URIRef, Literal]]:
    bad_literals: list[tuple[URIRef, URIRef, Literal]] = []

    for subject, predicate, obj in graph:
        if isinstance(obj, Literal):
            lexical = str(obj).strip().lower()
            if lexical in BAD_LITERAL_VALUES:
                bad_literals.append((subject, predicate, obj))

    return bad_literals


def _validate_sample_relations(graph: Graph) -> None:
    samples = set(graph.subjects(RDF.type, EMPKG.Sample))

    for relation_name in RELATION_PREDICATES:
        predicate = EMPKG[relation_name]
        for sample_uri in samples:
            count = len(list(graph.triples((sample_uri, predicate, None))))
            if count != 1:
                raise ValueError(
                    f"El Sample {sample_uri} tiene {count} relaciones {relation_name}; se esperaba 1"
                )


def _validate_location_mapping(graph: Graph, df: pd.DataFrame) -> None:
    """
    Valida que cada Sample apunte a la Location derivada de su fila de origen.

    Esta comprobación no exige que haya localizaciones reutilizadas: un CSV con
    una sola muestra o con todas las localizaciones distintas es válido. Cuando
    dos filas producen la misma clave canónica, ambas deben apuntar a la misma
    URI. También se detectaría una eventual colisión del hash abreviado si dos
    claves canónicas diferentes produjeran la misma URI.
    """
    key_by_location_uri: dict[URIRef, str] = {}

    for _, row in df.iterrows():
        sample_uri = make_sample_uri(row["sample_id"])
        actual_locations = list(graph.objects(sample_uri, EMPKG.wasCollectedAt))

        if len(actual_locations) != 1:
            raise ValueError(
                f"El Sample {sample_uri} tiene {len(actual_locations)} relaciones "
                "wasCollectedAt; se esperaba 1"
            )

        actual_location_uri = actual_locations[0]
        expected_location_key = make_location_key(row)
        expected_location_uri = make_location_uri(row)

        if actual_location_uri != expected_location_uri:
            raise ValueError(
                f"El Sample {sample_uri} apunta a {actual_location_uri}, pero la "
                f"Location esperada es {expected_location_uri}"
            )

        previous_key = key_by_location_uri.get(actual_location_uri)
        if previous_key is not None and previous_key != expected_location_key:
            raise ValueError(
                "Se detectó una colisión de URI de Location: dos claves "
                f"canónicas distintas producen {actual_location_uri}"
            )

        key_by_location_uri[actual_location_uri] = expected_location_key


def validate_graph(graph: Graph, df: pd.DataFrame) -> dict[str, int]:
    summary = {
        "triples_total": len(graph),
        "samples": count_subjects_of_type(graph, EMPKG.Sample),
        "studies": count_subjects_of_type(graph, EMPKG.Study),
        "locations": count_subjects_of_type(graph, EMPKG.Location),
        "empo_categories": count_subjects_of_type(graph, EMPKG.EMPOCategory),
        "environment_descriptions": count_subjects_of_type(
            graph, EMPKG.EnvironmentDescription
        ),
        "belongs_to_study": count_triples_with_predicate(graph, EMPKG.belongsToStudy),
        "was_collected_at": count_triples_with_predicate(graph, EMPKG.wasCollectedAt),
        "has_empo_category": count_triples_with_predicate(graph, EMPKG.hasEMPOCategory),
        "has_environment_description": count_triples_with_predicate(
            graph, EMPKG.hasEnvironmentDescription
        ),
        "bad_literals": len(find_bad_literals(graph)),
    }

    expected_samples = len(df)
    expected_studies = df["study_id"].nunique()
    expected_locations = len({make_location_key(row) for _, row in df.iterrows()})
    expected_empo = df["empo_3"].nunique()

    if summary["samples"] != expected_samples:
        raise ValueError(
            f"Se esperaban {expected_samples} Sample, pero hay {summary['samples']}"
        )
    if summary["studies"] != expected_studies:
        raise ValueError(
            f"Se esperaban {expected_studies} Study, pero hay {summary['studies']}"
        )
    if summary["locations"] != expected_locations:
        raise ValueError(
            f"Se esperaban {expected_locations} Location, pero hay {summary['locations']}"
        )
    if summary["empo_categories"] != expected_empo:
        raise ValueError(
            f"Se esperaban {expected_empo} EMPOCategory, pero hay {summary['empo_categories']}"
        )
    if summary["environment_descriptions"] != expected_samples:
        raise ValueError(
            "Se esperaban "
            f"{expected_samples} EnvironmentDescription, pero hay "
            f"{summary['environment_descriptions']}"
        )

    for key in (
        "belongs_to_study",
        "was_collected_at",
        "has_empo_category",
        "has_environment_description",
    ):
        if summary[key] != expected_samples:
            raise ValueError(
                f"Se esperaban {expected_samples} triples de {key}, pero hay {summary[key]}"
            )

    if summary["bad_literals"] != 0:
        raise ValueError(
            f"Se encontraron {summary['bad_literals']} literales problemáticos en el grafo"
        )

    _validate_sample_relations(graph)
    _validate_location_mapping(graph, df)

    return summary


def serialize_graph(graph: Graph, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    graph.serialize(destination=str(output_path), format="turtle")


def parse_ttl(path: Path) -> Graph:
    graph = create_empty_graph()
    graph.parse(str(path), format="turtle")

    print(f"El Turtle recargado tiene {len(graph)} triples")

    return graph


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera RDF/Turtle v0 de EMPKG-lite desde un CSV de muestras."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=default_input_path(),
        help="Ruta al CSV de entrada",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=default_output_path(),
        help="Ruta al fichero Turtle de salida",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    print(f"Entrada: {args.input}")
    print(f"Salida:  {args.output}")

    df = load_csv(args.input)
    graph = build_graph_from_dataframe(df)
    summary = validate_graph(graph, df)

    serialize_graph(graph, args.output)
    reloaded = parse_ttl(args.output)
    validate_graph(reloaded, df)

    print(f"Triples generados: {summary['triples_total']}")
    print(f"Samples: {summary['samples']}")
    print(f"Studies: {summary['studies']}")
    print(f"Locations: {summary['locations']}")
    print(f"EMPO categories: {summary['empo_categories']}")
    print(f"Environment descriptions: {summary['environment_descriptions']}")
    print(f"Turtle generado en: {args.output}")
    print("OK: validaciones principales superadas.")


if __name__ == "__main__":
    main()
