"""Path -> document types -> checks. Extend this table, not the dispatcher.

Patterns use fnmatch's repository-relative '/' paths. All matching rules apply.
Ordinary prose is a first-class type with no automated check.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentType:
    checks: tuple[str, ...] = ()
    affects: tuple[str, ...] = ()


@dataclass(frozen=True)
class Registration:
    paths: tuple[str, ...]
    types: tuple[str, ...]


@dataclass(frozen=True)
class Check:
    command: tuple[str, ...]
    requirements: tuple[str, ...] = ()


CHECKS = {
    "graph-schema": Check(("python3", "eng/ci/checks.py", "schema"), ("jsonschema==4.23.0",)),
    "task-links": Check(("python3", "eng/ci/checks.py", "links")),
    "ci-self-test": Check(("python3", "-m", "unittest", "discover", "-s", "eng/ci/tests", "-v"),
                          ("jsonschema==4.23.0",)),
}

TYPES = {
    "prose": DocumentType(),
    "repository-metadata": DocumentType(),
    "task-nodes": DocumentType(("graph-schema",), ("task-dependencies",)),
    "task-dependencies": DocumentType(("task-links",)),
    "task-packets": DocumentType((), ("task-dependencies",)),
    "task-fragments": DocumentType(("task-links",)),
    "graph-schema": DocumentType((), ("task-nodes",)),
    # Changing routing can remove an old path rule. Revalidate current users so
    # deleting an old rule and its referenced task cannot suppress validation.
    "ci-tooling": DocumentType(("ci-self-test",), ("task-nodes", "task-fragments")),
}

REGISTRATIONS = (
    Registration(("README.md", "AGENTS.md", "CURRENT-PHASE.md", "acceptance-register.md",
                  "api-execution-requirements.md", "documentation-policy.md", "execution-policy.md",
                  "milestones.md", "public-api-acceptance-workflow.md", "research-policy.md", "task-index.md",
                  "docs/*.md", "ledger/*.md", "templates/*.md", "prompts/*.md", "eng/ci/*.md",
                  "tasks/*.md", "research-tasks/*.md", "documentation-tasks/*.md"), ("prose",)),
    Registration(("LICENSE", ".gitignore", ".gitattributes"), ("repository-metadata",)),
    Registration(("research-graph.json", "documentation-graph.json", "delivery-graph.json"),
                 ("task-nodes", "task-dependencies")),
    Registration(("tasks/*.md", "research-tasks/*.md", "documentation-tasks/*.md"), ("task-packets",)),
    Registration(("fragments/*.json",), ("task-fragments",)),
    Registration(("schemas/graph-v1.schema.json",), ("graph-schema",)),
    Registration(("eng/ci/*.py", "eng/ci/tests/*.py", "eng/ci/requirements.txt", ".github/workflows/*.yml"),
                 ("ci-tooling",)),
)

GRAPH_FILES = ("research-graph.json", "documentation-graph.json", "delivery-graph.json")
