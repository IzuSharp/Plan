# Continuation10 — reject pull-local07; retain the measured gaps

**Keep integrated05. Do not integrate pull-local07.** The predefined two-provider,
two-reversed-round text1000 screen is complete and did not reproduce a useful CPU
reduction. The root accepts the independent rejection. Do not run this candidate's
conditional mixed gate, seek another favorable round, or reopen tail06. This
decision closes one candidate, not the entire DB-Exec-Parity-01 task.

The owner's [short-only scope](short-only-scope-08.md) remains binding. No long
measurement or matched-before long supplement was started. Historical 0/4 is a
cancelled plan, not a pending gate or permission to launch four long cells.

## Exact retained and rejected identities

The retained product is Korda `2ea67ce1902f330679c3ebff4d6d5733be20f69c`, tree
`4e3989f2ce9e0c554585aab5a8bbb656e689b18d`, on PR40. The actual integrated05
consumer source remains `867c869a7e51949122b3dd13e4c7c6df2a914ec7`, the same tree,
with package version `0.1.0-parity05.1`. Its five retained components remain
Worker-D, exact-valid decimal decoding, the SQLite prepare flag change, private
relation branch transfer and bounded private relation capacity.

The separate rejected source is `645cfa5f184d65a67fa71455a5f7271ee8469309`, tree
`244099ca35b396887d951299728a7bc2e0ecafb4`, with actual packages
`0.1.0-parity07.1`. Its product change is only the local-preference adapter and
HostPull's default choice from `3fb88246b2fee303578f0527970e3d084d89ab40`; later
commits add or correct finite tests. No part of this rejected candidate has been
merged into the retained branch. Its artifacts keep their original identities.

Both actual NuGet PackageReference AOT consumers from the local candidate feed
were built and bound to their package,
managed DLLs, generated C#, ELF/debug images and unchanged provider native image.
The [build record](pull-local07-closed-10/ordinary-consumer-builds.json) identifies
all bytes, commands and source trees. SQLite ELF is
`59b92a8f0493436ee7887c54153ce6f9c8afcf2e0c17812fc93eb462cea79a0e`;
PostgreSQL ELF is `a07ee215e4302b5afa27c24303a66d52721359b37202e407b3ed03b34adebc5e`.
They are ordinary consumers without the diagnostic hooks used by earlier work.

## Completed correctness and machine-code evidence

The actual default scheduler passed six finite scenarios and 178 assertions per
provider, along with the existing full NativeHost regression. ReadyScheduling
remains 4/82 and WorkerExecution 4/21 per provider; Program's own 438 assertions
are not the total of all suites. All listed final native owners were zero, with
36 separately recorded managed retirements. The final correctness run and source
binding passed 102 independent checks. No extra correctness matrix is pending.

Two different rejected test identities remain explicit. `c5b1ddb...` was never
built: independent source review corrected an expectation that cancellation must
defeat an already-ready result. `correctness-01` on `8d400ecc...` failed AOT
compilation because a test helper declared an int tuple where the API returns
uint; no database started. `correctness-02` on `645cfa5...` published and ran
successfully. These are not a hidden product runtime failure or a claimed
two-provider negative-control run. The [author report](pull-local07-closed-10/correctness-author.md)
and [independent review](pull-local07-closed-10/correctness-review.md) preserve the
exact limits of the original pg_ctl shutdown evidence.

The actual ordinary ELF analysis covered 44 bounded symbol/disassembly commands.
HostPull's empty-injection default selects Local; the common base fallback and
other materialized default paths still select Global. However, shared Signal
changed from one direct false call to an EEType comparison and two direct runtime
calls. Its code range grew from 240 to 261 bytes in both providers, so every path
through Signal bears that additional type test. The runtime can still use global
fallback or stealing; true does not guarantee execution on the same OS thread.
See [actual machine code](pull-local07-closed-10/actual-elf/README.md). This is
evidence of the compiled change, not exclusive CPU attribution or an assertion
that all other machine code is identical.

