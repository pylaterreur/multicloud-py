"""Regression coverage for the public release workflows."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"


def _load(name: str) -> dict:
    return yaml.safe_load((WORKFLOWS / name).read_text())


def test_release_workflow_uses_release_please_and_approved_pypi_publish() -> None:
    workflow = _load("release.yml")

    assert workflow["name"] == "Release"
    assert workflow["permissions"] == {}
    assert workflow["jobs"]["release-please"]["permissions"] == {
        "contents": "write",
        "pull-requests": "write",
    }
    assert workflow["jobs"]["publish"]["environment"] == "pypi"
    assert workflow["jobs"]["publish"]["permissions"] == {"id-token": "write"}


def test_testpypi_rehearsal_is_manual_and_uses_a_protected_environment() -> None:
    workflow = _load("test-pypi.yml")

    assert workflow["permissions"] == {}
    assert workflow["jobs"]["build-and-validate"]["permissions"] == {"contents": "read"}
    assert workflow["jobs"]["publish-testpypi"]["environment"] == "testpypi"
    assert workflow["jobs"]["publish-testpypi"]["permissions"] == {"id-token": "write"}
