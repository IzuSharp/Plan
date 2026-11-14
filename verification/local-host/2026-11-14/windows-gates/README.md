# Windows planning-gate execution — 2026-11-14

Executor: `/root/audit_scope`, using ArcForges Windows MCP `start_process`.
The [manifest](manifest.json) records exact commands, UTC times, exit codes,
unmodified gate-source hashes and raw stdout/stderr hashes. All thirteen gates
completed with exit code zero. The separate [schema command](schema-command.json)
validated all three graphs with the existing CI dependency `jsonschema==4.23.0`.
Its temporary uv environment did not install packages into the projects.

The actual inputs are Plan `dacaab7fc346da5b649e943a4d937a756345c492` and
Design `4c5c385779b753a4f06e59d07f80ad27ca10a841`. Shared local clones under
`Plan/.worktree/validation-pair/` preserve the required sibling names `Plan` and
`NativeWeave-Design`. They start clean at those exact commits, with
`core.autocrlf=false`, `core.longpaths=true` and Python UTF-8 mode. Fixed-output
gate runners only write derived reports inside these isolated clones. The
original repositories and accepted source bytes are not rewritten.

| Executed check | Result |
| --- | --- |
| English translation, Design and Plan | Both passed, including actual review linkage and immutable historical bytes |
| Contract and task English acceptance bindings | Both passed |
| `verify_completion.py --require-complete` | 34 Research, 32 Documentation, 21 contracts; 840 input entries, 114 packets, 10 fragments; 48 future Delivery nodes remain unauthorized |
| Graph structure and all three JSON schemas | Passed |
| Research-asset and logical-admission provenance | Passed |
| Source-lifecycle check | Original paired historical gate and current acceptance both passed |
| Lifecycle binding regression | 9/9 synthetic cases passed |
| Graph/evidence mutation regression | 28/28 synthetic cases passed, each requiring a valid copied baseline |
| Host selection | Original paired gate passed; all 9 current architecture policy negatives passed |
| Rust 1.100 evidence integrity | Original paired gate and current acceptance both passed |

The historical lifecycle, host and Rust checks run at their actual paired inputs,
Plan `5b346ebb5acdb387077d0faae16b00bbc77cb299` and Design
`ba21ecb5c2299b303584b120f2e6bd1c6d74783a`. Their original tool hashes and new
execution logs are preserved under `generated/verification/current-gates/frozen-history/`.
Old proposed states and host-selection alternatives do not describe current design.

## Collection classification

The generic runner copied the entire existing `verification/current-gates/` tree.
That also retained 24 unchanged historical files from `final-completion/` and
`pre-change-baseline.json`. They are **historical copies, not new executions**.
They remain here because the original unmodified run manifest references their
bytes. The [collection audit](collection-audit.json) identifies every artifact,
verifies each historical copy against its committed baseline bytes and separates
them from the 18 newly produced derived artifacts. Only this round's named
command records count as fresh executions. No successful command was retried,
and no gate failed or timed out.

`reproduce.py` preserves the original launcher and layout. It refuses to overwrite
an existing attempt or checkout. For another run, use fresh sibling clones at the
same commits and fresh output locations, then execute the manifest's commands;
do not run fixed-output checks over historical evidence. `run-schema.py` and
`schema-check.py` preserve the separately captured schema step.

These checks verify planning structure, exact accepted inputs, preserved provenance
and rejection of synthetic invalid evidence. They do not execute native research
fixtures, prove product conformance, authenticate real-world reviewer identities
or independently approve the later local-host supplements. This executor's scoped
collection audit is separate from the subsequent supplement review.
