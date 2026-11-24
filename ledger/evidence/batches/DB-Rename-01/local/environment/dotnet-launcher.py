#!/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3
"""Use the actual pinned SDK with its ordinary single-process build options."""
import json
import os
from pathlib import Path
import sys

sdk = "/workspace/scratch/82a414196324/tooling/dotnet/dotnet"
args = sys.argv[1:]
if args and args[0] in {"build", "restore", "publish", "msbuild"}:
    args = [args[0], "-m:1", "-nr:false", "-p:UseSharedCompilation=false", *args[1:]]
elif args and args[0] == "run":
    args = [args[0], "--disable-build-servers", *args[1:]]
with Path("/workspace/scratch/82a414196324/DB-Rename-01-sdk-invocations.jsonl").open("a") as stream:
    stream.write(json.dumps({"cwd": os.getcwd(), "executable": sdk, "arguments": args}) + "\n")
os.execv(sdk, [sdk, *args])
