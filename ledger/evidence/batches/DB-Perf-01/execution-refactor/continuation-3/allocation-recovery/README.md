# Allocation diagnostic recovery inputs

[receipt.json](receipt.json) is the unchanged original recovery receipt. It
records two families of five compilation attempts each. The successful fifth
attempts produced actual Native AOT executables for the ordinary before-SQLite
and Dapper.AOT-SQLite query-phase consumers. These were compilation-only
observations at this recovery checkpoint. Subsequent executions belong to
separate records; no timing or allocation result is inferred here.

| Attempt in each family | Retained outcome |
| --- | --- |
| 01 | Python parser failure before output creation: unmatched parenthesis |
| 02 | Overbroad output-directory guard falsely rejected an external consumer |
| 03 | Tool incorrectly compared raw signed NuGet archive SHA-512 to NuGet contentHash; exact failed builder source recovered and hash-verified |
| 04 | Offline feed omitted SDK downloadDependencies; exact failed builder source recovered and hash-verified |
| 05 | Real generator compilation and Native AOT publish both succeeded; executable was not run by the builder |

The original logs, output receipts and successful original/instrumented
generated sources are under `logs/` and `consumers/`. Hash-named builder sources
match the corresponding failed/successful receipt exactly. Attempts01/02
retain their original preflight failures; they have no output receipt or
hash-bound reconstructed prior source.

The adopted working builder was developed in local commit54361c2; its bytes
are included in [frozen public0f3816c](https://github.com/IzuSharp/Korda/tree/0f3816c4006488821f40afde91bbbd717d57ccd6/benchmarks/db-perf/allocation-diagnostics) and preserved under
[tool-sources/public-0f3816c](tool-sources/public-0f3816c/README.md).
Its SHA-256 is
`9697deb087e2a0d036dee4698e1c9bb7bfe6454c79585ee2b2eac77abc534932`;
the observer SHA-256 is
`3cd87e22b476fac01bb3933b0c1949174d4c5816640189e76faf772e88a5923b`.
Local b82e4d1/660ddd8 added automatic provenance-source copying after the two
successful builds. They are mentioned in the unchanged recovery receipt but
were **not adopted into public0f**. Archival copies here preserve the successful
builder's exact source without changing that product freeze.

The original standard external consumers must first be recovered with their
locked packages and asset graphs. The [ordinary consumer archive](../consumer-inputs.README.md)
preserves their sources and generated outputs, while package/binary hashes stay
in the original receipts. Then build fresh external overlay directories with
the tool's documented `--consumer` and `--output` arguments. The exact generate
and publish argv for both successful builds are in their
`allocation-build-receipt.json`. The tool's [README](tool-sources/public-0f3816c/README.md)
documents separate optional local execution and all result-scope limits.

The first compilation runs the actual generator against the instrumented source
so Dapper interceptor locations remain valid. The second compiles the captured
generated sources with only mapper bodies instrumented. SQL, parameters,
column matching, result shape and result oracle are retained. Korda's shipped
native library is checked byte-for-byte against the ordinary input consumer.

The generated mapper scope includes DTOs, string values and any codec/driver
scratch inside that body. List constructor/Add scopes and whole-process
allocation/GC windows are reported separately. `FrameworkOnlyBytes` remains
null. The executable and JSON explicitly set `TimingCredit=false`; instrumented
times must not be substituted for ordinary production measurements.
