"""The existing CI graph-schema gate, with its pinned validator dependency."""
from pathlib import Path
import importlib.metadata
import json
import jsonschema

PLAN = Path(r"C:\MyFile\Projects\IzuSharp\Plan\.worktree\validation-pair\Plan")
schema = json.loads((PLAN / "schemas/graph-v1.schema.json").read_bytes())
jsonschema.Draft202012Validator.check_schema(schema)
rows = []
for kind in ("research", "documentation", "delivery"):
    path = PLAN / (kind + "-graph.json")
    jsonschema.Draft202012Validator(schema).validate(json.loads(path.read_bytes()))
    rows.append({"path": path.name, "errors": []})
report = {"ok": True, "jsonschema_version": importlib.metadata.version("jsonschema"),
          "results": rows, "scope": "Existing CI schema validation only; no native or product execution"}
print(json.dumps(report, indent=2))
