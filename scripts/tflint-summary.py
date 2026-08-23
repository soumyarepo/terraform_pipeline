#!/usr/bin/env python3

import json
import sys
import html
from collections import Counter
from pathlib import Path


# ------------------------------------------------------------
# Validate arguments
# ------------------------------------------------------------

if len(sys.argv) != 4:
    print(
        "Usage: tflint-summary.py "
        "<tflint-results.json> "
        "<tflint-summary.md> "
        "<tflint-summary.html>"
    )
    sys.exit(2)


json_file = Path(sys.argv[1])
markdown_file = Path(sys.argv[2])
html_file = Path(sys.argv[3])


# ------------------------------------------------------------
# Load TFLint JSON
# ------------------------------------------------------------

if not json_file.exists():
    print(f"TFLint result file not found: {json_file}")
    sys.exit(1)


with json_file.open(encoding="utf-8") as f:
    data = json.load(f)


issues = data.get("issues", [])
tflint_errors = data.get("errors", [])


# ------------------------------------------------------------
# Friendly recommendations
# ------------------------------------------------------------

recommendations = {
    "terraform_unused_declarations":
        "Remove the unused declaration or use it in the Terraform configuration.",

    "terraform_required_version":
        "Add a terraform.required_version constraint.",

    "terraform_required_providers":
        "Add the provider under required_providers with an explicit version constraint.",

    "terraform_deprecated_interpolation":
        "Replace deprecated interpolation syntax with modern Terraform syntax.",

    "terraform_documented_variables":
        "Add a description to the Terraform variable.",

    "terraform_documented_outputs":
        "Add a description to the Terraform output."
}


friendly_names = {
    "terraform_unused_declarations":
        "Unused declarations",

    "terraform_required_version":
        "Missing required_version",

    "terraform_required_providers":
        "Missing provider version constraint",

    "terraform_deprecated_interpolation":
        "Deprecated interpolation",

    "terraform_documented_variables":
        "Undocumented variables",

    "terraform_documented_outputs":
        "Undocumented outputs"
}


# ------------------------------------------------------------
# Collect statistics
# ------------------------------------------------------------

rule_counts = Counter()
severity_counts = Counter()
affected_files = set()

details = []


for issue in issues:

    rule_info = issue.get("rule", {})

    rule = rule_info.get(
        "name",
        "unknown"
    )

    severity = rule_info.get(
        "severity",
        "warning"
    ).upper()

    message = issue.get(
        "message",
        "Unknown issue"
    )

    location = issue.get(
        "range",
        {}
    )

    filename = location.get(
        "filename",
        "unknown"
    ).replace("\\", "/")

    start = location.get(
        "start",
        {}
    )

    line = start.get(
        "line",
        "-"
    )

    fixable = issue.get(
        "fixable",
        False
    )

    rule_counts[rule] += 1
    severity_counts[severity] += 1
    affected_files.add(filename)

    details.append({
        "severity": severity,
        "rule": rule,
        "category": friendly_names.get(
            rule,
            rule
        ),
        "file": filename,
        "line": line,
        "message": message,
        "fix": recommendations.get(
            rule,
            "Review the TFLint finding and update the Terraform configuration."
        ),
        "fixable": fixable
    })


# ------------------------------------------------------------
# Overall status
# ------------------------------------------------------------

total_issues = len(issues)

warning_count = severity_counts.get(
    "WARNING",
    0
)

error_count = (
    severity_counts.get("ERROR", 0)
    + len(tflint_errors)
)


if error_count > 0:
    status = "FAILED"

elif warning_count > 0:
    status = "WARNING"

else:
    status = "PASSED"


if status == "PASSED":
    status_icon = "✅"
    status_text = "✅ PASSED"

elif status == "WARNING":
    status_icon = "⚠️"
    status_text = "⚠️ WARNING"

else:
    status_icon = "❌"
    status_text = "❌ FAILED"


# ------------------------------------------------------------
# Markdown Report
# ------------------------------------------------------------

md = []

md.append("# 🔎 Terraform TFLint Quality Gate")
md.append("")

md.append("## 🧾 Scan Summary")
md.append("")

md.append("| Metric | Result |")
md.append("|---|---:|")

md.append(
    f"| Status | **{status_icon} {status}** |"
)

md.append(
    f"| Total Issues | **{total_issues}** |"
)

md.append(
    f"| Errors | **{error_count}** |"
)

md.append(
    f"| Warnings | **{warning_count}** |"
)

md.append(
    f"| Affected Files | **{len(affected_files)}** |"
)

md.append("")


# ------------------------------------------------------------
# Category Summary
# ------------------------------------------------------------

md.append("## 📊 Issue Summary")
md.append("")

md.append(
    "| Category | Count | Recommended Fix |"
)

md.append(
    "|---|---:|---|"
)


for rule, count in rule_counts.items():

    category = friendly_names.get(
        rule,
        rule
    )

    fix = recommendations.get(
        rule,
        "Review the TFLint finding."
    )

    md.append(
        f"| {category} | {count} | {fix} |"
    )


if total_issues == 0:

    md.append(
        "| No issues detected | 0 | No action required ✅ |"
    )