## Closed ordinary short comparison

Twelve business processes and two fixture initializers ran serially on the same
Linux x64 host, with explicit peer quiet. Both providers used prepared/persistent
text1000, concurrency 1, batch 32, 2,048 measured businesses per process and 128
additional warmups. The order was 05, 07, Dapper, then Dapper, 07, 05. The complete
window was 2026-11-27 11:10:29–11:11:26 UTC. No process used an arrival-rate queue,
an allocation shim, a runtime spin override or a long measurement.

All 24,576 businesses and 24,576,000 result rows passed, with zero business errors,
retries or oracle failures. The independent review passed 1,607 checks and 836
unique file hashes, verified all eight before/after input identities, and proved
normal client/observer retirement and positive PG owner exit. Both Korda variants
executed 2,048 SQL businesses per cell; PG recorded 8,192 protocol submissions per
cell. Submissions are not the count of all wire messages.

| Provider | Round | 05 → 07 CPU, µs/success | CPU change | Service p99 change | Managed B/success change |
| --- | ---: | ---: | ---: | ---: | ---: |
| SQLite | 1 | 3,645.886 → 4,281.013 | +17.420% | +15.152% | +9.000 |
| SQLite | 2, reversed | 4,626.232 → 4,594.593 | −0.684% | 0.000% | +2.324 |
| PostgreSQL | 1 | 4,875.822 → 5,195.008 | +6.546% | +2.488% | −3.664 |
| PostgreSQL | 2, reversed | 5,182.597 → 5,185.553 | +0.057% | +4.651% | +0.539 |

The small reversed SQLite decrease does not repeat its first-round direction;
PG decreases in neither round. There is no allocation or latency reason to
override the predefined CPU gate. These observations reject this compiled
candidate; they do not prove that every possible local-queue strategy is slower.
The whole-candidate difference includes the shared EEType test. No evidence
assigns all regression to that test, or all CPU differences to queues, cache
misses, wakeups or RhSpinWait.

The [independent result report](pull-local07-closed-10/independent-results.md),
[formal round comparisons](pull-local07-closed-10/per-round-comparisons.json),
[all process metrics](pull-local07-closed-10/per-process.csv), and
[scope clarification](pull-local07-closed-10/independent-scope-note.md) are retained
byte-for-byte. The full audit validation is SHA256
`287990b79b380e728ebe6272e469e5a8fb824c535591f14254a43769a1c218d8`;
decision `ab27e5873bd37925369364bb0527f08c9dabe829801e5813c64ae972abf8bdcb`.

## There is still a measured gap, not a guaranteed recovery budget

| Provider | Round | 05 / Dapper CPU | 05 / Dapper service p99 | 05 / Dapper managed bytes |
| --- | ---: | ---: | ---: | ---: |
| SQLite | 1 | 5.554× | 3.101× | 1.01461× |
| SQLite | 2 | 7.099× | 3.263× | 1.01468× |
| PostgreSQL | 1 | 7.943× | 2.851× | 1.00933× |
| PostgreSQL | 2 | 9.422× | 2.567× | 1.00916× |

Thousand-row managed allocations are close while CPU remains several times
Dapper. The retained older numeric1 and related32 observations are in the
[separate existing-business table](pull-local07-closed-10/prior-retained05-gaps.md);
they were not rerun in this screen. SQLite numeric1 previously used about 335µs
client CPU against 17.2µs; related32 used about 516KB managed bytes against 74.1KB
SQLite / 51.2KB PG. Related32 means 32 relation keys and 53 result rows, not 32 rows.
All ratios remain tied to their own paired measurement, not pooled across screens.

CPU and allocations here are process-wide steady deltas. Framework-only zero
managed bytes is not proved; ordinary native allocation is unmeasured. RSS and
GC scopes stay as recorded. These short cells have no released-idle snapshot;
wait4 peak RSS is process-lifetime observation, not a steady peak. PG sampled
visible-tree inner/outer costs and the 7.839841-second owner lifetime cost remain
separate, with no edge extrapolation or addition into client CPU. This screen
does not establish sustained capacity, long-tail stability, or host exclusivity.

