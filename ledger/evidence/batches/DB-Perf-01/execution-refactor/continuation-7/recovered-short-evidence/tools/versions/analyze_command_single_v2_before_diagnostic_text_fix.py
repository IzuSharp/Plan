#!/usr/bin/env python3
"""Read completed single-case run.py directories; never launch a workload.

Example (use actual completed directories, not directories still being written):
  python3 analyze_single_case.py --source /path/to/Korda \
    --ordinary /evidence/ordinary-sqlite --ordinary /evidence/ordinary-postgresql \
    --diagnostic /evidence/ffi-sqlite --diagnostic /evidence/ffi-postgresql \
    --output /new/location/single-case-analysis.json

Ordinary observations reuse the existing raw_metrics arithmetic. Instrumented
receipts contribute only business checks and After-Before ABI count deltas;
their latency, CPU, allocation and provider-poll timing are never compared.
No historical acceptance matrix, performance threshold or host qualification
is added. Missing, failed, changed or unmatched evidence remains explicit.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile


CASES = ("numeric", "tx-rollback", "tx-commit")
DATASET = {"tenants": 8, "ordersPerTenant": 1024, "requestedRows": 32, "batchRows": 32}
OWNER_KEYS = ("sources", "sessions", "operations", "cursors", "buffers", "owners", "pullChannels")
FILES = {}
F = N = NEED = STRICT = METRICS = None


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(path, expected=None):
    path = Path(path).resolve(strict=True)
    name = str(path)
    if name not in FILES:
        with path.open("rb") as stream:
            FILES[name] = hashlib.file_digest(stream, "sha256").hexdigest()
    digest = FILES[name]
    require(expected is None or expected == digest, "SHA-256 mismatch: " + name)
    return {"path": name, "sha256": digest}


def read(path, expected=None):
    bound = identity(path, expected)
    return STRICT(Path(bound["path"]).read_bytes())


def bind_tree(value, base=None):
    if isinstance(value, dict):
        if isinstance(value.get("path"), str) and "sha256" in value:
            path = Path(value["path"])
            if not path.is_absolute():
                require(base is not None, "Relative evidence path has no owning receipt")
                path = base / path
                require(path.resolve().is_relative_to(base.resolve()), "Relative evidence escapes its receipt directory")
            identity(path, value["sha256"])
        for child in value.values():
            bind_tree(child, base)
    elif isinstance(value, list):
        for child in value:
            bind_tree(child, base)


def failure(error):
    return {"status": "invalid_or_missing", "errorType": type(error).__name__,
            "code": getattr(error, "code", None), "message": str(error)}


def load_helpers(source):
    global F, N, NEED, STRICT, METRICS
    analysis = source / "benchmarks/db-perf/analysis"
    # Both modules contain arithmetic/read-only definitions, not runner entry points.
    sys.dont_write_bytecode = True
    for name in ("strict_io", "raw_metrics"):
        path = analysis / (name + ".py")
        identity(path)
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    strict = sys.modules["strict_io"]
    F, N, NEED, STRICT = strict.field, strict.natural, strict.need, strict.strict_json
    METRICS = sys.modules["raw_metrics"]


def consumer_inputs(plan):
    inputs = plan["inputs"]
    bind_tree({key: value for key, value in inputs.items() if key != "consumers"})
    consumers = inputs["consumers"]
    for cohort, consumer in consumers.items():
        bind_tree({key: value for key, value in consumer.items() if key != "receiptData"})
        receipt = read(consumer["buildReceipt"]["path"], consumer["buildReceipt"]["sha256"])
        receipt_directory = Path(consumer["buildReceipt"]["path"]).parent
        bind_tree(receipt, receipt_directory)
        require(receipt == consumer["receiptData"], "Embedded build receipt differs: " + cohort)
        if cohort == "diagnostic":
            continue
        korda = cohort == "korda"
        require(cohort in ("korda", "dapper") and receipt["provider"] == plan["provider"], "Unexpected consumer/provider")
        require(receipt["kind"] == ("workload" if korda else "benchmark")
                and receipt["exit_code" if korda else "exitCode"] == 0, "Consumer build was not successful")
        require(not receipt.get("postValidationError") and not receipt.get("post_validation_error"),
                "Consumer failed after compilation")
        require(receipt["workloadManifestSha256"] == inputs["manifest"]["sha256"], "Consumer manifest differs")
        require(consumer["executable"]["sha256"] == receipt["executable_sha256" if korda else "executableSha256"],
                "Consumer executable differs from build receipt")
        identity(receipt["command"][2], receipt["project_sha256" if korda else "projectSha256"])
        require({name: value["sha256"] for name, value in consumer["sources"].items()} == receipt["sources"],
                "Bound consumer source set differs")
        if korda:
            require(receipt["project_references"] == 0, "Korda is not an independent package consumer")
            require(len(consumer["packages"]) == 1, "Unexpected Korda package set")
            package = next(iter(consumer["packages"].values()))
            require(package["sha256"] == receipt["package_sha256"], "Korda package differs")
            with zipfile.ZipFile(package["path"]) as archive:
                metadata = ET.fromstring(archive.read(next(name for name in archive.namelist() if name.endswith(".nuspec"))))
                require(metadata.find(".//{*}id").text == receipt["package"]
                        and metadata.find(".//{*}version").text == receipt["version"], "Package metadata differs")
                repository = metadata.find(".//{*}repository").attrib
                require(re.fullmatch(r"[0-9a-f]{40}", repository["commit"]) is not None, "Package source commit missing")
                consumer["verifiedPackageSource"] = {"package": package, "repository": repository}
            require({name: value["sha256"] for name, value in consumer["nativeImages"].items()} == receipt["native_images"],
                    "Korda native assets differ")
        else:
            require(consumer["packages"] == receipt["packages"], "Dapper package identities differ")
            if receipt.get("lifecycleSqlMode") == "matched":
                proof = receipt["generatedSqlContract"]
                generated = read(receipt_directory / proof["path"], proof["sha256"])
                require(generated["generatedFactoriesVerified"] is True and len(generated["calls"]) == 12,
                        "Matched lifecycle lacks its actual generated factory proof")
                contract = receipt["sqlContract"]
                static = read(receipt_directory / contract["path"], contract["sha256"])
                require(static["lifecycleSqlMode"] == "matched"
                        and static["manifestSha256"] == inputs["manifest"]["sha256"]
                        and static["validatorSha256"] == receipt["contractValidatorSha256"]
                        and static["lifecycle"]["policySha256"] == receipt["lifecycleSqlPolicySha256"],
                        "Matched SQL contract is not bound to this manifest/validator/policy")
                required_sources = {"Contracts.generated.cs", "LifecycleCases.cs", "LifecycleVerification.cs",
                                    "Models.cs", "Workload.cs"}
                require(set(static["sources"]) == required_sources and generated["sources"] == static["sources"]
                        and all(receipt["sources"].get(name) == digest for name, digest in static["sources"].items()),
                        "Matched generated/static SQL proofs differ from the actual consumer sources")
                generated_path = receipt_directory / generated["generatedFile"]
                require(generated_path.resolve().is_relative_to(receipt_directory.resolve()),
                        "Generated factory source escapes its consumer")
                generated_source = identity(generated_path, generated["generatedSha256"])
                require(generated["runtimeSqlTraceVerified"] is False and static["runtimeSqlTraceVerified"] is False,
                        "Static/generated SQL proofs cannot establish a runtime wire trace")
                consumer["verifiedLifecycleSql"] = {
                    "staticContract": identity(receipt_directory / contract["path"], contract["sha256"]),
                    "generatedContract": identity(receipt_directory / proof["path"], proof["sha256"]),
                    "generatedSource": generated_source,
                    "runtimeSqlTraceVerified": generated["runtimeSqlTraceVerified"],
                    "scope": "Actual emitted factories and source-bound SQL; driver wire text is not inferred as observed."}
    return consumers


def diagnostic_inputs(plan):
    consumers = plan["inputs"]["consumers"]
    diagnostic, ordinary = consumers["diagnostic"], consumers["korda"]
    receipt, original = diagnostic["receiptData"], ordinary["receiptData"]
    require(receipt["consumerKind"] == "workload" and receipt["instrumented"] is True
            and receipt["TimingComparisonEligible"] is False and receipt["timingCredit"] is False
            and receipt["allocationCredit"] is False, "Diagnostic flags do not exclude timing/allocation credit")
    require(receipt["commands"] and all(item["exitCode"] == 0 for item in receipt["commands"]), "Diagnostic build failed")
    require(all(receipt[key] is True for key in ("ordinaryConsumerUnchanged", "nativeImagesUnchanged", "packageUnchanged")),
            "Diagnostic ordinary-input preservation was not confirmed")
    require(receipt["sourceReceiptSha256"] == ordinary["buildReceipt"]["sha256"]
            and receipt["sourceExecutableSha256"] == ordinary["executable"]["sha256"]
            and receipt["sourcePackageSha256"] == original["package_sha256"]
            and receipt["sourceNativeImages"] == original["native_images"], "Diagnostic/ordinary provenance differs")
    require(receipt["runEnvironment"] == {"LD_PRELOAD": diagnostic["shim"]["path"]}, "Unexpected diagnostic environment")
    require(diagnostic["shim"]["sha256"] == receipt["outputs"]["libcursor_probe.so"]
            and diagnostic["executable"]["sha256"] == receipt["outputs"]["DbPerf.Korda"], "Diagnostic output hash differs")
    require({name: value["sha256"] for name, value in diagnostic["sources"].items()} == receipt["overlaySources"],
            "Diagnostic overlay source set differs")
    diagnostic["verifiedPackageSource"] = ordinary["verifiedPackageSource"]
    declarations = []
    source = Path(receipt["abiSource"])
    for name, digest in receipt["inventories"].items():
        declarations += read(source / name, digest)["signatures"]
    returns = {}
    for declaration in declarations:
        match = re.fullmatch(r"(\w+) NW_CDECL (\w+)\(.*\);", declaration)
        require(match is not None, "Unrecognized bound ABI declaration")
        require(match[2] not in returns, "Duplicate ABI declaration")
        returns[match[2]] = match[1]
    require(list(returns) == receipt["symbols"], "ABI counter order differs from exact inventories")
    for name, digest in receipt["tools"].items():
        identity(source / "benchmarks/db-perf/cursor-diagnostics" / name, digest)
    return returns


def planned_argv(plan, item):
    consumers = plan["inputs"]["consumers"]
    cohort, case = item["cohort"], item["case"]
    command = [consumers[cohort]["executable"]["path"], "--connection", "{connection}", "--case", case,
               "--mode", "prepared", "--session", "persistent", "--concurrency", "1", "--warmup", "64",
               "--rows", "32", "--batch-rows", "32", "--tenants", "8", "--orders-per-tenant", "1024"]
    if cohort == "dapper" and plan["provider"] == "sqlite":
        command += ["--native-library", plan["inputs"]["sqliteLibrary"]["path"]]
    if cohort == "diagnostic":
        command = [plan["inputs"]["env"]["path"], "LD_PRELOAD=" + consumers[cohort]["shim"]["path"], *command]
    if item["phase"] == "fixture":
        require(cohort == "korda" and case == "numeric", "Initialization must use ordinary Korda")
        command += ["--initialize", "--operations", "0"]
    else:
        command += ["--seconds", "15", "--idle-seconds", "0", "--output", "{output}/" + item["name"] + ".json"]
    return command


def validate_plan(folder, lane):
    plan = read(folder / "plan.json")
    runner = read(folder / "runner.json")
    require(plan["schemaVersion"] == 1 and plan["lane"] == "single-case-" + lane, "Wrong plan lane/schema")
    require(plan["provider"] in ("sqlite", "postgresql") and plan["longRunAcceptance"] is False, "Wrong plan scope")
    require(runner["planSha256"] == identity(folder / "plan.json")["sha256"]
            and runner["runnerSha256"] == plan["inputs"]["runner"]["sha256"], "Runner/plan binding differs")
    require(runner["hostQualifiedForLongRuns"] is False, "Unexpected long-run qualification")
    require(plan["selectedCases"] == list(CASES) and plan["dataset"] == DATASET, "Single-case dataset differs")
    require(plan["affinity"] == {"client": "0-3", "postgres": "4-7", "observer": "8"}
            and runner["cpuAffinity"] == [8], "Actual/planned observer affinity differs")
    consumers = consumer_inputs(plan)
    manifest = read(plan["inputs"]["manifest"]["path"], plan["inputs"]["manifest"]["sha256"])
    names = [item["name"] for item in manifest["queries"]]
    require(manifest["schemaVersion"] == 3 and len(names) == len(set(names)) == 35
            and plan["manifestCaseNames"] == names, "Manifest case sequence differs")
    require(all(manifest["dataset"][key] == value for key, value in DATASET.items()), "Manifest dataset differs")
    contracts = {item["name"]: item for item in manifest["queries"] if item["name"] in CASES}
    require(plan["caseContracts"] == contracts, "Embedded case contracts differ")
    cohorts = ("korda", "dapper") if lane == "ordinary" else ("diagnostic",)
    require(set(consumers) == ({"korda", "dapper"} if lane == "ordinary" else {"korda", "dapper", "diagnostic"}),
            "Plan consumer set differs")
    expected = ["fixture-initialize"] + [cohort + "-" + case for case in CASES for cohort in cohorts]
    require([item["name"] for item in plan["commands"]] == expected, "Commands are missing, duplicated or reordered")
    for item in plan["commands"]:
        require(item["argv"] == planned_argv(plan, item) and "--cases" not in item["argv"], "Actual planned arguments differ")
        require(item["cpus"] == "0-3" and item["longRunAcceptance"] is False, "Command affinity/scope differs")
        require(item["instrumented"] is (item["cohort"] == "diagnostic"), "Command instrumentation flag differs")
        require(item["phase"] == ("fixture" if item["name"] == "fixture-initialize" else lane)
                and item["timingRequested"] is (item["phase"] != "fixture" and lane == "ordinary")
                and item["timeoutSeconds"] == 600, "Command phase/timing scope differs")
        if item["phase"] == "fixture" or lane == "diagnostic":
            require(all(item[key] is False for key in ("TimingComparisonEligible", "timingCredit", "allocationCredit")),
                    "Non-timing command claims credit")
    connection, owner = plan.get("connection"), None
    if plan["provider"] == "postgresql":
        owner = read(folder / "postgres-owner.json")
        require(owner["exitCode"] == 0 and not any(key in owner for key in
                ("error", "shutdownError", "finalSampleError", "cpuGroupError")), "PostgreSQL owner did not retire successfully")
        require(owner["argv"][:3] == ["taskset", "-c", "4-7"]
                and owner["argv"][3] == plan["inputs"]["postgresTools"]["postgres"]["path"], "PostgreSQL executable/affinity differs")
        require(plan["postgres"]["data"] == str(folder / "pgdata") and "queryPlans" not in plan["postgres"],
                "Database ownership or server instrumentation differs")
        require(owner["argv"].count("-D") == owner["argv"].count("-p") == 1
                and owner["argv"][owner["argv"].index("-D") + 1] == str(folder / "pgdata"), "PostgreSQL actual data owner differs")
        port = owner["argv"][owner["argv"].index("-p") + 1]
        require(port.isdecimal() and 0 < int(port) < 65536, "Invalid PostgreSQL port")
        connection = "postgresql://korda@127.0.0.1:" + port + "/db_perf_01"
    else:
        require(connection == str(folder / "fixture.sqlite"), "SQLite fixture is not owned by this run")
    returns = diagnostic_inputs(plan) if lane == "diagnostic" else None
    return plan, manifest, connection, returns, owner


def command_receipt(folder, plan, item, connection):
    receipt = read(folder / (item["name"] + ".command.json"))
    expected = [value.replace("{output}", str(folder)).replace("{connection}", connection) for value in item["argv"]]
    require(receipt["argv"] == ["taskset", "-c", item["cpus"], *expected], "Executed argv differs from bound plan")
    require(receipt["name"] == item["name"] and receipt["phase"] == item["phase"], "Command identity differs")
    start, end = (N(receipt[key], key, 1) for key in ("startedMonotonicNs", "finishedMonotonicNs"))
    require(start < end, "Command interval is reversed")
    expected_files = {item["name"] + suffix for suffix in (".stdout.log", ".resources.jsonl")}
    require(set(receipt["files"]) == expected_files, "Command logs/resources are not fully bound")
    for name, digest in receipt["files"].items():
        identity(folder / name, digest)
    failures = sorted(folder.glob(item["name"] + ".json.*failure.json"))
    for path in failures:
        identity(path)
    require(not failures, "Failure sidecar exists")
    require(receipt["success"] is True and receipt["exitCode"] == 0 and receipt["timedOut"] is False
            and receipt["observerErrors"] == [], "Command failed/timed out or observer failed")
    return receipt


def raw_receipt(folder, item):
    path = folder / (item["name"] + ".json")
    data = read(path)
    stdout = (folder / (item["name"] + ".stdout.log")).read_text()
    prefix = "DB_PERF_RESULT "
    require(stdout.count(prefix) == 1, "Hashed stdout lacks one unambiguous result")
    # The bound producers serialize compact JSON in exactly one result line.
    logged = stdout.split(prefix, 1)[1].splitlines()[0]
    require(STRICT(logged) == data, "Raw receipt differs from the command's hashed stdout")
    return data


def validate_raw(raw, plan, item, command):
    cohort, provider = item["cohort"], plan["provider"]
    consumer = plan["inputs"]["consumers"][cohort]
    route = "independent-csharp-micro-orm-dapper-aot" if cohort == "dapper" else "korda-public-fluent"
    expected_provider = {("korda", "sqlite"): "Sqlite", ("korda", "postgresql"): "PostgreSql",
                         ("dapper", "sqlite"): "Microsoft.Data.Sqlite.Core", ("dapper", "postgresql"): "Npgsql"}
    require(F(raw, "route") == route and F(raw, "provider") == expected_provider[("dapper" if cohort == "dapper" else "korda", provider)],
            "Actual route/provider differs")
    require(F(raw, "nativeAot") is True and F(raw, "executableSha256") == consumer["executable"]["sha256"], "Actual executable differs")
    require(F(raw, "case") == item["case"] and F(raw, "actualCaseIds") == [item["case"]], "Actual case selection differs")
    settings = {"mode": "prepared", "sessionMode": "persistent", "concurrency": 1, "warmupPerWorker": 64, **DATASET}
    require(all(F(raw, key) == value for key, value in settings.items()), "Receipt settings differ from command")
    require(F(raw, "emptyDriver") is False and F(raw, "offeredLoad") is None
            and F(raw, "nativeAllocationProfile") is None and F(raw, "idle") is None, "Unexpected driver, offered, allocation or idle mode")
    if cohort == "diagnostic":
        require(F(raw, "instrumented") is True and all(F(raw, key) is False for key in
                ("timingComparisonEligible", "timingCredit", "allocationCredit")), "Instrumented raw receipt claims credit")
    else:
        require(F(raw, "timingComparisonEligible") is True and F(raw, "instrumented", optional=True) in (None, False),
                "Ordinary receipt is instrumented or timing-ineligible")
        require(all(F(F(raw, key), "ffi", optional=True) is None for key in ("before", "after", "drained")),
                "Ordinary native snapshots contain ABI instrumentation")
    if cohort != "dapper":
        native = consumer["nativeImages"]
        require(len(native) == 1, "Unexpected Korda native image set")
        bound = next(iter(native.values()))
    else:
        bound = plan["inputs"].get("sqliteLibrary")
    if bound is not None:
        require(F(raw, "loadedNativeSha256") == bound["sha256"]
                and Path(F(raw, "loadedNativePath")).resolve() == Path(bound["path"]), "Actual loaded native image differs")
    require(command["startedMonotonicNs"] <= F(raw, "steadyStartMonotonicNs")
            < F(raw, "steadyEndMonotonicNs") <= command["finishedMonotonicNs"], "Steady interval escapes command")


def business(raw, plan, case):
    oracle = METRICS.oracle(raw)
    contract = plan["caseContracts"][case]
    expected = F(raw, "expectedResults")[case]
    require(F(expected, "rows") == contract["expectedRows"]
            and str(F(expected, "digest")) == contract["expectedDigest"], "Business oracle differs from manifest")
    completed = N(F(raw, "completed"), "successful operations", 1)
    require(F(raw, "started") == F(raw, "planned") == completed and F(raw, "failed") == F(raw, "retries") == 0
            and F(raw, "errors") == [], "Business operations failed, retried or did not reconcile")
    require(F(raw, "rows") == completed * contract["expectedRows"], "Business row total differs")
    cases = F(raw, "cases")
    require(len(cases) == 1 and F(cases[0], "name") == case and F(cases[0], "started") == completed
            and F(cases[0], "succeeded") == completed and F(cases[0], "failed") == 0
            and F(cases[0], "rows") == F(raw, "rows"), "Per-case counters differ")
    seconds = F(raw, "seconds")
    require(F(raw, "timeSeriesTruncated") is False and seconds
            and [F(item, "second") for item in seconds] == list(range(len(seconds))), "Per-second series has holes/truncation")
    for key in ("completed", "failed", "rows"):
        require(sum(N(F(item, key), "second " + key) for item in seconds) == F(raw, key), "Per-second total differs: " + key)
    sql = F(raw, "actualDiagnosticSql")[case]
    require(isinstance(sql, str) and sql, "SQL description is missing")
    sql_contract = contract.get("sql", {}).get(plan["provider"])
    if case == "numeric":
        if F(raw, "route") == "independent-csharp-micro-orm-dapper-aot":
            # The actual generated Dapper consumer uses named parameter bindings.
            # Preserve both texts; this is not a claim about captured wire SQL.
            source = plan["inputs"]["consumers"]["dapper"]["sources"]["Contracts.generated.cs"]
            text = Path(source["path"]).read_text()
            actual = {STRICT(value) for value in re.findall(r'private const string Sql0 = ("(?:[^"\\]|\\.)*");', text)}
            require(actual == {sql}, "Dapper numeric receipt differs from bound generated SQL")
            if plan["provider"] == "sqlite":
                pieces = sql_contract.split("?")
                sql_contract = pieces[0] + "".join("@p" + str(index) + piece for index, piece in enumerate(pieces[1:], 1))
            else:
                sql_contract = re.sub(r"\$(\d+)", r"@p\1", sql_contract)
        require(sql == sql_contract, "Numeric SQL differs beyond the declared driver parameter spelling")
    return {"successfulOperations": completed, "rows": F(raw, "rows"), "expectedRowsPerOperation": contract["expectedRows"],
            "expectedDigest": contract["expectedDigest"], "oracle": oracle,
            "digestEvidence": "source-bound per-operation sticky oracle; actual aggregate result digest is not serialized",
            "sqlOrDescription": sql, "sqlSha256": hashlib.sha256(sql.encode()).hexdigest(),
            "sqlEvidence": "actual SQL equals manifest with declared driver parameter spelling; wire text not captured" if case == "numeric" else
                           "lifecycle description only; receipt does not retain each executed statement",
            "caseModeContract": F(raw, "caseModeContracts")[case], "transactionContract": F(raw, "transactionContract"),
            "perSecondCounts": seconds}


def ffi_counts(raw, returns, case, count):
    before, after = (F(F(raw, boundary), "ffi") for boundary in ("before", "after"))
    deltas = {name: {} for name in returns}
    for field in ("Calls", "PendingReturns", "OkReturns"):
        first, last = F(before, field), F(after, field)
        require(len(first) == len(last) == len(returns), "ABI counter vector length differs")
        for index, name in enumerate(returns):
            delta = N(last[index], "after " + field) - N(first[index], "before " + field)
            require(delta >= 0, "ABI cumulative counter decreased")
            deltas[name][field] = delta
    for name, result in returns.items():
        values = deltas[name]
        require(values["PendingReturns"] + values["OkReturns"] <= values["Calls"], "ABI return counts exceed calls")
        require(result == "nw_status" or values["PendingReturns"] == values["OkReturns"] == 0,
                "Non-status function contains status counters")
    calls = lambda name: deltas[name]["Calls"]
    direct = F(F(raw, "before"), "commandCompletions", optional=True) is not None
    require(not direct or all(name in returns for name in ("nw_db_command_request_v1", "nw_db_command_take_v1",
            "nw_db_command_take_error_v1", "nw_db_command_cancel_v1")), "Loaded command extension lacks its ABI inventory")
    mandatory = 0 if direct else {"numeric": 0, "tx-rollback": 3, "tx-commit": 4}[case]
    commands = {"numeric": 0, "tx-rollback": 3, "tx-commit": 4}[case] if direct else 0
    # CloseController.Request first observes LocalResourcesReleased. A finished
    # transaction may release its owner immediately, without a child-close
    # command; otherwise it issues exactly one close and awaits its proof.
    # Infer only the count permitted by that source branch. This aggregate
    # inventory does not observe individual command kinds or prove the branch.
    optional_close = calls("nw_db_command_request_v1") - commands * count if direct else None
    optional_close_limit = count if direct and case != "numeric" else 0
    pulls = 1 if case == "numeric" else 3
    updates = {"numeric": 0, "tx-rollback": 1, "tx-commit": 2}[case]
    close = calls("nw_db_close_create_v1")
    expected = {
        "nw_db_operation_start_v1": mandatory * count + close,
        "nw_db_mutation_create_v1": 0 if direct else updates * count,
        "nw_db_tx_begin_create_v1": 0 if direct or case == "numeric" else count,
        "nw_db_tx_finish_create_v1": 0 if direct or case == "numeric" else count,
        # FindAsync builds From(...).SelectAll().SingleOrDefaultAsync; it is a
        # query pull. Mutation pull is for returning mutations, absent here.
        "nw_db_cursor_pull_create_v1": pulls * count,
        "nw_db_cursor_pull_mutation_create_v1": 0,
        "nw_db_cursor_pull_close_request_v1": pulls * count,
        "nw_db_cursor_pull_close_take_v1": pulls * count,
        "nw_db_cursor_fetch_create_v1": 0, "nw_db_execute_create_v1": 0,
    }
    if direct:
        expected.update({"nw_db_close_create_v1": 0,
                         "nw_db_command_take_v1": calls("nw_db_command_request_v1"),
                         "nw_db_command_take_error_v1": 0, "nw_db_command_cancel_v1": 0})
        expected.update({name: 0 for name in returns if name.startswith("nw_db_operation_")})
    mismatches = {name: {"actual": calls(name), "expected": value} for name, value in expected.items() if calls(name) != value}
    if direct and not 0 <= optional_close <= optional_close_limit:
        mismatches["nw_db_command_request_v1"] = {
            "actual": calls("nw_db_command_request_v1"),
            "expectedRange": [commands * count, commands * count + optional_close_limit]}
    if not 0 <= close <= (0 if direct or case == "numeric" else count):
        mismatches["nw_db_close_create_v1"] = {"actual": close, "expectedRange": [0, 0 if case == "numeric" else count]}
    for name in (*expected, *(("nw_db_command_request_v1",) if direct else ())):
        if returns[name] == "nw_status" and deltas[name]["OkReturns"] != calls(name):
            mismatches[name + ".OkReturns"] = {"actual": deltas[name]["OkReturns"], "expected": calls(name)}
    retire = deltas["nw_db_operation_try_retire_v1"]
    starts = calls("nw_db_operation_start_v1")
    if retire["OkReturns"] != starts or retire["PendingReturns"] + retire["OkReturns"] != retire["Calls"]:
        mismatches["nw_db_operation_try_retire_v1"] = {"actual": retire, "expectedOkReturns": starts,
                                                       "expectedOtherReturns": 0}
    return {"boundary": "After minus Before only; excludes warmup and later owner drain",
            "timingCredit": False, "allocationCredit": False, "deltas": deltas,
            "callsPerSuccessfulOperation": {name: values["Calls"] / count for name, values in deltas.items()},
            "generic": {"mandatoryStartsPerBusinessOperation": mandatory, "actualStarts": starts,
                        "conditionalTransactionCloseCreates": close, "tryRetire": retire,
                        "pendingFractionOfRetireAttempts": retire["PendingReturns"] / retire["Calls"] if retire["Calls"] else None,
                        "scope": "Pending counts attempts, not unique operations or timer expirations; pending may precede terminal delivery"},
            "commandCompletion": {"supportedByLoadedNativeImage": direct,
                "mandatoryPerBusinessOperation": commands,
                "inferredConditionalChildCloseCommands": optional_close,
                "conditionalChildCloseRange": [0, optional_close_limit] if direct else None,
                "scope": "Transactions have begin, nonreturning mutation(s) and finish. Dispose issues zero or one child-close command according to LocalResourcesReleased. Request/take/OK counts must reconcile; aggregate ABI counters do not identify individual command kinds. Ordinary healthy work creates no generic operation."},
            "expectedStructure": {"status": "matches" if not mismatches else "mismatch", "mismatches": mismatches,
                                  "scope": "Healthy persistent C1 path. Transaction Dispose may skip close after observed retirement; otherwise it uses one generic close on legacy sources or one child-close command on direct-completion sources."}}


def analyze_command(folder, plan, item, manifest, connection, returns):
    command = command_receipt(folder, plan, item, connection)
    result = {"status": "valid", "name": item["name"], "provider": plan["provider"],
              "cohort": item["cohort"], "case": item["case"], "phase": item["phase"],
              "command": identity(folder / (item["name"] + ".command.json")),
              "commandInterval": [command["startedMonotonicNs"], command["finishedMonotonicNs"]]}
    if item["phase"] == "fixture":
        result.update(timingCredit=False, allocationCredit=False)
        return result
    raw = raw_receipt(folder, item)
    validate_raw(raw, plan, item, command)
    consumer = plan["inputs"]["consumers"][item["cohort"]]
    result.update(receipt=identity(folder / (item["name"] + ".json")),
                  consumerReceipt=consumer["buildReceipt"], executable=consumer["executable"],
                  manifest=plan["inputs"]["manifest"], business=business(raw, plan, item["case"]))
    result["packageSource"] = consumer.get("verifiedPackageSource")
    result["lifecycleSqlProof"] = consumer.get("verifiedLifecycleSql")
    if item["cohort"] != "dapper":
        drained = {key: N(F(F(raw, "drained"), key), "drained " + key) for key in OWNER_KEYS}
        command_counts = [F(F(raw, boundary), "commandCompletions", optional=True)
                          for boundary in ("before", "after", "drained")]
        require(all(value is None for value in command_counts) or all(value is not None for value in command_counts),
                "Command completion counter availability changed across boundaries")
        if command_counts[0] is not None:
            for boundary, value in zip(("before", "after", "drained"), command_counts):
                N(value, boundary + " commandCompletions")
            drained["commandCompletions"] = command_counts[2]
        require(F(raw, "ownersReturnedToZero") is True and not any(drained.values()), "Korda owners did not return to zero")
        result["drainedOwners"] = drained
    if item["cohort"] == "diagnostic":
        result.update(timingCredit=False, allocationCredit=False, shim=consumer["shim"],
                      abiSourceCommit=consumer["receiptData"]["abiSourceCommit"],
                      ordinaryConsumerReceipt=plan["inputs"]["consumers"]["korda"]["buildReceipt"],
                      ffi=ffi_counts(raw, returns, item["case"], result["business"]["successfulOperations"]))
        if result["ffi"]["expectedStructure"]["status"] != "matches":
            result["status"] = "structure_mismatch"
        return result
    measured = METRICS.measurement(raw, {"workloadCaseIds": [item["case"]], "seconds": 15}, manifest)
    client = METRICS.client_metrics(raw, measured)
    result.update(ordinaryTimingEligible=True, longRunAcceptance=False, measured=measured, client=client,
                  owners=METRICS.owner_metrics(raw, measured, manifest),
                  lifetime={key: command[key] for key in ("processLifetimeUserCpuSeconds", "processLifetimeSystemCpuSeconds", "processLifetimeMaxRssBytes")},
                  lifetimeScope="wait4 process lifetime; not subtracted from or substituted for steady CPU/allocation endpoints")
    return result


def analyze_folder(folder, lane):
    result = {"directory": str(folder), "lane": lane, "status": "valid", "commands": []}
    try:
        plan, manifest, connection, returns, owner = validate_plan(folder, lane)
        result.update(provider=plan["provider"], plan=identity(folder / "plan.json"),
                      runner=identity(folder / "runner.json"), manifest=plan["inputs"]["manifest"],
                      consumerBuilds={key: value["buildReceipt"] for key, value in plan["inputs"]["consumers"].items()},
                      sourceIdentityScope=plan["identityScope"], hostAdmission="unproven; no host or long-run qualification inferred")
        if owner is not None:
            result["postgresOwner"] = {"receipt": identity(folder / "postgres-owner.json"),
                                       "accountingScope": owner["accounting"], "completeSteadyServerCpu": None}
        previous_end = None
        for item in plan["commands"]:
            record = {"name": item["name"], "provider": plan["provider"], "cohort": item["cohort"], "case": item["case"], "phase": item["phase"]}
            try:
                actual = read(folder / (item["name"] + ".command.json"))
                record["commandOutcome"] = {key: actual.get(key) for key in ("exitCode", "success", "timedOut", "observerErrors")}
                record = analyze_command(folder, plan, item, manifest, connection, returns)
                require(previous_end is None or previous_end <= record["commandInterval"][0], "Serial command intervals overlap")
                previous_end = record["commandInterval"][1]
            except (ValueError, OSError, KeyError, TypeError, IndexError, AttributeError, zipfile.BadZipFile, ET.ParseError) as error:
                record.update(failure(error))
            result["commands"].append(record)
        if any(item["status"] != "valid" for item in result["commands"]):
            result["status"] = "invalid_or_missing"
    except (ValueError, OSError, KeyError, TypeError, IndexError, AttributeError, zipfile.BadZipFile, ET.ParseError) as error:
        result.update(failure(error))
    return result


def comparisons(runs, diagnostic_requested):
    records = [record for run in runs if run["status"] == "valid" for record in run["commands"] if record.get("phase") != "fixture"]
    output = []
    for provider in ("sqlite", "postgresql"):
        for case in CASES:
            pair = {"provider": provider, "case": case, "status": "valid"}
            selected = {}
            for cohort in ("korda", "dapper", "diagnostic"):
                matches = [item for item in records if (item.get("provider"), item.get("case"), item.get("cohort")) == (provider, case, cohort)]
                selected[cohort] = matches[0] if len(matches) == 1 and matches[0]["status"] == "valid" else None
                pair[cohort] = {"status": "valid", "receipt": matches[0]["receipt"]} if selected[cohort] else {
                    "status": "not_requested" if cohort == "diagnostic" and not diagnostic_requested else "missing_invalid_or_ambiguous",
                    "matchingRecords": len(matches)}
            a, b, diagnostic = (selected[name] for name in ("korda", "dapper", "diagnostic"))
            if a and b:
                same_business = all(a["business"][key] == b["business"][key] for key in
                                    ("expectedRowsPerOperation", "expectedDigest", "transactionContract"))
                same_manifest = a["manifest"]["sha256"] == b["manifest"]["sha256"]
                pair["equivalence"] = {"businessOracleAndManifestEqual": same_business and same_manifest,
                                       "actualSqlOrDescriptionTextEqual": a["business"]["sqlSha256"] == b["business"]["sqlSha256"],
                                       "statementTextEquivalence": "same statement/bind contract with driver parameter spelling; wire text not captured" if case == "numeric" else
                                           "business SQL and typed value bindings matched by source and actual generated factories; driver transaction controls remain distinct; wire text not captured"
                                           if b.get("lifecycleSqlProof") else
                                           "unproven; historical transaction receipts contain descriptions and upstream command forms differ"}
                if b.get("lifecycleSqlProof"):
                    pair["equivalence"]["lifecycleSqlProof"] = b["lifecycleSqlProof"]
                ratios = {}
                for key in ("successOpsPerSecond", "p50MicrosecondsUpper", "p95MicrosecondsUpper", "p99MicrosecondsUpper"):
                    denominator = b["measured"]["normalized"][key]
                    ratios[key] = a["measured"]["normalized"][key] / denominator if denominator else None
                for key, category, name in (("cpuSecondsPerOperation", "cpu", "seconds_per_success"),
                                             ("managedBytesPerOperation", "managed", "bytes_per_success")):
                    denominator = b["client"][category][name]
                    ratios[key] = a["client"][category][name] / denominator if denominator else None
                pair["kordaOverDapper"] = ratios if same_business and same_manifest else None
                if not same_business or not same_manifest:
                    pair["status"] = "equivalence_failed"
            else:
                pair["status"] = "missing_invalid_or_ambiguous"
            if diagnostic:
                same = a is not None and diagnostic["ordinaryConsumerReceipt"] == a["consumerReceipt"]
                pair["diagnosticMatchesOrdinaryBuild"] = same
                pair["diagnosticBusinessAndSqlEqual"] = bool(same and all(diagnostic["business"][key] == a["business"][key]
                    for key in ("expectedRowsPerOperation", "expectedDigest", "sqlSha256", "transactionContract")))
                if not pair["diagnosticBusinessAndSqlEqual"]:
                    pair["status"] = "diagnostic_binding_failed"
            elif diagnostic_requested:
                pair["status"] = "missing_invalid_or_ambiguous"
            output.append(pair)
    return output


def markdown(result):
    lines = ["# Single-case ordinary and ABI observations", "", "Validation: **" + result["status"] + "**.", "",
             "C1, persistent session, requested prepared mode, 15 seconds per case. Transactions include ordinary CRUD construction because these APIs have no prepared overload.", "",
             "Ordinary metrics include the complete business operation. CPU, managed allocation and GC cover the whole consumer process between steady endpoints; business and harness allocations are included. Framework-only allocation remains unproven.", "",
             "| Provider | Cohort | Case | Ops | Ops/s | p50 / p95 / p99 (µs) | CPU µs/op | Managed B/op | GC 0/1/2 |", "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |"]
    for run in result["runs"]:
        if run["status"] != "valid":
            continue
        for item in run["commands"]:
            if item["status"] != "valid" or "measured" not in item:
                continue
            metrics, client = item["measured"]["normalized"], item["client"]
            latency = " / ".join(f"{metrics[f'p{p}MicrosecondsUpper']:.3f}" for p in (50, 95, 99))
            gc = "/".join(map(str, client["managed"]["gc_delta_counts"]))
            lines.append(f"| {item['provider']} | {item['cohort']} | {item['case']} | {metrics['counts']['succeeded']} | "
                         f"{metrics['successOpsPerSecond']:.3f} | {latency} | {client['cpu']['seconds_per_success'] * 1e6:.3f} | "
                         f"{client['managed']['bytes_per_success']:.3f} | {gc} |")
    lines += ["", "## Separate ABI diagnostics", "", "These are independent instrumented processes. Only After−Before count deltas are used. Pending counts attempts, not unique operations or timer expirations; no diagnostic latency or allocation is credited.", "",
              "| Provider | Case | Business ops | Generic starts | Mandatory starts | Conditional tx close | Retire calls | Pending | OK | Structure |", "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |"]
    for run in result["runs"]:
        if run["status"] != "valid":
            continue
        for item in run["commands"]:
            if "ffi" not in item:
                continue
            generic = item["ffi"]["generic"]
            count, retire = item["business"]["successfulOperations"], generic["tryRetire"]
            lines.append(f"| {item['provider']} | {item['case']} | {count} | {generic['actualStarts']} | "
                         f"{generic['mandatoryStartsPerBusinessOperation'] * count} | {generic['conditionalTransactionCloseCreates']} | "
                         f"{retire['Calls']} | {retire['PendingReturns']} | {retire['OkReturns']} | {item['ffi']['expectedStructure']['status']} |")
    lines += ["", "## Evidence boundaries", "",
              "Numeric SQL is checked against the actual manifest and generated Dapper source, retaining the distinct placeholder spelling. Matched lifecycle builds additionally bind their static SQL contract, actual emitted command factories, complete generated source and input hashes; historical builds without that proof retain their earlier SQL limitation. Driver transaction controls remain distinct, and no runtime wire trace is inferred from generated source or a lifecycle description. Each successful business operation passed the source-bound sticky oracle; an independent aggregate actual digest is not serialized.", "",
              "Every requested directory and validation failure is retained below. JSON includes raw receipt/command/input hashes, source package commit metadata, owner drain, per-second business counts, RSS and ordinary cumulative CPU/allocation arithmetic. No long-run or host qualification is granted.", ""]
    for run in result["runs"]:
        lines.append(f"- `{run['directory']}`: {run['status']}" + ("; " + run["message"] if "message" in run else ""))
        for item in run["commands"]:
            if item["status"] != "valid":
                lines.append(f"  - `{item['name']}`: {item['status']}; {item.get('message', 'see structural mismatches in JSON')}")
    lines += ["", "Pair comparisons: " + ", ".join(item["provider"] + "/" + item["case"] + "=" + item["status"] for item in result["comparisons"]), ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", type=Path, required=True, help="checkout supplying the existing arithmetic helpers")
    parser.add_argument("--ordinary", type=Path, action="append", default=[], help="completed ordinary run.py directory; repeat per provider")
    parser.add_argument("--diagnostic", type=Path, action="append", default=[], help="completed diagnostic directory; repeat per provider")
    parser.add_argument("--host", type=Path, help="optional actual host observation, retained without granting admission")
    parser.add_argument("--series", type=Path, help="optional completed outer runner series with actual exit codes/argv/log hashes")
    parser.add_argument("--output", type=Path, required=True, help="fresh JSON outside every raw evidence directory")
    args = parser.parse_args()
    require(args.ordinary or args.diagnostic, "Supply completed evidence directories")
    inputs = [(folder.resolve(), lane) for lane in ("ordinary", "diagnostic") for folder in getattr(args, lane)]
    require(len({folder for folder, _ in inputs}) == len(inputs), "An evidence directory was supplied more than once")
    output = args.output.resolve()
    text_output = output.with_suffix(".md")
    require(output.suffix == ".json" and not output.exists() and not text_output.exists()
            and all(not output.is_relative_to(folder) for folder, _ in inputs), "Use fresh JSON/Markdown outputs outside raw evidence")
    load_helpers(args.source.resolve(strict=True))
    identity(__file__)
    runs = [analyze_folder(folder, lane) for folder, lane in inputs]
    outer_series = read(args.series) if args.series is not None else None
    if outer_series is not None:
        for run in runs:
            try:
                matches = [item for item in outer_series if item["command"][-2:] == ["--output", run["directory"]]]
                require(len(matches) == 1, "Outer series has a missing/duplicate run")
                actual = matches[0]
                plan = read(Path(run["directory"]) / "plan.json")
                require(actual["exitCode"] == 0 and actual["command"] == plan["runnerCommand"]
                        and actual["planSha256"] == identity(Path(run["directory"]) / "plan.json")["sha256"],
                        "Actual outer runner exit/argv/plan differs")
                run["outerRunner"] = {"exitCode": 0, "log": identity(actual["log"], actual["logSha256"]),
                                      "startedUtc": actual["startedUtc"], "finishedUtc": actual["finishedUtc"]}
            except (ValueError, OSError, KeyError, TypeError, IndexError) as error:
                run.update(failure(error))
    pairs = comparisons(runs, bool(args.diagnostic))
    result = {"schemaVersion": 1, "scope": "Local C1 single-case closed-loop observations; no offered-load or long-run acceptance",
              "ordinaryMetrics": "Uninstrumented receipts only; whole-process allocation/GC include business and harness; framework-only 0 B is unproven",
              "diagnosticMetrics": "Only After-Before ABI Calls/PendingReturns/OkReturns; no diagnostic latency, CPU, allocation or poll-time comparison",
              "hostAdmission": "unproven", "longRunAcceptance": False, "frameworkOnlyBytes": None,
              "runs": runs, "comparisons": pairs, "inputFiles": FILES, "inputMutationCheck": "pending",
              "hostObservation": identity(args.host) if args.host is not None else None,
              "outerSeries": identity(args.series) if args.series is not None else None}
    changed = []
    for name, expected in FILES.items():
        try:
            with Path(name).open("rb") as stream:
                if hashlib.file_digest(stream, "sha256").hexdigest() != expected:
                    changed.append(name)
        except OSError:
            changed.append(name)
    result["inputMutationCheck"] = {"unchanged": not changed, "changedOrMissingFiles": changed}
    if changed:
        for pair in pairs:
            pair.pop("kordaOverDapper", None)
            pair["status"] = "input_changed"
    result["status"] = "valid_observations" if not changed and all(run["status"] == "valid" for run in runs) \
        and all(pair["status"] == "valid" for pair in pairs) else "incomplete_or_invalid"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    with text_output.open("x") as stream:
        stream.write(markdown(result))
    print(json.dumps({"output": str(output), "status": result["status"], "runs": len(runs), "comparisons": len(pairs)}))
    return 0 if result["status"] == "valid_observations" else 1


if __name__ == "__main__":
    raise SystemExit(main())
