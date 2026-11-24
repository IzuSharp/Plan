"""Resume package checks after an observed local setup failure, retaining native evidence."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

root = Path.cwd()
scope = sys.argv[1]
sys.path.insert(0, str(root / "eng/ci"))
from database_plan import catalog_steps
from runner import Context

plan_path = root / "artifacts/plan.json"
plan = json.loads(plan_path.read_text())
steps = catalog_steps(scope)
names = plan["actions"][scope]
assert len(set(names)) == len(names)
assert all(all(dep in names[:i] for dep in steps[name].needs) for i, name in enumerate(names))
if scope == "linux":
    start = names.index("database.regressions")
    completed = ["database.native", "database.api"]
    prior_text = (root.parent / "DB-Rename-01-linux-initial-format-failure.log").read_text()
    assert re.search(r"^database.native: [0-9.]+s$", prior_text, re.M)
    assert "Build succeeded." in (root / "artifacts/logs/build.log").read_text()
    assert "ERROR: dotnet-format failed" in prior_text
    assert re.search(r"^database.api: [0-9.]+s$", (root.parent / "DB-Rename-01-linux-build-server-interrupted.log").read_text(), re.M)
    print("The full workspace formatter is blocked by the host's Unix socket restriction; it is NOT counted as passed. Remaining functional checks follow.", flush=True)
    manifest_path = root / "artifacts/db-scope/native-build/manifest.json"
else:
    start = names.index("public.pack")
    completed = names[:start]
    assert completed == (["sqlite.build"] if scope == "sqlite" else ["postgresql.build", "postgresql.dependencies"])
    prior_text = (root.parent / f"DB-Rename-01-{scope}-initial-version-failure.log").read_text()
    for name in completed:
        assert re.search(r"^" + re.escape(name) + r": [0-9.]+s$", prior_text, re.M), name
    assert 'ValueError("Package or version differs from the verification plan")' in prior_text
    manifest_path = root / f"artifacts/provider-native/{scope}/manifest.json"
manifest = json.loads(manifest_path.read_text())
git = lambda *args: subprocess.check_output(["git", *args], text=True).strip()
assert not git("status", "--porcelain")
assert manifest["sourceCommit"] == git("rev-parse", "HEAD")
assert manifest["sourceTree"] == git("rev-parse", "HEAD^{tree}")
assert manifest["sourceDirty"] is False
for asset in manifest["assets"]:
    assert hashlib.sha256(Path(asset["path"]).read_bytes()).hexdigest() == asset["sha256"]
ctx = Context(plan_path)
if scope != "linux":
    ctx.variables["version"] = plan["versions"][scope]
print(json.dumps({"resume": scope, "completed_actions": completed,
                  "native_manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                  "source_commit": manifest["sourceCommit"], "version": ctx.variables["version"]}), flush=True)
with tempfile.TemporaryDirectory(prefix="nw-native-check-") as session:
    os.environ["NW_NATIVE_CHECK_SESSION"] = session
    ctx.execute(steps, names[start:])
