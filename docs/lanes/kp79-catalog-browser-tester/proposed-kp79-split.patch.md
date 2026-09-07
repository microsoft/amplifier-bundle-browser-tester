# PROPOSED PATCH — split `model_performance-kp79` into per-repo children

**Status:** proposal artifact. **Not applied by this lane.** Shipped here under the lane's
ARTIFACT ROOT because `GOAL.md`'s own defect clause prescribes exactly this handling:

> "that is a DEFECT IN THIS GOAL, not a task. Report it against the goal, **ship the patch
> as an artifact under your ARTIFACT ROOT**, and resolve — do not edit another repo, and
> do not invent a fourth outcome branch."

This lane reported the defect and ships the patch. It cannot perform the third verb
(`resolve`) — that verb is itself gated behind the thing that is blocked, which is the
defect biting a second time.

---

## The defect, in two lines

`model_performance-kp79` is **one item naming ~12 repos**. It was launched into **five
lanes, each owning exactly one repo**. Only one lane can hold it, so four are guaranteed a
refused claim — and the winner's own branch A instructs it to `work_resolve` the
twelve-repo sweep once its single repo is done.

## Why this must be applied BEFORE the holder resolves

`kp79-catalog-android-tester` holds the item and is live. When it resolves, `kp79` closes
with `status: resolved` — the signal every downstream reader treats as "swept". At that
moment ~10 repos look done that were never touched, and four lanes' published PRs
(including `amplifier-bundle-browser-tester#8`) are orphaned under a closed item with no
surviving pointer to them.

Splitting first costs ~5 minutes. Splitting after means reopening `kp79`, which clears
`closed_at` and moves every throughput roll-up by one item.

---

## Patch A — restructure the queue (sanctioned tools only, no raw `bd`)

Create one child per repo, then make the parent depend on them so it cannot close first.

```python
# 1. One child per repo named in kp79's own description.
#    Each child is what a per-repo lane can legitimately claim AND resolve.
for repo, done in [
    ("amplifier-bundle-dot-graph",            "open"),
    ("amplifier-bundle-reality-check",        "open"),
    ("amplifier-bundle-android-tester",       "open"),   # currently in flight
    ("amplifier-bundle-ios-tester",           "open"),
    ("amplifier-bundle-browser-tester",       "DONE"),   # PR #8, evidence below
    ("amplifier-bundle-context-intelligence", "open"),
    ("amplifier-bundle-attractor",            "open"),
    ("amplifier-work-tracker",                "open"),   # length/shape fix, NOT an example strip
    ("amplifier-bundle-stories",              "open"),   # CHECK first; may already be compliant
    ("amplifier-bundle-converge",             "open"),
]:
    work_add(
        project="model_performance",
        title=f"STAGE 1 (A): agent-description catalog hygiene — {repo}",
        description=(
            "Per-repo child of model_performance-kp79. Scope is THIS REPO ONLY.\n"
            "Standard: trigger-first, <= ~600 chars, explicit USE WHEN / DO NOT USE WHEN, "
            "ZERO <example>/<commentary>. Skills: trigger-first, single paragraph, <= ~400 chars.\n"
            "Deliverables: fidelity table, before/after char counts, delegate-catalog render "
            "before/after with bytes saved quoted, validate-agents verdict on the branch, "
            "CI green where CI exists (say so plainly where it does not).\n"
            "Spend: $0. Text edits, a recipe run, a catalog render."
        ),
        acceptance=(
            "Given this repo's agents, when its PR lands, then every frontmatter description "
            "is trigger-first, <= ~600 chars, carries explicit USE WHEN / DO NOT USE WHEN, and "
            "contains ZERO <example> or <commentary> blocks.\n\n"
            "Given fidelity, then a per-agent table lists any USE WHEN / DO NOT USE WHEN fact "
            "present in stock and absent in lean; expected none, anything dropped restored with "
            "the byte delta noted.\n\n"
            "Given the measurement, then the delegate agent catalog is rendered from a scratch "
            "session before and after with the bytes saved quoted — not merely the file diff.\n\n"
            "Given descriptions already compliant, then the lane says so and skips rather than "
            "editing to produce a diff."
        ),
    )

# 2. Parent cannot close before its children.
for child_id in NEW_CHILD_IDS:
    work_dep(project="model_performance", item_id="model_performance-kp79",
             depends_on=child_id, dep_type="blocks")
```

**Ordering note.** `kp79` is currently `held`. `work_dep` does not require a claim, so the
edges can be declared now. A `blocks` edge is enforced at *claim* time, not at resolve
time, so **the edges alone do not stop the holder from resolving** — they make the
structure correct for everyone after. If the holder is expected to resolve imminently,
message that lane (or let it resolve and then `work_reopen` with the split as the reason).

## Patch B — the child already satisfied

`amplifier-bundle-browser-tester` needs no work. Close its child on creation with:

```python
work_resolve(
    id=<browser_tester_child_id>,
    reason=(
        "DONE. 3/3 agent descriptions trigger-first, <= ~600 chars (560/582/522), explicit "
        "USE WHEN / DO NOT USE WHEN, ZERO <example>/<commentary>. Delegate catalog rendered "
        "before/after from a scratch bundle load: this bundle's slice 2574 -> 1781 bytes, "
        "-793 bytes (-30.8%) paid on every turn of every session. Fidelity: 0 stock routing "
        "facts dropped, 0 restorations. validate-agents v1.7.0 on the branch: PASS WITH "
        "WARNINGS, 3 agents, 0 errors (3 NO_TOOLS_SECTION warnings all pre-existing at HEAD). "
        "pytest tests/: 14 passed. Repo has NO CI. Repo ships NO skills. "
        "Draft PR: https://github.com/microsoft/amplifier-bundle-browser-tester/pull/8 "
        "(head 19e598ab2b857240e77e6d391e988554140f84af). Spend $0."
    ),
)
```

## Patch C — the `GOAL.md` wording that caused this

Every per-repo lane's `GOAL.md` Procedure 1 currently reads:

```
1. FIRST: work_claim(project="model_performance", item_id="model_performance-kp79")
```

Five lanes, one id. Replace with the lane's **own child id**:

```
1. FIRST: work_claim(project="model_performance", item_id="<THIS LANE'S CHILD ID>")
```

And branch A's first conjunct should name the child, not the sweep parent:

```
A. RESOLVED. Work item <THIS LANE'S CHILD ID> is resolved with a user-readable summary
   AND the deliverables below exist (as a draft PR on the module's origin).
```

**The general rule worth keeping:** a lane's terminal state must be reachable using only
the paths and items that lane owns. A one-repo lane told to resolve a twelve-repo sweep
item has an unreachable branch A by construction — and, worse, a branch A that is
*harmful* to satisfy.

---

## Evidence backing the browser-tester child

| | |
|---|---|
| PR | https://github.com/microsoft/amplifier-bundle-browser-tester/pull/8 (draft, open) |
| Branch | `lane/kp79-catalog-browser-tester` |
| head_sha | `19e598ab2b857240e77e6d391e988554140f84af` (read back via `git ls-remote`) |
| Catalog saving | 2574 → 1781 bytes, **−793 (−30.8%)** |
| Fidelity | 0 facts dropped, 0 restorations |
| validate-agents | PASS WITH WARNINGS, 3 agents, 0 errors |
| Tests | `pytest tests/` → 14 passed |
| CI | none in this repo |
| Spend | $0.00 |

Full detail: `DONE-NOTE.md` in this directory.
