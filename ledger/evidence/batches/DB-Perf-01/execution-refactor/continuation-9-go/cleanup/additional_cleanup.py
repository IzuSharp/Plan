#!/usr/bin/env python3
"""DB-Go-01 supplementary cleanup; default mode only inspects exact targets.

The root agent supplies a fixed-commit archival/readback acceptance before
--execute. This helper never signals a process and never changes the original
frozen final_cleanup.py. Its own workspace is left for the root to clear last.
"""

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
from urllib.parse import urlparse


TASK = "DB-Go-01-additional-cleanup"
WORK = "/workspace/scratch/2dfe9fb1bc53"
INVENTORY = WORK + "/cleanup-additional-inventory.json"
INVENTORY_SHA = "ac1bcdcbba1ef5a704b330fd0924861a1f5b680c734a7287001cc7ff3c13f277"
ACCEPTANCE = WORK + "/additional-cleanup-acceptance.json"
RECEIPT = WORK + "/additional-cleanup-receipt.json"
ROOTS = ("/workspace/scratch/697b7eeade37", "/workspace/scratch/e91ce0ee6584/recovery")
PRIMARY_ROOTS = ("/workspace/scratch/4a65d70f0fe1", "/workspace/scratch/fd78534029f7", "/workspace/scratch/166b48a091b9")
# Read-only process watch scope, copied from the unchanged original inventory
# ff44db8a718951a07c15d00035c5ea516ddd0b0af3628d532c8c57e9ef87f71b.
# These paths are NEVER deletion targets of this supplementary helper.
PRIMARY_TEMPORARY = (
    "/tmp/DB-Exec-10-before-current-postgresql-phases-01",
    "/tmp/DB-Exec-10-before-current-sqlite-phases-01",
    "/tmp/DB-Exec-10-close-build-postgresql-01",
    "/tmp/DB-Exec-10-close-build-sqlite-01",
    "/tmp/DB-Exec-10-close-pack-postgresql-01",
    "/tmp/DB-Exec-10-close-pack-postgresql-02",
    "/tmp/DB-Exec-10-close-pack-sqlite-01",
    "/tmp/DB-Exec-10-close-pack-sqlite-02",
    "/tmp/DB-Exec-10-close-quiet",
    "/tmp/DB-Exec-10-diag-postgresql-alloc-01",
    "/tmp/DB-Exec-10-diag-postgresql-ffi-01",
    "/tmp/DB-Exec-10-diag-sqlite-alloc-01",
    "/tmp/DB-Exec-10-diag-sqlite-ffi-01",
    "/tmp/DB-Exec-10-find",
    "/tmp/DB-Exec-10-pack-postgresql",
    "/tmp/DB-Exec-10-pack-postgresql-02",
    "/tmp/DB-Exec-10-pack-sqlite",
    "/tmp/DB-Exec-10-pack-sqlite-02",
    "/tmp/DB-Exec-10-tool-archives",
    "/tmp/korda-b04-096f39db646e48948707f6b63922e53e",
    "/tmp/korda-b04-b63a0f1840aa48f7abec2be6a217629c",
    "/tmp/korda-pull-scheduler-3dca5414251e4185bcf589802227e4e0",
    "/tmp/korda-pull-scheduler-948c45a341a14250b2b7217ec1d4c9c7",
    "/tmp/nw-b13-e6981e702eb541cfbc86757fe81d8644.db",
    "/tmp/nw-b14-3d1c63ce58404d6aafbca494fa09028e",
    "/tmp/nw-b14-450a3a070f80404ea31336d5ecc554d9",
    "/tmp/nw-b14-5471f8429d8945c0a7cc5e87dd777dc4",
    "/tmp/nw-b14-62ddf2a927824b169ebf029b447f859d",
    "/tmp/nw-b14-9c3f8b9dd1754528b918664892449b9b",
    "/tmp/nw-b14-c17720e2f89547bb90305bc6b80480cc",
    "/tmp/nw-b14-dd3cc5e9a90a442390a8d8cff7231caf",
    "/tmp/nw-b14-e811192ee38c4b16983f1393cfd10b1b",
)
HTTP_CACHE = "/home/agent/.local/share/NuGet/http-cache"
NUGET_SCRATCH = "/tmp/NuGetScratchagent"
TELEMETRY = "/home/agent/.config/go/telemetry"
SHA = re.compile(r"[0-9a-f]{64}")
# These four directory identities are from the separately archived, existing
# cleanup-inventory-addendum-01.json, not newly inferred configuration targets.
WRAPPER_SOURCE_SHA = "734e0d9cd667337d72834f17c1f893d589c9854b5ab921683d660110be192b21"
WRAPPERS = (
    (TELEMETRY + "/local", 41, 185),
    (TELEMETRY + "/upload", 41, 189),
    (TELEMETRY, 41, 184),
    ("/home/agent/.config/go", 41, 183),
)


