from __future__ import annotations

import importlib.util
import sys
from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import RDF, XSD

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "03_to_rdf.py"
INPUT_CSV = PROJECT_ROOT / "data" / "samples" / "kg_v0_test_samples.csv"

EMPKG = Namespace("https://w3id.org/empkg/ontology/")


def _load_rdf_module():
    spec = importlib.util.spec_from_file_location("to_rdf_03", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"No se pudo cargar el módulo desde {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["to_rdf_03"] = module
    spec.loader.exec_module(module)
    return module


rdf = _load_rdf_module()


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, True),
        (pd.NA, True),
        (float("nan"), True),
        ("", True),
        (" ", True),
        ("unknown", True),
        ("Unknown", True),
        ("Missing: Not provided", True),
        ("marine biome", False),
    ],
)
def test_is_missing(value, expected) -> None:
    assert rdf.is_missing(value) is expected


def test_sanitize_id_for_uri() -> None:
    assert rdf.sanitize_id_for_uri("1001.SKB7") == "1001_SKB7"
    assert (
        rdf.sanitize_id_for_uri("1883.2011.491.Crump.Artic.LTREB.main.lane4.NoIndex")
        == "1883_2011_491_Crump_Artic_LTREB_main_lane4_NoIndex"
    )

    with pytest.raises(ValueError, match="valor ausente"):
        rdf.sanitize_id_for_uri(None)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Water (saline)", "water_saline"),
        ("Water (non-saline)", "water_non_saline"),
        ("Soil (non-saline)", "soil_non_saline"),
    ],
)
def test_sanitize_label_for_uri(value, expected) -> None:
    assert rdf.sanitize_label_for_uri(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (70.06601667, "70_06601667"),
        (-143.1903833, "m143_1903833"),
        (0.5, "0_5"),
        (0.0, "0_0"),
        (pd.NA, "na"),
        (None, "na"),
        ("", "na"),
    ],
)
def test_sanitize_number_for_uri(value, expected) -> None:
    assert rdf.sanitize_number_for_uri(value) == expected


def test_make_location_uri_deduplicates_identical_rows() -> None:
    row_a = pd.Series(
        {
            "country": "GAZ:United States of America",
            "latitude_deg": 33.194,
            "longitude_deg": -117.241,
            "depth_m": 0.15,
            "altitude_m": 0.0,
            "elevation_m": 114.0,
        }
    )
    row_b = row_a.copy()
    row_b["sample_id"] = "other.sample"

    assert rdf.make_location_uri(row_a) == rdf.make_location_uri(row_b)


def test_make_location_uri_differs_when_depth_changes() -> None:
    row_a = pd.Series(
        {
            "country": "GAZ:United States of America",
            "latitude_deg": 33.194,
            "longitude_deg": -117.241,
            "depth_m": 0.15,
            "altitude_m": 0.0,
            "elevation_m": 114.0,
        }
    )
    row_b = row_a.copy()
    row_b["depth_m"] = 1.0

    assert rdf.make_location_uri(row_a) != rdf.make_location_uri(row_b)


def test_add_decimal_literal_if_present_skips_missing_values() -> None:
    graph = rdf.create_empty_graph()
    subject = rdf.EMPKG.Sample

    rdf.add_decimal_literal_if_present(graph, subject, rdf.EMPKG.ph, pd.NA)

    assert len(graph) == 0


def test_add_decimal_literal_if_present_uses_xsd_decimal() -> None:
    graph = rdf.create_empty_graph()
    subject = rdf.EMPKG.Sample

    rdf.add_decimal_literal_if_present(graph, subject, rdf.EMPKG.ph, "7.8")

    literal = next(graph.objects(subject, rdf.EMPKG.ph))
    assert isinstance(literal, Literal)
    assert literal.datatype == XSD.decimal
    assert literal.toPython() == Decimal("7.8")


def test_add_integer_literal_if_present_uses_xsd_integer() -> None:
    graph = rdf.create_empty_graph()
    subject = rdf.EMPKG.Sample

    rdf.add_integer_literal_if_present(graph, subject, rdf.EMPKG.biomTotalReads, 5000)

    literal = next(graph.objects(subject, rdf.EMPKG.biomTotalReads))
    assert isinstance(literal, Literal)
    assert literal.datatype == XSD.integer
    assert literal.toPython() == 5000


def test_build_graph_from_dataframe_expected_counts() -> None:
    df = rdf.load_and_validate_csv(INPUT_CSV)
    graph = rdf.build_graph_from_dataframe(df)
    summary = rdf.validate_graph(graph, df)

    assert summary["triples_total"] == 588
    assert summary["samples"] == 17
    assert summary["studies"] == 15
    assert summary["locations"] == 15
    assert summary["empo_categories"] == 17
    assert summary["environment_descriptions"] == 17
    assert summary["bad_literals"] == 0


def test_location_deduplication_between_samples() -> None:
    df = pd.read_csv(INPUT_CSV)
    row_skb7 = df.loc[df["sample_id"] == "1001.SKB7"].iloc[0]
    row_skd6 = df.loc[df["sample_id"] == "1001.SKD6"].iloc[0]

    assert rdf.make_location_uri(row_skb7) == rdf.make_location_uri(row_skd6)


def test_each_sample_has_exactly_four_main_relations() -> None:
    df = rdf.load_and_validate_csv(INPUT_CSV)
    graph = rdf.build_graph_from_dataframe(df)

    for sample_uri in graph.subjects(RDF.type, EMPKG.Sample):
        for relation_name in rdf.RELATION_PREDICATES:
            predicate = EMPKG[relation_name]
            count = len(list(graph.triples((sample_uri, predicate, None))))
            assert count == 1, f"{sample_uri} -> {relation_name}"


def test_round_trip_serialization(tmp_path: Path) -> None:
    df = rdf.load_and_validate_csv(INPUT_CSV)
    graph = rdf.build_graph_from_dataframe(df)
    summary = rdf.validate_graph(graph, df)

    output_path = tmp_path / "empkg_v0_test.ttl"
    rdf.serialize_graph(graph, output_path)
    reloaded = rdf.parse_and_verify_ttl(output_path, summary["triples_total"])
    reloaded_summary = rdf.validate_graph(reloaded, df)

    assert reloaded_summary == summary


def test_find_bad_literals_is_empty_for_built_graph() -> None:
    df = rdf.load_and_validate_csv(INPUT_CSV)
    graph = rdf.build_graph_from_dataframe(df)

    assert rdf.find_bad_literals(graph) == []


def test_main_generates_valid_ttl(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    output_path = tmp_path / "empkg_v0_test.ttl"
    monkeypatch.chdir(PROJECT_ROOT)

    rdf.main(["--input", str(INPUT_CSV), "--output", str(output_path)])

    graph = Graph()
    graph.parse(str(output_path), format="turtle")
    assert len(graph) == 588
