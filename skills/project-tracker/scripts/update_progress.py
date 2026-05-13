#!/usr/bin/env python3
"""
update_progress.py — Project Tracker Progress Updater

Reads project-memory/progress/progress.json and regenerates:
  - progress diagrams in project-memory/progress/diagrams/
  - a summary report at project-memory/progress/summary.md

Also marks discovery-v4 run IDs in the progress.json watermark as processed.

Usage:
    python3 skills/project-tracker/scripts/update_progress.py [--discovery-run <run_id>]

Run from the repository root.
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parents[3]
PROGRESS_FILE = REPO_ROOT / "project-memory" / "progress" / "progress.json"
DIAGRAMS_DIR = REPO_ROOT / "project-memory" / "progress" / "diagrams"
SUMMARY_FILE = REPO_ROOT / "project-memory" / "progress" / "summary.md"


def load_progress() -> dict:
    with open(PROGRESS_FILE, "r") as f:
        return json.load(f)


def save_progress(data: dict) -> None:
    data["metadata"]["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[update_progress] Saved: {PROGRESS_FILE}")


def mark_watermark(data: dict, run_id: str) -> bool:
    """Mark a discovery run as processed in the watermark. Returns True if added."""
    watermarks = data["metadata"].setdefault("watermarks", {})
    processed = watermarks.setdefault("discovery-v4-processed", [])
    if run_id not in processed:
        processed.append(run_id)
        print(f"[update_progress] Watermark: marked discovery-v4/{run_id} as processed")
        return True
    print(f"[update_progress] Watermark: discovery-v4/{run_id} already processed")
    return False


def generate_status_diagram(nodes: list) -> str:
    """Generate a Mermaid pie chart of node statuses."""
    counts = defaultdict(int)
    for node in nodes:
        counts[node.get("status", "unknown")] += 1

    lines = ["```mermaid", "pie title Feature Status Distribution"]
    for status, count in sorted(counts.items()):
        lines.append(f'    "{status}" : {count}')
    lines.append("```")
    return "\n".join(lines)


def generate_dependency_diagram(nodes: list, edges: list) -> str:
    """Generate a Mermaid flowchart of feature dependencies."""
    node_map = {n["id"]: n for n in nodes}

    lines = ["```mermaid", "flowchart TD"]

    # Add nodes with status-based styling
    status_style = {
        "done": ":::done",
        "in_progress": ":::inprogress",
        "planned": ":::planned",
        "decision": ":::decision",
    }

    for node in nodes:
        nid = node["id"].replace("-", "_")
        label = node["name"]
        status = node.get("status", "planned")
        style = status_style.get(status, "")
        lines.append(f'    {nid}["{label}"]{style}')

    # Add edges
    for edge in edges:
        src = edge["from"].replace("-", "_")
        dst = edge["to"].replace("-", "_")
        note = edge.get("note", "")
        if note:
            lines.append(f'    {src} -->|"{note[:40]}"| {dst}')
        else:
            lines.append(f"    {src} --> {dst}")

    # Styles
    lines += [
        "    classDef done fill:#22c55e,color:#fff,stroke:#16a34a",
        "    classDef inprogress fill:#3b82f6,color:#fff,stroke:#2563eb",
        "    classDef planned fill:#f59e0b,color:#fff,stroke:#d97706",
        "    classDef decision fill:#8b5cf6,color:#fff,stroke:#7c3aed",
    ]
    lines.append("```")
    return "\n".join(lines)


def generate_summary(data: dict) -> str:
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    meta = data.get("metadata", {})
    watermarks = meta.get("watermarks", {})
    discovery_runs = watermarks.get("discovery-v4", [])
    processed_runs = watermarks.get("discovery-v4-processed", [])

    counts = defaultdict(int)
    by_group = defaultdict(list)
    for node in nodes:
        counts[node.get("status", "unknown")] += 1
        by_group[node.get("group", "other")].append(node)

    planned_nodes = [n for n in nodes if n.get("status") == "planned"]
    in_progress_nodes = [n for n in nodes if n.get("status") == "in_progress"]
    done_nodes = [n for n in nodes if n.get("status") == "done"]

    lines = [
        "# Project Progress Summary",
        "",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d')}  ",
        f"**Source:** `project-memory/progress/progress.json`",
        "",
        "---",
        "",
        "## Status Overview",
        "",
        "| Status | Count |",
        "|--------|-------|",
    ]
    for status, count in sorted(counts.items()):
        lines.append(f"| {status} | {count} |")

    lines += [
        "",
        "---",
        "",
        "## Discovery Runs Tracked",
        "",
        "| Run ID | Processed |",
        "|--------|-----------|",
    ]
    for run_id in discovery_runs:
        processed = "yes" if run_id in processed_runs else "no"
        lines.append(f"| {run_id} | {processed} |")

    lines += [
        "",
        "---",
        "",
        "## In Progress",
        "",
    ]
    for node in in_progress_nodes:
        lines.append(f"- **{node['id']}**: {node['name']}")
        if node.get("notes"):
            first_sentence = node["notes"].split(".")[0] + "."
            lines.append(f"  - {first_sentence}")

    lines += [
        "",
        "---",
        "",
        "## Planned (Discovered, Not Started)",
        "",
    ]
    for node in planned_nodes:
        blocked = node.get("blocked_by", [])
        blocked_str = f" -- blocked by: {', '.join(blocked[:2])}" if blocked else ""
        lines.append(f"- **{node['id']}**: {node['name']}{blocked_str}")

    if done_nodes:
        lines += ["", "---", "", "## Done", ""]
        for node in done_nodes:
            lines.append(f"- **{node['id']}**: {node['name']}")

    lines += [
        "",
        "---",
        "",
        "## Dependency Graph",
        "",
        generate_dependency_diagram(nodes, edges),
        "",
        "---",
        "",
        "## Status Distribution",
        "",
        generate_status_diagram(nodes),
        "",
    ]

    return "\n".join(lines)


def write_diagrams(nodes: list, edges: list) -> None:
    DIAGRAMS_DIR.mkdir(parents=True, exist_ok=True)

    # Dependency diagram
    dep_file = DIAGRAMS_DIR / "dependency-graph.md"
    with open(dep_file, "w") as f:
        f.write("# Feature Dependency Graph\n\n")
        f.write(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n\n")
        f.write(generate_dependency_diagram(nodes, edges))
        f.write("\n")
    print(f"[update_progress] Diagram: {dep_file}")

    # Status pie diagram
    status_file = DIAGRAMS_DIR / "status-distribution.md"
    with open(status_file, "w") as f:
        f.write("# Feature Status Distribution\n\n")
        f.write(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n\n")
        f.write(generate_status_diagram(nodes))
        f.write("\n")
    print(f"[update_progress] Diagram: {status_file}")

    # Planned features table
    planned = [n for n in nodes if n.get("status") == "planned"]
    planned_file = DIAGRAMS_DIR / "planned-features.md"
    with open(planned_file, "w") as f:
        f.write("# Planned Features\n\n")
        f.write(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n\n")
        f.write("| ID | Name | Group | Blocked By |\n")
        f.write("|----|------|-------|------------|\n")
        for node in planned:
            blocked = node.get("blocked_by", [])
            blocked_str = "; ".join(blocked[:2]) if blocked else "—"
            f.write(f"| {node['id']} | {node['name']} | {node.get('group', '—')} | {blocked_str} |\n")
    print(f"[update_progress] Diagram: {planned_file}")


def main():
    parser = argparse.ArgumentParser(description="Update project progress tracker and regenerate diagrams.")
    parser.add_argument("--discovery-run", metavar="RUN_ID", help="Mark a specific discovery-v4 run as processed in the watermark")
    args = parser.parse_args()

    if not PROGRESS_FILE.exists():
        print(f"[update_progress] ERROR: progress.json not found at {PROGRESS_FILE}")
        sys.exit(1)

    print(f"[update_progress] Loading: {PROGRESS_FILE}")
    data = load_progress()

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    print(f"[update_progress] Nodes: {len(nodes)}, Edges: {len(edges)}")

    # Mark watermark if run ID provided
    if args.discovery_run:
        mark_watermark(data, args.discovery_run)

    # Regenerate diagrams
    write_diagrams(nodes, edges)

    # Regenerate summary
    summary = generate_summary(data)
    with open(SUMMARY_FILE, "w") as f:
        f.write(summary)
    print(f"[update_progress] Summary: {SUMMARY_FILE}")

    # Save updated progress.json (updates the 'updated' timestamp)
    save_progress(data)

    print("[update_progress] Done.")


if __name__ == "__main__":
    main()
