# PG-codec-B: observed repeated configuration parsing

The complete source-scope control is
`measurements/pg-codec-b-baseline-02/completion.json` and `results.json`.
Twelve separate real PostgreSQL / Release Native AOT processes each execute one
measured business after eight warmup operations. The original workload source,
SQL, DTOs, generated readers, digest validation and ownership drain are retained;
diagnostic snapshot calls bracket the normal workload start/completion gate.
This is allocation/call attribution only, with no ordinary latency or CPU credit.

## Measured result, identical counts/bytes in both rounds

| Original business | Decimal outputs | Config JSON parses inside decode | Codec validation calls inside decode | Entire decimal decode malloc/calloc calls | Requested bytes in decimal decode |
| --- | ---: | ---: | ---: | ---: | ---: |
| numeric32 (Int64 negative control) | 0 | 0 | 0 | 0 | 0 |
| money1 | 1 | 4 | 3 | 48 | 1,136 |
| money32 | 32 | 128 | 96 | 1,536 | 36,352 |
| money1000 | 1,000 | 4,000 | 3,000 | 48,000 | 1,135,980 |
| wide32 | 32 | 128 | 96 | 1,536 | 36,352 |
| customer-totals (9 groups) | 9 | 36 | 27 | 432 | 10,242 |

For money1000, the four JSON parse scopes per value account for **40,000 calls /
860,000 requested bytes**. The three Codec validation scopes account for
**36,000 calls / 885,000 bytes**, and the separate numeric range-configuration
scope accounts for **11,000 calls / 247,000 bytes**. These are nested inclusive
scopes; do not sum parse+validation totals. The latter two disjoint configuration
validation/range scopes predict 47,000 removable calls and 1,132,000 requested
bytes if the stack parser succeeds. This is a testable prediction, not a claimed
candidate result. The residual decimal conversion allocation must be measured
separately after the candidate.

All measured requests completed with no business errors, retries or oracle
failures; native ownership returned to zero. Each scope had equal cumulative
entry/exit counts both before and after its request. Counters are monotonic and
no scoped allocator calls failed. Raw cumulative counters, process ID and
monotonic snapshot boundaries are in each `*.json.codec.json`, beside the ordinary
workload receipt and command record.

## Actual call chain and falsified first assumption

`postgres_decode_into` first calls `check_profile -> Codec::validate`. The next
OID compatibility check calls `postgres_compatible -> postgres_oid ->
check_profile -> Codec::validate`. Canonical value validation calls
`validate_scalar -> Codec::validate`, then parses the configuration once again
to read precision/scale. Thus each successful nonnull decimal output parses the
same configuration **four** times and validates it **three** times.

The initial three-parse source prediction missed the OID helper. The first run
is preserved at `measurements/pg-codec-b-baseline-01`: numeric negative control
passed, money1 produced the correct business result, and the three-parse
hypothesis assertion failed on actual four-parse evidence. It is not a product
correctness failure or discarded data. The corrected second run is complete.

The original ordinary ELF SHA-256
`1909e79db9265f9da2d2b22073090e03c06989fcd4af06ba656a493bce047fed`
contains `postgres_decode_into` at 0x9d410, `check_profile` at 0x9acd0,
`Codec::validate` at 0x30480, `validate_scalar` at 0x3a190 and `parse_json` at
0x30bf0. Retained actual call instructions bind this source path. Diagnostic
producer, package, native image, AOT ELF and generated code have their separate
identities under `builds/pg-codec-b-diagnostic-postgresql` and
`consumers/pg-codec-b-diagnostic-postgresql/korda-workload`.

## Measurement boundary and limitation

The independent shim attributes successful public glibc malloc/calloc/realloc
calls only while the current thread is in a source scope. It has no heap address
table, live-byte or free accounting; these requested byte totals do not describe
peak RSS, retained storage or allocator metadata. Other threads' unrelated
allocations are excluded by TLS scope masks. `scope-test` independently validates
nesting, conditional nested attribution, thread isolation, outside-scope negative
control and snapshot layout. Existing broad native allocation profiles remain
the process-level heap evidence; these local counters add call-site attribution.

This finding does not explain the Int64/string 1000-row phase CPU gap. That
business contains no configured decimal. Its execution/lifetime/scheduling
costs require their own observations.

## Selected isolated experiment

The first candidate is **decimal configuration only**. Use exact canonical
primitive parsing of all accepted precision/scale combinations; preserve the
existing invalid-input diagnostic path and all existing validation locations,
NULL/OID/profile/shape checks, decimal flags, 96-bit coefficient, scale/overflow
checks and error ordering. Do not cache the mutable Codec object. Do not change
the numeric binary conversion itself in the same experiment. FixedScaleMoney
remains unchanged because its per-source resource control is not yet established.

Before any ordinary performance claim: run all 463 valid precision/scale
configurations, malformed configuration and mutation/error precedence controls,
existing scalar/contracts/provider suites, actual independent provider packages
and AOT consumers; repeat the diagnostic scope control on the candidate, then
let the parent run ordinary serial interleaved A/B.
