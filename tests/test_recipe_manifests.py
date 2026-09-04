"""Conformance check over the recipes this bundle SHIPS.

The rule, in one sentence:

    A shipped recipe that references a namespaced agent must declare that
    agent in its own ``schema_version: 2`` dependency manifest.

Why this exists
---------------
A recipe with no ``schema_version`` runs *legacy-caller-bound*: its ``agent:``
strings resolve from the **calling session's** agent map, not from anything
the recipe itself declares. That is harmless for a recipe that spawns nothing,
and fatal for one that does -- it can only run from a bundle that happens to
carry the same agents. Every recipe in this bundle spawns an agent, so before
this rule landed, all eight died on their first step ("Agent
'browser-tester:browser-operator' not found in configuration") from any
session bundle that did not already include browser-tester.

Declaring the closure makes the recipe portable: the runner resolves every
agent from the declared dependency, and an undeclared reference is refused at
preflight instead of at the first spawn.

Deliberately dependency-light
-----------------------------
This module imports only ``pytest`` and ``PyYAML`` -- no Amplifier packages --
so any CI runner can execute it with ``pytest tests/`` and nothing else
installed. The deeper check (that the shipped *parser* accepts the manifest,
not just that the YAML looks right) is exercised separately by
``amplifier_recipe_runner validate``; see the PR body for that evidence.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

# <repo-root>/tests/this_file.py -> <repo-root>
_REPO_ROOT = Path(__file__).resolve().parents[1]
_RECIPES_DIR = _REPO_ROOT / "recipes"

#: Every shipped recipe references an agent and every one is migrated, so this
#: is empty. It is kept -- rather than deleted -- because it is the ONLY
#: sanctioned way to leave a file on legacy, and an entry must carry a reason.
#:
#: The known legitimate reason is ``agent: self``: a self-referential step
#: cannot be made v2-safe, because the closed-world resolver has no agent named
#: ``self`` to resolve against (bundle-recipes tracker item ``recipes-80q``).
#: Such a file stays legacy with a top-of-file comment saying so.
_EXEMPT: dict[str, str] = {}

#: Guards against a vacuous pass if the glob ever stops finding anything.
_MINIMUM_SHIPPED_RECIPES = 8


def _recipes() -> list[Path]:
    return sorted(_RECIPES_DIR.rglob("*.yaml"))


def _rel(path: Path) -> str:
    return path.relative_to(_REPO_ROOT).as_posix()


def _walk_steps(steps: Any) -> list[dict]:
    """Every step dict, including steps nested under foreach/parallel blocks."""
    found: list[dict] = []
    if not isinstance(steps, list):
        return found
    for step in steps:
        if not isinstance(step, dict):
            continue
        found.append(step)
        for nested_key in ("steps", "then", "else", "body"):
            found.extend(_walk_steps(step.get(nested_key)))
    return found


def _referenced_agents(data: dict) -> set[str]:
    """Namespaced ``agent:`` references, read straight off the YAML.

    ``agent: self`` and bare (un-namespaced) names are excluded: the first is
    the documented un-migratable case, the second is not a bundle reference.
    """
    agents: set[str] = set()
    for step in _walk_steps(data.get("steps")):
        agent = step.get("agent")
        if isinstance(agent, str) and ":" in agent:
            agents.add(agent)
    return agents


def _declared_agents(data: dict) -> set[str]:
    """Agents declared across every dependency's ``required_agents``."""
    declared: set[str] = set()
    for dep in data.get("dependencies") or ():
        if isinstance(dep, dict):
            declared.update(dep.get("required_agents") or ())
    return declared


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def undeclared_agents(path: Path) -> set[str]:
    """Namespaced agents a recipe references but its own manifest never supplies.

    Empty for a recipe that references no namespaced agent at all -- such a
    recipe is entitled to stay legacy, which is what keeps a hypothetical
    bash-only recipe exempt without having to name it.

    Exported (no leading underscore) because
    :func:`test_check_catches_an_undeclared_agent` proves the rule bites by
    calling exactly this helper on a synthetic file.
    """
    data = _load(path)
    referenced = _referenced_agents(data)
    if not referenced:
        return set()
    if data.get("schema_version") != 2:
        # Legacy: the manifest supplies nothing, so everything is undeclared.
        return referenced
    return referenced - _declared_agents(data)


# ---------------------------------------------------------------------------
# The rule
# ---------------------------------------------------------------------------


