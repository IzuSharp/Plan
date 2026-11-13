# Independent review: Plan host/profile gates and lifecycle task packets

Reviewer: `/root/design_source_review`. Author of the reviewed Plan changes: `/root/plan_recovery`. This reviewer did not write the graph validator, host-policy tests, schemas or Plan packets.

**The frozen gate/schema/task-packet changes pass this review. Final cross-repository pairing and checkpoint verification are recorded separately once that input is frozen.** This review does not accept product contracts, authorize Delivery, select a default Server, or certify future protocol implementations.

## Scope and preserved phase

The base is Plan `04c2f043c0ec60a2d49dd3ca8ea4ad1c8c888d89`. The author's v3 freeze covers 64 files: 53 changed packets and supporting graphs, validator/schema, policies and workflow. All 114 existing IDs remain; 61 packets are unchanged. Independent comparison confirmed unchanged task status, acceptance evidence, independent-review arrays, write scopes and outputs. All 48 Delivery nodes remain `planned_candidate` with `not_authorized` implementation authorization.

The packet revisions preserve the actual evidence boundary. R07's completed synchronous-admission experiments do not establish async callback retirement. Database's six finite SQLite cases do not establish PostgreSQL lost-ACK recovery or a C# AOT adapter. Server's Bytes/Tokio/Body cases do not establish a C# handler, transport or RSS bound. Kestrel remains a required research comparator and an unselected product host; Rust remains another unselected host.

## Gate behavior reviewed

- Conditional `start` dependencies constrain readiness and are checked again at acceptance. Conditional `acceptance` dependencies allow unrelated local work to start but prevent final acceptance without the selected implementation.
- All declared selection inputs must resolve to selected/excluded, and the Server host group requires at least one selected host. Neither both excluded nor one selected plus another undecided silently enables delivery. Both selected is supported without making either a default.
- Selected host choices and node content enter the subject snapshot. Profile-matrix changes also change the node digest. Previous evidence/review bindings cannot be reused after those changes.
- Proposed release scopes validate referenced task revisions and conditional selection references. The required Rust Database component cannot be silently made optional through `when=selected`.
- B18/B19 support an explicit protocol-by-host matrix. Both hosts may be selected while a protocol is intentionally enabled only on Kestrel; that case does not create an irrelevant Rust protocol implementation dependency. Every enabled profile still needs an applicable accepted design.

## Closed findings and packet corrections

| ID | Finding | Final disposition |
| --- | --- | --- |
| PLAN-REV-001 | The initial host-profile gate checked that a contract was accepted but did not prove its supported host. Assigning an accepted Kestrel-only protocol contract to the Rust profile could bypass the missing-design guard. | Closed. `contract_host_profiles` first requires the existing accepted-contract validation, reads the same spec bytes under their content SHA256, and parses exactly one strict host-scope declaration. Missing, malformed, duplicate, wrong-host or hash-drift declarations fail closed. |
| PLAN-REV-002 | A separate packet review found A07's result cleanup wording could imply releasing an OwnedResult after transfer to the application merely because nobody awaited it or a duplicate notification arrived. | v3 checked and accepted as a correction. Native ownership before take, managed wrapper ownership after take, and application ownership after successful publication are separate. Duplicate notification cannot trigger another take/free. |
| PLAN-REV-003 | A separate packet review found B05's rollback wording could allow a later cleanup response to refine an earlier Unknown commit. | v3 checked and accepted as a correction. Cleanup rollback/no-active-transaction only updates cleanup/disposition. Refining Unknown requires recovery evidence bound to the original transaction identity. |

The host-scope declaration is part of the contract's hashed, independently reviewed specification. It is not a new freely settable approval flag. `contract_accepted` requires the exact registry key to be accepted **and** successfully validated into the checked-contract set; that validation includes spec hash, evidence, review binding and contract dependencies. Human reviewer identity and truthful execution still require substantive review, as the validator itself documents.

The current C-PROTOCOL specification is not changed or accepted by this patch. D19 must add its explicit scope and complete real acceptance before even its Kestrel profile can use this new gate. Rust support requires corresponding new design/evidence, not a broadening of a selector alone.

## Actual independent checks

The reviewer independently executed all 28 isolated host/profile cases from the frozen v2 source, validated all three graph schemas, and checked all 64 input hashes before and after execution. The test module's report-writing main was not invoked, leaving the reviewed source tree unchanged. The positive policy fixtures explicitly seed checked contract state and suppress unrelated authorization/evidence checks; they are not represented as real contract acceptance.

A separate in-memory negative check used the actual 21-proposed-contract registry. Merely changing C-PROTOCOL's status field to accepted did not pass validation, populate the checked-contract set or expose a host scope; missing spec/evidence/review requirements rejected it. No registry or product ledger was changed.

The reviewer also independently ran the complete Validator in the author's isolated preflight pair, after confirming its 64 files matched v2. Result: 34 research, 32 documentation and 48 Delivery nodes; zero accepted contracts; no ready or continuable Delivery. That preflight used a then-current Design snapshot and is explicitly not final pair verification.

v3 changes only A07, B05 and their packet hashes in the Delivery graph. The gate implementation/schema are unchanged. The two text corrections were independently compared and read; the forthcoming final paired validation, rather than the earlier v2 preflight, will bind the final graph bytes.

## History and remaining integration step

`verify_research_assets.py` correctly distinguishes the historical merged migration snapshot from current research edits. It checks the original migration's 33 changed/81 unchanged packets and unchanged Delivery graph at the exact old commit, preserves the historical checkpoint bytes, verifies all original migrated assets/evidence, and separately checks the current 114 packets. It does not relabel current legitimate packet changes as part of the old migration or count preserved logs as new execution.

The remaining integration check is the final `source-driven-baseline.json` Design commit/registry pin, new lifecycle checkpoint and current-pair verification. The original graph mutation and Rust regression suites must remain passing at that final pair. No new native experiment needs to be rerun for this Plan-only change.
