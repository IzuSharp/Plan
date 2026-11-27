# frame-pool08: actual ordinary PostgreSQL ELF readback

The already completed27-command capture confirms the selected pool and ownership paths in the actual ordinary PostgreSQL Native AOT consumer. This short report only analyzes those saved instructions. No additional ELF scan, build, database process, sampling or timing was run, and it has no performance credit.

## Actual identities

| Identity | ownership05 baseline | frame-pool08 candidate |
| --- | --- | --- |
| Source | `69b2383dadc280f1a81de592592a1442069eed0c` | `13b25de2b67d858d8b6524f615e3a84b4c541817` |
| ELF SHA256 | `b9e5407c6eadf09220655e41188c13fc746cd14e02542703a4c1f432eaf3799b` | `51a57c0fdb443537bd12abed678e06115ad8336223f63ececab4b230d756b3b1` |
| DBG SHA256 | `7cf9f56ca4cd8e34973b3e957efb7ba948600c6e6b29c1e14e8eaad856eba4b4` | `a38b75dd846f3ccaa6127bfa0ca6a8ec21a3d7fd4e1608ce36230ab1ecccaf3a` |
| Matching ELF/DBG BuildID | `6899b2a49481bc8cfb856dbb7ed3bc2eb3450159` | `bbfed7cb3f7e58295ce64e7b1b5ebaa8a492f234` |

Both bind native SHA256 `edbab539bcae6424ff693cbb8fa8c69d5bb2aa16e20ea8aa84f6d93505190ccf`. Saved capture checks verify source/build/binding/image identities before and after reading. The [capture receipt](actual-elf-postgresql-01/receipt.json), SHA256 `1f216caacddaf3d48cfad4ba754e6ae3082dd411d84bd12428f74d7bcc4fb153`, retains commands, selected symbols, source mappings and bounded instruction records.

## Confirmed finite paths

| Question | Actual PG candidate evidence | Interpretation |
| --- | --- | --- |
| Rental eligibility and ownership | Encode subtracts4097 at `0x133b55`, compares unsigned to61439 at `0x133b5b`; Rent slot0x30 at `0x133b9a`, caller byref assignment at `0x133ba6`. | Only eligible4097–65536 frames rent; ownership is recorded before subsequent frame writes/sidecars. |
| Logical length | Encode result stores size at `0x134130`; Seal loads/checks it at `0x1342dc` / `0x1342fb`, then passes logical length to BindingChecks.View at `0x134436` / `0x134439` before Compile at `0x1344d0`. | Physical pool capacity is not sent as command length. Matching source return is line129; submission is lines150/156. |
| Small successful stack path | Single-root success branch `0x1342a5` skips Encode. Finally null checks `0x134662` and `0x134773` precede pool access. | Selected successful stack path avoids pool initialization. Candidate still has different prologue/finally instructions; this does not prove zero added CPU. |
| Pool bounds | `.cctor` loads65536 at `0x138a73` and4 at `0x138a78`, then calls ConfigurableArrayPool constructor at `0x138a7d`. | Actual ordinary code contains the intended private bounded pool. Cold construction still requires work. |
| Clear on both returns | Normal return loads1 at `0x134686` before slot0x38 call `0x13468e`; exceptional return repeats this at `0x13479c` / `0x1347a4`. Concrete pool Return calls System.Array.Clear at `0x26d1bc`, then Bucket.Return at `0x26d1d8`. | `clearArray: true` survives ordinary lowering. PG Array.Clear body was not additionally disassembled; the direct edge is bound here. |

The virtual slot targets were not read from a running process. Their relationship to ConfigurableArrayPool follows the actual constructor and matching committed source; no dynamic target observation is claimed. SQLite-specific hydrated addresses are not transferred to PostgreSQL. Pool Rent/Return and bucket bodies are saved for review, but their hit rate, allocation frequency and contention are unknown from this static capture.

Both committed ordinary Query.Binding source and defined-symbol searches contain none of `FrameRentalLocalFault`, `FrameRentalFaultPoint` or `FrameRentalResourceMetrics`. Normal SealFrameCache is product code. Exact-symbol absence alone is bounded by inlining/trimming, with actual source/build bindings providing the additional evidence.

There is no whole-binary equality claim, no CPU derived from instruction counts, and no end-to-end result in this report. Root's subsequently completed ordinary12 result analysis remains a separate evidence source.
