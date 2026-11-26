# Already-released final close: isolated finite validation

**This candidate is not selected for performance or publication acceptance.**
Retain it only if root-owned independent package/AOT gates and paired ordinary
measurements establish a measurable benefit over public `17da07e`.

## Fixed sources

The prospective selection precedes implementation: Plan
`f7908d1e6a97fe875165fa6b379ab5a54b8c64fc` and Design
`ab942cd3f5ed2332f0e9958bec6996905f0be678`.

- Reference: `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`.
- Initial experiment: `4bfdbf781ce1ad74b2c3c58b41c68124c9243713`, tree
  `a056bcd9c7560b8bc9f3c48a56d8bf04df1c52a7`.
- Final local candidate: `d18d5654a7a69bce3a379c6fa8621b9d1d4b2767`, tree
  `f22333b98bf80fc539d819d642a9c692d2af7002`.

The final change only moves mutex-protected proof evaluation before publishing
`close_` and `closing_`, while holding the same channel lock. New fetch admission
cannot interleave, and acceptance follows all potentially throwing setup. This
was a source-review correction after the initial gates passed, not an observed
test failure. Both exact source versions and their results remain separate.

## Scope of the candidate

Only final close whose existing resource proof is already complete may skip
`controls.post`. Source control admission, both independent tail tickets,
CloseWorker receipt/error generation, accessor release and one generation-zero
notification remain. The proof requires a real completed cursor-cleanup fence
and completed fetch fence, not just EOF, ready or the cursor retired flag.
Outstanding results/errors and held batches conservatively keep the queue.
The original queued path handles every incomplete proof.

The callback may run before the native request returns. Managed setup/control/
callback-entry guards are reused unchanged. The fast branch does not wait,
issue provider I/O, change a batch limit, prefetch, remove EOF admission errors
or release the Session gate before consumer cleanup.

## Actual finite results

| Source | Gate | Observed result | Raw file |
| --- | --- | --- | --- |
| `4bfdbf7` | Fresh locked native build; streaming | PASS, 6 retained families / 394 checks | `build-01.log`, `streaming-01.log` |
| `4bfdbf7` | Native transaction lifecycle | PASS, 13 retained families / 120 checks | `transactions-01.log` |
| `4bfdbf7` | Actual isolated PostgreSQL 18 protocol | PASS, 432 checks | `postgres-01.log` and its server/consumer logs |
| `d18d565` | Incremental build and affected streaming rerun | PASS, 6 retained families / 394 checks | `build-02.log`, `streaming-02.log` |
| `d18d565` | Locked clang-format and full committed diff whitespace | Exit 0 for both | `format-and-diff-exits.json` |

The final source does not inherit execution credit for the earlier transaction
or PostgreSQL run. Its affected streaming gate was rerun once for the concrete
acceptance-boundary correction. The final streaming suite includes actual SQLite
and the retained native lifecycle/fault seams. PostgreSQL protocol coverage is
its existing native suite, not proof that every final-close branch was directly
exercised by a new PostgreSQL AOT consumer. Root owns those independent package
and Native AOT consumption gates.

New/strengthened native assertions prove same-thread ready-before-return only
with actual released proof; no control submission in that case; a completed
cursor still waits a held earlier fetch ticket; `retired=true` without cleanup
publication still queues; held final notification blocks public snapshots,
generic join and Source join in both queued and inline paths; outstanding rich
errors keep their queue and both error identities; and Source admission-stop
still rejects even an already-released cursor. Existing borrowed-batch, EOF
error, Session gate and quarantine tests remain. Positive suite owner counters
for source/session/cursor/buffer/pull return to zero; individual final-close
checks also verify Source reservations/tickets and generic operation counts.

## Archive and limitations

[close-quiet-validation.json](close-quiet-validation.json) records exact source
blobs, commands, tool exits, all 15 available pre-receipt raw files, and three
native test executable hashes. [raw-evidence.tar.gz](raw-evidence.tar.gz) also
contains that immutable receipt and the four complete final source files;
[manifest.json](manifest.json) records every member, and
[readback.json](readback.json) confirms exact content/metadata readback and
identical deterministic reconstruction. Full base-to-final and initial-to-final
patches are included. There were no observed build/test failures in this finite
candidate sequence.

The initial streaming executable was overwritten by the final incremental
build. Its initial raw log and exact committed source remain; no initial ELF hash
is invented. The two other test executables retain their initial-source identity.
Binaries are omitted from Git; their content hashes and exact local reproduction
commands remain in the receipt. No product native assets were swapped, no
benchmark or allocation load was run by this author, and no CI configuration
was changed. Earlier `17da` timings and the initial experimental packages cannot
be relabeled as measurements of this final source.
