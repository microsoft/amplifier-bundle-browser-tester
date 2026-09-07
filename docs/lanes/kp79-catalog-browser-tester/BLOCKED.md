# BLOCKED — lane kp79-catalog-browser-tester

**OUTCOME branch C.** The item cannot be resolved by this lane. Reason is **not** the
spend cap (the cap is $0 and it funded every deliverable).

## What is blocked, and why

`work_claim(project="model_performance", item_id="model_performance-kp79")` was refused
on this lane's first tool call:

```
claim model_performance-kp79 as 'agent-spark-1-2776671' failed:
Error claiming model_performance-kp79: issue already claimed by agent-spark-1-2776455
```

The holder is **live, not stale**:

- `work_status` reports `held_stale: 0` for project `model_performance`.
- pid `2776455` is running (`amplifier run /goal @GOAL.md`, started 09:30:49).
- `readlink /proc/2776455/cwd` ->
  `/home/bkrabach/dev/hw-model-performance/lanes/kp79-catalog-android-tester/amplifier-bundle-android-tester`

## Root cause: one sweep item, five per-repo lanes

The single item `model_performance-kp79` was launched into **five** concurrent lanes,
each of whose `GOAL.md` Procedure 1 instructs it to claim **that same item id**:

```
lanes/kp79-catalog-android-tester        <- won the claim race, holds the item
lanes/kp79-catalog-browser-tester        <- this lane, refused
lanes/kp79-catalog-dot-graph
lanes/kp79-catalog-infographic-builder
lanes/kp79-catalog-reality-check
```

Exactly one holder can exist, so **four of the five lanes are structurally guaranteed to
be refused**.

### The more serious half of this defect

`kp79` is a **sweep item spanning roughly twelve repos** (its own description names
dot-graph, reality-check, android-tester, ios-tester, browser-tester,
context-intelligence, attractor, work-tracker, stories, converge, plus queued
dtu/amplifier-tester and third-party notify / amplifier-online). Each lane, however, owns
**exactly one repo**.

So the lane that *wins* the race inherits a contradiction: its own `GOAL.md` branch A
tells it to `work_resolve` **kp79** once its **single repo's** deliverables exist. Doing
that closes the sweep on behalf of the other ~11 repos it never touched — and a resolved
item is the signal everyone downstream reads as "swept".

**The collision is the visible symptom; premature closure is the expensive one.** A
per-repo lane can never legitimately be the thing that resolves a twelve-repo sweep item.

**Remedy:** one work item per repo (children of a `kp79` parent, so the parent closes only
when the children do), or a lane contract that does not require holding a claim in order
to do repo-local work.

**Immediate risk, worth acting on before it lands:** the holding lane
(`kp79-catalog-android-tester`) may resolve `kp79` on completing android-tester alone. If
it does, this repo's work (PR #8) and the three other lanes' work are silently orphaned
under a closed item.

## `work_release` was NOT called — deliberately

Procedure 5 requires releasing "while you still HOLD the item". This lane **never held**
it. Releasing another live session's hold would be wrong, and the tool would refuse.
There is nothing for this lane to release.

## The deliverables shipped anyway

Every deliverable is a $0 text edit inside this lane's own repo, so stopping would have
left `amplifier-bundle-browser-tester` unswept at zero saving. The work is on
`lane/kp79-catalog-browser-tester` as a **draft PR**; the manager decides whether to
merge it. Nothing outside this repo was touched.

Result: 3/3 agent descriptions trigger-first, <= ~600 chars, explicit USE WHEN / DO NOT
USE WHEN, **zero `<example>`/`<commentary>`**; **-793 catalog bytes (-30.8%)** measured
by rendering the delegate agent catalog before and after; `validate-agents` **PASS WITH
WARNINGS** (3 agents, 0 errors, 3 pre-existing `NO_TOOLS_SECTION` warnings);
`pytest tests/` **14 passed**; repo has **no CI**.

Full evidence: `docs/lanes/kp79-catalog-browser-tester/DONE-NOTE.md`.
