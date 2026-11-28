#!/usr/bin/env python3
"""Current graph schema and task-reference rules; no execution/history claims."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

from registry import GRAPH_FILES, INDEPENDENT_GRAPHS, IndependentGraph


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


def independent_graph(root: Path, key: str) -> tuple[IndependentGraph, dict]:
    matches = [item for item in INDEPENDENT_GRAPHS if item.key == key]
    if len(matches) != 1:
        raise ValueError(f"Unknown or duplicate independent graph registration {key!r}")
    registration = matches[0]
    path = root / registration.path
    if not path.is_file():
        raise ValueError(f"Missing registered independent graph {registration.path}")
    graph = json.loads(path.read_text())
    if not isinstance(graph, dict):
        raise ValueError(f"{registration.path}: graph must be an object")
    for field in ("direction", "task_prefix"):
        if graph.get(field) != getattr(registration, field):
            raise ValueError(f"{registration.path}: {field} does not match its registration")
    return registration, graph


def independent_schema(root: Path, key: str) -> None:
    from jsonschema import Draft202012Validator
    registration, graph = independent_graph(root, key)
    specification = json.loads((root / registration.schema).read_text())
    Draft202012Validator.check_schema(specification)
    errors = list(Draft202012Validator(specification).iter_errors(graph))
    if errors:
        first = errors[0]
        raise ValueError(f"{registration.path}:{'/'.join(map(str, first.absolute_path))}: {first.message}")
    print(f"Independent graph schema: {registration.direction} valid")


def independent_links(root: Path, key: str) -> None:
    registration, graph = independent_graph(root, key)
    prefix = registration.task_prefix
    task_pattern = re.compile(re.escape(prefix) + r"[A-Z0-9]+(?:-[A-Z0-9]+)*")
    contract_pattern = re.compile(re.escape(prefix) + r"C\d{2,}")

    def references(value: object, field: str) -> list[str]:
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            raise ValueError(f"{field}: expected reference list")
        if len(set(value)) != len(value):
            raise ValueError(f"{field}: duplicate reference")
        return value

    design = graph.get("design")
    if not isinstance(design, dict):
        raise ValueError(f"{registration.path}: missing design binding")
    revision = design.get("commit")
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", revision):
        raise ValueError(f"{registration.path}: design commit must be a full 40-hex pin")
    contracts = references(design.get("contracts"), "design.contracts")
    if not contracts or any(not contract_pattern.fullmatch(item) for item in contracts):
        raise ValueError(f"{registration.path}: invalid or foreign design contract ID")
    authorized = graph.get("implementation_authorized")
    if type(authorized) is not bool:
        raise ValueError(f"{registration.path}: implementation_authorized must be a boolean")
    current_nodes = graph.get("nodes")
    if not isinstance(current_nodes, list) or not current_nodes:
        raise ValueError(f"{registration.path}: nodes must be a nonempty array")
    nodes: dict[str, dict] = {}
    for node in current_nodes:
        task = node.get("id") if isinstance(node, dict) else None
        if not isinstance(task, str) or not task_pattern.fullmatch(task):
            raise ValueError(f"{registration.path}: invalid or foreign task ID {task!r}")
        if task in nodes:
            raise ValueError(f"Duplicate independent task ID {task}")
        if node.get("status") not in ("planned_candidate", "in_progress", "completed", "accepted"):
            raise ValueError(f"{task}: invalid task status")
        if not authorized and node["status"] != "planned_candidate":
            raise ValueError(f"{task}: implementation is not authorized; status must be planned_candidate")
        nodes[task] = node

    edges: dict[str, set[str]] = {}
    packets: set[str] = set()
    packet_root = (root / registration.packet_directory).resolve()
    for task, node in nodes.items():
        edges[task] = set()
        for field in ("start_dependencies", "acceptance_dependencies"):
            for ref in references(node.get(field), f"{task}.{field}"):
                if not task_pattern.fullmatch(ref):
                    raise ValueError(f"{task}.{field}: foreign task reference {ref}")
                if ref not in nodes:
                    raise ValueError(f"{task}.{field}: missing task {ref}")
                edges[task].add(ref)
        required_contracts = references(node.get("contracts"), f"{task}.contracts")
        if not required_contracts:
            raise ValueError(f"{task}: at least one contract reference is required")
        for ref in required_contracts:
            if ref not in contracts:
                raise ValueError(f"{task}.contracts: unknown contract {ref}")
        packet = node.get("packet")
        expected = f"{registration.packet_directory}/{task}.md"
        if packet != expected:
            raise ValueError(f"{task}: missing/unsafe task packet; expected {expected!r}")
        path = (root / packet).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_relative_to(packet_root) or not path.is_file():
            raise ValueError(f"{task}: missing/unsafe task packet {packet!r}")
        lines = path.read_text().splitlines()
        heading = re.match(r"^#\s+([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+)(?=\s|:|$)", lines[0]) if lines else None
        if heading is None or heading[1] != task:
            raise ValueError(f"{task}: task packet first heading must identify {task}")
        packets.add(packet)

    visited: set[str] = set()
    active: set[str] = set()

    def visit(task: str) -> None:
        if task in active:
            raise ValueError(f"Independent task dependency cycle involving {task}")
        if task in visited:
            return
        active.add(task)
        for ref in sorted(edges[task]):
            visit(ref)
        active.remove(task)
        visited.add(task)

    for task in nodes:
        visit(task)
    current_packets = {path.relative_to(root).as_posix()
                       for path in (root / registration.packet_directory).rglob("*.md")}
    orphaned = sorted(current_packets - packets)
    if orphaned:
        raise ValueError(f"{registration.direction}: orphan task packet {orphaned[0]}")
    print(f"Independent task links: {registration.direction}, {len(nodes)} unique IDs, valid local references and packets")


if __name__ == "__main__":
    try:
        mode = sys.argv[1]
        if mode in ("independent-schema", "independent-links"):
            {"independent-schema": independent_schema, "independent-links": independent_links}[mode](Path.cwd(), sys.argv[2])
        else:
            {"schema": schema, "links": links}[mode](Path.cwd())
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(f"Check failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
