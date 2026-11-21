# Epoch-002: canonical measurement and profiling source adoption

**Verdict: ACCEPT for the exact source identities below; execution and performance credit remain zero.** This review resolves two independently prepared fixes before any epoch-002 formal timing. It does not invalidate or relabel the earlier unexecuted `b4e077` review.

| Input | Commit or SHA-256 |
| --- | --- |
| Canonical public Plan source | `2b3053b28d289c9e1e2abb675d93a54648872d7e` |
| Adopted `diagnostics/recovery-measure-002/measurement-sources.json` | `a71deb1272c3b29dd1573e5dacfccc0c53db01d72807dd091b4b78e18456728b` |
| Unchanged build source index | `268d10b6b058f6c599fc1128b8a2a7ad7949f723d842647756e542ba70756795` |
| Existing canonical measurement review | `efef3add75f148c081250cb83de723936aae6d0a4825295d7f496d869c5fd69c` |
| One-field profiling rebind commit | `73a73de13109e6209fb384d6ee79ff3e0157e31e` |
| Adopted `diagnostics/recovery-profile-002/sources.json` | `06218c47c7c2af06b75c3094f39ea61413b7c979ec674b16da5925735998c2a8` |

## Independent reads and checks

The reviewer read the complete `b4e077`-to-`a71deb` admission/measurement/documentation diff, the canonical public [measurement caller review](measurement-caller-review.md), the relevant original `protocol_compare.py` and `tests/Perf01/verify_long.py` helpers, the original protocol producer's recovery summary, and the profiling caller's actual invocation paths. All **71 indexed Git source blobs** match: seven caller files, 19 Plan dependencies and 45 common NativeWeave files. All 49 indexed Python files parse as AST. These are source checks; no module was imported or executed.

The canonical long path adds `long=False` to `Context.check_protocol`. For long calls it uses the original streaming `object_metadata` reader for five bounded lifecycle/status fields, excluding the complete `scenarios` object and its potentially large nested sparse histograms. It retains the existing producer/native binding helpers and requires completed, valid, service-standard-passing, recovered and drained summaries. The fixed finite recovery record is not the ordinary request ledger.

`Run.protocol` selects this path only for the existing long stage. `Run.long` still requires the unchanged original complete `verify_long.py` invocation and an accepted receipt with at least 1,800 effective seconds before recording duration credit. Its per-request correctness, recovery, resource-release and D−C checks are not replaced by metadata or a Boolean summary. Short cells retain `read_cell` and their original scenario checks. No frozen workload, arrival rate, service limit, noise formula, publication gate, capacity confirmation, process owner, lock or selected-role rule changed in this adoption.

## Profiling compatibility and exact rebind

The diagnostic caller at `45435a350d2686eac0adcfe71f6409a8e4698d8a` invokes `ctx.check_protocol(output, role, passing=False)`. The added optional argument therefore remains `long=False`, retaining the original short reader and its exact profiling-only ineligibility issue. The caller still requires that issue and rejects any additional correctness/retirement issue. It uses unchanged `Context` and `Run.command` interfaces and does not call the removed private long-identity method.

The reviewer compared the original and rebound profile indexes as parsed JSON: **only** `measurement_source_index_sha256` changes, from `b4e07743394c01e2eaf21c8d7d8345f43ea97bb72d0a8ea4fbedd9a15df173c5` to `a71deb1272c3b29dd1573e5dacfccc0c53db01d72807dd091b4b78e18456728b`. All four indexed profiling files (`profile.py`, `pg_probe.py`, `plan.json`, `README.md`) are byte-identical, with their existing hashes independently checked. The [previous profiling source review](profiling-source-review.md) therefore remains applicable to the original probe CLI, role/native identities, PostgreSQL ownership/teardown, CPU placement and zero-formal-credit rules.

The public `a71deb` source and rebound `06218c47` profile index are the prospective execution identities. Prior `b4e077` / `9664da30` source-review records remain historical, unexecuted preparations. This note supplies no actual populated-input acceptance, B18 pass, profile result, measurement, restored raw evidence, or long-run segment.
