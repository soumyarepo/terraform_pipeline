#!/usr/bin/env python3
import argparse, json, os, html
from collections import Counter

p = argparse.ArgumentParser()
p.add_argument("plan")
p.add_argument("outputs")
p.add_argument("--markdown", required=True)
p.add_argument("--html", required=True)
args = p.parse_args()

with open(args.plan, encoding="utf-8") as f:
    plan = json.load(f)
with open(args.outputs, encoding="utf-8") as f:
    outputs = json.load(f)

rows, counts = [], Counter()
for rc in plan.get("resource_changes", []):
    acts = rc.get("change", {}).get("actions", [])
    if acts == ["create"]: action="ADD"
    elif acts == ["update"]: action="CHANGE"
    elif acts == ["delete"]: action="DELETE"
    elif "create" in acts and "delete" in acts: action="REPLACE"
    else: continue
    counts[action] += 1
    rows.append((action, rc.get("type",""), rc.get("address",""), "SUCCESS"))

env = os.getenv("DEPLOY_ENV","production")
region = os.getenv("AWS_REGION","")
commit = os.getenv("GIT_COMMIT","")
run = os.getenv("PIPELINE_RUN","")

md = [
"# Terraform Deployment Report", "",
f"Environment: **{env}**  ",
f"AWS Region: **{region}**  ",
f"Git Commit: `{commit}`  ",
f"Pipeline Run: `{run}`  ", "",
"## Summary", "",
"| Action | Count |", "|---|---:|"
]
for a in ("ADD","CHANGE","DELETE","REPLACE"):
    md.append(f"| {a} | {counts[a]} |")
md += ["", "## Applied Resource Changes", "",
       "| Action | Resource Type | Terraform Address | Status |",
       "|---|---|---|---|"]
for r in rows:
    md.append(f"| {r[0]} | `{r[1]}` | `{r[2]}` | {r[3]} |")
if not rows:
    md.append("| NO CHANGE | - | - | SUCCESS |")
md += ["", "## Terraform Outputs", "", "| Output | Value |", "|---|---|"]
for k,v in sorted(outputs.items()):
    md.append(f"| `{k}` | `{json.dumps(v.get('value'))}` |")
open(args.markdown,"w",encoding="utf-8").write("\n".join(md)+"\n")

trs = "".join(
    f"<tr><td>{html.escape(r[0])}</td><td>{html.escape(r[1])}</td>"
    f"<td><code>{html.escape(r[2])}</code></td><td>{html.escape(r[3])}</td></tr>"
    for r in rows
) or "<tr><td>NO CHANGE</td><td>-</td><td>-</td><td>SUCCESS</td></tr>"

summary = "".join(f"<tr><td>{a}</td><td>{counts[a]}</td></tr>"
                  for a in ("ADD","CHANGE","DELETE","REPLACE"))
outrows = "".join(
    f"<tr><td>{html.escape(k)}</td><td><code>{html.escape(json.dumps(v.get('value')))}</code></td></tr>"
    for k,v in sorted(outputs.items())
)
doc = f"""<!doctype html><html><body>
<h2>Terraform AWS Deployment - SUCCESS</h2>
<p><b>Environment:</b> {html.escape(env)}<br>
<b>AWS Region:</b> {html.escape(region)}<br>
<b>Git Commit:</b> <code>{html.escape(commit)}</code><br>
<b>Pipeline Run:</b> {html.escape(run)}</p>
<h3>Summary</h3>
<table border="1" cellpadding="6" cellspacing="0"><tr><th>Action</th><th>Count</th></tr>{summary}</table>
<h3>Applied Resource Changes</h3>
<table border="1" cellpadding="6" cellspacing="0">
<tr><th>Action</th><th>Resource Type</th><th>Terraform Address</th><th>Status</th></tr>{trs}</table>
<h3>Terraform Outputs / Resource Details</h3>
<table border="1" cellpadding="6" cellspacing="0"><tr><th>Output</th><th>Value</th></tr>{outrows}</table>
</body></html>"""
open(args.html,"w",encoding="utf-8").write(doc)
