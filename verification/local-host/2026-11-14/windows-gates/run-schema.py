"""Capture the schema gate via a disposable uv environment, with no global installs."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess

root = Path(__file__).resolve().parent
env = os.environ.copy()
env.update(PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
command = ["uv", "run", "--no-project", "--with", "jsonschema==4.23.0", "python", str(root / "schema-check.py")]
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
result = subprocess.run(command, cwd=root, env=env, capture_output=True, timeout=180)
(root / "schema.stdout").write_bytes(result.stdout)
(root / "schema.stderr").write_bytes(result.stderr)
sha = lambda data: hashlib.sha256(data).hexdigest()
report = {"command": command, "started_at_utc": started,
          "finished_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "exit_code": result.returncode, "stdout_sha256": sha(result.stdout),
          "stderr_sha256": sha(result.stderr), "script_sha256": sha((root / "schema-check.py").read_bytes()),
          "capture_script_sha256": sha(Path(__file__).read_bytes()),
          "dependency": "jsonschema==4.23.0", "installation_scope": "uv disposable cached environment"}
(root / "schema-command.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(result.stdout.decode("utf-8", errors="replace"), end="")
print("schema exit", result.returncode)
raise SystemExit(result.returncode)
