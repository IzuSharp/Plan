# Perf-01 baseline B06 functional verification

The actual scoped verifier completed at2026-11-19T11:26:22Z with exit0.
All24 commands passed, including locked native streaming tests and fixture,
actual SQLite and PostgreSQL18.0 providers, Release/JIT, Linux Native AOT,
compiled API/XML, formatting and both component samples. The preserved command
and source manifests bind the exact inputs and outputs; these are functional
checks, not performance samples or long-duration credit.

The integration source was a723bac2274ea760ef5afbe025edbee32589b9ae. Runtime
implementation remained ea5fa528035d025bd7a28698ee7c71194432236c; only Perf-01
measurement/test sources had changed. The scoped native test bridge is a test
artifact, not the B24 package library used in the performance cohort.

Root invoked the exact Python3.12.14 interpreter under taskset CPUs2,3 after
sourcing ROOT/perf01-toolchain/env.sh, with --postgres-bin pointing to the
locked18.0 installation and --design-root pointing to pinned Designc62cdb8a.
The private PostgreSQL process exited through the verifier's normal shutdown.
Original top-level JSON/log files were copied and read back byte-for-byte as
listed in preservation.json. Binary archives/database data are omitted and
remain reconstructible using the exact commands.
