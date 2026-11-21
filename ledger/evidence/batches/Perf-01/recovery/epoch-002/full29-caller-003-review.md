# Perf-01 final full29 caller: independent source review

## Conclusion and scope

**No blocking source issue found in the frozen caller reviewed below.** The 29 command recipes remain the original recipes. The changed B20 result-reader loop matches the final product's actual output and its additional HTTP/1.1 and HTTP/2 close-before-Finish checks. The final-role admission requires the original before/common evidence and the separately built, selected after evidence; it does not transfer an earlier after attempt's credit. The existing exclusive reservation, finite process owner, and retirement requirements remain in force.

This is an independent source review by the `perf01_delivery_review` agent. Verification used source reads, SHA-256 checks, Python AST parsing, and `git show` of the exact product commit, on CPU 8. No target Python module was imported. No build, restore, fixture, native test, benchmark, or workload was run by this review. It grants no execution, performance, long-duration, or global acceptance credit. Actual execution receipts remain necessary.

All paths below are relative to the corresponding project repository. Diagnostic paths are beneath `ledger/evidence/batches/Perf-01/diagnostics/` in Plan.

## Frozen inputs

| Input | SHA-256 or commit |
| --- | --- |
| Final caller `recovery-regressions-003/sources.json` | `9e58869e945097a8dac9360bd1b13a55fe73f69002e3a922cbca33d38874a6db` |
| Final caller `run.py` | `785389d1a0814ab2f2e58263b8e1d017e1ef3509a184a240dc385180fe346226` |
| Final result reader `results.py` | `f7e4932f9c1f9f3bd9b8a8ba1e1dc0bc119d421f5fd5bab4a25e5366e346816d` |
| Original `recovery-regressions-002/sources.json` | `20ebc83402a1ded7fcec377ad82805edb597fd0f9291eb01015b0f9618620a38` |
| Reused original `recovery-regressions-002/recipes.py` | `ceeffe11d8a59888c5a3b5d61289c8609b2e7fcfa618ab82c539fcba594a6b7b` |
| Context `recovery-measure-002/measurement-sources.json` | `6b1d1e8ec6ee80271fdbbeb1c6d13909b92ca13c7a28cbc4fd4085f98f6a4c2c` |
| Fresh-after adapter `recovery-after-003/sources.json` | `66cc5531f6cacc557b8adf5a29ff7853d74a16f22c94279e441703cec2332692` |
| Original owner/build controls `recovery-build-001/sources.json` | `c7526f08d3c50c6d58f7336adae6ebab5fb82b606cce140108a48f6b54b3d0ab` |
| Final NativeWeave product | `2f40348c3db80a4fbee7a99e721b374a597b16df` |
| Product `tests/Server.Diagnostics/Program.cs` | `59a41cd5bd3276844e6e38b296167059d367cd1dc6927792719085489e6d6559` |
| Before product / common driver | `ea5fa528035d025bd7a28698ee7c71194432236c` / `2e3995df8d86583ee9443348276ca8d918056bfc` |
| Locked Design | `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9` |

The named index hashes and their declared local file maps were independently verified. All 18 product recipe-source hashes in the final index match `git show` at the final product commit. The only changed product entry compared with the prior recipe-source map is `tests/Server.Diagnostics/Program.cs`. Eleven relevant Python files parsed successfully as ASTs, without importing or executing their code.

## Original command population is retained

The new caller imports the hash-pinned original `recovery-regressions-002/recipes.py`; there is no replacement recipe implementation. Static inspection finds 29 distinct `add` calls, and the runtime caller additionally requires 29 distinct labels.

| Subset | Outer commands | Retained scope |
| --- | ---: | --- |
| B17 | 6 | JIT restore/build/run and Native AOT restore/publish/run |
| B15 | 1 | Existing selected-native application verifier, including its nested checks |
| B19 managed | 10 | JIT, exact API checks, Native AOT, package consumer |
| B20 managed | 12 | Debug defaults, Release JIT, API/XML, both original Debug sample modes, Native AOT, package consumer |

Arguments, flags, deadlines, selected-native parameters, and binary inventory plans therefore remain those of the original recipe file. No cost or benchmark mode was added. The original sample source is still pinned at `65b29c33814812de4fbb28b840358da5722751660eac0cfa45021c652273ab8a`; its assertions and both sample invocations remain present.

## B20 result adaptation matches product source

The prefix and suffix of `results.py` outside the single B20 diagnostic assertion loop are byte-identical to the prior reader. That loop now reads one exact, line-anchored completion summary and requires the observed count/configuration to match: Debug defaults 5 with dynamic code, Release JIT 122 with dynamic code, and Release Native AOT 122 without dynamic code.

At the selected product commit, `CloseBeforeFinishAsync` contains six `Check` calls. `Main` invokes it once for HTTP/1.1 and once for HTTP/2 outside the defaults-only path. Those twelve checks explain the change from 110 to 122; Debug defaults remains 5. The new reader also requires each protocol-specific payload marker once and each of the five shared close/Finish lifecycle markers twice. All checked text is emitted by those existing product `Check` calls. The successful Finish marker's trailing space matches the source expression when its exception value is null.

The prior ownership-join and throwing-listener retirement checks remain. Outside this loop, the original B17 actual count and lifecycle checks, B15 application/package checks, B19 observed JIT/AOT count equality and retirement checks, B20 API/XML and sample checks, package proof validation, and command/log/binary hash checks are unchanged. This adaptation strengthens the final product's coverage; it does not replace an observed count with an invented execution result.

## Actual before/after binding and ownership

The caller change also adapts admission to the fresh after producer; it is not merely a count edit. `run.py` requires the exact reviewed Context index, the exact after-adapter index, an actual after-input descriptor, `ctx.after_rebuild`, the original reservation, and `ctx.selected == recipe_reference_commit`. The latter binds the selected product to the full final commit even though the source-only index's `selected_final_commit` field is null.

`Context.validate_after_inputs` permits only fresh output/control locations and the after product path/package versions to differ from the original build inputs. It preserves all other inputs and rejects overlapping destinations and reused package versions. Before and common use the original inputs; after uses its own actual inputs and source index. `build.completed` validates the appropriate original producer recipes and completed, zero-exit, retired child receipts. The fresh-after execution must also identify the same original baseline inputs, source index, admission hash, and actual before proof. Existing paired producer checks remain.

Both roles' B18 functional proofs are required. Context compares their exact planned two-command recipes, child receipt and log hashes, successful retirement, source/native binding, and toolchain/freeze identity. The after proof must additionally bind the same fresh-after producer receipt. The full29 caller chooses exactly one Server native asset from that after binding, pins its hash, and uses the actual selected checkout.

The existing lock is opened without replacement and acquired with nonblocking exclusive `flock` before Context import or expensive admission. It is held around admission, all commands, and result collection. CPU 8, fresh output/cache destinations, source stability checks, and disk floors remain required. The c752 owner is reused without modification: the public process tree and subreaper track descendants, each command has a finite deadline, cleanup preserves failures, and completion requires retirement. A leader's zero exit alone is insufficient. The caller preserves the failed command receipt when available and writes a completed result only after all commands and result validation succeed. Fixture executable/native inventories are checked before and after execution.

## Remaining execution obligations

This review does not assert that the new full29 run has completed, that the original sample failure is resolved, or that the five before/after high-load groups have passed. The actual fresh-after build and B18 prerequisites must exist before admission, and all 29 commands plus their result checks must then succeed with the bound native asset. The caller explicitly records zero performance-credit seconds and does not reuse historical execution credit. Normal repository review and CI requirements remain separate.
