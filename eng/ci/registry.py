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


@dataclass(frozen=True)
class IndependentGraph:
    key: str
    path: str
    direction: str
    task_prefix: str
    packet_directory: str
    schema: str = "schemas/independent-graph-v1.schema.json"


# Independent directions do not become nodes or dependencies of the historical
# R/D/A/B graphs. Each registration owns its own selected checks and packet root.
INDEPENDENT_GRAPHS = (
    IndependentGraph("orm", "docs/korda-orm/implementation-graph.json",
                     "Korda-Orm-01", "ORM-", "docs/korda-orm/tasks"),
)


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


for graph in INDEPENDENT_GRAPHS:
    schema_check = f"{graph.key}-graph-schema"
    links_check = f"{graph.key}-task-links"
    nodes_type = f"{graph.key}-task-nodes"
    links_type = f"{graph.key}-task-dependencies"
    packets_type = f"{graph.key}-task-packets"
    schema_type = f"{graph.key}-graph-schema"
    CHECKS[schema_check] = Check(("python3", "eng/ci/checks.py", "independent-schema", graph.key),
                                ("jsonschema==4.23.0",))
    CHECKS[links_check] = Check(("python3", "eng/ci/checks.py", "independent-links", graph.key))
    TYPES[nodes_type] = DocumentType((schema_check,), (links_type,))
    TYPES[links_type] = DocumentType((links_check,))
    TYPES[packets_type] = DocumentType((), (links_type,))
    TYPES[schema_type] = DocumentType((), (nodes_type,))
    REGISTRATIONS += (
        Registration((graph.path,), (nodes_type, links_type)),
        Registration((graph.packet_directory + "/*.md",), (packets_type,)),
        Registration((graph.schema,), (schema_type,)),
    )
    tooling = TYPES["ci-tooling"]
    TYPES["ci-tooling"] = DocumentType(tooling.checks, tooling.affects + (nodes_type,))
