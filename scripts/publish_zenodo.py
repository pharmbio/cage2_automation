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


def require_token() -> str:
    token = os.environ.get("ZENODO_TOKEN", "").strip()
    if not token:
        raise SystemExit("ZENODO_TOKEN environment variable is not set")
    return token


def read_deposition_id() -> str | None:
    if not ZENODO_ID_PATH.is_file():
        return None
    content = ZENODO_ID_PATH.read_text().strip()
    return content or None


def raise_for_zenodo_error(response: requests.Response) -> None:
    if response.status_code >= 400:
        print(response.text, file=sys.stderr)
        raise SystemExit(1)


def _auth_params(token: str) -> dict:
    return {"access_token": token}


def create_deposition(token: str) -> dict:
    response = requests.post(
        f"{ZENODO_API_BASE}/deposit/depositions",
        params=_auth_params(token),
        json={},
    )
    raise_for_zenodo_error(response)
    return response.json()


def create_new_version(token: str, deposition_id: str) -> dict:
    response = requests.post(
        f"{ZENODO_API_BASE}/deposit/depositions/{deposition_id}/actions/newversion",
        params=_auth_params(token),
    )
    raise_for_zenodo_error(response)
    draft_url = response.json()["links"]["latest_draft"]
    draft_response = requests.get(draft_url, params=_auth_params(token))
    raise_for_zenodo_error(draft_response)
    return draft_response.json()


def build_archive(version: str) -> Path:
    archive_path = REPO_ROOT / f"lab_adaption-{version}.zip"
    subprocess.run(
        [
            "git",
            "archive",
            "--format=zip",
            "-o",
            str(archive_path),
            "HEAD",
        ],
        cwd=REPO_ROOT,
        check=True,
    )
    return archive_path


def remove_existing_files(token: str, draft: dict) -> None:
    for file_entry in draft.get("files", []):
        file_id = file_entry["id"]
        deposition_id = draft["id"]
        response = requests.delete(
            f"{ZENODO_API_BASE}/deposit/depositions/{deposition_id}/files/{file_id}",
            params=_auth_params(token),
        )
        raise_for_zenodo_error(response)


def upload_file(token: str, draft: dict, file_path: Path) -> None:
    bucket_url = draft["links"]["bucket"]
    with open(file_path, "rb") as fh:
        response = requests.put(
            f"{bucket_url}/{file_path.name}",
            params=_auth_params(token),
            data=fh,
        )
    raise_for_zenodo_error(response)


def update_metadata(token: str, draft: dict, metadata: dict) -> None:
    response = requests.put(
        draft["links"]["self"],
        params=_auth_params(token),
        json=metadata,
    )
    raise_for_zenodo_error(response)


def publish(token: str, draft: dict) -> dict:
    response = requests.post(
        draft["links"]["publish"],
        params=_auth_params(token),
    )
    raise_for_zenodo_error(response)
    return response.json()


def main() -> None:
    token = require_token()
    citation = load_citation(CITATION_PATH)
    metadata = build_zenodo_metadata(citation)
    version = citation["version"]

    existing_id = read_deposition_id()
    if existing_id is None:
        draft = create_deposition(token)
    else:
        draft = create_new_version(token, existing_id)

    remove_existing_files(token, draft)
    archive_path = build_archive(version)
    upload_file(token, draft, archive_path)
    update_metadata(token, draft, metadata)
    record = publish(token, draft)

    if existing_id is None:
        ZENODO_ID_PATH.write_text(f"{record['id']}\n")

    print(f"Published Zenodo record: {record['id']}")
    print(f"DOI: {record['doi']}")


if __name__ == "__main__":
    main()
