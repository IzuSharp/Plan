# Codec generator invalidity and DB provenance-verifier failure

These two actual failures give no completed matrix, diagnostic workload,
capacity or long-duration credit. Product source and successful producer
outputs remain unchanged. Original controls, logs and raw measurements remain
in the measurement workspace. The adjacent JSON preserves exact values/hashes.

## Codec: successful operations in an invalid generator sample

The final003 codec stage stopped at15:54:37.901261 UTC on its first managed
ZLibStream cell. The preceding before/final/direct Rust cells exited0 and
retired owned/adopted processes; their complete resource-reader eligibility
is not inferred from the small owner controls.

The managed target exited0. All16,095 measured, 2,695 warmup and12 recovery
operations succeeded. Its only invalid reason is `generator_dispatch_lag`:
the original driver rejects dispatch later than the frozen100ms limit. The
sample stays invalid despite successful content checks/recovery and arrival
p99 of168.371301ms. No codec correctness failure or target crash was observed.
The failed owner SHA-256 is
`332900863bae682a32301643eae4c57755d3eb2323115ed3359586b6be7059bf`.

The unchanged full codec reader refuses generator-invalid inputs, including
optional managed inputs. The remaining20 cells need an explicit continuation.
A separately named core-only report may use that reader's existing optional
managed omission, preserving all three before/final/direct processes. It must
retain the invalid managed observation and cannot claim a complete managed W1
comparison. No replacement process has run at this checkpoint. Managed codec
results remain valid-corpus call-only because strict trailing-data and ownership
semantics differ from NativeWeave/direct miniz.

## DB: zero-producer verification failed, original builds retained

`verify-before-binding-001` ran from16:00:37.276721 through16:00:38.415475 UTC.
The exact package-folder spelling check passed. The next check incorrectly
equated the signed `Microsoft.DotNet.ILCompiler/11.0.0` package's content hash
with the entire archive SHA-512. Its receipt remains failed, SHA-256
`5c0274a0091b4cf1d54daa03cb8cc27ef8418eae8008837298087f90c1a79db7`.
No producer was rerun. The original interrupted owner and the separate failed
owner containing two successfully completed consumers also remain unchanged.

An idle-window diagnosis read exactly22 referenced archives, 29,769,171 bytes.
All64 package occurrences match raw SHA-512 sidecars and NuGet metadata content
hashes. The42 occurrences with saved reference-build archive/lock snapshots
match those snapshots; the22 observer occurrences have no separate saved
reference snapshot and are explicitly N/A for that check. The observer uses the
same22 already checked archive files. All45 NativeWeave occurrences match the
selected feed; the19 external occurrences are N/A for that feed check.

Exactly seven signed Microsoft packages have distinct archive/content hashes.
The fifteen actually resolved unsigned NativeWeave packages have equal hashes
and match their selected feed. The seventeen selected feed archives are a
different population from fifteen actual NativeWeave resolutions. Both hash
types and exact package identities remain in the public JSON. There is no
command/environment catalog or TLS material in this bundle.

## Primary source explanation and limits

The actual NuGet source reads distinguish these hashes:

- [PackageExtractor](https://source.dot.net/NuGet.Packaging/PackageExtractor.cs.html),
  `InstallFromSourceAsync`, lines504–518 and814–828, stores raw archive SHA-512
  separately from the unsigned-content hash in `.nupkg.metadata`.
- [PackageArchiveReader](https://source.dot.net/NuGet.Packaging/PackageArchiveReader.cs.html),
  `GetContentHash`, lines488–512, uses a distinct signed-content path.
- [SignedPackageArchiveUtility](https://source.dot.net/NuGet.Packaging/Signing/Archive/SignedPackageArchiveUtility.cs.html),
  `GetPackageContentHash`, lines551–585, omits the signature entry and adjusts
  ZIP offsets when hashing content.

The viewed site's Web Access links identify dotnet/dotnet commit
`94b6099229a6b7490015cb2e208b34a80e4b55ea`. This explains the semantics; it
is not asserted to be the exact source snapshot of locked SDK11.0.100. No NuGet
implementation was imported, package rewritten, SDK upgraded or signature gate
bypassed. A prospective recovery can bind the seven exact observed external
tuples while retaining actual archive/source checks. This checkpoint does not
claim that such recovery has executed or passed.

These public numbers and the manifest remain in Plan Git history. Complete raw
operational evidence remains local; no remote full-raw archive is claimed.
[The fixed workload configuration](../../reproduction/workloads-001/README.md)
and the original acceptance thresholds remain unchanged.
