# A19 Linux x64 handoff

## Scope and source

- Batch: Task-01; task: A19 revision 0.4.0; platform: Linux x64 only.
- Owner: /root/a19. Implementation branch: `task/Task-01-A19-linux`.
- Implementation worktree: `/workspace/scratch/0898a75257bc/.worktree/Task-01-A19-linux/NativeWeave`.
- Commits: `1069438` (models/checker/input and transition identities), then `d78d6ddb81afdb01efc0e2dbe056e7b441f26487` (documentation, examples, regressions and evidence runner).
- Locked Design: `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`; Plan input: `050d54cc2433901cbe896f7490af0e94ba631415`.
- 24 Design input files are SHA-256 verified; 88 candidate transitions have existing owner/spec/refinement mappings.
- No root solution, Cargo workspace, build, CI or other task scope was modified.

## Actual execution

Command, from the implementation worktree:

```sh
python tests/Verification.Models/run.py --design-root /workspace/scratch/0898a75257bc/.worktree/Task-01-linux/NativeWeave-Design --output-dir artifacts/A19/linux-committed-1
```

The exact committed scope is clean. The run passed 18 regression tests, minimal and advanced examples, five complete candidate state graphs with bounded progress, and eleven deliberately unsafe controls with their specific expected counterexamples. No candidate was resource-limited; all negative traces replayed after JSON serialization. State/time exhaustion and unresolved cycles are inconclusive, never passed.

| Candidate | States | Transitions | Maximum non-stuttering actions from initial state |
| --- | ---: | ---: | ---: |
| admission/candidate | 157 | 284 | 8 |
| retirement/candidate | 5169 | 17479 | 26 |
| results/candidate | 802 | 1635 | 13 |
| dispatcher/candidate | 269 | 467 | 15 |
| mailbox/candidate | 35 | 44 | 11 |

Primary evidence: `artifacts/A19/linux-committed-1/run.json`, all raw `.stdout`/`.stderr` files, `models/summary.json`, `models/source-manifest.json` and the sixteen per-case JSON reports. The source manifest excludes itself and records every A19 source/test/guide/sample file.

`run.json` SHA-256: `7d1d8d657848a95199fc66e7ccf2547bf7b6a8630efce678546e74e2fffd417c`.

Model source-manifest SHA-256: `041a434487c3a28e4e8918caa4aaa7d0c4f85a7e5085e5b660dc0c085a21c569`.

## Failure history and scope limits

- `artifacts/A19/checkpoint/input-failure.json` preserves one failed development invocation with a wrong relative Design path. The corrected invocation succeeded; no protocol input was changed.
- `artifacts/A19/development/retirement-omit_setup.json` preserves an early negative-control oracle mismatch. The mutation had also removed registration drain, so a shorter, different violation appeared first. The corrected mutation removes only the setup barrier at its two uses; it preserves the registration/control barriers and finds `reclaimed_before_start_return`.
- `artifacts/A19/checkpoint-2/` and `artifacts/A19/pre-review-1/` retain earlier successful checkpoints. Final acceptance refers to `linux-committed-1` only.
- Evidence kind is `model_check`. The models are finite and sequentially consistent, with explicit continued-execution/fairness and finite actor-return premises. They are not Rust/CLR weak-memory, GC/FFI, Native AOT, real domain, performance or release proofs.
- The registration-drain negative is a cleanup-contract failure; no native use-after-free is claimed for it.
- No application API, managed assembly, native ABI or package is introduced. XML/application Reference, API binary diff and package/AOT consumer checks are precisely not applicable to A19's specific model_check matrix.
- Current concrete implementation refinement is `not_yet_bound`; A03/A06/A07/A08 own those future algorithms and A20 owns actual refinement testing. The optional binding validator requires exact commits, source/test hashes, symbols and synchronization rules and never claims source validation executes those tests.
- Windows execution is deferred. No additional platform/CI matrix was added.

## Integration and next step

Cherry-pick both commits in order or integrate the branch. No shared manifest patch is needed. To include this in an existing maintainer build, invoke `python -m unittest discover -s tests/Verification.Models -p 'test_*.py' -v`; the full evidence command above additionally verifies the read-only Design pin.

Root should copy the committed run, necessary failure history and this handoff into `Plan/ledger/evidence/A19/`, update the batch handoff, and bind the independent review to the exact A19 source manifest. No remote push/PR was attempted by this agent; root owns connector publication and local/remote commit mappings.

Implementation and Linux checks are complete; independent technical review and batch integration remain pending. Do not mark Windows or full multi-platform acceptance complete.
