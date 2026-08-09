"""Parse programme catalogue YAML from a synced meta checkout (ADR-012).

Discovery-input only — never loads GATEFLOW_* process knobs from meta YAML.
"""

from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

import yaml

from src.models.programme_catalogue_models import CatalogueCandidate


class CatalogueParseError(Exception):
    """Named catalogue shape/missing-file failure (REQ-06) — no partial list."""

    def __init__(self, message: str, *, reason: str) -> None:
        super().__init__(message)
        self.reason = reason


def parse_candidates(meta_checkout_root: str | Path, *, org: str) -> list[CatalogueCandidate]:
    """Read programme.yaml + service-catalog-<org>.yaml; return full candidate list.

    Fail closed on missing/malformed documents — never returns a partial list.
    """
    root = Path(meta_checkout_root)
    if not root.is_dir():
        raise CatalogueParseError(
            "programme meta checkout root is not a directory",
            reason="meta_checkout_missing",
        )
    cleaned_org = org.strip()
    if not cleaned_org:
        raise CatalogueParseError(
            "org is required to resolve service-catalog file",
            reason="catalogue_org_missing",
        )

    programme_path = root / "config" / "programme.yaml"
    catalog_path = root / "config" / f"service-catalog-{cleaned_org}.yaml"
    if not programme_path.is_file():
        raise CatalogueParseError(
            "programme.yaml not found under synced meta config/",
            reason="programme_yaml_missing",
        )
    if not catalog_path.is_file():
        raise CatalogueParseError(
            f"service-catalog-{cleaned_org}.yaml not found under synced meta config/",
            reason="service_catalog_missing",
        )

    programme_doc = _load_yaml_mapping(programme_path, reason_prefix="programme_yaml")
    catalog_doc = _load_yaml_mapping(catalog_path, reason_prefix="service_catalog")

    if programme_doc.get("kind") != "Programme":
        raise CatalogueParseError(
            "programme.yaml kind must be Programme",
            reason="programme_yaml_invalid_kind",
        )
    programme_org = programme_doc.get("org")
    if not isinstance(programme_org, str) or not programme_org.strip():
        raise CatalogueParseError(
            "programme.yaml org is required",
            reason="programme_yaml_org_missing",
        )
    if programme_org.strip() != cleaned_org:
        raise CatalogueParseError(
            "programme.yaml org does not match connect org",
            reason="programme_org_mismatch",
        )

    if catalog_doc.get("kind") != "ServiceCatalog":
        raise CatalogueParseError(
            "service-catalog kind must be ServiceCatalog",
            reason="service_catalog_invalid_kind",
        )
    catalog_org = catalog_doc.get("org")
    if not isinstance(catalog_org, str) or catalog_org.strip() != cleaned_org:
        raise CatalogueParseError(
            "service-catalog org missing or mismatched",
            reason="service_catalog_org_mismatch",
        )

    services = catalog_doc.get("services")
    if not isinstance(services, dict) or not services:
        raise CatalogueParseError(
            "service-catalog services map is required and non-empty",
            reason="service_catalog_services_missing",
        )

    candidates: list[CatalogueCandidate] = []
    for key, entry in services.items():
        if not isinstance(key, str) or not key.strip():
            raise CatalogueParseError(
                "service-catalog service key must be a non-empty string",
                reason="service_catalog_invalid_key",
            )
        if not isinstance(entry, dict):
            raise CatalogueParseError(
                f"service entry {key!r} must be a mapping",
                reason="service_catalog_invalid_entry",
            )
        status = entry.get("status")
        if not isinstance(status, str) or not status.strip():
            raise CatalogueParseError(
                f"service {key!r} status is required",
                reason="service_catalog_status_missing",
            )
        links = entry.get("links")
        if not isinstance(links, dict):
            raise CatalogueParseError(
                f"service {key!r} links mapping is required",
                reason="service_catalog_links_missing",
            )
        repo_url = links.get("repo")
        if not isinstance(repo_url, str) or not repo_url.strip():
            raise CatalogueParseError(
                f"service {key!r} links.repo is required",
                reason="service_catalog_repo_missing",
            )
        parsed = _parse_github_org_repo(repo_url.strip())
        if parsed is None:
            raise CatalogueParseError(
                f"service {key!r} links.repo is not a github org/repo URL",
                reason="service_catalog_repo_unparseable",
            )
        cand_org, cand_repo = parsed
        candidates.append(
            CatalogueCandidate(
                org=cand_org,
                repo=cand_repo,
                service_key=key.strip(),
                status=status.strip(),
            )
        )

    if not candidates:
        raise CatalogueParseError(
            "service-catalog produced zero candidates",
            reason="service_catalog_empty",
        )
    return candidates


def _load_yaml_mapping(path: Path, *, reason_prefix: str) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CatalogueParseError(
            f"failed to read {path.name}",
            reason=f"{reason_prefix}_unreadable",
        ) from exc
    try:
        loaded: Any = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise CatalogueParseError(
            f"{path.name} is not valid YAML",
            reason=f"{reason_prefix}_malformed",
        ) from exc
    if not isinstance(loaded, dict):
        raise CatalogueParseError(
            f"{path.name} root must be a mapping",
            reason=f"{reason_prefix}_not_mapping",
        )
    return loaded


def _parse_github_org_repo(url: str) -> Optional[tuple[str, str]]:
    cleaned = url.rstrip("/")
    if cleaned.endswith(".git"):
        cleaned = cleaned[:-4]
    if cleaned.startswith("git@"):
        # git@github.com:org/repo
        if ":" not in cleaned:
            return None
        path = cleaned.split(":", 1)[1]
        parts = [p for p in path.split("/") if p]
        if len(parts) < 2:
            return None
        return parts[0], parts[1]
    parsed = urlparse(cleaned)
    if parsed.scheme not in {"http", "https"}:
        return None
    host = (parsed.hostname or "").lower()
    if host != "github.com":
        return None
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2:
        return None
    return parts[0], parts[1]
