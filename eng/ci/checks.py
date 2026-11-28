#!/usr/bin/env python3
"""Current graph schema and task-reference rules; no execution/history claims."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

from registry import GRAPH_FILES


def graphs(root: Path) -> dict[str, dict]:
    return {name: json.loads((root / name).read_text()) for name in GRAPH_FILES}


def schema(root: Path) -> None:
    from jsonschema import Draft202012Validator
    specification = json.loads((root / "schemas/graph-v1.schema.json").read_text())
    Draft202012Validator.check_schema(specification)
    validator = Draft202012Validator(specification)
    current_graphs = graphs(root)
    for name, graph in current_graphs.items():
        errors = list(validator.iter_errors(graph))
        if errors:
            first = errors[0]
            raise ValueError(f"{name}:{'/'.join(map(str, first.absolute_path))}: {first.message}")
    print("Graph schema: all current graphs valid")


def links(root: Path) -> None:
    nodes: dict[str, dict] = {}
    current_graphs = graphs(root)
    for name, graph in current_graphs.items():
        if not isinstance(graph.get("nodes"), list):
            raise ValueError(f"{name}: nodes must be an array")
        for node in graph["nodes"]:
            task = node.get("id") if isinstance(node, dict) else None
            if not isinstance(task, str) or not re.fullmatch(r"[RDAB]\d{2,}", task):
                raise ValueError(f"{name}: invalid task ID {task!r}")
            if task in nodes:
                raise ValueError(f"Duplicate task ID {task}")
            nodes[task] = node
    edges: dict[str, set[str]] = {}
    for task, node in nodes.items():
        edges[task] = set()
        for field in ("start_dependencies", "acceptance_dependencies", "research_refs", "documentation_refs",
                      "reference_only_research_refs", "selection_inputs", "cross_review_by", "integration_artifact_requirements"):
            refs = node.get(field, [])
            if not isinstance(refs, list) or any(not isinstance(ref, str) for ref in refs):
                raise ValueError(f"{task}.{field}: expected task ID list")
            if len(set(refs)) != len(refs):
                raise ValueError(f"{task}.{field}: duplicate task reference")
            for ref in refs:
                if ref not in nodes:
                    raise ValueError(f"{task}.{field}: missing task {ref}")
                if field in ("start_dependencies", "acceptance_dependencies"):
                    edges[task].add(ref)
        for ref, revision in node.get("dependency_pins", {}).items():
            if ref not in nodes:
                raise ValueError(f"{task}.dependency_pins: missing task {ref}")
            if revision != nodes[ref].get("revision"):
                raise ValueError(f"{task}.dependency_pins: revision mismatch for {ref}")
        for field in ("workspace_manifest_integration_owner", "native_host_task"):
            if field in node and node[field] not in nodes:
                raise ValueError(f"{task}.{field}: missing task {node[field]}")
        for condition in node.get("conditional_dependencies", []):
            if not isinstance(condition, dict) or "task_id" not in condition:
                raise ValueError(f"{task}: conditional dependency requires task_id")
            ref = condition["task_id"]
            if ref not in nodes:
                raise ValueError(f"{task}: missing conditional task {ref}")
            selector = condition.get("condition", {}).get("task_id")
            if selector not in nodes:
                raise ValueError(f"{task}: missing conditional selector {selector}")
            if condition.get("revision") != nodes[ref].get("revision"):
                raise ValueError(f"{task}: conditional revision mismatch for {ref}")
            edges[task].add(ref)
        for group in node.get("required_selection_groups", []):
            for ref in group.get("task_ids", []):
                if ref not in nodes:
                    raise ValueError(f"{task}: missing selection task {ref}")
        for profile in node.get("protocol_host_profiles", []):
            ref = profile.get("host_task_id")
            if ref not in nodes:
                raise ValueError(f"{task}: missing protocol host {ref}")
        for component in node.get("release_scope", {}).get("components", []):
            ref = component.get("task_id")
            if ref not in nodes:
                raise ValueError(f"{task}: missing release component {ref}")
            if component.get("revision") != nodes[ref].get("revision"):
                raise ValueError(f"{task}: release component revision mismatch for {ref}")
        prompt = node.get("prompt", "")
        path = (root / prompt).resolve()
        if not prompt or not path.is_relative_to(root.resolve()) or not path.is_file():
            raise ValueError(f"{task}: missing/unsafe task packet {prompt!r}")
    visited: set[str] = set()
    active: set[str] = set()

    def visit(task: str) -> None:
        if task in active:
            raise ValueError(f"Task dependency cycle involving {task}")
        if task in visited:
            return
        active.add(task)
        for ref in sorted(edges[task]):
            visit(ref)
        active.remove(task)
        visited.add(task)

    for task in nodes:
        visit(task)
    for graph in current_graphs.values():
        for field in ("server_host_task", "server_application_task"):
            policy = graph.get("architecture_policy", {})
            if field in policy and policy[field] not in nodes:
                raise ValueError(f"architecture_policy.{field}: missing task {policy[field]}")
    for path in sorted((root / "fragments").rglob("*.json")):
        fragment = json.loads(path.read_text())
        doc = fragment.get("documentation_task_id")
        if doc not in nodes or not doc.startswith("D"):
            raise ValueError(f"{path.name}: unknown documentation task {doc}")
        delivery = fragment.get("delivery_task_ids", [])
        if not isinstance(delivery, list) or any(not isinstance(t, str) for t in delivery):
            raise ValueError(f"{path.name}: invalid delivery_task_ids")
        if len(set(delivery)) != len(delivery):
            raise ValueError(f"{path.name}: duplicate delivery task")
        for task in delivery:
            if task not in nodes or not task.startswith(("A", "B")):
                raise ValueError(f"{path.name}: unknown delivery task {task}")
        if set(fragment.get("task_details", {})) != set(delivery):
            raise ValueError(f"{path.name}: task_details must match delivery_task_ids")
        for item in fragment.get("design_inputs", []):
            if item.get("id") not in nodes:
                raise ValueError(f"{path.name}: unknown design input {item.get('id')}")
    print(f"Task links: {len(nodes)} unique IDs, valid references, packets and acyclic dependencies")


if __name__ == "__main__":
    try:
        {"schema": schema, "links": links}[sys.argv[1]](Path.cwd())
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(f"Check failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
