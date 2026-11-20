# Recovery epoch 001 configuration review

## Verdict

**ACCEPT for the configuration-only boundary at the four identities below.**
No build, measurement, functional acceptance, performance claim or long-duration
credit is granted by this review. Toolchain receipts, the new portable execution
owner, complete actual producer/consumer bindings, reviewed current reader
schemas and fresh noise remain separate pending admission requirements.

| Project-relative reviewed file | SHA-256 |
| --- | --- |
| `ledger/evidence/batches/Perf-01/recovery/epoch-001/freeze.json` | `eda07013d5fa06f793ea9f15667cc99f4a7a4368c733bbbba75f76932319f862` |
| `ledger/evidence/batches/Perf-01/recovery/epoch-001/policy.json` | `b70aebe88bbf271b1ea53dad2b68b8e29c9f1796b32bb0e1721ab09db3f54760` |
| `ledger/evidence/batches/Perf-01/recovery/epoch-001/grpc-budget-profile-v2.json` | `fcd529ae210b57a6c3030f7521127204f665f33978ec50d848d13259a7b697af` |
| `ledger/evidence/batches/Perf-01/recovery/epoch-001/README.md` | `b65e29ba7f8f4dc4087a0dd1119bf0dcfb102397bdd9b2f92ad8b08db4d25bf6` |

The comparison base is public Plan
`0d2ed1b460ca194978cd595417739bce99adc224`. Its historical prospective policy
SHA-256 is `0c7cd866b1ad0fc86d647e31dd1b6fe0b148d2e7ca54d83b7286cec09f11cafc`.
The fixed baseline remains product
`ea5fa528035d025bd7a28698ee7c71194432236c`; the current retained candidate and
public driver checkout remain `2e3995df8d86583ee9443348276ca8d918056bfc`.

## Concrete finding and correction

The initial freeze `05fa6b6a0e7482d8dab583e58823483824c03717540f5f999361a7d81ac7864e`
called CPU8 `controller_cpu_ids`. The unchanged public
`protocol_calibrate.py` explicitly requires its own process affinity to equal
CPUs2,3 at initial and repeated admission. Treating CPU8 as that measurement
controller would fail the original gate and would make the freeze ambiguous.

Root corrected only the distinction in the reviewed freeze and documentation:
`outer_supervisor_cpu_ids=[8]`, `measurement_controller_cpu_ids=[2,3]`,
service/database CPUs2,3, and generator CPUs0,1. The ambiguous field was removed.
No public calibrator or affinity gate was adapted or bypassed. This correction
resolves the concrete issue found in this configuration review.

## Independently checked source and workload boundaries

The reviewer compared 35 explicit source bindings, comprising 11 public driver
files, three product locks at each of the two product commits, nine public
profiles, and nine public analysis sources. All declared digests matched the
actual Git objects; these reads covered 592,752 source bytes. The complete
`long_groups` dictionary equals the public reproduction workload dictionary,
whose SHA-256 is
`30af3a81ca377436cdedcae33a074b91df510256d403ba9fca11763186da44cf`.
The copied gRPC profile bytes equal the original public profile bytes.

The policy delta is limited to explicit recovery metadata, the current stripped
boot identity, the historical first-runtime-change identity, and the prospective
fixed-long-rate rule. The existing SLOs, resource limits, capacity ladder and
refinement algorithm, A21 bootstrap/quantile definitions, protocol mixes and
other policy fields remain unchanged. `policy_revision: 4` is the unchanged
public calibrator schema; separate recovery fields identify the new epoch.

The five prospective long rates remain PostgreSQL144/s, SQLite40/s, HTTP500/s,
gRPC115/s and codec192/s, with the original concurrency/workers, seed, period,
operation targets, observation policies, warmup, recovery and idle settings.
The unchanged calibrators may report their original 80%-of-capacity proposal;
the new policy explicitly prevents that proposal from silently replacing the
fixed rows. A failed fresh before prerequisite is preserved and stops admission.
Any change requires a reviewed prospective freeze before matched measurements;
an after result cannot retune its paired before rate.

Historical five-before-long acceptance, the completed 54-process protocol
cohort and completed six-process ON noise are kept separate from this epoch.
The current counters start at zero, and neither old noise ranges nor historical
long credit transfers. The interrupted 18-process comparison remains terminal
outcome unknown. Missing private owners, readers and diagnostic sources are
identified as unavailable, not represented by their historical hashes alone.

The recorded historical first runtime change
`da95b81282b25152e82c9aa7877cd872ea9e03a0` resolves to the existing product commit
with subject `perf(interop): reuse validated defaults and own import references`.
The recovery first-change field remains null. No new product edit is claimed.

## Limits and remaining admission

The configuration's Python executable identity was supplied by root; this
source-only review did not rehash an executable or an SDK/archive payload.
Actual recovered compiler, SDK and PostgreSQL receipts remain required before
production, as declared by the freeze. Future producer receipts must bind the
actual clean source, complete common/domain package graph, consumer resolution,
native assets and application outputs. Reproduction-relative profile names must
resolve to their actual pinned inputs at that later admission.

The source review initially attempted to find the four database analysis files
under a diagnostic subdirectory and stopped on that incorrect path assumption.
The files were then located at their actual public batch-root paths; the final
35-source comparison used those exact paths. This was a read-only lookup issue,
not a product or workload outcome.

Only source/small metadata reads and documentation changes were performed on
CPU8. No executor import, workload, product test, compiler, raw journal reader,
payload restoration or large-payload hashing was executed. The accepted
configuration does not substitute for review and bounded validation of the new
portable owner or the reader/provenance adapters.
