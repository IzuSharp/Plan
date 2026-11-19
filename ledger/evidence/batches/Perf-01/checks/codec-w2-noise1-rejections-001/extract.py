#!/usr/bin/env python3
"""Bounded, read-only post-run extraction for the preserved W2 noise-1 rejection."""
import argparse, collections, hashlib, json, math, pathlib, time
from datetime import datetime, timezone

def now(): return datetime.now(timezone.utc).isoformat()
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):
    if path.stat().st_size > 2_000_000: raise ValueError("metadata size limit")
    return json.loads(path.read_text())
def compact_resource(row):
    result = {"observer_ns": row["observer_ns"]}
    for key in ("target", "generator"):
        source = row[key]
        result[key] = {k: source.get(k) for k in ("cpu_seconds", "rss_bytes", "peak_rss_bytes", "threads", "open_file_descriptors", "affinity")}
    return result

p=argparse.ArgumentParser(); p.add_argument("--cell",type=pathlib.Path,required=True); p.add_argument("--output",type=pathlib.Path,required=True)
args=p.parse_args()
if args.output.exists(): raise SystemExit("refusing overwrite")
began=now(); started=time.monotonic_ns()
cell=args.cell.resolve(); summary=load(cell/"summary.json"); plan=load(cell/"plan.json"); result=load(cell/"result.json")
scans={}
def rows(name, max_rows=100000):
    path=cell/name; initial=path.stat(); h=hashlib.sha256(); count=0; total=0
    if initial.st_size > 32_000_000: raise ValueError("raw file size limit")
    with path.open("rb") as f:
        for line in f:
            count+=1; total+=len(line)
            if count>max_rows or len(line)>65536: raise ValueError("row limit")
            h.update(line)
            yield json.loads(line)
    final=path.stat()
    if (initial.st_ino,initial.st_size,initial.st_mtime_ns)!=(final.st_ino,final.st_size,final.st_mtime_ns): raise ValueError("input changed")
    actual=h.hexdigest()
    if actual!=summary["files"][name]: raise ValueError("producer hash mismatch: "+name)
    scans[name]={"bytes":total,"rows":count,"sha256":actual,"maximum_rows":max_rows,"maximum_line_bytes":65536}

failures=[]; phase_counts=collections.Counter(); context={}
# Root identified the failed IDs before this retained extraction. The finite context
# is deliberately bounded, rather than a new full-distribution or performance scan.
for row in rows("operations.jsonl",25000):
    phase_counts[(row["phase"],row["outcome"])]+=1
    if row["outcome"]!="ok": failures.append(row)
    if 7424<=row["id"]<=7938: context[row["id"]]=row
if [r["id"] for r in failures]!=[7680,7681,7682]: raise ValueError("unexpected failure set")
lo=min(r["dispatch_ns"] for r in failures); hi=max(r["completion_ns"] for r in failures)
window=(lo-1_000_000_000,hi+1_000_000_000)
pending={}; active={}; reject_snapshots=[]; dispatch=[]; work_events=[]; telemetry=[]; drain=[]
last_observer=0
for row in rows("events.jsonl",70000):
    t=row["observer_ns"]; kind=row["kind"]
    if t<last_observer: raise ValueError("nonmonotonic observer ledger")
    last_observer=t
    if kind=="dispatch":
        pending[row["id"]]=row
        if window[0]<=t<=window[1]: dispatch.append(row)
    elif kind=="admitted": active[row["id"]]=row
    elif kind=="completed":
        if row.get("status")=="rejected":
            reject_snapshots.append({"event":row,"active":list(active.values()),"pending_not_yet_observed_admitted_ids":[i for i in pending if i not in active],"pending_count_before_completion":len(pending)})
        active.pop(row["id"],None); pending.pop(row["id"],None)
    if kind in ("admitted","completed") and window[0]<=t<=window[1]:
        work_events.append({k:row[k] for k in ("observer_ns","kind","id","status") if k in row})
    if kind in ("snapshot","telemetry") and window[0]-1_000_000_000<=t<=window[1]+1_000_000_000: telemetry.append(row)
    if kind in ("drained","idle"): drain.append(row)
    if len(pending)>256 or len(active)>2: raise ValueError("logical outstanding bound")
