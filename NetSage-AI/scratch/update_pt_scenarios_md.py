import csv
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
csv_path = base_dir / "data" / "cases.csv"
md_path = base_dir / "docs" / "packet_tracer_scenarios.md"

with open(csv_path, "r", encoding="utf-8") as f:
    cases = list(csv.DictReader(f))

with open(md_path, "w", encoding="utf-8") as f:
    f.write("# NetSage AI — Packet Tracer Troubleshooting Scenarios\n\n")
    f.write(f"This document provides full details for all **{len(cases)} Packet Tracer lab scenarios** in the NetSage AI dataset.\n\n")
    f.write("## Ground-Truth Architecture Overview\n\n")
    f.write("Each scenario is divided into:\n")
    f.write("- **Public Evidence**: Case ID, Category, User-visible Symptom, Topology Note, Cisco Show Commands.\n")
    f.write("- **Ground Truth**: Expected Root Cause, OSI Layer, Severity, Recommended Fix, Verification Procedure.\n\n")
    f.write("---\n\n")

    for case in cases:
        f.write(f"## {case['case_id']} — {case['concept']} ({case['severity']} Severity)\n\n")
        f.write(f"- **Category Tag**: `{case['concept']}`\n")
        f.write(f"- **OSI Layer**: `{case['osi_layer']}`\n")
        f.write(f"- **Severity**: `{case['severity']}`\n")
        f.write(f"- **Network Topology**: {case['topology_note']}\n")
        f.write(f"- **Expected User Symptom**: {case['symptom']}\n")
        f.write(f"- **Observed Show Commands**:\n```text\n{case['show_outputs']}\n```\n")
        f.write(f"- **Expected Root Cause**: {case['expected_fault']}\n")
        f.write(f"- **Recommended Fix**: {case['expected_fix']}\n")
        f.write(f"- **Verification Procedure**: {case['verification']}\n\n")
        f.write("---\n\n")

print(f"Successfully generated {md_path} with {len(cases)} scenarios.")
