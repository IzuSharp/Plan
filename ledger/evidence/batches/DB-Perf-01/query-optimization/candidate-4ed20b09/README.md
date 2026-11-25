# Published complete-query implementation candidate

This checkpoint records Korda `4ed20b09a245a787a3efccc9dcf2ab3c9f85d4d9` and
Design `439c9c2005e1633c08afce07c7652b35b31647a3` for PRs 37/20/34. The product
tree is `1c95420b34a2291e4b63fdc08caf32409a3eb4ee`. The earlier `dd990f23`
attempt/tree `2643545ab41562bebe6c8d1f1811da9d3ced5257` failed the existing
shared Linux formatter gate. The published two-file correction has a new normal
CI run in progress; the required full gate is not yet claimed passed.
No performance, final-package, merge or release acceptance is claimed.

## Included evidence

| Record | Meaning |
| --- | --- |
| [Checkpoint](checkpoint.json) | Source identities, component totals, binary hashes, API boundary and four pending local long cells |
| [CI plan](ci-plan.json) and [selection](ci-selection.json) | Actual committed-diff routing, compatibility byte equality and independent provider checks; zero benchmark execution modules |
| [Earlier CI plan](ci-plan-dd990f23.json) | Unmodified selection from the initial published attempt |
| [CI formatting failure](ci-format-failure.json) | Two files, 180 WHITESPACE diagnostics, exit 2, complete-log hashes and paused consumer preparation |
| [Formatting follow-up](formatting-followup.json) | Exact new source/tree, folder formatter/idempotence success, full-scope local Unix socket limitation, and new required CI still in progress |
| [Native correctness](native-correctness.json) | 926 checks/52 goldens, Host/cache checks, exact origin-budget differential and sanitizer limitation |
| [Release excerpts](native-release-excerpts.log) and [ASan/UBSan excerpts](native-asan-ubsan-excerpts.log) | Exact selected result lines; local paths and elapsed test times omitted |
| [Origin failure](origin-reproduction.log) | Actual pre-fix cross-command CTE budget rejection |
| [LSan failure excerpt](lsan-limitation-excerpts.log) | Earlier 866-check run failed after assertions because LSan could not operate under the ptrace restriction |
| [Frozen ABI](frozen-abi.json) and [native assets](native-assets.json) | Original rejection statuses/zero owner counts and exact exports/GLIBC/native hashes; local paths and host details omitted |
| [Binding result](binding-result.json) and [log](binding.log) | Unmodified synthetic AOT results: 137 assertions/13 cases, including 53 complete-command-only assertions |
| [Fluent correctness](fluent-correctness.json) and [log](fluent.log) | Two-provider cases, 1321 combined assertions and 502 managed retirements; performance-shaped fields excluded |
| [Binding API](binding-api.log) and [Fluent API](fluent-api.log) | Unmodified API/XML check summaries |
| [Prepared applications](prepared-applications.json) | Six before/recovered phase/resource build identities, no measured results; later attempted SQLite final consumers remain diagnostic |
| [Documentation validation](documentation-validation.json) and [frozen gate output](frozen-record-gate.json) | Existing Plan integrity/schema checks at immutable `38f8ce8a`; no current product or performance acceptance |
| [Evidence index](evidence-index.json) | Original input digests, extraction labels and retained-file digests |

These files were inspected before inclusion. Exact result/log copies are marked
separately from authored summaries or selected-field/line extractions. The original
input SHA-256 identifies omitted local bytes; an extraction is not presented as
that original raw file. No source archive, restore graph, environment archive,
command-line archive or executable is attached.

Managed AOT runtime tests preceded final XML/comment/generated-guide-only edits.
The runtime behavior matches the reviewed candidate, and final product/API/XML
checks were rebuilt, but the retained executable is not relabeled as an exact
build of the entire final comment or later formatting state. Native source paths
match both published trees. Component results do not replace final exact-package consumption.

The final sanitizer pass disabled leak detection explicitly. Owner drain, a
successful ASan/UBSan run and LSan are different observations; LSan remains
unverified. The existing source-bound before/Dapper smoke and all historical
measurements keep their original identities. Four local 1800-second cells remain
pending and no new effective time is credited.
