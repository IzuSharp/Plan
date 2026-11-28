# DB-Scope-01 — database product scope plan

The selected product is a strongly typed Fluent ORM for PostgreSQL and SQLite,
usable from ordinary C# applications and Native AOT. At this historical stage
Rust SeaQuery/SQLx supplied execution; DB-CPP-01 subsequently replaced the native
implementation while preserving behavior.

Retain Database Host, source/pool/session ownership, transactions, migrations,
parameters, typed queries, static model/DTO mapping, relations/CRUD, streaming,
cancellation, errors, disposal and independently packaged native assets.
Remove owned HTTP/gRPC/MCP servers and protocol wrappers, unrelated engines,
HelloWorld/scaffold products and orphan tooling. Preserve database tests from
mixed services. Application-selected hosting remains outside the library.

The sequence was scope/plan, Design, implementation pruning, Linux regression,
external consumers, independent review and normal delivery. Seven phases and
fourteen acceptance claims were recorded complete. No performance campaign,
additional ORM feature or public package release was accepted in this batch.
See the [final Linux result](results/linux-acceptance-summary.md).
