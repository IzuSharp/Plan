# Executed final v5 database noise freezes

Both reviewed extraction scripts exited **0** on CPU8 between **13:10:14.014705 and 13:10:20.116721 UTC on 2026-11-19**. Root explicitly released an exclusive non-timing window after final DB calibration and waited until completion before starting protocol calibration. No application workload, build or test ran in these commands. Exact argv, script hashes, timestamps, log hashes, interpreter identity and output hashes are preserved in `receipt.json`; `00.log` and `01.log` are verbatim output.

The source is the clean detached ce2 DB timing checkout, with the unchanged A21 `dfb57cf6…` and original reader `8034692b…`. This is distinct from the later post-run-only protocol verifier. No input hash equality is weakened. The final three before-only confirmation processes are used exactly as predeclared; older v4 attempts are excluded.

| Provider | Anchor (/s) | Paired long (/s) | Mixed band (ms) | Cycle band (ms) | Page band (ms) | Frozen receipt SHA-256 |
|---|---:|---:|---:|---:|---:|---|
| sqlite | 50 | 40 | 12.531994 | 22.679202 | 2.378022 | `c3cd91e963ff3390d58821487a628cf7c311d367f085eb63b13437fca034ec68` |
| postgresql | 180 | 144 | 2.499892 | 3.167865 | 1.831796 | `5bb25871bdd4863158f6b0aa0791b321b8ae147f122ec4ff9400c5b1106f7585` |

The retained `sqlite-noise.json` and `postgresql-noise.json` are exact copies of the newly created original receipts under `ROOT/perf01-evidence/noise/`. Each records the complete three-process means/sums/counts, actual application identities and measurement windows, source/configuration and hashes of every consumed summary, frozen plan, dataset and full observation. These receipts are small metadata, not replacements for the full raw ledgers. Raw evidence remains at the absolute paths they pin.

Absolute noise is the larger of 1,000 ns and the before-process mean range; relative noise is zero. The existing A21 comparison later consumes fresh matched before/after or before/direct process means. No after observations or product runtime edits influenced these bands. A mean allowance is not a confidence interval for p99, and three replicates have limited precision. Failed calibration cells remain separately preserved.

All output hashes were read back after creation and match the execution receipt. Repository copies are retained with Plan Git history; local raw scratch retention is not guaranteed until root publishes and verifies the full evidence artifact. This record grants no 30-minute credit and does not claim before/after performance improvement.