# ------------------------------------------------------------
# Issues by file
# ------------------------------------------------------------

file_counts = Counter(
    issue["file"]
    for issue in details
)


md.append("")
md.append("## 📁 Issues by File")
md.append("")

md.append(
    "| File | Issues |"
)

md.append(
    "|---|---:|"
)


for filename, count in sorted(
    file_counts.items(),
    key=lambda item: (
        -item[1],
        item[0]
    )
):

    md.append(
        f"| `{filename}` | {count} |"
    )


if total_issues == 0:

    md.append(
        "| - | 0 |"
    )


# ------------------------------------------------------------
# Detailed Issues
# ------------------------------------------------------------

md.append("")
md.append("## 📋 Detailed Findings")
md.append("")

md.append(
    "| # | Severity | Rule | File | Line | Message | Fixable | Recommended Fix |"
)

md.append(
    "|---:|---|---|---|---:|---|---|---|"
)


for index, issue in enumerate(
    details,
    start=1
):

    if issue["severity"] == "ERROR":
        severity_icon = "❌"

    elif issue["severity"] == "WARNING":
        severity_icon = "⚠️"

    else:
        severity_icon = "ℹ️"

    message = issue["message"].replace(
        "|",
        "\\|"
    )

    fix = issue["fix"].replace(
        "|",
        "\\|"
    )

    fixable_text = (
        "✅ Yes"
        if issue["fixable"]
        else "❌ No"
    )

    md.append(
        f"| {index} "
        f"| {severity_icon} {issue['severity']} "
        f"| `{issue['rule']}` "
        f"| `{issue['file']}` "
        f"| {issue['line']} "
        f"| {message} "
        f"| {fixable_text} "
        f"| {fix} |"
    )


if total_issues == 0:

    md.append(
        "| 1 | ✅ PASSED | - | - | - | "
        "No TFLint issues detected | - | No action required |"
    )


# ------------------------------------------------------------
# Write Markdown Report
# ------------------------------------------------------------

markdown_file.write_text(
    "\n".join(md) + "\n",
    encoding="utf-8"
)


# ------------------------------------------------------------
# HTML Category Summary
# ------------------------------------------------------------

summary_rows = ""


for rule, count in rule_counts.items():

    category = friendly_names.get(
        rule,
        rule
    )

    fix = recommendations.get(
        rule,
        "Review the TFLint finding."
    )

    summary_rows += f"""
    <tr>
        <td>{html.escape(category)}</td>
        <td style="text-align:center;">
            <strong>{count}</strong>
        </td>
        <td>{html.escape(fix)}</td>
    </tr>
    """


if total_issues == 0:

    summary_rows = """
    <tr>
        <td>No issues detected</td>
        <td style="text-align:center;">0</td>
        <td>No action required</td>
    </tr>
    """


# ------------------------------------------------------------
# HTML file summary
# ------------------------------------------------------------

file_rows = ""


for filename, count in sorted(
    file_counts.items(),
    key=lambda item: (
        -item[1],
        item[0]
    )
):

    file_rows += f"""
    <tr>
        <td>{html.escape(filename)}</td>
        <td style="text-align:center;">
            {count}
        </td>
    </tr>
    """


if total_issues == 0:

    file_rows = """
    <tr>
        <td>-</td>
        <td style="text-align:center;">0</td>
    </tr>
    """


# ------------------------------------------------------------
# HTML Detailed Findings
# ------------------------------------------------------------

detail_rows = ""


for index, issue in enumerate(
    details,
    start=1
):

    if issue["severity"] == "ERROR":
        severity_display = "❌ ERROR"

    elif issue["severity"] == "WARNING":
        severity_display = "⚠️ WARNING"

    else:
        severity_display = f"ℹ️ {issue['severity']}"

    fixable_display = (
        "✅ Yes"
        if issue["fixable"]
        else "❌ No"
    )

    detail_rows += f"""
    <tr>
        <td>{index}</td>

        <td>
            {html.escape(severity_display)}
        </td>

        <td>
            <code>{html.escape(issue['rule'])}</code>
        </td>

        <td>
            <code>{html.escape(issue['file'])}</code>
        </td>

        <td style="text-align:center;">
            {issue['line']}
        </td>

        <td>
            {html.escape(issue['message'])}
        </td>

        <td style="text-align:center;">
            {html.escape(fixable_display)}
        </td>

        <td>
            {html.escape(issue['fix'])}
        </td>
    </tr>
    """


if total_issues == 0:

    detail_rows = """
    <tr>
        <td>1</td>
        <td>✅ PASSED</td>
        <td>-</td>
        <td>-</td>
        <td>-</td>
        <td>No TFLint issues detected</td>
        <td>-</td>
        <td>No action required</td>
    </tr>
    """


# ------------------------------------------------------------
# Status CSS
# ------------------------------------------------------------

if status == "PASSED":

    status_class = "passed"

elif status == "WARNING":

    status_class = "warning"

else:

    status_class = "failed"


# ------------------------------------------------------------
# HTML Report
# ------------------------------------------------------------

html_report = f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
Terraform TFLint Quality Gate
</title>


