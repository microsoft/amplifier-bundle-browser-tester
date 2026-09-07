#!/usr/bin/env python3
"""Render the delegate agent-catalog lines a scratch session would receive.

Reproduces tool-delegate's own rendering exactly:
    _get_agent_list() -> coordinator.config["agents"], sorted by name
    description       -> "\n".join(f"  - {name}: {desc}")
(foundation modules/tool-delegate/__init__.py:909-941 and :1114-1125)

Usage: render_catalog.py <bundle.md> <ns-prefix> [<ns>=<override-base-path> ...]

The override exists because a bundle's own namespace resolves through the
registry to the INSTALLED copy under ~/.amplifier/cache, not to the checkout
you are editing.  Without it the "after" render is byte-identical to "before"
and the measurement is silently wrong.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from amplifier_foundation import load_bundle


def main(argv: list[str]) -> int:
    bundle_path, ns_prefix = argv[1], argv[2]
    overrides = dict(a.split("=", 1) for a in argv[3:])

    bundle = asyncio.run(load_bundle(bundle_path))
    for ns, base in overrides.items():
        bundle.source_base_paths[ns] = Path(base)
    bundle.load_agent_metadata()
    plan = bundle.to_mount_plan()
    agents = plan.get("agents", {}) or {}

    rows = []
    for name, cfg in sorted(agents.items(), key=lambda kv: kv[0]):
        desc = (cfg or {}).get("description", "No description")
        line = f"  - {name}: {desc}"
        rows.append(
            {
                "name": name,
                "resolved_from": str(bundle.resolve_agent_path(name)),
                "desc_chars": len(desc),
                "line_bytes": len(line.encode()) + 1,  # +1 for the joining newline
                "line": line,
            }
        )

    scoped = [r for r in rows if r["name"].startswith(ns_prefix)]
    print(
        json.dumps(
            {
                "bundle": bundle_path,
                "overrides": overrides,
                "agents_total_in_catalog": len(rows),
                "scoped_prefix": ns_prefix,
                "scoped_agents": len(scoped),
                "scoped_desc_chars": sum(r["desc_chars"] for r in scoped),
                "scoped_catalog_bytes": sum(r["line_bytes"] for r in scoped),
                "catalog_bytes_all_agents": sum(r["line_bytes"] for r in rows),
                "rows": [{k: v for k, v in r.items() if k != "line"} for r in scoped],
            },
            indent=2,
        )
    )
    print("\n===== RENDERED CATALOG LINES (scoped) =====", file=sys.stderr)
    for r in scoped:
        print(r["line"], file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
