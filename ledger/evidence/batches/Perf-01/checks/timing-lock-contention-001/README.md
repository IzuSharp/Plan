# Perf-01 pre-load timing-lock contention

The first final protocol calibration attempt, `before-http-v5`, failed at
**2026-11-19 13:11:06.535951 UTC**. Preparation exited zero, but the run process
exited one when `run.py:540` requested nonblocking exclusive `flock` on the
existing timing lock. It raised `BlockingIOError` / errno 11 before entering
`run_cell`. The prepared cell has no execution subtree or final result. Its
planned 30-second, 8/s point started no application workload and receives **zero
measurement or long-duration credit**.

The integration owner's later direct probe acquired and released that original
lock successfully at **13:13:40.924060 UTC**. The lock remained device 27,
inode **3301407**. These observations establish temporary contention followed
by availability. The holder's identity was not exposed in the available
per-exec PID namespace. No descriptor-inheritance, particular process, or
product defect is established as its cause.

No lock file was deleted or replaced, no process was signalled, and no runtime
or driver code was changed for this incident. The failed attempt remains
immutable. Root began a separate `v5r1` attempt at **13:14:33.288914 UTC** using
the same controller and arguments apart from its fresh attempt label. That
start is an owner-reported fact, not a completion or validity claim.

The four accompanying files are exact copies of the original small diagnostic
receipt, failed controller and logs. Their source and copied bytes were
SHA-256 checked on CPU 8; no test, workload, build, lock probe or process action
was performed by the documenting reviewer.

| File | SHA-256 |
|---|---|
| `receipt.json` | `93d742e93c8cbae0562cdbecc3d4e5ba51441187058718865d02a18f56306bc1` |
| `controller.json` | `2a5632d9be2fbdbf99575422f9bae4ad024f29d820108a22a7aedc381d61d153` |
| `00-run.log` | `8aec45a7de0b3aa259554d55d4357deda71b1a215c6b281ad31a82e0cffed132` |
| `00-prepare.log` | `7576f2aaee30eb5794fcfcbd4d59734a0368ff5a1ebe8ab27e44445a6db232bf` |

Original locations are retained verbatim in `receipt.json`. The failed controller
records its missing-result error and the prepare/run exit codes. This record
must remain separate from any eventual `v5r1` selection and final paired results.
