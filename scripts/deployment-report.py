#!/usr/bin/env python3
import json, sys

if len(sys.argv) != 2:
    print("Usage: deployment-report.py <outputs.json>", file=sys.stderr)
    sys.exit(2)

with open(sys.argv[1], encoding="utf-8") as f:
    outputs = json.load(f)

print("# Terraform Deployment Report\n")
print("| Output | Value |")
print("|---|---|")
for name, item in sorted(outputs.items()):
    value = item.get("value")
    print(f"| `{name}` | `{json.dumps(value, default=str)}` |")

print("\nDeployment completed successfully.")
