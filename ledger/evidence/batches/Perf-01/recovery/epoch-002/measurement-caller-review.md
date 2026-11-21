# Epoch-002 measurement caller source review

**Verdict: ACCEPT for the exact source below. Execution and performance credit: zero.**

This independent review covers `diagnostics/recovery-measure-002/admission.py`,
`measure.py`, `database_capacity.py`, its adapted database reader and the indexed
source dependencies. It checks the public driver's actual schemas and CLI
arguments. Only these review files were written; no caller, control module,
workload, build, service or test was imported or run by the reviewer.

## Exact reviewed bytes

| Input | SHA-256 |
|---|---|
| `measurement-sources.json` | `a71deb1272c3b29dd1573e5dacfccc0c53db01d72807dd091b4b78e18456728b` |
| `admission.py` | `b725cf969098c1fa5bf05c1244f22ff1e070ae60250f1699cff6f1c439329df4` |
| `measure.py` | `c8546af97fe18445d4e34c4ee5bd690a66fd39820fde3af041c87ddcb65a8360` |
| `database_capacity.py` | `41e96b34b1a75a4347be348d3e65060e09ad2bf1e88636be0958e390cb5bb681` |
| `readers/database_compare.py` | `6ccbe1d00d75c8c84fa41e2d9ab6353a49fe476c8d0a24f7b5c767ad79d57108` |
| Unchanged build source index | `268d10b6b058f6c599fc1128b8a2a7ad7949f723d842647756e542ba70756795` |
| Unchanged `tests/Perf01/verify_long.py` | `3f5eec2ffa18d0622463bda571ffdfd063c500d5aa5169cc92273d185201de82` |

All **71 indexed files** matched their hashes: seven caller,
45 NativeWeave and 19 Plan files. All 49 indexed Python files parsed
as Python AST. The accompanying JSON records the complete caller hash set and
original reader/A21/workload identities. Before remains
`ea5fa528035d025bd7a28698ee7c71194432236c`; the common driver remains
`2e3995df8d86583ee9443348276ca8d918056bfc`. The locked Design is
`c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`. The immutable admission does not select
an after commit; its separate exact final binding supplies that identity.

## Findings and dispositions

1. **Long protocol admission corrected.** The short reader's 64 MiB file bound
   cannot admit every long sparse histogram. The first streaming revision also
   selected the entire `scenarios` object, whose nested histograms can exceed
   the streaming value reader's 4 MiB record bound. The reviewed source excludes
   those histograms, retaining only small lifecycle/status metadata and the
   original build/native identity checks. Short calls retain their original
   reader and scenario-summary check. Long credit still requires the unchanged
   full verifier, which checks every independent client correctness flag,
   oracle and request row, the effective duration, service limits and release.
2. **Noise identity retained and tightened.** The existing ten-scene gate is
   unchanged in scope. Each publication key must now equal the completed
   execution's actual group/scene, and that execution must be before-only. Its
   original receipt, numeric projection, source context and readback bindings
   remain checked. A21 noise/percentile definitions are unchanged.
3. **Domain schemas match their producers.** The database reader's sole adapted
   eligibility condition accepts raw native `Disposed` and direct/managed
   `Stopped`. Other correctness, durability and resource checks remain. DB
   capacity retains the original ladder, refinement and three fresh passing
   confirmations. Protocol, codec, noise, comparison and capacity argument and
   receipt mappings were checked against their pinned sources.
4. **Execution ownership and failure evidence remain explicit.** The existing
   finite owner, exclusive reservation, immutable before admission and separate
   after binding remain in use. Failed/interrupted directories are preserved;
   no historical measurement or automatic retry receives new credit.

No blocking source finding remains for these exact bytes. This is not proof
that populated local inputs, builds/B18 checks, noise, capacity, real TLS drain
or long runs pass. Those existing runtime checks must supply their own receipts.
The reviewer ran no workload and adds no publication prerequisite. This review
preserves the prepared all-noise gate and grants **0 seconds / 0 segments**.
