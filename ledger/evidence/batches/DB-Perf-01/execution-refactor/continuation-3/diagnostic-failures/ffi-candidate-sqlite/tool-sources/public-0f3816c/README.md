# Local cursor ABI diagnostic

`build.py --consumer <external-query-phases-app> --source <matching-Korda-source> --output <fresh-folder>`
builds a separate Native AOT consumer and a Linux/glibc `LD_PRELOAD` probe. Use the
returned `runEnvironment` only for this diagnostic executable. Run the ordinary
1/100/1000-row arguments against the same dedicated local database.

The probe intercepts actual `dlsym` resolutions of the bound database C ABI and
forwards every call with the original exact signature, callback record and
owner. It counts managed-to-native calls and `NW_PENDING` returns per symbol.
The phase consumer captures counters outside each operation window. The native
provider bytes and package stay unchanged and are rehashed by the builder.
Calls to the diagnostic count export itself can be excluded when summing the
business execution path. Native-to-managed notifications are not intercepted;
the public Host contract tests count their accepted/ready/taken generations.

For PostgreSQL, the probe additionally counts actual provider-originated `poll`
calls, timeout/error returns and their elapsed time. These are socket waits,
not physical round trips or counts of protocol messages: buffered messages may
need no `poll`, while one required response can need several. Pair them with the
ordinary receipt's SQL execution/send counters and the source-verified
Parse/Describe/Sync and Execute/ReadyForQuery boundaries.

**No instrumented timing or allocation receives acceptance credit.** Generated
shim C, original/overlay managed source hashes, ABI inventories, compiler,
package, actual provider, executable and logs are retained. A separate ordinary
consumer supplies performance results. This tool has no CI registration and
must only run on the local Linux measurement machine.
