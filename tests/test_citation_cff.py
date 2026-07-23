from pathlib import Path

import yaml

CITATION_PATH = Path(__file__).resolve().parents[1] / "CITATION.cff"


def _load_raw_text():
    return CITATION_PATH.read_text()


def _load_yaml():
    return yaml.safe_load(_load_raw_text())


def test_citation_cff_exists():
    assert CITATION_PATH.is_file()


def test_citation_cff_has_required_top_level_keys():
    data = _load_yaml()
    for key in (
        "cff-version",
        "message",
        "title",
        "authors",
        "version",
        "date-released",
        "license",
        "repository-code",
        "abstract",
    ):
        assert key in data, f"missing key: {key}"


def test_citation_cff_authors_have_required_fields():
    data = _load_yaml()
    assert len(data["authors"]) >= 1
    for author in data["authors"]:
        assert "given-names" in author
        assert "family-names" in author


def test_citation_cff_version_matches_pyproject():
    import re

    pyproject_text = (
        Path(__file__).resolve().parents[1] / "pyproject.toml"
    ).read_text()
    match = re.search(r'version = "([^"]+)"', pyproject_text)
    assert match is not None
    assert _load_yaml()["version"] == match.group(1)


def test_citation_cff_has_bumpversion_markers():
    raw = _load_raw_text()
    assert 'version: "0.1.0"' in raw
    import re

    assert re.search(r"__date__ = '\d{4}-\d{2}-\d{2}'", raw)