<style>

body {{
    font-family:
        Arial,
        Helvetica,
        sans-serif;

    background-color: #f6f8fa;

    padding: 20px;

    color: #24292f;
}}


.container {{

    max-width: 1200px;

    margin: auto;

    background-color: #ffffff;

    padding: 30px;

    border-radius: 10px;

    border: 1px solid #d0d7de;
}}


h1 {{
    color: #24292f;
    margin-bottom: 10px;
}}


h2 {{
    color: #24292f;
    margin-top: 30px;
}}


.status {{
    font-size: 20px;
    font-weight: bold;
    padding: 12px;
    border-radius: 6px;
}}


.status.passed {{
    background-color: #dafbe1;
    color: #116329;
}}


.status.warning {{
    background-color: #fff8c5;
    color: #9a6700;
}}


.status.failed {{
    background-color: #ffebe9;
    color: #cf222e;
}}


.cards {{
    display: flex;
    gap: 15px;
    margin-top: 20px;
    margin-bottom: 25px;
}}


.card {{
    flex: 1;

    background-color: #f6f8fa;

    border: 1px solid #d0d7de;

    border-radius: 8px;

    padding: 18px;

    text-align: center;
}}


.card-title {{
    font-size: 14px;
    color: #57606a;
}}


.card-value {{
    font-size: 28px;
    font-weight: bold;
    margin-top: 8px;
}}


table {{
    width: 100%;

    border-collapse: collapse;

    margin-top: 15px;

    margin-bottom: 30px;
}}


th {{
    background-color: #24292f;

    color: white;

    padding: 11px;

    text-align: left;

    border: 1px solid #24292f;
}}


td {{
    border: 1px solid #d0d7de;

    padding: 10px;

    vertical-align: top;
}}


tr:nth-child(even) {{
    background-color: #f6f8fa;
}}


code {{
    font-family:
        Consolas,
        Monaco,
        monospace;

    background-color: #eff1f3;

    padding: 2px 5px;

    border-radius: 4px;
}}


.footer {{
    margin-top: 30px;

    padding-top: 15px;

    border-top: 1px solid #d0d7de;

    color: #57606a;

    font-size: 12px;
}}


</style>

</head>


<body>


<div class="container">


<h1>
🔎 Terraform TFLint Quality Gate
</h1>


<p>
Terraform static code analysis has completed.
The results below summarize the detected
quality and configuration issues.
</p>


<div class="status {status_class}">

Status: {status_text}

</div>


<div class="cards">


<div class="card">

<div class="card-title">
Total Issues
</div>

<div class="card-value">
{total_issues}
</div>

</div>


<div class="card">

<div class="card-title">
Errors
</div>

<div class="card-value">
{error_count}
</div>

</div>


<div class="card">

<div class="card-title">
Warnings
</div>

<div class="card-value">
{warning_count}
</div>

</div>


<div class="card">

<div class="card-title">
Affected Files
</div>

<div class="card-value">
{len(affected_files)}
</div>

</div>


</div>


<h2>
📊 Issue Summary
</h2>


<table>

<thead>

<tr>

<th>
Category
</th>

<th>
Count
</th>

<th>
Recommended Fix
</th>

</tr>

</thead>


<tbody>

{summary_rows}

</tbody>

</table>


<h2>
📁 Issues by File
</h2>


<table>

<thead>

<tr>

<th>
File
</th>

<th>
Issues
</th>

</tr>

</thead>


<tbody>

{file_rows}

</tbody>

</table>


<h2>
📋 Detailed Findings
</h2>


<table>

<thead>

<tr>

<th>
#
</th>

<th>
Severity
</th>

<th>
Rule
</th>

<th>
File
</th>

<th>
Line
</th>

<th>
Message
</th>

<th>
Fixable
</th>

<th>
Recommended Fix
</th>

</tr>

</thead>


<tbody>

{detail_rows}

</tbody>

</table>


<div class="footer">

Generated automatically by the Terraform CI/CD pipeline using TFLint.

</div>


</div>


</body>

</html>
"""


# ------------------------------------------------------------
# Write HTML report
# ------------------------------------------------------------

html_file.write_text(
    html_report,
    encoding="utf-8"
)


# ------------------------------------------------------------
# Console Summary
# ------------------------------------------------------------

print("")
print("=" * 72)
print("TERRAFORM TFLINT QUALITY GATE")
print("=" * 72)

print(
    f"Status         : {status}"
)

print(
    f"Total Issues   : {total_issues}"
)

print(
    f"Errors         : {error_count}"
)

print(
    f"Warnings       : {warning_count}"
)

print(
    f"Affected Files : {len(affected_files)}"
)


print("")
print("ISSUE CATEGORY SUMMARY")
print("-" * 72)


if rule_counts:

    for rule, count in rule_counts.items():

        category = friendly_names.get(
            rule,
            rule
        )

        print(
            f"{category:<42} {count}"
        )

else:

    print(
        "No TFLint issues detected."
    )


print("")
print("-" * 72)

print(
    f"Markdown report : {markdown_file}"
)

print(
    f"HTML report     : {html_file}"
)

print("=" * 72)