## Next question, with completed work excluded

The old runtime spin sensitivity already ran 16 matched processes on both
providers, both implementations and two reversed rounds. It proved net CPU
sensitivity to the runtime setting, with no stable latency improvement. It did
not isolate precise exclusive spin time or test current 05. The
[deduplication readback](pull-local07-closed-10/spin-dedup/README.md) prevents
repeating that general experiment as a new discovery. No runtime override is
selected for the product or ordinary acceptance.

The next read-only question concerns the already measured related32 resource
cost: From 51,712B, final frame 60,504B and final tape copying 59,680B remain after
the retained capacity change. These inclusive observations are not summed as
exclusive CPU. Inspect whether a private final buffer has provable unique
ownership and can be transferred without changing input snapshots, public
Combine, mapper identity, DDL behavior or error order. This is not yet an adopted
strategy, implementation, or promised gain. A specific Plan/Design decision and
finite validation must precede any product edit. The [remaining-space review](pull-local07-closed-10/remaining-space.md)
and its [measurement-source clarification](pull-local07-closed-10/gap-source-clarification.md)
retain known failures and unknown costs.

## Persistence, CI and recovery

Supplement04 is now durably published in Plan
`ded73d7cd90cb692bea554c5e780df0ca9e05e3f`, subtree
`2e587d83d91168b040890cc2941044b69d2acd0e`. The root read back all 152 actual remote
files (201,059,061B), including binary parts, rather than trusting blob metadata.
See the [publication receipt](pull-local07-closed-10/archive04-publication.json)
and [actual byte readback](pull-local07-closed-10/archive04-byte-readback.json).
The 52 local compressed duplicate parts were then removed under a separate
identity-checked receipt; all original 2,404 source/raw/artifact files remain.

Pull-local07's complete new sources, actual builds, failures, generated code,
symbols and raw results are still local pending append-only supplement05. This
checkpoint publishes selected readable results, not a claim that uploading the
new full archive is complete. Its [source index](pull-local07-closed-10/source-records.json)
binds every copied selection. Four duplicate/rebuildable intermediates from each
new ordinary consumer were reclaimed after exact retained-input verification;
actual out, package, generated and build evidence remains unchanged.

Archive04's existing Plan CI run45984275158 was cancelled at the existing
30-minute job boundary after six full-history Plan checkouts consumed roughly 25
minutes. Completed historical gates passed; the remaining gate and schema did
not complete. [Observed timestamps and logs](pull-local07-closed-10/archive04-ci-cancelled.json)
support timeout attribution as an inference, not a fabricated annotation.
The [pinned-action review](pull-local07-closed-10/ci-checkout-review.md) supports a
transport-only correction: add `filter: blob:none` to the seven existing checkout
steps. Full commit/tree history, every frozen ref, path, command, verifier byte,
permission, artifact path and the 30-minute timeout remain unchanged. The
[byte-diff receipt](pull-local07-closed-10/ci-checkout-diff.json) verifies that
removing exactly those seven added lines restores the original workflow bytes.
Current-HEAD files still materialize, and historical blobs can be fetched on
demand; no precise speedup is claimed. Normal CI must still pass every original
gate and the final schema. No performance work is added or executed in CI, and
no successful CI claim is made for the cancelled run or the unrun correction.

Resume at `/workspace/scratch/0669b59f9cae/DB-Exec-Parity-01`. Three mains were
rechecked unchanged. Korda PR40, Design PR21 and Plan PR36 remain unmerged; Go
drafts 39/35 remain untouched. Continue only unfinished resource investigation,
evidence persistence and the authorized review/normal merge/existing release and
actual public NuGet AOT verification. Keep completed 07 work closed and all long
measurements cancelled.