class Refusal(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise Refusal(message)


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def within(path, root):
    return path == root or path.startswith(root + "/")


def identity(path):
    value = os.lstat(path)
    return {"device": value.st_dev, "inode": value.st_ino,
            "mode": stat.S_IFMT(value.st_mode), "uid": value.st_uid}


def regular_bytes(path, limit=None):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        value = os.fstat(fd)
        require(stat.S_ISREG(value.st_mode), "Regular file required: " + path)
        require(value.st_uid == os.geteuid(), "File ownership changed: " + path)
        if limit is not None:
            require(value.st_size <= limit, "Control file exceeds size bound: " + path)
        with os.fdopen(fd, "rb", closefd=False) as stream:
            result = stream.read()
        after = os.fstat(fd)
        require((value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns) ==
                (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns),
                "File changed while reading: " + path)
        return result
    finally:
        os.close(fd)


def sha_file(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        before = os.fstat(fd)
        require(stat.S_ISREG(before.st_mode), "Regular file required: " + path)
        digest = hashlib.sha256()
        with os.fdopen(fd, "rb", closefd=False) as stream:
            while block := stream.read(1024 * 1024):
                digest.update(block)
        after = os.fstat(fd)
        require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
                (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns),
                "File changed while hashing: " + path)
        return digest.hexdigest()
    finally:
        os.close(fd)


def path_guard(path):
    require(os.path.isabs(path) and os.path.normpath(path) == path, "Non-canonical target")
    require(os.path.realpath(path) == path, "Symlink target or ancestor: " + path)
    current = Path(path)
    while str(current) != "/":
        require(not stat.S_ISLNK(os.lstat(current).st_mode), "Symlink ancestor: " + str(current))
        current = current.parent


def mount_guard(paths):
    for line in Path("/proc/self/mountinfo").read_text().splitlines():
        mount = line.split()[4]
        mount = re.sub(r"\\([0-7]{3})", lambda m: chr(int(m[1], 8)), mount)
        require(not any(within(mount, path) for path in paths), "Nested or target mount: " + mount)


def check_inventory_identity(row, file_hash=True):
    path = row["path"]
    path_guard(path)
    value = os.lstat(path)
    require(value.st_dev == row["device"] and value.st_ino == row["inode"]
            and value.st_uid == row["uid"] == os.geteuid()
            and stat.filemode(value.st_mode) == row["mode"],
            "Inventory identity changed: " + path)
    if stat.S_ISREG(value.st_mode):
        require(value.st_size == row["bytes"] and value.st_mtime_ns == row["mtimeNs"],
                "Inventory file metadata changed: " + path)
        if file_hash and "sha256" in row:
            require(sha_file(path) == row["sha256"], "Inventory content changed: " + path)
    return identity(path)


def tree_snapshot(root):
    """Hash paths, inode identities and content without following symlinks."""
    path_guard(root)
    digest = hashlib.sha256()
    counts = {"files": 0, "directories": 0, "symlinks": 0, "fileBytes": 0}
    for directory, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames.sort()
        filenames.sort()
        # Child directories are counted when visited. Symlink directories
        # must be included here because os.walk deliberately does not visit them.
        links = [name for name in dirnames if os.path.islink(os.path.join(directory, name))]
        for name in [".", *links, *filenames]:
            path = directory if name == "." else os.path.join(directory, name)
            value = os.lstat(path)
            record = {"path": os.path.relpath(path, root), **identity(path)}
            if stat.S_ISREG(value.st_mode):
                record.update(bytes=value.st_size, mtimeNs=value.st_mtime_ns, sha256=sha_file(path))
                counts["files"] += 1
                counts["fileBytes"] += value.st_size
            elif stat.S_ISLNK(value.st_mode):
                record["link"] = os.readlink(path)
                counts["symlinks"] += 1
            elif stat.S_ISDIR(value.st_mode):
                counts["directories"] += 1
            else:
                raise Refusal("Special file in cleanup tree: " + path)
            digest.update(canonical(record) + b"\n")
    return {"sha256": digest.hexdigest(), **counts}


def checked_files_in_directory(row):
    check_inventory_identity(row)
    actual = []
    for directory, dirs, files in os.walk(row["path"], followlinks=False):
        require(not any(os.path.islink(os.path.join(directory, p)) for p in dirs),
                "Unexpected cache/temp symlink directory")
        actual.extend(os.path.join(directory, name) for name in files)
    expected = [item["path"] for item in row["files"]]
    require(len(expected) == row["fileCount"] and set(actual) == set(expected),
            "Unexpected/missing file in inventory directory: " + row["path"])
    for item in row["files"]:
        require(within(item["path"], row["path"]), "Inventory file escapes owning directory")
        check_inventory_identity(item)


def git(*args):
    result = subprocess.run(["git", *args], cwd="/tmp", env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
    require(result.returncode == 0, "Git command failed: " + result.stderr.decode(errors="replace")[-1000:])
    return result.stdout


def registrations(bare):
    result = []
    for record in git("--git-dir=" + bare, "worktree", "list", "--porcelain").decode().strip().split("\n\n"):
        row = dict(line.partition(" ")[::2] for line in record.splitlines())
        if row and "bare" not in row:
            require("locked" not in row and "prunable" not in row, "Locked/prunable worktree needs review")
            result.append(row)
    return result


def repository_snapshot(row):
    path, bare = row["worktree"], row["gitDirectory"]
    path_guard(path)
    path_guard(bare)
    head = git("-C", path, "rev-parse", "HEAD").decode().strip()
    require(head == row["head"], "Repository HEAD changed: " + path)
    diff = git("-C", path, "diff", "--binary", "HEAD", "--")
    require(len(diff) == row["diffBytes"] and sha_bytes(diff) == row["diffSha256"], "Tracked diff changed: " + path)
    refs = git("--git-dir=" + bare, "for-each-ref", "--format=%(refname) %(objectname)").decode().splitlines()
    require(refs == row["refs"], "Local repository refs changed: " + bare)
    for item in row["dirtyFiles"]:
        check_inventory_identity(item)
    status = git("-C", path, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    return {"path": path, "bare": bare, "head": head, "identity": identity(path),
            "diffSha256": sha_bytes(diff), "statusSha256": sha_bytes(status),
            "refsSha256": sha_bytes(canonical(refs))}


def build_plan(inventory):
    require(tuple(x["path"] for x in inventory["additionalProjectRoots"]) == ROOTS, "Project root scope changed")
    temps = inventory["additionalMsbuildTemporaryDirectories"]
    require(len(temps) == 66 and len({x["path"] for x in temps}) == 66, "MSBuild inventory count changed")
    require(all(re.fullmatch(r"/tmp/MSBuildTemp[A-Za-z0-9]{6}", x["path"]) for x in temps), "Unexpected MSBuild path")
    require(inventory["additionalNuGetHttpCache"]["path"] == HTTP_CACHE, "NuGet HTTP scope changed")
    require(inventory["additionalNuGetScratch"]["path"] == NUGET_SCRATCH, "NuGet scratch scope changed")
    require(inventory["additionalGoTelemetry"]["path"] == TELEMETRY, "Go telemetry scope changed")
    telemetry = inventory["additionalGoTelemetry"]["files"]
    require(len(telemetry) == 9 and all(Path(x["path"]).parent == Path(TELEMETRY + "/local") for x in telemetry), "Telemetry scope changed")
    rows = [*inventory["additionalProjectRoots"], *temps, inventory["additionalNuGetHttpCache"], inventory["additionalNuGetScratch"]]
    paths = [row["path"] for row in rows]
    mount_guard(paths + [TELEMETRY])
    for row in rows:
        check_inventory_identity(row)
        if "files" in row:
            checked_files_in_directory(row)
    require(all(x["bytes"] == 0 for x in inventory["additionalNuGetScratch"]["files"]), "NuGet scratch is not only empty locks")
    checked_files_in_directory(inventory["additionalGoTelemetry"])
    wrappers = []
    for path, device, inode in WRAPPERS:
        path_guard(path)
        current = identity(path)
        require(current == {"device": device, "inode": inode, "mode": stat.S_IFDIR, "uid": os.geteuid()}, "Telemetry wrapper identity changed")
        wrappers.append({"path": path, "identity": current, "entries": sorted(os.listdir(path))})
    repositories = [repository_snapshot(row) for row in inventory["additionalRepositories"]]
    require(len(repositories) == 5, "Repository inventory count changed")
    worktrees = []
    for row in repositories:
        if row["bare"].startswith(ROOTS[0] + "/repos/"):
            listing = registrations(row["bare"])
            require(len(listing) == 1 and listing[0]["worktree"] == row["path"] and listing[0]["HEAD"] == row["head"], "Unexpected registered worktree")
            worktrees.append(row)
    require(len(worktrees) == 3, "Exactly three extra registered worktrees required")
    return {"schemaVersion": 1, "task": TASK, "inventorySha256": INVENTORY_SHA,
            "targets": [{"path": x["path"], "identity": identity(x["path"]), "snapshot": tree_snapshot(x["path"])} for x in rows],
            "worktrees": worktrees, "repositoryStates": repositories,
            "telemetryFiles": [{**row, "identity": identity(row["path"])} for row in telemetry],
            "emptyOnlyWrappers": wrappers, "wrapperSourceSha256": WRAPPER_SOURCE_SHA}


def processes(targets):
    blockers, preserved = [], []
    build_names = {"go", "gofmt", "cgo", "compile", "link", "asm", "gcc", "g++", "cc", "c++", "clang", "clang++", "rustc", "cargo", "dotnet", "MSBuild", "postgres", "pg_ctl", "initdb", "ninja", "cmake"}
    watch = tuple(targets) + PRIMARY_ROOTS + PRIMARY_TEMPORARY
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit() or int(entry.name) == os.getpid():
            continue
        try:
            exe = os.readlink(entry / "exe").removesuffix(" (deleted)")
            cwd = os.readlink(entry / "cwd").removesuffix(" (deleted)")
            name = (entry / "comm").read_text().strip()
            argv = [os.fsdecode(x) for x in (entry / "cmdline").read_bytes().split(b"\0") if x]
            hits = []
            for kind, value in [("exe", exe), ("cwd", cwd)]:
                if any(within(value, target) for target in watch):
                    hits.append(kind)
            for value in argv:
                if value.startswith("/") and any(within(value, target) for target in watch):
                    hits.append("argv-path")
            for descriptor in (entry / "fd").iterdir():
                try:
                    value = os.readlink(descriptor).removesuffix(" (deleted)")
                    if any(within(value, target) for target in watch):
                        hits.append("open-file")
                        break
                except FileNotFoundError:
                    pass
            for line in (entry / "maps").read_text().splitlines():
                fields = line.split(None, 5)
                if len(fields) == 6 and any(within(fields[5].removesuffix(" (deleted)"), target) for target in watch):
                    hits.append("mapped-file")
                    break
            if name in build_names or name.startswith(("db-perf", "DbPerf")):
                hits.append("build-or-database-process")
            if hits:
                row = {"pid": int(entry.name), "exe": exe, "cwd": cwd, "name": name, "reasons": sorted(set(hits))}
                if int(entry.name) in {1, 2, 5} and not any(within(exe, root) for root in (*ROOTS, *PRIMARY_ROOTS)):
                    preserved.append(row)
                else:
                    blockers.append(row)
        except (FileNotFoundError, ProcessLookupError):
            pass  # A process exited during enumeration.
        except PermissionError as error:
            blockers.append({"pid": int(entry.name), "reason": "Cannot inspect live process", "path": str(error.filename)})
    return {"blockers": blockers, "preservedPlatformProcesses": preserved, "signalsSent": 0}


def immutable_url(value):
    parsed = urlparse(value if isinstance(value, str) else "")
    return parsed.scheme == "https" and parsed.netloc == "github.com" and not parsed.query and not parsed.fragment and re.fullmatch(r"/IzuSharp/(?:Plan|Korda|Korda-Design)/(?:blob|tree|commit)/[0-9a-f]{40}(?:/.*)?", parsed.path) is not None


def validate_gate(gate, helper_sha, plan_sha):
    require(gate.get("schemaVersion") == 1 and gate.get("task") == TASK, "Wrong acceptance task/schema")
    for key in ("accepted", "allTaskDataReviewed", "legacyRetentionResolved"):
        require(gate.get(key) is True, "Missing root evidence acceptance: " + key)
    require(gate.get("helperSha256") == helper_sha and gate.get("inventorySha256") == INVENTORY_SHA and gate.get("planSha256") == plan_sha, "Helper/inventory/plan differs from root acceptance")
    report = gate.get("report", {})
    require(report.get("reportedToUser") is True and immutable_url(report.get("url")), "Fixed-commit report and prior user reporting required")
    covers, checked = set(), []
    for row in gate.get("archives", []):
        require(immutable_url(row.get("url")), "Archive must use a fixed commit URL")
        require(SHA.fullmatch(row.get("sha256", "")) and row.get("readbackVerified") is True and row.get("readbackSha256") == row["sha256"], "Actual remote archive byte readback missing")
        path = row["path"]
        require(within(path, WORK) or any(within(path, root) for root in PRIMARY_ROOTS), "Archive outside task evidence roots")
        path_guard(path)
        require(sha_file(path) == row["sha256"], "Archived bytes changed: " + path)
        checked.append({"path": path, "sha256": row["sha256"], "url": row["url"], "readbackSha256": row["readbackSha256"]})
        covers.update(row.get("covers", []))
    require({"additional-source-history", "additional-evidence", "cleanup-inventory"}.issubset(covers), "Supplemental retention coverage incomplete")
    require(gate.get("sourceChecks"), "Critical original-source hash checks required")
    for row in gate["sourceChecks"]:
        path = row["path"]
        require(SHA.fullmatch(row.get("sha256", "")), "Invalid source SHA")
        require(within(path, WORK) or any(within(path, root) for root in (*ROOTS, *PRIMARY_ROOTS)) or re.match(r"^/tmp/MSBuildTemp[A-Za-z0-9]{6}/", path), "Source check outside reviewed evidence scope")
        path_guard(path)
        require(sha_file(path) == row["sha256"], "Critical source changed: " + path)
        checked.append({"path": path, "sha256": row["sha256"]})
    return checked


def save_receipt(receipt):
    """Persist progress outside every deletion target; never overwrite a symlink."""
    temporary = RECEIPT + ".tmp"
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(canonical(receipt) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())
    if os.path.lexists(RECEIPT):
        require(stat.S_ISREG(os.lstat(RECEIPT).st_mode) and os.lstat(RECEIPT).st_uid == os.geteuid(), "Receipt identity changed")
    os.replace(temporary, RECEIPT)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--process-check-only", action="store_true", help="Read-only process check across both cleanup scopes; no tree scan or mutation")
    args = parser.parse_args()
    receipt = {"schemaVersion": 1, "task": TASK, "startedAtUtc": utc(), "executed": False, "actions": [], "signalsSent": 0}
    try:
        raw = regular_bytes(INVENTORY, 8 * 1024 * 1024)
        require(sha_bytes(raw) == INVENTORY_SHA, "Inventory bytes differ from reviewed exact inventory")
        inventory = json.loads(raw)
        helper_sha = sha_file(os.path.abspath(__file__))
        if args.process_check_only:
            require(not args.execute, "Process-only mode cannot execute deletion")
            paths = list(ROOTS) + [x["path"] for x in inventory["additionalMsbuildTemporaryDirectories"]] + [HTTP_CACHE, NUGET_SCRATCH, TELEMETRY]
            observation = processes(paths)
            receipt.update(status="read-only-process-check", helperSha256=helper_sha,
                           observedAtUtc=utc(), processes=observation,
                           primaryRootCount=len(PRIMARY_ROOTS), primaryTemporaryCount=len(PRIMARY_TEMPORARY))
            print(json.dumps(receipt, indent=2))
            return 1 if observation["blockers"] else 0
        plan = build_plan(inventory)
        plan_sha = sha_bytes(canonical(plan))
        watch = [x["path"] for x in plan["targets"]] + [TELEMETRY]
        process_state = processes(watch)
        receipt.update(helperSha256=helper_sha, inventorySha256=INVENTORY_SHA, plan=plan, planSha256=plan_sha, processes=process_state)
        if not args.execute:
            receipt.update(status="dry-run-no-mutation", acceptancePath=ACCEPTANCE,
                           requiredArchiveCoverage=["additional-source-history", "additional-evidence", "cleanup-inventory"],
                           note="No target, process or existing control file was changed.")
            print(json.dumps(receipt, indent=2))
            return 0
        require(os.path.abspath(__file__) == WORK + "/additional_cleanup.py", "Execute the reviewed exact helper path")
        require(shutil.rmtree.avoids_symlink_attacks, "Symlink-resistant rmtree required")
        require(not os.path.lexists(RECEIPT), "An execution receipt already exists; inspect interrupted work before fresh acceptance")
        gate_raw = regular_bytes(ACCEPTANCE, 8 * 1024 * 1024)
        gate = json.loads(gate_raw)
        verified = validate_gate(gate, helper_sha, plan_sha)
        require(not process_state["blockers"], "Active process blocks cleanup; no signal will be sent")
        # Archive hashing can take time. Recheck every source/cache tree and
        # process immediately before the first deletion.
        for row in plan["targets"]:
            path_guard(row["path"])
            require(identity(row["path"]) == row["identity"] and tree_snapshot(row["path"]) == row["snapshot"], "Target changed since plan: " + row["path"])
        require(not processes(watch)["blockers"], "A task/build process appeared")
        mount_guard(watch)
        before = os.statvfs("/workspace/scratch")
        receipt.update(executed=True, status="executing", acceptanceSha256=sha_bytes(gate_raw), verifiedFiles=verified,
                       filesystemAvailableBytesBefore=before.f_bavail * before.f_frsize)
        os.chdir("/tmp")
        save_receipt(receipt)

        def action(path, kind, operation):
            path_guard(path)
            mount_guard([path])
            receipt["inProgress"] = {"path": path, "action": kind}
            save_receipt(receipt)
            operation()
            receipt["actions"].append({"path": path, "action": kind, "finishedAtUtc": utc()})
            receipt.pop("inProgress", None)
            save_receipt(receipt)

        for row in plan["worktrees"]:
            require(identity(row["path"]) == row["identity"], "Worktree inode changed")
            require(not processes(watch)["blockers"], "Active process before worktree removal")
            action(row["path"], "git-worktree-removed-and-unregistered",
                   lambda row=row: git("--git-dir=" + row["bare"], "worktree", "remove", "--force", "--", row["path"]))
            require(not registrations(row["bare"]), "Worktree registration remains")
        for row in plan["targets"]:
            path = row["path"]
            path_guard(path)
            require(identity(path) == row["identity"], "Target inode changed: " + path)
            require(not processes(watch)["blockers"], "Active process before target removal")
            if path not in ROOTS:
                require(tree_snapshot(path) == row["snapshot"], "Cache/temp contents changed: " + path)
            action(path, "removed-exact-directory", lambda path=path: shutil.rmtree(path))
        for row in plan["telemetryFiles"]:
            check_inventory_identity(row)
            require(not processes(watch)["blockers"], "Active process before telemetry cleanup")
            action(row["path"], "removed-exact-telemetry-file", lambda row=row: os.unlink(row["path"]))
        for row in plan["emptyOnlyWrappers"]:
            path = row["path"]
            require(identity(path) == row["identity"], "Telemetry wrapper inode changed")
            require(not os.listdir(path), "Telemetry wrapper is nonempty; leave it for review: " + path)
            action(path, "removed-empty-telemetry-wrapper", lambda path=path: os.rmdir(path))
        require(not any(os.path.lexists(path) for path in watch), "A supplementary target remains")
        after = os.statvfs("/workspace/scratch")
        receipt.update(status="completed", finishedAtUtc=utc(), allAdditionalTargetsAbsent=True,
                       filesystemAvailableBytesAfter=after.f_bavail * after.f_frsize,
                       filesystemAvailableBytesDelta=after.f_bavail * after.f_frsize - receipt["filesystemAvailableBytesBefore"],
                       byteAccounting="Observed availability delta, not file-size sum; concurrent activity can affect it.",
                       sharedPlatformRuntimePreserved=True, originalFrozenHelperUnmodified=True,
                       controlFilesRetainedForRootFinalCleanup=[os.path.abspath(__file__), INVENTORY, ACCEPTANCE, RECEIPT])
        save_receipt(receipt)
        print(json.dumps(receipt, indent=2))
        return 0
    except Exception as error:
        receipt.update(status="refused-or-partially-completed", finishedAtUtc=utc(), errorType=type(error).__name__, error=str(error),
                       note="No unverified retry or signalling. Preserve this receipt; review any inProgress action before resuming with a new exact inventory/acceptance.")
        if receipt["executed"]:
            save_receipt(receipt)
        print(json.dumps(receipt, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
