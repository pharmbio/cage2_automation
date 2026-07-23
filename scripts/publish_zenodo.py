"""Publish this repository as a new Zenodo deposition version."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import requests
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
CITATION_PATH = REPO_ROOT / "CITATION.cff"
ZENODO_ID_PATH = REPO_ROOT / ".zenodo_id"

ZENODO_API_BASE = "https://zenodo.org/api"


def load_citation(citation_path: Path) -> dict:
    return yaml.safe_load(citation_path.read_text())


def build_zenodo_metadata(citation: dict) -> dict:
    creators = [
        {"name": f"{author['family-names']}, {author['given-names']}"}
        for author in citation["authors"]
    ]
    return {
        "metadata": {
            "title": citation["title"],
            "creators": creators,
            "description": citation["abstract"],
            "license": citation["license"],
            "version": citation["version"],
            "upload_type": "software",
            "keywords": citation.get("keywords", []),
        }
    }
