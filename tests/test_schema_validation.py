"""Tests for CDDBS briefing JSON schema validation."""

import json
from pathlib import Path

import jsonschema
import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SCHEMA_PATH = Path(__file__).parent.parent / "schemas" / "briefing_v1.json"


@pytest.fixture
def schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


@pytest.fixture
def high_quality():
    with open(FIXTURES_DIR / "high_quality_briefing.json") as f:
        return json.load(f)


@pytest.fixture
def medium_quality():
    with open(FIXTURES_DIR / "medium_quality_briefing.json") as f:
        return json.load(f)


@pytest.fixture
def low_quality():
    with open(FIXTURES_DIR / "low_quality_briefing.json") as f:
        return json.load(f)


@pytest.fixture
def minimal_valid():
    with open(FIXTURES_DIR / "minimal_valid_briefing.json") as f:
        return json.load(f)


class TestSchemaValidity:
    """Test that the schema itself is valid."""

    def test_schema_is_valid_draft7(self, schema):
        jsonschema.Draft7Validator.check_schema(schema)

    def test_schema_has_required_fields(self, schema):
        required = schema.get("required", [])
        expected = [
            "metadata",
            "executive_summary",
            "key_findings",
            "subject_profile",
            "confidence_assessment",
            "limitations",
            "methodology",
        ]
        for field in expected:
            assert field in required, f"Missing required field: {field}"

    def test_schema_version(self, schema):
        assert schema.get("version") == "1.2.0"


@pytest.fixture
def telegram_channel():
    with open(FIXTURES_DIR / "telegram_channel_briefing.json") as f:
        return json.load(f)


@pytest.fixture
def cross_platform():
    with open(FIXTURES_DIR / "cross_platform_briefing.json") as f:
        return json.load(f)


class TestValidBriefings:
    """Test that valid briefing fixtures pass schema validation."""

    def test_high_quality_validates(self, schema, high_quality):
        jsonschema.validate(high_quality, schema)

    def test_medium_quality_validates(self, schema, medium_quality):
        jsonschema.validate(medium_quality, schema)

    def test_low_quality_validates(self, schema, low_quality):
        jsonschema.validate(low_quality, schema)

    def test_minimal_valid_validates(self, schema, minimal_valid):
        jsonschema.validate(minimal_valid, schema)

    def test_telegram_channel_validates(self, schema, telegram_channel):
        jsonschema.validate(telegram_channel, schema)

    def test_cross_platform_validates(self, schema, cross_platform):
        jsonschema.validate(cross_platform, schema)