if pending or active: raise ValueError("unretired event ledger")
resources=[]
for row in rows("resources.jsonl",200):
    if window[0]-1_000_000_000<=row["observer_ns"]<=window[1]+1_000_000_000: resources.append(compact_resource(row))
active_ids=sorted({r["id"] for snap in reject_snapshots for r in snap["active"]})
active_rows=[]
for i in active_ids:
    if i not in context: raise ValueError("active context outside declared bound")
    active_rows.append(context[i])
nearby_success=[r for r in context.values() if r["outcome"]=="ok" and window[0]<=r["completion_ns"]<=window[1]]
top_calls=sorted(nearby_success,key=lambda r:r["target"]["call_ns"],reverse=True)[:12]
admissions=[r for r in work_events if r["kind"]=="admitted"]
admission_gaps=sorted([{"from":a,"to":b,"gap_ns":b["observer_ns"]-a["observer_ns"]} for a,b in zip(admissions,admissions[1:])],key=lambda r:r["gap_ns"],reverse=True)[:6]
dispatch_gaps=[b["dispatch_ns"]-a["dispatch_ns"] for a,b in zip(dispatch,dispatch[1:])]
bins=collections.Counter(math.floor((r["dispatch_ns"]-lo)/100_000_000) for r in dispatch)
selected=set(active_ids)|{r["id"] for r in top_calls}|set(range(7675,7688))
payload={"schema_version":1,"scope":"bounded post-run diagnostic; no workload, profile, test, rerun, or acceptance credit",
 "began_at_utc":began,"completed_at_utc":now(),"extract_elapsed_ns":time.monotonic_ns()-started,
 "cell":str(cell),"extractor_sha256":digest(pathlib.Path(__file__)),
 "input_files":{n:{"bytes":(cell/n).stat().st_size,"sha256":digest(cell/n)} for n in ("summary.json","plan.json","result.json","phase-progress.json")},
 "raw_scans":scans,"phase_outcomes":[{"phase":k[0],"outcome":k[1],"count":v} for k,v in sorted(phase_counts.items())],
 "result":result,"plan":{k:plan[k] for k in ("source_commit","manifest_sha256","controller_sha256","a21_sha256","corpus_manifest_sha256","actual_loaded_native","planned_rate","workers","queue_capacity","max_in_flight","warmup_seconds","duration_seconds","recovery_seconds","recovery_rate","deadline_ms","max_lag_ms","period_ns","limits","seed")},
 "summary":{k:summary[k] for k in ("valid","offered","successes","successful_operations_per_second","arrival_success_ns","target_cpu_seconds","target_cpu_percent_one_core","rss_before_bytes","rss_after_bytes")},
 "failure_rows":failures,"rejection_event_snapshots":reject_snapshots,
 "window_ns":list(window),"dispatch_window":{"count":len(dispatch),"maximum_lag_ns":max(r["dispatch_ns"]-r["scheduled_ns"] for r in dispatch),"minimum_gap_ns":min(dispatch_gaps),"maximum_gap_ns":max(dispatch_gaps),"counts_per_100ms_relative_to_first_failed_dispatch":dict(sorted(bins.items()))},
 "active_rows_at_rejection":active_rows,"largest_nearby_codec_calls":top_calls,"largest_nearby_observed_admission_gaps":admission_gaps,
 "nearby_selected_operations":[context[i] for i in sorted(selected) if i in context],
 "telemetry_brackets":telemetry,"resource_brackets":resources,"final_owner_observations":drain,
 "limits_of_inference":["Event times are controller observation times; pending-not-admitted includes pipe and observation delay and is not an exact queue gauge.","One-second cumulative GC counters do not locate pause intervals or distinguish scheduler, native work, and GC in an individual call.","Native public-call durations are elapsed time and do not measure CPU time or prove a causal stack."]}
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
print(json.dumps({"receipt":str(args.output),"receipt_sha256":digest(args.output),"raw_scans":scans,"active_rows":active_rows,"dispatch_window":payload["dispatch_window"],"admission_gaps":admission_gaps,"top_calls":[{"id":r["id"],"case":r["case"],"action":r["action"],"interface":r["interface"],"call_ns":r["target"]["call_ns"],"operation_ns":r["target"]["operation_ns"],"admitted_ns":r["admitted_ns"],"completion_ns":r["completion_ns"]} for r in top_calls],"telemetry":telemetry,"resources":resources},indent=2))
