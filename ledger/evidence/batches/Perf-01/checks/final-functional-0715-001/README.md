# Perf-01 final functional checklist — 0715ffb6

All **nine targeted Linux x64 functional gates passed** on product commit
`0715ffb6376b1ae08259ad7e2cb30ff0320d83e7`, tree
`cd0a6022e0115c22f133aedf6c801d9244640523`. This report projects the existing
gate009 and gate010 receipts and their actual referenced results. It runs no
gate or build and assigns **zero performance or long-duration acceptance credit**.

The public [numeric and hash checklist](summary.json) is 13,068 bytes, SHA-256
`d98959cea260eaada93f731d647469b0fe3219dc847a4b61243ae204c445e15f`.
It includes all ten recorded gate attempts, including the original failed B17
launch. Every copied string is an explicit status/task/gate enum or a source or
content hash. Local paths, command bodies and log bodies are excluded.

## Actual execution split

| Attempt | Actual UTC start | Actual UTC finish | Passed gates | Failed gates | Receipt SHA-256 |
| --- | --- | --- | --- | --- | --- |
| 009 | 2026-11-20 07:18:44.024656 | 2026-11-20 07:23:37.383322 | A07, A08, A18, B06, B16 | B17 | `fe5b62c6c9b16590440df2dfa96433f5b88923e4a09efd029e45f98c4f7e7064` |
| 010 | 2026-11-20 07:24:38.447855 | 2026-11-20 07:33:18.431159 | B17, B19, B15, B18 | None | `cbc12e491301c0d0d2cc0518058a540e2eb9bbeee730952a16dff659b197a31e` |

Gate009 remains a failed execution receipt. Its B17 launch passed the wire
generation check, then failed during exact-layout compiler discovery with
`FileNotFoundError` for `clang-19`, before the native build phase. The failed
component result and its failure log remain separately hash-bound:

- Failed B17 result: `cd5c07581fb5d9aa1c0a74d369b4335b02d204474be06cd041890f18608c5a00`.
- Failed exact-layout log: `cf8feded89cbe0861bea3b5a9f20ab03fa392d269cb8d869457e55eaefb5332a`.

Gate010 adds the existing compiler alias directory to executable lookup and
asserts the unchanged pinned compiler SHA-256
`0a3c55936ac43954fbe4914e6e73b577ca9e35e75d89ef13d3e28c187f41ca1a`.
It binds the exact failed 009 receipt before continuing. Product source is
unchanged; none of the five previously passed gates is rerun. The successful
B17 attempt uses a fresh output, preserving its failed predecessor.

The reviewed runner hashes are
`155b6178ac2ee53c2c728b068ce857575468ad6c0f17e16c0403582911583183`
for 009 and
`1736c1778cfc13ea64ca44aeb058749ff07399331de2c53ba9e8b06b8806db08`
for 010. Both receipts record the same source/tree and `x86-64-v2` Native AOT
instruction setting.

## Verified gate counts

The JIT and Native AOT columns retain each test program's actual counter name.
Assertions, checks, scenarios and verifier subcommands are different units and
are not combined into a single test count.

| Gate | Targeted component | Attempt | JIT | Native AOT | Recorded verifier subcommands |
| --- | --- | ---: | ---: | ---: | ---: |
| A07 | Async operation and native retirement | 009 | 355 assertions | 356 assertions | 39 |
| A08 | Execution admission, close and worker joins | 009 | 489 assertions | 490 assertions | 34 |
| A18 | Native HTTP async proof and managed handler bridge | 009 | 127 checks | 127 checks | 54 |
| B06 | Bounded database streaming with actual providers | 009 | 674 assertions; 62 cases | 674 assertions; 62 cases | 24 |
| B16 | Server streaming ownership and credit | 009 | 81 assertions | 82 assertions | 23 |
| B17 | Native server binding and real transports | 010 | 85 checks; 43 dispatches | 85 checks; 43 dispatches | 19 |
| B19 | MCP protocol integration | 010 | 291 assertions | 291 assertions | 21 |
| B15 | Server application integration | 010 | 85 assertions | 85 assertions | 15 |
| B18 | gRPC integration and lifecycle | 010 | 662 assertions | 663 assertions | 18 |

The nine successful gates contain 247 recorded verifier subcommands. These
include compilation, metadata checks, fixture execution and deliberate negative
fixtures. A nonzero subcommand exit can therefore be an expected negative
fixture; the checklist retains the actual count without calling it a failed
gate. Gate pass/fail comes from its completed verifier result and outer exit.

Additional bounded observations read from the same evidence are:

- A07: 59 native owners created and released in each mode; zero live owners,
  retained input bytes and result owners; the lost-wake regression flag passes.
- A08: 47 jobs, engines and close owners retire in each mode, with zero live
  jobs and bad releases; the test output confirms actual worker joins.
- A18: 12 races in each mode and zero live resources after actual native HTTP.
- B06 and B16: the reported managed/native ownership and credit counters return
  to zero in both modes.
- B17: 19 native unit tests pass with zero failed, ignored, measured or filtered
  tests. Both managed modes check HTTP/1.1 and HTTP/2, including TLS cases.
- B19: 180 Native AOT managed-retirement observations, five consumer compile
  fixtures, nine rejected preparse cases and one successful preparse case.
- B18: 393 JIT and 395 Native AOT managed retirements; 71 public symbols, five
  negative compile fixtures, eight ABI records and 103 offsets.

The B15/B18 functional server copy is recorded as
`67d70943dfd19cc1f52b9ad8dc9872de21e763eaf04433c8316efc1e5055c23f`.
That is the functional fixture identity recorded by 010, separate from the
actual package identities bound to performance measurements.

## Evidence checks and limits

All nine result files were read. Their content hashes match the hashes in the
outer receipts where supplied. B06 publishes `summary.json` instead of
`result.json`; its source-manifest hash was reconciled to a clean 0715ffb6 source,
and its 24-command receipt and both provider logs were checked separately. Every
additional log used to extract a count was matched to its existing component
command-receipt hash before reading that count. Result hashes and count-evidence
hashes are retained in the public JSON.

No executable or native library was rehashed by this projection. Recorded
binary hashes remain backed by the original verifiers and runner. This is a
targeted functional checkpoint, not an assertion of completed performance
comparison, five paired 30-minute groups, all-platform acceptance, package
publication, CI completion or final repository approval. Those records remain
separate. The original failed launch contributes no acceptance credit.