class TestInvalidBriefings:
    """Test that invalid briefings fail schema validation."""

    def test_missing_executive_summary(self, schema, minimal_valid):
        del minimal_valid["executive_summary"]
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(minimal_valid, schema)

    def test_missing_key_findings(self, schema, minimal_valid):
        del minimal_valid["key_findings"]
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(minimal_valid, schema)

    def test_missing_metadata(self, schema, minimal_valid):
        del minimal_valid["metadata"]
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(minimal_valid, schema)

    def test_missing_confidence_assessment(self, schema, minimal_valid):
        del minimal_valid["confidence_assessment"]
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(minimal_valid, schema)

    def test_missing_limitations(self, schema, minimal_valid):
        del minimal_valid["limitations"]
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(minimal_valid, schema)

    def test_missing_methodology(self, schema, minimal_valid):
        del minimal_valid["methodology"]
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(minimal_valid, schema)

    def test_invalid_confidence_level(self, schema, minimal_valid):
        minimal_valid["confidence_assessment"]["overall"] = "very_high"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(minimal_valid, schema)

    def test_invalid_platform(self, schema, minimal_valid):
        minimal_valid["subject_profile"]["platform"] = "myspace"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(minimal_valid, schema)

    def test_empty_key_findings(self, schema, minimal_valid):
        minimal_valid["key_findings"] = []
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(minimal_valid, schema)

    def test_too_many_findings(self, schema, minimal_valid):
        minimal_valid["key_findings"] = [
            {"finding": f"Finding {i}", "confidence": "low", "evidence": [{"type": "pattern", "reference": "ref"}]}
            for i in range(6)
        ]
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(minimal_valid, schema)

    def test_finding_missing_evidence(self, schema, minimal_valid):
        minimal_valid["key_findings"][0] = {
            "finding": "A finding without evidence",
            "confidence": "low",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(minimal_valid, schema)

    def test_empty_string_summary(self, schema, minimal_valid):
        minimal_valid["executive_summary"] = "Too short"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(minimal_valid, schema)


class TestNarrativeDataset:
    """Test that the known narratives dataset is valid."""

    def test_narratives_file_is_valid_json(self):
        path = Path(__file__).parent.parent / "data" / "known_narratives.json"
        with open(path) as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_narratives_has_categories(self):
        path = Path(__file__).parent.parent / "data" / "known_narratives.json"
        with open(path) as f:
            data = json.load(f)
        assert "categories" in data
        assert len(data["categories"]) >= 5

    def test_each_narrative_has_required_fields(self):
        path = Path(__file__).parent.parent / "data" / "known_narratives.json"
        with open(path) as f:
            data = json.load(f)
        for cat in data["categories"]:
            assert "id" in cat
            assert "name" in cat
            assert "narratives" in cat
            for narr in cat["narratives"]:
                assert "id" in narr
                assert "name" in narr
                assert "keywords" in narr
                assert len(narr["keywords"]) >= 3
                assert "source_refs" in narr

    def test_total_narratives_count(self):
        path = Path(__file__).parent.parent / "data" / "known_narratives.json"
        with open(path) as f:
            data = json.load(f)
        total = sum(len(cat["narratives"]) for cat in data["categories"])
        assert total >= 15, f"Expected at least 15 narratives, got {total}"

    def test_metadata_count_matches_actual(self):
        path = Path(__file__).parent.parent / "data" / "known_narratives.json"
        with open(path) as f:
            data = json.load(f)
        actual = sum(len(cat["narratives"]) for cat in data["categories"])
        declared = data["metadata"]["total_narratives"]
        assert actual == declared, f"Metadata says {declared} but actual is {actual}"

    def test_telegram_amplification_category_exists(self):
        path = Path(__file__).parent.parent / "data" / "known_narratives.json"
        with open(path) as f:
            data = json.load(f)
        cat_ids = [c["id"] for c in data["categories"]]
        assert "telegram_amplification" in cat_ids


class TestMultiPlatformSchema:
    """Test v1.2 multi-platform schema features."""

    def test_telegram_platform_accepted(self, schema, telegram_channel):
        assert telegram_channel["subject_profile"]["platform"] == "telegram"
        jsonschema.validate(telegram_channel, schema)

    def test_platform_metadata_accepted(self, schema, telegram_channel):
        assert "platform_metadata" in telegram_channel["subject_profile"]
        meta = telegram_channel["subject_profile"]["platform_metadata"]
        assert meta["telegram_channel_type"] == "channel"
        jsonschema.validate(telegram_channel, schema)

    def test_cross_platform_identities_accepted(self, schema, cross_platform):
        assert "cross_platform_identities" in cross_platform
        assert len(cross_platform["cross_platform_identities"]) >= 1
        jsonschema.validate(cross_platform, schema)

    def test_network_graph_accepted(self, schema, telegram_channel):
        assert "network_graph" in telegram_channel
        graph = telegram_channel["network_graph"]
        assert len(graph["nodes"]) >= 3
        assert len(graph["edges"]) >= 3
        assert len(graph["communities"]) >= 1
        jsonschema.validate(telegram_channel, schema)

    def test_new_evidence_types_accepted(self, schema, telegram_channel):
        all_evidence_types = set()
        for f in telegram_channel["key_findings"]:
            for ev in f["evidence"]:
                all_evidence_types.add(ev["type"])
        assert "forward" in all_evidence_types
        assert "channel_meta" in all_evidence_types
        jsonschema.validate(telegram_channel, schema)

    def test_new_indicator_types_accepted(self, schema, telegram_channel):
        indicators = telegram_channel["narrative_analysis"]["behavioral_indicators"]
        indicator_types = {i["indicator"] for i in indicators}
        assert "forwarding_pattern" in indicator_types
        assert "channel_growth" in indicator_types
        jsonschema.validate(telegram_channel, schema)

    def test_invalid_evidence_type_rejected(self, schema, minimal_valid):
        minimal_valid["key_findings"][0]["evidence"][0]["type"] = "invalid_type"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(minimal_valid, schema)

    def test_invalid_indicator_type_rejected(self, schema):
        briefing = {
            "metadata": {"briefing_id": "test", "generated_at": "2026-01-01T00:00:00Z", "model_version": "test", "prompt_version": "test", "cddbs_version": "test"},
            "executive_summary": "A" * 50,
            "key_findings": [{"finding": "test", "confidence": "low", "evidence": [{"type": "pattern", "reference": "test"}]}],
            "subject_profile": {"account_handle": "test", "platform": "twitter"},
            "confidence_assessment": {"overall": "low", "factors": {"data_completeness": "low", "source_reliability": "low", "analytical_consistency": "low", "corroboration": "low"}},
            "limitations": {"cannot_determine": ["x"], "data_gaps": ["y"]},
            "methodology": {"data_collection": "test", "analysis_model": "test", "prompt_version": "test"},
            "narrative_analysis": {"behavioral_indicators": [{"indicator": "invalid_indicator", "description": "test"}]}
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(briefing, schema)
