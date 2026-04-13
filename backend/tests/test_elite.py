"""Tests for elite_profiles.yaml loading and structure validation."""

from __future__ import annotations

from pathlib import Path


from app.services.crawlers.orchestrator import _load_elite_profiles, get_elite_presets

YAML_PATH = (
    Path(__file__).resolve().parent.parent / "app" / "services" / "crawlers" / "elite_profiles.yaml"
)


class TestLoadProfiles:
    def test_file_exists(self):
        assert YAML_PATH.exists(), f"elite_profiles.yaml not found at {YAML_PATH}"

    def test_loads_without_error(self):
        profiles = _load_elite_profiles()
        assert isinstance(profiles, dict)
        assert "institutions" in profiles
        assert "researchers" in profiles
        assert "presets" in profiles

    def test_institutions_have_required_fields(self):
        profiles = _load_elite_profiles()
        for inst in profiles["institutions"]:
            assert "id" in inst, f"Institution missing 'id': {inst}"
            assert "name" in inst, f"Institution missing 'name': {inst}"
            assert inst["id"].startswith("I"), f"Institution ID should start with I: {inst['id']}"

    def test_researchers_have_required_fields(self):
        profiles = _load_elite_profiles()
        for researcher in profiles["researchers"]:
            assert "id" in researcher, f"Researcher missing 'id': {researcher}"
            assert "name" in researcher, f"Researcher missing 'name': {researcher}"
            assert researcher["id"].startswith("A"), (
                f"Researcher ID should start with A: {researcher['id']}"
            )

    def test_institutions_count(self):
        profiles = _load_elite_profiles()
        assert len(profiles["institutions"]) >= 15

    def test_researchers_count(self):
        profiles = _load_elite_profiles()
        assert len(profiles["researchers"]) >= 10


class TestPresets:
    def test_get_presets_returns_dict(self):
        presets = get_elite_presets()
        assert isinstance(presets, dict)
        assert len(presets) >= 4

    def test_preset_names(self):
        presets = get_elite_presets()
        expected = {"top_ai_labs", "nlp_leaders", "deep_learning_pioneers", "china_top_cs"}
        assert expected.issubset(set(presets.keys()))

    def test_preset_structure(self):
        presets = get_elite_presets()
        for name, preset in presets.items():
            assert "description" in preset, f"Preset '{name}' missing description"
            assert "min_citations" in preset, f"Preset '{name}' missing min_citations"
            assert "year_from" in preset, f"Preset '{name}' missing year_from"
            # Must have at least researchers or institutions
            has_researchers = len(preset.get("researchers", [])) > 0
            has_institutions = len(preset.get("institutions", [])) > 0
            assert has_researchers or has_institutions, (
                f"Preset '{name}' has no researchers or institutions"
            )

    def test_preset_ids_reference_valid_profiles(self):
        """Preset institution/researcher IDs should reference entries in the profiles."""
        profiles = _load_elite_profiles()
        all_inst_ids = {inst["id"] for inst in profiles["institutions"]}
        all_researcher_ids = {r["id"] for r in profiles["researchers"]}

        for name, preset in profiles["presets"].items():
            for rid in preset.get("researchers", []):
                assert rid in all_researcher_ids, (
                    f"Preset '{name}' references unknown researcher: {rid}"
                )
            for iid in preset.get("institutions", []):
                assert iid in all_inst_ids, f"Preset '{name}' references unknown institution: {iid}"
