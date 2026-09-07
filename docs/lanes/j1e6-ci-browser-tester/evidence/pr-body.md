## What this adds

`.github/workflows/ci.yml` — the first workflow in this repo. **Nothing else is touched:** no agent, no recipe, no context file, no packaging, no docs.

Until now this repo has had **no `.github/workflows/` at all**, so every merge to `main` was verified by whoever opened the PR running things locally. That is not *less* verified than CI, but it is verified by a *different mechanism* each time, and it leaves nothing for a reviewer to look at. PR #8 (the agent-catalog hygiene change) merged that way.

Modeled on [`amplifier-bundle-context-intelligence`](https://github.com/microsoft/amplifier-bundle-context-intelligence/blob/main/.github/workflows/ci.yml)'s `ci.yml` and on the sibling bundle [`amplifier-bundle-notify#12`](https://github.com/microsoft/amplifier-bundle-notify/pull/12), adapted where this repo differs.

## The jobs

Four checks (three jobs, one matrixed), on `push` to `main` and on `pull_request` against `main`. **No path filters anywhere** — a filter that doesn't match leaves a check silently absent, which looks exactly like a passing one. **No error-suppressing directive and no shell fallback that discards an exit code**, anywhere in the file.

| check | what it runs |
|---|---|
| `Lint` | `uvx ruff@0.16.6 check --isolated --select E4,E7,E9,F .` |
| `Tests (py3.11)` | `pytest tests/ -q --tb=short` |
| `Tests (py3.13)` | `pytest tests/ -q --tb=short` |
| `Bundle structure (YAML)` | parses `bundle.md` frontmatter + every `behaviors/*.yaml` |

`permissions: contents: read` only. `timeout-minutes: 10` on every job — a job stuck at "in_progress" reads as "not done yet" rather than "broken", which is how a false green gets merged.

## Proof it can go red

**A CI that has never been observed red is decoration.** A wrong path filter, a wrong test directory, or a step that swallows its exit code all look identical to a working workflow on a green PR.

So before this PR was opened, the same workflow was pushed on a throwaway branch with **one deliberate defect per job**, and the run was observed to fail:

- **RED** — https://github.com/microsoft/amplifier-bundle-browser-tester/actions/runs/34150708849 (scratch PR #9, now **closed**, branch `ci/red-proof-j1e6` **deleted**)
- **GREEN** — https://github.com/microsoft/amplifier-bundle-browser-tester/actions/runs/34150837431 (this PR, workflow-only commit `042d993`)

All four checks went red for their intended reasons:

| check | deliberate defect | observed in the job log |
|---|---|---|
| `Lint` | `zz_ci_red_proof_lint.py` referencing `deliberately_undefined_name` | ``F821 Undefined name `deliberately_undefined_name` `` … `Found 1 error.` |
| `Tests (py3.11)` | `assert 1 == 2` in `tests/test_zz_ci_red_proof.py` | `1 failed, 14 passed in 0.11s` |
| `Tests (py3.13)` | same | `1 failed, 14 passed in 0.11s` |
| `Bundle structure (YAML)` | malformed `behaviors/zz-ci-red-proof.yaml` | `- behaviors/zz-ci-red-proof.yaml: mapping values are not allowed here` |

**The `14 passed` in that red run is the load-bearing detail.** It is a genuine *test* failure inside a suite that collected and executed — not a setup error, not an install error, not a lint error that happened to be red. Collection succeeded; 14 real assertions ran; the 15th, the planted one, failed.

The corresponding green lines, same checks, this PR:

```
Lint                    | All checks passed!
Tests (py3.11)          | 14 passed in 0.06s
Tests (py3.13)          | 14 passed in 0.09s
Bundle structure (YAML) | 2 YAML document(s) parsed.  /  Bundle structure OK.
```

## What the suite actually covers

**This repo is not a zero-test repo, and the gate is not an import smoke.** `tests/test_recipe_manifests.py` — **14 tests**, all wired, none skipped:

| test | count | what it asserts |
|---|---|---|
| `test_shipped_recipe_declares_every_agent_it_references` | 8 (parametrized, one per shipped recipe) | every shipped recipe declares, in its own `schema_version: 2` manifest, each namespaced agent it references |
| `test_recipe_discovery_is_not_vacuous` | 1 | the glob actually finds ≥ 8 recipes — guards against a vacuous pass |
| `test_check_catches_a_legacy_recipe`, `…_an_undeclared_agent`, `…_exempts_a_recipe_with_no_agent_steps`, `…_finds_agents_nested_under_foreach` | 4 | the rule bites, on synthetic fixtures |
| `test_exemptions_are_pinned_and_reasoned` | 1 | no file can quietly slip onto the legacy-exempt list |

That is the rule that keeps these recipes runnable from a session bundle that does not already carry `browser-tester` (before it landed, all eight died on their first step). It is genuine coverage of something this bundle ships. It does **not** cover the agents, the context files, or `agent-browser` itself — nothing here drives a browser.

`bundle.md`'s frontmatter and `behaviors/*.yaml` are covered by the third job; before this PR nothing checked them at all, and a typo there breaks bundle load on a user's machine rather than here.

## Adaptations from the template, and why

| template does | here | why |
|---|---|---|
| `uv sync --frozen` | `uv run --no-project --with 'pytest>=8.0' --with 'PyYAML>=6.0'` | this repo ships **no `pyproject.toml` and no `uv.lock`** — there is nothing for `uv` to sync. The suite is deliberately dependency-light (its own module docstring says so): pytest and PyYAML, no Amplifier packages. |
| `uv sync --only-group dev` + `uv run ruff` | `uvx ruff@0.16.6` | no `[dependency-groups] dev` to install from |
| repo's `[tool.ruff]` config | `--isolated --select E4,E7,E9,F` | this repo has no `[tool.ruff]`. Pinning the tool **and** the rule set means the gate cannot drift red without a visible edit to this file. Same pin and same tier as the sibling `amplifier-bundle-notify`. |
| per-module test jobs | a single root `Tests` job | this bundle carries **no `modules/`** — it is agents, context, behaviors and recipes |
| — | Python 3.11 **and** 3.13 | cover the family's floor and a current minor; the suite uses PEP 604/585 syntax under `from __future__ import annotations` |

There is no `Makefile` in this repo, so there were no existing `check`/`test` entry points to invoke instead of naming commands.

The bundle-structure check is inlined in the workflow (heredoc, quoted delimiter, nothing interpolated into the Python source) rather than added as a script, so the workflow commit really is one file. It fails loud if `behaviors/*.yaml` matches **zero** files — a structure gate that checks nothing is the same decoration problem as a CI that never goes red.

## Findings surfaced while wiring this — deliberately not fixed here

Clean `main` @ `9260481` is **green** on the gate as wired. Two things sit just outside it, both reported rather than papered over, and neither touched by this PR:

**1. `ruff format --check` reports 3 files.** All three are committed lane artifacts under `docs/lanes/kp79-catalog-browser-tester/` — `DONE-NOTE.md`, `proposed-kp79-split.patch.md`, `evidence/render_catalog.py`. Two of the three are *markdown*: ruff 0.16 also formats Python code blocks inside `.md`, so a prose file with an illustrative snippet is in scope for the formatter. Reformatting committed evidence is out of scope for a workflow-only PR, and a formatter gate that is red on day one is worse than none — so `format --check` is not wired.

**2. ruff's full default rule set reports exactly 1 finding**, also in that lane-artifact directory:

```
EXE001 Shebang is present but file is not executable
 --> docs/lanes/kp79-catalog-browser-tester/evidence/render_catalog.py:1:1
```

So this repo is one `chmod +x` away from passing ruff's full modern default tier — not 35 findings away, as some siblings are. If you want the stronger gate, drop `--select E4,E7,E9,F` from the lint step and take that fix as its own commit. The narrower tier was chosen for consistency with the other bundle CI lanes, not to reach green — it is clean either way.

Also worth knowing: `ruff check` scans `.py` only, while `ruff format` scans `.md` too. That asymmetry is why (1) and (2) name different files.

## Cost

Four short `ubuntu-latest` checks per push/PR. No scheduled runs, no matrix beyond two Python versions, **no LLM-backed validation recipes and no API keys** — the recipes under `recipes/` are never executed by CI, only parsed. `permissions: contents: read`.

## Commits

| commit | contents |
|---|---|
| `042d993` | **the workflow, and nothing else** — this is the commit the GREEN run above tested |
| follow-up | this lane's own evidence note and the two verbatim run logs, under `docs/lanes/j1e6-ci-browser-tester/`, matching the `docs/lanes/kp79-…/` convention already on `main`. Changes no shipped file and no workflow. |

Every commit on this branch after `042d993` adds only lane evidence under `docs/lanes/`, and each has run green on the same four checks — see the Checks tab for the head commit. The two URLs quoted above are the red/green pair for the workflow-only commit, which is the pair this workflow was gated on.

---

Generated with Amplifier
