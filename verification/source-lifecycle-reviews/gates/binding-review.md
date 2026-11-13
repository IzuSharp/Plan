# Independent review: Plan lifecycle provenance binding

Reviewer: `/root/design_source_review`. Author: `/root/plan_recovery`. `/root/migration_evidence` independently cross-checked the initial binding tool and workflow. This review is separate from contract/task acceptance and does not authorize product implementation.

## Scope at this checkpoint

The source-binding tool and workflow corrections pass static review and all nine synthetic binding regression cases were independently executed from exact copied inputs. The final cross-repository Design/Plan pair has not yet been generated or executed at this checkpoint. A later final-pair result must identify that exact Design commit, registry hash, Plan baseline and lifecycle checkpoint.

The new verifier requires the actual Design HEAD, baseline Design commit and checkpoint Design commit to agree. Registry bytes must match both the committed file and the declared SHA256. Every declared Design input is checked against its recorded size/hash and the exact committed bytes. The historical Plan base supplies the original task status, acceptance arrays, write scopes, outputs and Delivery authorization; all of those remain unchanged. The 53 changed packets must match their recorded before/after revisions and SHA256 values; the other 61 nodes remain identical to the base.

It delegates preservation/source/checkout/log checks to Design's existing integrity verifier. That delegate reads preserved evidence; it does not rebuild native experiments. The merge commit is the current design input. The separate `tested_source_commit` remains the source that actually executed the native CI run. These identities are intentionally distinct.

## Closed findings

| ID | Initial issue | Reviewed correction |
| --- | --- | --- |
| PLAN-REV-004 | The checkpoint could point to a different summary while the delegated Design verifier read its fixed `verification/source-lifecycle/results.json`. Merely matching summary counters would not establish that both checks concerned the same source. | The manifest path is now fixed to the real Design manifest. Exactly one matching entry must exist in the pinned input list. Actual bytes must match both the checkpoint manifest SHA256 and that entry's SHA256/size. Checkpoint source/run identity must match this manifest, and the delegated result must return boolean `true`, the same tested source and matching counters with no accepted contracts or product execution. |
| PLAN-REV-005 | The workflow uploaded the old migration checkpoint but omitted the new lifecycle checkpoint. | The artifact now explicitly includes the lifecycle checkpoint and the scoped independent review directory, alongside the baseline and generated reports. |

The initial defective source and workflow are retained in `binding-initial-inputs/`. This was a static finding before final pairing, not a claim that a complete false pair was executed successfully.

## Independent regression evidence

`binding-regression/` contains the exact copied Python inputs, execution command, raw stdout/stderr and generated result. All nine cases passed: one same-manifest positive case and eight expected-rejection cases for an alternate summary path, missing/duplicate input records, digest drift, checkpoint source drift, delegated source mismatch, a truthy non-boolean result, and mismatched execution counts.

These are explicitly synthetic tests of the binding functions. They do not authenticate a CI provider, execute Rust/.NET, supply product acceptance evidence or replace the final complete pair verification. The reviewer did not modify or execute the report writer in the author's source tree.

| Reviewed input | SHA256 |
| --- | --- |
| `tools/verify_source_lifecycle.py` | `b0cae8ebacb9df4f7bdb8c9b46584d247f7cd83b968b0d7801406f798129ce36` |
| `tools/source_lifecycle_binding_checks.py` | `77700cc381793c884abf0e2b8c50d47d6e113d09edebccc763cef7097a114ee0` |
| `.github/workflows/native-slices-final-check.yml` | `100e951f3950cc992c25150998a2d7ee0f4977b01775a02941187888b4db82c1` |

The workflow checks out the exact baseline Design SHA with full history, uses read-only content permission, runs source-integrity and graph-policy checks, and archives the new checkpoint. It contains no native experiment rerun and does not alter a contract/task ledger. The checker writes a generated verification report, so final independent execution will use an isolated repository copy to preserve the author's frozen files.
