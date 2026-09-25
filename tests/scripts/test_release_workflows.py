"""Regression coverage for the public release workflows."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"


def _load(name: str) -> dict:
    return yaml.safe_load((WORKFLOWS / name).read_text())


def _workflow_dispatch_inputs(workflow: dict) -> dict:
    # PyYAML 1.1 may parse the unquoted YAML key ``on`` as ``True``.
    return workflow.get("on", workflow.get(True))["workflow_dispatch"]["inputs"]


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
    assert "vars.PYPI_BOOTSTRAP_COMPLETE == 'true'" in workflow["jobs"]["publish"]["if"]


def test_testpypi_rehearsal_bootstraps_three_projects_per_selected_batch() -> None:
    workflow = _load("test-pypi.yml")
    inputs = _workflow_dispatch_inputs(workflow)

    assert workflow["permissions"] == {}
    assert inputs["batch"] == {
        "description": "Bootstrap batch to publish (three packages per run)",
        "required": True,
        "default": "1",
        "type": "choice",
        "options": ["1", "2", "3", "4", "5", "6", "7"],
    }
    assert workflow["jobs"]["select-bootstrap-batch"]["permissions"] == {}
    assert workflow["jobs"]["build-and-validate"]["permissions"] == {"contents": "read"}
    publish = workflow["jobs"]["publish-testpypi"]
    assert publish["needs"] == ["select-bootstrap-batch", "build-and-validate"]
    assert publish["strategy"]["max-parallel"] == 3
    assert publish["environment"] == "testpypi-${{ matrix.project }}"
    assert publish["permissions"] == {"id-token": "write"}


def test_testpypi_bootstrap_batches_cover_every_distribution_once() -> None:
    workflow = _load("test-pypi.yml")
    selector = workflow["jobs"]["select-bootstrap-batch"]["steps"][0]["run"]
    selected_projects = re.findall(r'"project":"([^"]+)"', selector)
    package_projects = {
        tomllib.loads(path.read_text())["project"]["name"]
        for path in REPO_ROOT.glob("packages/*/*/pyproject.toml")
    }

    assert len(selected_projects) == 21
    assert len(set(selected_projects)) == 21
    assert set(selected_projects) == package_projects


def test_production_pypi_bootstrap_uses_selected_branch_and_staged_batches() -> None:
    workflow = _load("bootstrap-pypi.yml")
    inputs = _workflow_dispatch_inputs(workflow)

    assert workflow["name"] == "Bootstrap production PyPI"
    assert workflow["permissions"] == {}
    assert set(inputs) == {"batch"}
    assert inputs["batch"]["options"] == ["1", "2", "3", "4", "5", "6", "7"]
    assert workflow["concurrency"]["group"] == (
        "pypi-bootstrap-${{ github.sha }}-${{ inputs.batch }}"
    )

    build = workflow["jobs"]["build-and-validate"]
    assert build["needs"] == "select-bootstrap-batch"
    assert build["permissions"] == {"contents": "read"}
    assert "ref" not in build["steps"][0].get("with", {})

    publish = workflow["jobs"]["publish"]
    assert publish["needs"] == ["select-bootstrap-batch", "build-and-validate"]
    assert publish["strategy"]["max-parallel"] == 3
    assert publish["environment"] == "pypi-${{ matrix.project }}"
    assert publish["permissions"] == {"id-token": "write"}

    selector = workflow["jobs"]["select-bootstrap-batch"]["steps"][0]["run"]
    selected_projects = re.findall(r'"project":"([^"]+)"', selector)
    package_projects = {
        tomllib.loads(path.read_text())["project"]["name"]
        for path in REPO_ROOT.glob("packages/*/*/pyproject.toml")
    }
    assert len(selected_projects) == 21
    assert len(set(selected_projects)) == 21
    assert set(selected_projects) == package_projects
