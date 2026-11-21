# Current epoch-002 role callers: independent source review

**Verdict: ACCEPT for execution as source only.** No blocking issue was found
in the inspected role-binding delta. This review does not establish a successful
build, functional regression, profile, measurement, report generation or long
segment. Root remains the sole executor under the existing finite owner and
exclusive reservation.

## Exact reviewed sources

Paths below are relative to `ledger/evidence/batches/Perf-01/diagnostics/`.

| Source index | SHA-256 |
|---|---|
| `recovery-measure-002/measurement-sources.json` | `6b1d1e8ec6ee80271fdbbeb1c6d13909b92ca13c7a28cbc4fd4085f98f6a4c2c` |
| `recovery-profile-002/sources.json` | `6e0a16a6b4f84afc811b559dcdb1d62bfb32032c59bd3bd6aa030a0e778a4b42` |
| `recovery-after-003/sources.json` | `66cc5531f6cacc557b8adf5a29ff7853d74a16f22c94279e441703cec2332692` |
| `recovery-report-002/sources.json` | `06ef0a962f13084abba9f6d37d6d0a836ca94493b624555f935aa32ba39e1d00` |

The companion JSON binds the principal code files and records the source-only
validation scope. This is a new narrow review of these exact versions; earlier
reviews of different indexes were not treated as acceptance of current bytes.

## Findings

Compared with reviewed measurement index `a71deb1272c3b29dd1573e5dacfccc0c53db01d72807dd091b4b78e18456728b`,
only indexed `admission.py` and `MEASUREMENT.md` changed. The new admission
allows exactly five fresh-after input differences: output, control, product
path, package version and upgrade version. Other inputs compare equal,
including the freeze, toolchain, Python dependencies, build environment,
baseline product and common driver. Fresh destinations must be disjoint from
the admitted source/output locations.

Before and common always retain their actual original build inputs, producer
receipts and build source index
`268d10b6b058f6c599fc1128b8a2a7ad7949f723d842647756e542ba70756795`.
After uses its own explicitly paired input/source descriptors. Its producer
and B18 receipts must name the unchanged baseline descriptors and the exact
actual before proof; B18 additionally binds the actual new after producer.
The unchanged original `build.completed`, producer plan and B18 plan still
check the commands, artifact identities and retirement. The common corpus,
comparators and before-produced protocol client keep their original roles.

The full fresh-after caller was read for these receipt-generation and
prerequisite paths. Relative to the reviewed inspect-proxy version, the only
profile code change selects a Shared manifest through `ctx.role_outputs[role]`.
The inherited proxy/fallback behavior and its limited preparation scope remain
unchanged. Measurement workload, reader, noise, capacity and statistical
implementations are unchanged by this role-binding delta.

The old report adapter index
`00757dd85400382b4213bbb7c45a69026f0d4dc42f6223a6f100fa764219aa0e`
requires every producer to use the baseline input/source identity and therefore
rejects a separately produced after role. Use the reviewed `06ef0a…` report
adapter above for this sequence. Its per-role producer mapping, exact baseline
prerequisite and selected-final receipt checks match the new admission. The
existing `report-after-admission-review.md` remains the separate report change
review; no statistics or aggregation change is implied.

## Validation and limits

The reviewer read the changes and relevant unchanged producer/receipt checks,
verified all 16 indexed files (7 measurement, 4 profile, 2 fresh-after, 3 report),
and parsed four Python files as AST without importing the target modules.
No build, test, service, profile, workload or report was executed. There are no
new numeric results, performance claims or long-test credits.

The prepared private queue contains raw command data only. It is neither an
execution record nor a replacement admission check; it contains no after
dependency for its before-only entries. Root must select the unified reviewed
caller versions before execution. Existing formal receipts must retain their
original measurement index and must not be relabelled to a newer one.
