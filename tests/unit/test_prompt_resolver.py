"""Unit tests for PromptResolver (INIT-GATEFLOW-005 W0)."""

from pathlib import Path

import pytest
import yaml

from src.business_services.prompt_resolver import PromptResolver
from src.models.prompt_package_models import BoundPromptInputs, PromptResolveError


@pytest.fixture
def resolver() -> PromptResolver:
    return PromptResolver()


@pytest.fixture
def pin_workspace(tmp_path: Path) -> Path:
    prompts = tmp_path / "prayog-skills" / "skills" / "development" / "pre-implement" / "prompts"
    prompts.mkdir(parents=True)
    (prompts / "schema.yaml").write_text(
        yaml.dump(
            {
                "prompt_id": "pre-implement",
                "revision": "1.0.0",
                "variables": {
                    "ticket": {"required": True, "type": "string"},
                    "initiative": {"required": False, "type": "string"},
                    "skill_id": {"required": True, "type": "string"},
                    "workspace": {"required": True, "type": "string"},
                    "handoff_path": {"required": True, "type": "string"},
                },
            }
        ),
        encoding="utf-8",
    )
    (prompts / "template.md").write_text(
        "ticket={{ticket}} initiative={{initiative}} skill={{skill_id}} "
        "ws={{workspace}} handoff={{handoff_path}}\n",
        encoding="utf-8",
    )
    return tmp_path


def test_resolve_and_render_happy(resolver: PromptResolver, pin_workspace: Path) -> None:
    package = resolver.resolve_package(str(pin_workspace), "pre-implement")
    rendered = resolver.bind_and_render(
        package,
        BoundPromptInputs(
            ticket="55",
            initiative="INIT-X",
            skill_id="pre-implement",
            workspace="/ws",
            handoff_path="/tmp/h/handoff.md",
        ),
    )
    assert rendered.prompt_id == "pre-implement"
    assert rendered.prompt_revision == "1.0.0"
    assert "ticket=55" in rendered.message
    assert "initiative=INIT-X" in rendered.message
    assert "handoff=/tmp/h/handoff.md" in rendered.message


def test_missing_package_fails(resolver: PromptResolver, tmp_path: Path) -> None:
    with pytest.raises(PromptResolveError, match="prompt_package_missing"):
        resolver.resolve_package(str(tmp_path), "pre-implement")


def test_required_bind_miss_fails(resolver: PromptResolver, pin_workspace: Path) -> None:
    package = resolver.resolve_package(str(pin_workspace), "pre-implement")
    with pytest.raises(PromptResolveError, match="prompt_bind_required_missing"):
        resolver.bind_and_render(
            package,
            BoundPromptInputs(
                ticket=" ",
                initiative="",
                skill_id="pre-implement",
                workspace="/ws",
                handoff_path="/tmp/h",
            ),
        )


def test_optional_initiative_empty(resolver: PromptResolver, pin_workspace: Path) -> None:
    package = resolver.resolve_package(str(pin_workspace), "pre-implement")
    rendered = resolver.bind_and_render(
        package,
        BoundPromptInputs(
            ticket="55",
            initiative="",
            skill_id="pre-implement",
            workspace="/ws",
            handoff_path="/tmp/h",
        ),
    )
    assert "initiative=" in rendered.message


def test_undeclared_template_var_fails(resolver: PromptResolver, tmp_path: Path) -> None:
    prompts = tmp_path / "prayog-skills" / "skills" / "development" / "pre-implement" / "prompts"
    prompts.mkdir(parents=True)
    (prompts / "schema.yaml").write_text(
        yaml.dump(
            {
                "prompt_id": "pre-implement",
                "revision": "1.0.0",
                "variables": {"ticket": {"required": True, "type": "string"}},
            }
        ),
        encoding="utf-8",
    )
    (prompts / "template.md").write_text("{{ticket}} {{unknown}}\n", encoding="utf-8")
    package = resolver.resolve_package(str(tmp_path), "pre-implement")
    with pytest.raises(PromptResolveError, match="prompt_template_undeclared_var"):
        resolver.bind_and_render(
            package,
            BoundPromptInputs(
                ticket="1",
                skill_id="pre-implement",
                workspace="/ws",
                handoff_path="/h",
            ),
        )
