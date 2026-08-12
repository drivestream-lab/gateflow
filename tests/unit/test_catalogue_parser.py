"""Unit tests for CatalogueParser (INIT-GATEFLOW-013 W0 / REQ-05–06)."""

from pathlib import Path

import pytest

from src.engine.catalogue_parser import CatalogueParseError, parse_candidates


def _write_valid_meta(root: Path, *, org: str = "drivestream-lab") -> None:
    config = root / "config"
    config.mkdir(parents=True)
    (config / "programme.yaml").write_text(
        f"""apiVersion: launchpad/v1
kind: Programme
org: {org}
meta_repo: prayog-meta
""",
        encoding="utf-8",
    )
    (config / f"service-catalog-{org}.yaml").write_text(
        f"""apiVersion: launchpad/v1
kind: ServiceCatalog
org: {org}
services:
  gateflow:
    stack: python-backend
    status: live
    links:
      repo: https://github.com/{org}/gateflow
  launchpad:
    stack: platform-tooling
    status: live
    links:
      repo: https://github.com/{org}/launchpad.git
""",
        encoding="utf-8",
    )


def test_parse_candidates_happy_path(tmp_path: Path) -> None:
    _write_valid_meta(tmp_path)
    candidates = parse_candidates(tmp_path, org="drivestream-lab")
    assert [(c.org, c.repo, c.service_key) for c in candidates] == [
        ("drivestream-lab", "gateflow", "gateflow"),
        ("drivestream-lab", "launchpad", "launchpad"),
    ]


def test_parse_candidates_missing_programme_yaml(tmp_path: Path) -> None:
    (tmp_path / "config").mkdir(parents=True)
    with pytest.raises(CatalogueParseError) as exc:
        parse_candidates(tmp_path, org="drivestream-lab")
    assert exc.value.reason == "programme_yaml_missing"


def test_parse_candidates_malformed_catalog(tmp_path: Path) -> None:
    _write_valid_meta(tmp_path)
    catalog = tmp_path / "config" / "service-catalog-drivestream-lab.yaml"
    catalog.write_text("not: a: valid: [", encoding="utf-8")
    with pytest.raises(CatalogueParseError) as exc:
        parse_candidates(tmp_path, org="drivestream-lab")
    assert exc.value.reason == "service_catalog_malformed"


def test_parse_candidates_missing_repo_link_no_partial(tmp_path: Path) -> None:
    config = tmp_path / "config"
    config.mkdir(parents=True)
    (config / "programme.yaml").write_text(
        "kind: Programme\norg: drivestream-lab\n",
        encoding="utf-8",
    )
    (config / "service-catalog-drivestream-lab.yaml").write_text(
        """kind: ServiceCatalog
org: drivestream-lab
services:
  ok:
    status: live
    links:
      repo: https://github.com/drivestream-lab/ok
  bad:
    status: live
    links: {}
""",
        encoding="utf-8",
    )
    with pytest.raises(CatalogueParseError) as exc:
        parse_candidates(tmp_path, org="drivestream-lab")
    assert exc.value.reason == "service_catalog_repo_missing"


def test_parse_candidates_ssh_repo_rejected(tmp_path: Path) -> None:
    config = tmp_path / "config"
    config.mkdir(parents=True)
    (config / "programme.yaml").write_text(
        "kind: Programme\norg: drivestream-lab\n",
        encoding="utf-8",
    )
    (config / "service-catalog-drivestream-lab.yaml").write_text(
        """kind: ServiceCatalog
org: drivestream-lab
services:
  gateflow:
    status: live
    links:
      repo: git@github.com:drivestream-lab/gateflow.git
""",
        encoding="utf-8",
    )
    with pytest.raises(CatalogueParseError) as exc:
        parse_candidates(tmp_path, org="drivestream-lab")
    assert exc.value.reason == "service_catalog_repo_not_https"
