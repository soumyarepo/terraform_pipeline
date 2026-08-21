#!/usr/bin/env python3
import json, sys
from collections import Counter

with open(sys.argv[1], encoding="utf-8") as f:
    plan = json.load(f)

counts = Counter()
rows = []
for rc in plan.get("resource_changes", []):
    actions = rc.get("change", {}).get("actions", [])
    if actions == ["create"]:
        action = "ADD"
    elif actions == ["update"]:
        action = "CHANGE"
    elif actions == ["delete"]:
        action = "DELETE"
    elif "create" in actions and "delete" in actions:
        action = "REPLACE"
    else:
        continue
    counts[action] += 1
    rows.append((action, rc.get("type",""), rc.get("address","")))

print("## Terraform Plan Summary\n")
print("| Action | Count |")
print("|---|---:|")
for a in ("ADD","CHANGE","DELETE","REPLACE"):
    print(f"| {a} | {counts[a]} |")
print("\n## Planned Resource Changes\n")
print("| Action | Resource Type | Terraform Address |")
print("|---|---|---|")
for row in rows:
    print(f"| {row[0]} | `{row[1]}` | `{row[2]}` |")
if not rows:
    print("| NO CHANGE | - | - |")
