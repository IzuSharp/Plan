# Aggregate reference fix and current CI checkpoint

This follow-up records published Korda `034b40ea0635027aa2132a4feb90343cf80a3081`,
tree `fbb71d978af30999afb21c86d42b5237bbfbcb62`, alongside Design
`439c9c2005e1633c08afce07c7652b35b31647a3`. It follows the
[unchanged earlier checkpoint](../candidate-4ed20b09/README.md). Its earlier
in-progress wording is an observation at that earlier checkpoint, not the current result.

The second ordinary CI failed its existing clean-source gate after formatting,
API checks and native CTests passed. Uploaded CI diagnostics omit the actual dirty
path list. The exact existing API generators locally reproduced changes to the
three tracked aggregate references from the changed Fluent XML; two complete
rounds produced identical reference bytes and diff. This source-evidence boundary
is recorded explicitly, and the gate remains unchanged.

| Evidence | Scope |
| --- | --- |
| [Current checkpoint](checkpoint.json) | Exact publications, previous failures and four still-pending local long cells |
| [Second CI failure](ci-source-failure.json) and [selected job lines](ci-source-excerpts.log) | Actual failure and the missing nested source-status output |
| [Reference fix](aggregate-reference-fix.json) | Three files, 87 additions/87 deletions, six successful generator invocations and 14 idempotent references |
| [NativeHost API log](Data.NativeHost-api.log), [Migrations API log](Data.Migrations-api.log), [Relations API log](Orm.Relations-api.log) | Exact public signature/XML outputs, identical in both local rounds and the failed CI API stage |
| [Current actual plan](ci-plan.json) and [selection](ci-selection.json) | Four ordinary scopes; three newly selected existing API checks; independent providers and no benchmark jobs |
| [V2 local correctness](v2-local-correctness.json) | Six actual Native AOT consumers built, 280/280 scheduled short operations, both-provider lifecycle success; no timing acceptance |
| [Documentation validation](documentation-validation.json) | Frozen historical gate, preserved earlier bytes, links and evidence digests; no current product acceptance |
| [Evidence index](evidence-index.json) | Original input digests and explicit extraction boundaries |

Normal CI run [45614292641](https://github.com/IzuSharp/Korda/actions/runs/45614292641)
is in progress at this checkpoint. V3 applications from that exact producer are
pending. V2 mixed, phase and resource binaries belong to `4ed20b09`, even though
the new fix changes documentation only and all 30 consumer/build inputs are
byte-identical. They are not relabeled as final-candidate measurements.

No formal performance run, final package acceptance, merge or release is claimed.
The prior native/managed implementation evidence and remaining gaps stay in the
preceding checkpoint; no source, restore, environment or executable archive is added.