def test_recipe_discovery_is_not_vacuous() -> None:
    """The glob must actually find the shipped recipes."""
    found = _recipes()
    assert len(found) >= _MINIMUM_SHIPPED_RECIPES, (
        f"expected at least {_MINIMUM_SHIPPED_RECIPES} recipes under "
        f"{_rel(_RECIPES_DIR)}, found {len(found)}: {[_rel(p) for p in found]}"
    )


@pytest.mark.parametrize("recipe_path", _recipes(), ids=_rel)
def test_shipped_recipe_declares_every_agent_it_references(recipe_path: Path) -> None:
    """A shipped recipe never borrows an agent from its caller."""
    rel = _rel(recipe_path)
    if rel in _EXEMPT:
        pytest.skip(f"exempt: {_EXEMPT[rel]}")

    undeclared = undeclared_agents(recipe_path)
    assert not undeclared, (
        f"{rel} references {sorted(undeclared)} but does not declare them. A "
        f"legacy recipe resolves `agent:` from the CALLING session, so this "
        f"file cannot run from a bundle that lacks those agents. Add "
        f"`schema_version: 2` and a `dependencies:` block listing them in "
        f"`required_agents` (see recipes/form-automation.yaml)."
    )


def test_exemptions_are_pinned_and_reasoned() -> None:
    """An exemption must name a real file and carry a reason.

    Keeps the debt visible: a file cannot quietly slip onto the legacy list.
    """
    for rel, reason in _EXEMPT.items():
        assert (_REPO_ROOT / rel).is_file(), f"exemption names a missing file: {rel}"
        assert reason.strip(), f"exemption for {rel} has no reason"


# ---------------------------------------------------------------------------
# The check must actually bite
# ---------------------------------------------------------------------------


def test_check_catches_a_legacy_recipe(tmp_path: Path) -> None:
    """A recipe with agent steps but no ``schema_version`` is caught."""
    bad = tmp_path / "legacy.yaml"
    bad.write_text(
        yaml.safe_dump(
            {
                "name": "legacy",
                "description": "spawns an agent, declares nothing",
                "steps": [
                    {
                        "id": "a",
                        "agent": "browser-tester:browser-operator",
                        "prompt": "hi",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    assert undeclared_agents(bad) == {"browser-tester:browser-operator"}


def test_check_catches_an_undeclared_agent(tmp_path: Path) -> None:
    """A v2 recipe that references an agent it never declared is caught."""
    bad = tmp_path / "partial.yaml"
    bad.write_text(
        yaml.safe_dump(
            {
                "schema_version": 2,
                "dependencies": [
                    {
                        "source": "git+https://example.invalid/bundle@v1",
                        "kind": "bundle",
                        "required_agents": ["browser-tester:browser-operator"],
                    }
                ],
                "name": "partial",
                "description": "declares one agent, references two",
                "steps": [
                    {
                        "id": "a",
                        "agent": "browser-tester:browser-operator",
                        "prompt": "hi",
                    },
                    {"id": "b", "agent": "foundation:zen-architect", "prompt": "hi"},
                ],
            }
        ),
        encoding="utf-8",
    )
    assert undeclared_agents(bad) == {"foundation:zen-architect"}


def test_check_exempts_a_recipe_with_no_agent_steps(tmp_path: Path) -> None:
    """A recipe that spawns nothing is not required to declare anything."""
    ok = tmp_path / "bash-only.yaml"
    ok.write_text(
        yaml.safe_dump(
            {
                "name": "bash-only",
                "description": "no agent steps at all",
                "steps": [{"id": "a", "type": "bash", "command": "echo hi"}],
            }
        ),
        encoding="utf-8",
    )
    assert undeclared_agents(ok) == set()


def test_check_finds_agents_nested_under_foreach(tmp_path: Path) -> None:
    """A nested step's agent is not invisible to the rule."""
    nested = tmp_path / "nested.yaml"
    nested.write_text(
        yaml.safe_dump(
            {
                "name": "nested",
                "description": "agent hides inside a foreach body",
                "steps": [
                    {
                        "id": "loop",
                        "foreach": "{{items}}",
                        "steps": [
                            {
                                "id": "inner",
                                "agent": "browser-tester:visual-documenter",
                                "prompt": "hi",
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    assert undeclared_agents(nested) == {"browser-tester:visual-documenter"}
