"""REQ-27 / Q-6 / G5 — gateflow-owned dormancy guard for ForgeClient.delete_branch.

Proves zero production call sites invoke ``delete_branch`` this INIT.
Does not claim prayog-skills REQ-29 (pin outcome edges).
"""

from __future__ import annotations

import ast
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRC_ROOT = _REPO_ROOT / "src"
_METHOD_DEF_FILE = (_SRC_ROOT / "infra_services" / "forge_client.py").resolve()


def _call_sites_for_delete_branch(py_path: Path) -> list[tuple[Path, int]]:
    """Return (path, lineno) for attribute calls ``*.delete_branch(...)``."""
    tree = ast.parse(py_path.read_text(encoding="utf-8"), filename=str(py_path))
    hits: list[tuple[Path, int]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "delete_branch":
            hits.append((py_path, node.lineno))
    return hits


def test_delete_branch_has_zero_production_callers() -> None:
    """No shipped ``src/`` call site may invoke delete_branch (structural dormancy)."""
    offenders: list[str] = []
    for path in sorted(_SRC_ROOT.rglob("*.py")):
        resolved = path.resolve()
        for hit_path, lineno in _call_sites_for_delete_branch(path):
            # Method definition body may contain the name only as a Call if
            # someone recurses — allow only the definition file's def, not calls.
            if resolved == _METHOD_DEF_FILE:
                # Calls inside forge_client.py itself are also forbidden (no
                # self-wiring). Attribute on the def line is not a Call.
                offenders.append(f"{hit_path.relative_to(_REPO_ROOT)}:{lineno}")
                continue
            offenders.append(f"{hit_path.relative_to(_REPO_ROOT)}:{lineno}")

    assert (
        offenders == []
    ), "REQ-27 dormancy: unexpected production delete_branch call site(s): " + ", ".join(offenders)


def test_delete_branch_method_exists_on_forge_client() -> None:
    """Capability is present (built) even while dormant — REQ-26 surface."""
    from src.infra_services.forge_client import ForgeClient

    assert callable(getattr(ForgeClient, "delete_branch", None))
