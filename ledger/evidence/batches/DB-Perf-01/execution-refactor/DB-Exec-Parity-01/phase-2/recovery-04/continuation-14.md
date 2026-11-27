# Continuation14 — public delivery verified, performance gap remains

**The retained product is merged and both independent `0.1.0-preview.5` public
NuGet packages have passed the existing signature and Release Native AOT consumer
checks. Local performance work is finished for this round. No new measurement,
profile, calibration, pressure run or long run is selected.** This continuation
finishes the interrupted evidence and delivery work; it does not award Dapper
parity or reopen the rejected experiments.

The [delivery receipt index](delivery-14/README.md) preserves the actual merge,
CI, public-package, archive publication and byte-readback records. The current
Plan record still needs its own normal PR merge and main check when first
committed. The observed result of that final repository operation belongs in
[Plan #36](https://github.com/IzuSharp/Plan/pull/36), after it occurs; this document
does not predict its own future CI success. On recovery, read that PR's final
delivery receipt before repeating any operation.

## Merged sources and observed product delivery

| Item | Exact observed result |
| --- | --- |
| Product | [Korda #40](https://github.com/IzuSharp/Korda/pull/40), normal merge `36bd5ba169b628ba4d61dd9fe260eaef5ff15599` |
| Product tree | `f7660759bba43ae83324620e2fb731efd479c3b5`, identical to reviewed PR head `106fe68b6f6c2537f478daf65a71ab97cc4b15ff` and ordinary build source `69b2383dadc280f1a81de592592a1442069eed0c` |
| Product main CI | [46007977394](https://github.com/IzuSharp/Korda/actions/runs/46007977394), `push/main`, completed successfully |
| Design | [Korda-Design #21](https://github.com/IzuSharp/Korda-Design/pull/21), normal merge `9299fb88fa11d1b61f4fe01e8fb18684f530e515` |
| Design main checks | [46008241874](https://github.com/IzuSharp/Korda-Design/actions/runs/46008241874) and [46008241884](https://github.com/IzuSharp/Korda-Design/actions/runs/46008241884), both completed successfully |
| Plan evidence before this record | Archive06 published as `cf466f6d242bdca48d172bacdabae260771d2ad3`, following readable checkpoint `ee1148884041a14e6c046c8ff0c83b7b126bde54` |

The product run passed the shared checks, independent PostgreSQL and SQLite
package/API/correctness/AOT checks, Secret scan, selected CodeQL jobs and Verify.
The existing release rules then published both packages. No workflow, release
policy, module selection or product code was changed by this continuation.
The earlier committed product impact plan remains the routing evidence; a Plan
evidence-only update does not create a new product diff to validate.

Equal source trees do not relabel old measured binaries. The ordinary results in
Continuation13 remain bound to the actual `0.1.0-parity05.2` build, generated
sources and native image. The newly built public `preview.5` packages establish
the public-consumer delivery result below, not a new performance sample.

## Actual public NuGet verification

| Package | Version | Index and signature passed, UTC | Public AOT passed, UTC | Publication job |
| --- | --- | --- | --- | --- |
| `Korda.Database.PostgreSql` | `0.1.0-preview.5` | 2026-11-27 13:50:55 | 2026-11-27 13:51:48 | `140540738780` |
| `Korda.Database.Sqlite` | `0.1.0-preview.5` | 2026-11-27 13:52:44 | 2026-11-27 13:53:42 | `140540738813` |

Both jobs completed successfully without a manual rerun. The independently read
public artifacts passed 160 payload/consumer checks and 71 additional release
checks. The [compact report](delivery-14/public-release/public-release-summary.json)
and [full audit](delivery-14/public-release/public-release-audit-final.json) bind
the actual packages, source commit/tree, input fingerprints, NuGet signature
logs, artifact hashes and consumer results.

For each package, the signed registry package's unsigned entries equal the tested
candidate. Its NuGet repository signature matches the existing owner and certificate
policy. The signed archive SHA is correctly allowed to differ from the upload SHA.
The public consumer actually invoked `consume.py --public` at the reviewed source,
using only the public application-package source and an isolated application cache.
SDK tooling can use the existing warm fallback; this is not a fully cold SDK claim.

Each standalone package's scaffold, original and C# model-edited applications was
published as Native AOT and executed successfully: six publish/execute commands
per package exited zero. Only the C# model edit changed between the original and
edited application inputs. Application identities changed while the native hash
remained identical and matched the actual public package. The four shipped/tutorial
source files also retain their recorded identities.

The existing release proves the two standalone package consumers separately. It
does not prove a combined public application referencing both packages. Its artifact
recipe did not retain temporary consumer ELF, restored NuGet.Config or project.assets
bytes; no such absent files are invented. Source/public invocation, package and native
hashes, raw publish/execute logs and actual run receipts establish the reported scope.
The read-only audit did not rerun cryptographic tools or consumers locally.

One preserved audit attempt initially compared verbose planner output with the
exported plan without applying the existing removal of `reasons`. The correction
matches `plan_run.py` exactly and still compares every other field. This was an audit
comparison failure, not a product failure or a reason to rerun CI.

## Archive06 and recovery durability

The [closed-candidate archive](archives-06/PUBLICATION.md) adds six already-built
payload groups: 21 parts, 71,202,192 compressed bytes and 1,908 expanded members.
The final published subtree contains 117 paths and 76,575,755 bytes, including
metadata and immutable upload records. Its exact tree is
`1693c16ea9b511ed794d74307351c686963c08dd` under Plan commit
`cf466f6d242bdca48d172bacdabae260771d2ad3`.

Root verified the actual remote branch reference after a normal fast-forward,
then checked exact subtree membership, modes, lengths, Git blob SHA-1 and SHA-256
for every file. All 117 passed. The final read used previously fetched immutable
Git objects; blob preflight and full blob reading explicitly disabled lazy fetch.
It is complete actual-byte verification of the published commit, not a claim that
each blob was downloaded from the network again.

The first bounded reader stopped before reading any blob because its disk-space
gate was not satisfied. Git's merge diffstat had fetched the otherwise sparsely
excluded archive parts into the object cache. That failed receipt is retained,
alongside the successful cached-only readback and the unchanged source parts.
Only positively identified redundant cache material may be reclaimed with its own
receipt; original experiment/source/generated/ELF/raw evidence is preserved.

Archive01–05 keep their original bytes and readback identities. Archive06 closes
the source/generated/actual-binary/raw preservation of the already rejected 08
screen and its common ownership baseline. Final release evidence is stored
separately in `delivery-14/public-release`, because it occurred after Archive06
was frozen. Its audit inputs are ordinary files with a relative-path manifest,
so the recorded audit can be reproduced without the old scratch symlinks.

## Performance result and stopping scope

The product retains the five retained 05 changes: admitted managed execution of native
pulls, exact canonical decimal recognition with original fallback/validation,
SQLite statement-lifetime prepare flags, exclusively owned private relation
branch transfer, and bounded private relation capacity. The separate metadata
before native-owner-adoption change is a correctness repair.

Tail06, pull-local07 and frame08 remain rejected and absent from the product.
Frame08 repeatedly saved about 60.77–60.82 KB/business (11.77–11.78%), but the
predeclared common CPU/tail/memory tradeoff was not established. No extra favorable
round, optional mixed extension or long run is pending.

| Existing measured scope | SQLite | PostgreSQL |
| --- | --- | --- |
| Current ownership05 related32 client CPU / Dapper | 3.22–4.56 times | 7.61–10.05 times |
| Current ownership05 related32 process managed bytes / Dapper | about 6.97 times | about 10.08 times |
| Earlier original05 text1000 client CPU / Dapper, separate source identity | 5.55 / 7.10 times | 7.94 / 9.42 times |

These are the existing matched short-run observations, not new measurements or
confidence intervals. The older thousand-row workload had only about 1% managed
allocation difference, so allocation alone does not explain its CPU gap. Earlier
retained 05 PG mixed queued-p99 increases of 26.238% / 17.593% and released-idle RSS
risks remain visible. Client process costs are not exclusively framework costs;
PG server accounting remains separate in the original reports.

**Dapper parity, whole-framework steady 0 B and sustained capacity remain unproved.**
There is still optimization space, but the gap does not prove that all of it is
recoverable. [The remaining execution boundary](remaining-execution-boundary-13.md)
identifies request/batch demand, executor start, completion publication and consumer
resumption as the next attribution question. It selects no new implementation or
measurement here. Closed 06/07/08 results do not prove all scheduling or native
execution strategies exhausted. This turn closes the explicitly resumed delivery
work, rather than presenting an unmeasured claim of ultimate performance limits.

The owner cancelled all four originally proposed long cells before they started.
They remain zero executed and zero currently required, with the original requirement
preserved as history. No previous task's long tests are credited to this product.

## Final recovery rule

Current entrypoints and `status.json` now point here. Their earlier stale state is
preserved in the delivery snapshot; old phase reports and the original evidence
manifest retain their original snapshot meaning. Do not resume a historical
baseline build, rejected experiment or four-cell campaign from an old paragraph.

The only remaining operation when this record is first committed is its own normal
Plan #36 review/merge/main-CI check. Read that PR's final receipt; when it confirms
the exact final head/merge/tree and successful existing main CI, stop. Do not run
additional performance work to finish a documentation gate. Go drafts Plan #35 and
Korda #39 remain open drafts at their recorded original heads and are unchanged.
