#!/usr/bin/env python3
import json, sys
from collections import Counter

if len(sys.argv) != 2:
    print("Usage: terraform-plan-summary.py <tfplan.json>", file=sys.stderr)
    sys.exit(2)

with open(sys.argv[1], encoding="utf-8") as f:
    plan = json.load(f)

counts = Counter()
rows = []

for rc in plan.get("resource_changes", []):
    address = rc.get("address", "")
    actions = rc.get("change", {}).get("actions", [])
    if actions == ["create"]:
        action = "ADD"; counts["ADD"] += 1
    elif actions == ["update"]:
        action = "CHANGE"; counts["CHANGE"] += 1
    elif actions == ["delete"]:
        action = "DELETE"; counts["DELETE"] += 1
    elif set(actions) == {"create", "delete"}:
        action = "REPLACE"; counts["REPLACE"] += 1
    elif "create" in actions and "delete" in actions:
        action = "REPLACE"; counts["REPLACE"] += 1
    else:
        continue
    rows.append((action, rc.get("type", ""), address))

print("## Terraform Plan Summary\n")
print("| Action | Count |")
print("|---|---:|")
for action in ("ADD", "CHANGE", "DELETE", "REPLACE"):
    print(f"| {action} | {counts[action]} |")

print("\n## Resources\n")
print("| Action | Resource Type | Terraform Address |")
print("|---|---|---|")
for action, rtype, address in rows:
    print(f"| {action} | `{rtype}` | `{address}` |")

if not rows:
    print("\nNo infrastructure changes detected.")
