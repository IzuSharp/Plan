# Task-01 scoped Plan candidate review

Candidate: `71bfddd74aaa91cdec385a5505d9eba22e4335f0`. Reviewer: `/root/b01`. This review read exact Git objects and compared recorded hashes. It made no Plan changes and executed no product, historical model, benchmark or runtime acceptance again.

## Result

The four Linux component statuses and their accepted source identities are consistent. The candidate correctly preserves Linux-only claims, defers other platforms, and leaves global acceptance and A13 completion false. Every change from the locked Plan input is under `ledger/`; the historical accepted planning snapshot is unchanged.

All four component author trees agree with the recorded publication mappings. The accepted source hashes match the final integration commit `39d3dc3bde90304cf8baf6d59bbfa75959cc8ed5`: A01 30 owned paths, A19 17, A21 16, and B01 38. All listed integration commits are ancestors of that integration head. The component review chains resolve the earlier findings; B01's formatter supplement preserves the prior run-4 and split-lock binding.

All four relative handoff links and every explicit status evidence path resolve in this candidate. Of the retained task result/review files with conventional local originals, 682 are byte-identical; none differ. The original B01 packet's 163 entries are accounted for by 102 retained files and 61 hash-identified omissions. All 84 omission-overlay entries are absent and carry valid SHA-256 identities. These checks establish the local candidate's internal identities, not remote availability.

## Corrections reported to the orchestrator

1. `status-linux.json` places the final local integration commit next to the previous publication's remote commit/tree. The final local tree is `814094f77140c01068ac82514709c4dc208360cf`; the recorded `dae562e...`/`825c8d2...` belongs to previous local `c3ea6da...`. Replace with the actual final receipt or label the previous checkpoint separately. The orchestrator subsequently reported final remote `22fe70a66312f1a8ec0767d244e3b74762e7ff99` and successful CI run `43811091217`; those are not yet fields in this reviewed candidate.
2. `B01/review/B01-format-independent/Compare.runtimeconfig.json` is a reproducible generated configuration that the formatter review explicitly excludes. Omit it and retain its identity if needed.
3. The formatter packet manifest names intentionally omitted `TokenCompare.cs`, but the batch omission overlay does not yet list it. Its SHA-256 is `5f91725b79ceeb536f6fcbaaad9272cf71a8bde7857abf405661972a1ab20086`. Preserve that hash if the manifest remains; do not restore source to the archive merely to satisfy a historical manifest.

## Publication limit

Automatic approval review has rejected publication of the broad source/probe archive and, according to the orchestrator's later report, the reduced logs/results archive. This exact local candidate is therefore not a durable remote evidence claim. The orchestrator is preparing a materially smaller handoff/status/hash-only checkpoint. Its final handoff must state what actually persisted, identify the publication receipt and paired-integrity outcome, and mark raw logs/results as local or unpublished unless publication is later approved and succeeds. Prior manifests can remain immutable identity records with an explicit availability overlay; they do not prove their named files are remotely present.

The existing Plan `paired-integrity` workflow runs for `ledger/**` changes on PRs targeting `main`. The final current-head result is still required. No re-acceptance of the historical global research snapshot or unrelated experiment rerun is necessary for this ledger-only change.
