import sys
from pathlib import Path

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
        "title: Test Title\nversion: \"1.2.3\"\nauthors:\n"
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
