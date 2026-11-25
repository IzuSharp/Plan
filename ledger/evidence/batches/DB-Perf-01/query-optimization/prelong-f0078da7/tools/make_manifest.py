#!/usr/bin/env python3
"""List explicit DB-Perf-01 receipts, including expected missing/failed cells; no execution."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", required=True)
    parser.add_argument("--resource-root")
    parser.add_argument("--failure-review")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(args.campaign).resolve()
    out = {"schemaVersion": 1, "identity": str(root / "identity.json"), "entries": [], "digestOnly": []}
    manifests = set()
    for kind in ("phase", "short", "long"):
        for provider in ("sqlite", "postgresql"):
            plan_name = f"{kind}-{provider}"
            plan_path = root / "plans" / (plan_name + ".json")
            plan = json.loads(plan_path.read_text())
            if plan.get("schemaVersion") != 1 or plan.get("provider") != provider:
                raise ValueError("Unexpected plan schema/provider")
            manifests.add(plan["workloadManifest"])
            out["digestOnly"].append({"id": "plan/" + plan_name, "path": str(plan_path)})
            result_dir = root / "results" / plan_name
            for command in plan["commands"]:
                name = command["name"]
                if not isinstance(name, str) or not name or not all(c in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in name):
                    raise ValueError("Unexpected command identity")
                setup = command["phase"] == "setup-excluded"
                item = {"id": plan_name + "/" + name, "kind": "setup" if setup else "phase" if kind == "phase" else "mixed",
                        "observer": str(result_dir / (name + ".command.json")),
                        "resources": str(result_dir / (name + ".resources.jsonl")),
                        "digestOnly": [{"role": "stdout", "path": str(result_dir / (name + ".stdout.log"))}],
                        "request": {"provider": provider, **{k: command[k] for k in ("route", "mode", "repetition", "timeoutSeconds", "expectedSeconds") if k in command}}}
                if not setup:
                    item["result"] = str(result_dir / (name + ".result.json"))
                    item["failure"] = item["result"] + ".failure.json"
                    item["appId"] = ("phase" if kind == "phase" else "mixed") + "/" + provider + "/" + command["route"]
                out["entries"].append(item)
    if len(manifests) != 1:
        raise ValueError("Plans bind different workload manifests")
    out["workload"] = manifests.pop()
    if args.resource_root:
        base = Path(args.resource_root).resolve()
        for route in ("before", "candidate"):
            for provider in ("sqlite", "postgresql"):
                for repetition in range(3):
                    d = base / f"{route}-{provider}" / f"process-{repetition}"
                    out["entries"].append({"id": f"resource-{provider}/{route}-process-{repetition}", "kind": "resource",
                        "appId": f"resource/{provider}/{route}", "result": str(d / "result.json"),
                        "observer": str(d / "probe.command.json"), "resources": str(d / "probe.resources.jsonl"),
                        "digestOnly": [{"role": "stdout", "path": str(d / "probe.stdout.log")},
                                       {"role": "postgres-owner", "path": str(d / "postgres-owner.json")}],
                        "request": {"route": route, "provider": provider, "repetition": repetition}})
    if args.failure_review:
        out["failureReview"] = str(Path(args.failure_review).resolve())
    with Path(args.output).open("x") as stream:
        json.dump(out, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"entries": len(out["entries"]), "performanceExecuted": False, "manifestIsLocalOnly": True}))


if __name__ == "__main__":
    main()
