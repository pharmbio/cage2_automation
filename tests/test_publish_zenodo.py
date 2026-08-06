import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import publish_zenodo  # noqa: E402


SAMPLE_CITATION = {
    "cff-version": "1.2.0",
    "title": "Lab Automation Framework Template and Demo",
    "abstract": "A template for lab automation.",
    "authors": [
        {"given-names": "Mark", "family-names": "Doerr"},
        {"given-names": "Stefan", "family-names": "Maak"},
    ],
    "license": "MIT",
    "version": "0.1.0",
    "keywords": ["laboratory automation", "SiLA"],
}


def test_load_citation_parses_yaml(tmp_path):
    citation_file = tmp_path / "CITATION.cff"
    citation_file.write_text(
        'title: Test Title\nversion: "1.2.3"\nauthors:\n'
        "  - given-names: Ada\n    family-names: Lovelace\n"
    )
    result = publish_zenodo.load_citation(citation_file)
    assert result["title"] == "Test Title"
    assert result["version"] == "1.2.3"
    assert result["authors"][0]["family-names"] == "Lovelace"


def test_build_zenodo_metadata_shape():
    payload = publish_zenodo.build_zenodo_metadata(SAMPLE_CITATION)
    metadata = payload["metadata"]
    assert metadata["title"] == "Lab Automation Framework Template and Demo"
    assert metadata["description"] == "A template for lab automation."
    assert metadata["upload_type"] == "software"
    assert metadata["license"] == "MIT"
    assert metadata["version"] == "0.1.0"
    assert metadata["keywords"] == ["laboratory automation", "SiLA"]


def test_build_zenodo_metadata_creators_format():
    payload = publish_zenodo.build_zenodo_metadata(SAMPLE_CITATION)
    creators = payload["metadata"]["creators"]
    assert creators == [
        {"name": "Doerr, Mark"},
        {"name": "Maak, Stefan"},
    ]


def test_require_token_missing_raises(monkeypatch):
    monkeypatch.delenv("ZENODO_TOKEN", raising=False)
    with pytest.raises(SystemExit, match="ZENODO_TOKEN"):
        publish_zenodo.require_token()


def test_require_token_present_returns_value(monkeypatch):
    monkeypatch.setenv("ZENODO_TOKEN", "abc123")
    assert publish_zenodo.require_token() == "abc123"


def test_read_deposition_id_missing_file_returns_none(tmp_path, monkeypatch):
    monkeypatch.setattr(publish_zenodo, "ZENODO_ID_PATH", tmp_path / ".zenodo_id")
    assert publish_zenodo.read_deposition_id() is None


def test_read_deposition_id_blank_file_returns_none(tmp_path, monkeypatch):
    id_file = tmp_path / ".zenodo_id"
    id_file.write_text("   \n")
    monkeypatch.setattr(publish_zenodo, "ZENODO_ID_PATH", id_file)
    assert publish_zenodo.read_deposition_id() is None


def test_read_deposition_id_present_returns_stripped_value(tmp_path, monkeypatch):
    id_file = tmp_path / ".zenodo_id"
    id_file.write_text("123456\n")
    monkeypatch.setattr(publish_zenodo, "ZENODO_ID_PATH", id_file)
    assert publish_zenodo.read_deposition_id() == "123456"


class _FakeResponse:
    def __init__(self, status_code, text="error body"):
        self.status_code = status_code
        self.text = text


def test_raise_for_zenodo_error_raises_on_4xx(capsys):
    response = _FakeResponse(400, "bad request details")
    with pytest.raises(SystemExit):
        publish_zenodo.raise_for_zenodo_error(response)
    assert "bad request details" in capsys.readouterr().err


def test_raise_for_zenodo_error_noop_on_2xx():
    response = _FakeResponse(201, "")
    publish_zenodo.raise_for_zenodo_error(response)  # should not raise
