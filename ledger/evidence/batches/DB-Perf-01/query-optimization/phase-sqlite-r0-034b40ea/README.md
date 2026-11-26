# First completed SQLite phase repetition — provisional

This records actual local Linux Native AOT observations for published product
`034b40ea0635027aa2132a4feb90343cf80a3081`, before any proposed serializer fast path.
The source/binary freeze is `f493d3d315f7e1c9411d05cf41d94c0d15bdb0fc1c8270324348280df7e2f7b4`.
Only repetition `r0` is included. Later SQLite repetitions and PostgreSQL results
remain outside this checkpoint; no complete-campaign conclusion is drawn.

The three product columns are Korda preview.3, the recovered CI input and the
complete-command candidate.

| Managed allocation, B/op | Original baseline | Recovered input | Complete-command candidate |
| --- | ---: | ---: | ---: |
| Ordinary Fluent | 72,662.45 | 21,460.75 | 29,879.16 |
| Warm Prepare | 53,803.01 | 14,430.32 | 14,435.28 |
| Complete parameterized Host SQL | 61,909.63 | 17,899.57 | 17,981.26 |

Dynamic Fluent is **8,418.41 B/op (+39.23%) above the recovered input** in this
first repetition. These are whole-process window deltas divided by completed
operations; they do not attribute allocations to individual phases. Each cell
contains three 256-operation windows after 64 warmups. Every operation verifies
the same complete 100-row DTO list and alternating typed tenant values 1/2.
Within each product run, all three lanes use one session and C++ Host. SQLite
raw SQL uses an explicit ordinal marker `?1` where Fluent/prepared use `?`;
the exact spelling limitation is preserved in the identity record.

| Evidence | Scope |
| --- | --- |
| [Selected immutable identities](input-identity.json) | Original freeze digest, source/package/binary/harness identities and SQL/connection conditions |
| [Numeric r0 receipts](sqlite-r0.json) | Raw cumulative allocation endpoints, GC/CPU/native counters, four phase totals, first execution and preparation observations |
| [Ordinary CI](ordinary-ci.json) | All required normal CI gates passed at this source; zero benchmark jobs; no performance credit |
| [Priorities and selected follow-up](followup-priorities.json) | Dynamic regression first, strict private-root encoding proposal, and an unproven wait hypothesis |
| [Evidence index](evidence-index.json) | Original digests and explicit extraction boundaries |
| [Documentation validation](documentation-validation.json) | Current link/digest/history checks; no build or performance execution by this evidence update |

Read-complete occupies 90.5–94.1% of the observed window wall time. Process CPU is
about 1.77–1.98 ms/op versus 12.22–14.44 ms/op wall. The source's default 10 ms
callback retry timer is an investigation hypothesis only: these receipts have no
retry counts or callback timeline, so they do not establish its contribution.
No timer/spin change is selected. The serializer follow-up is planned, not an
implemented or measured success. All four final local 30-minute mixed cells
still have zero accepted seconds; final performance and stopping decisions remain pending.
