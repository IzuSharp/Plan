# Perf-01 final build binding

The final Linux x64 build uses product commit
`0715ffb6376b1ae08259ad7e2cb30ff0320d83e7`, tree
`cd0a6022e0115c22f133aedf6c801d9244640523`, and actual candidate package version
`0.1.0-perf01.after.3`. All nine producers completed successfully between
2026-11-20 07:07:45.509242 and 07:17:02.217218 UTC. The build execution receipt
SHA-256 is `b7cb16c833fc2197b74515ffc7d5dbdde9724d9398e5839e5716a0dc5735d594`.

[The numerical checklist](public-checklist.json) records the actual package,
native-library, application-consumer and manifest hashes, the frozen five-group
loads and their resource/error limits. Its SHA-256 is
`e8e1de83307947317c3b95f726f03cc621b13c3321f368bb09d109e093f64b3a`.
The measured application inputs and the original drivers remain unchanged.
The protocol client is the same original independent client binary used before.

The offline preparation validated actual bytes and before-manifest references;
its five-group binding SHA-256 is
`646bed58f9564c36bb66f2577855c8f4185fc1b3be32af47ef1ad59caab7ffd9`.
Publishing and fetching this checklist is a prerequisite of the existing
long-run supervisor. This record does not claim an after measurement or grant
any effective-load duration. The five already accepted before groups remain
attached to their original binaries and configurations.

| Group | Planned arrival/s | Concurrency / workers | Effective-load target, seconds |
| --- | ---: | ---: | ---: |
| PostgreSQL | 144 | 16 | 1802 |
| SQLite | 40 | 16 | 1802 |
| HTTP | 500 | 64 | 1802 |
| gRPC | 115 | 64 | 1802 |
| Compression / decompression | 192 | 2 | 1802 |

The mixed HTTP/gRPC paths, expected cancellation/deadline probes, database
durability settings and codec's 32 separately counted partitions retain the
accepted before definitions. Warm-up, recovery and idle observation are outside
the credited effective-load interval. gRPC remains identity-only; standalone
codec measurements do not establish protocol compression gains.

This public record contains project identities and synthetic-load configuration.
Local operational bindings and process-control logs are excluded. The checked-in
record has repository-history retention; no CI-artifact expiry applies to it.
