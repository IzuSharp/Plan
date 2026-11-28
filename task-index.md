# Task index

The graphs retain historical IDs, recorded states and dependencies. Later batch
results are in [CURRENT-PHASE.md](CURRENT-PHASE.md); these task definitions do not
authorize resuming implementation.

The separate [Korda.Orm implementation plan](docs/korda-orm/README.md) owns its
`ORM-*` task identities and independent graph. Its planned candidates do not
change the historical states or dependencies listed below.

## Research

| ID | Task | Recorded state | Packet |
| --- | --- | --- | --- |
| R01 | Stable Toolchains and Modern Language Mechanisms | accepted | [R01](research-tasks/R01.md) |
| R02 | Native AOT, Trimming, and Platform Support | accepted | [R02](research-tasks/R02.md) |
| R03 | C ABI, Layout, and Version Negotiation | accepted | [R03](research-tasks/R03.md) |
| R04 | P/Invoke, Callback Entry Points, and FFI Call Cost | accepted | [R04](research-tasks/R04.md) |
| R05 | Binding Generators and Contract Description Sources | accepted | [R05](research-tasks/R05.md) |
| R06 | Roslyn Incremental Generation and Analyzers | accepted | [R06](research-tasks/R06.md) |
| R07 | Handles, Ownership, GC, and Parent-Child Resources | accepted | [R07](research-tasks/R07.md) |
| R08 | Callback Unregistration, Reentrancy, and Release Races | accepted | [R08](research-tasks/R08.md) |
| R09 | Async, Cancellation, and Completion State Machines | accepted | [R09](research-tasks/R09.md) |
| R10 | Buffers, Pinning, Batching, and Data Transfer | accepted | [R10](research-tasks/R10.md) |
| R11 | Errors, Panics, Exceptions, and Fault Isolation | accepted | [R11](research-tasks/R11.md) |
| R12 | Concurrency, Executors, Thread Affinity, and Shutdown | accepted | [R12](research-tasks/R12.md) |
| R13 | MSBuild/Cargo, Linking, and Target Platforms | accepted | [R13](research-tasks/R13.md) |
| R14 | Packaging, Compatibility, Independent Releases, and Provenance | accepted | [R14](research-tasks/R14.md) |
| R15 | Formal Methods and Concurrency Proof Obligations | accepted | [R15](research-tasks/R15.md) |
| R16 | Differential, Property, Fuzz, and Fault Testing | accepted | [R16](research-tasks/R16.md) |
| R17 | End-to-End Performance, Memory, and Development Cost | accepted | [R17](research-tasks/R17.md) |
| R18 | Capability-Based Engine Integration and Generality | accepted | [R18](research-tasks/R18.md) |
| R19 | PostgreSQL Drivers and Pure C# Baselines | accepted | [R19](research-tasks/R19.md) |
| R20 | SQLite Adaptation, Concurrency, and Threading Restrictions | accepted | [R20](research-tasks/R20.md) |
| R21 | Connection Pools, Transactions, Cancellation, and Recovery | accepted | [R21](research-tasks/R21.md) |
| R22 | Type Mapping, Batched Streams, and Schema Evolution | accepted | [R22](research-tasks/R22.md) |
| R23 | Strongly Typed Queries, Expression Boundaries, and Static Capture | accepted | [R23](research-tasks/R23.md) |
| R24 | SQL Semantics, Relational Algebra, and Parameter Safety | accepted | [R24](research-tasks/R24.md) |
| R25 | ORM Features, Tracking, and Comparison of Existing Solutions | accepted | [R25](research-tasks/R25.md) |
| R26 | Kestrel and Pure C# AOT Server Baselines | accepted | [R26](research-tasks/R26.md) |
| R27 | Rust Networking Engines and C# Handler Boundaries | accepted | [R27](research-tasks/R27.md) |
| R28 | gRPC, MCP, TLS, and Protocol Adaptation | accepted | [R28](research-tasks/R28.md) |
| R29 | Request Streams, Backpressure, Timeouts, and Graceful Shutdown | accepted | [R29](research-tasks/R29.md) |
| R30 | Observability, Diagnostic Correlation, and Cost | accepted | [R30](research-tasks/R30.md) |
| R31 | Database + Server Reference Application and Fault Recovery | accepted | [R31](research-tasks/R31.md) |
| R32 | Desktop GUI/GPU and Thread-Affinity Extensions | accepted | [R32](research-tasks/R32.md) |
| R33 | iOS/Android, Static Linking, and Platform Lifecycles | accepted | [R33](research-tasks/R33.md) |
| R34 | Boundary Security, Input Validation, and Resource Abuse | accepted | [R34](research-tasks/R34.md) |

## Documentation

| ID | Task | Recorded state | Packet |
| --- | --- | --- | --- |
| D01 | Toolchain, AOT, and Platform Specification | accepted | [D01](documentation-tasks/D01.md) |
| D02 | ABI and Type Layout Contract | accepted | [D02](documentation-tasks/D02.md) |
| D03 | Binding IR, Generator, and Analyzer Specification | accepted | [D03](documentation-tasks/D03.md) |
| D04 | Ownership and Resource Lifetime Contract | accepted | [D04](documentation-tasks/D04.md) |
| D05 | Callback Registration, Revocation, and Quiescence Contract | accepted | [D05](documentation-tasks/D05.md) |
| D06 | Async Completion and Cancellation Contract | accepted | [D06](documentation-tasks/D06.md) |
| D07 | Buffer, Transfer, and Memory Contract | accepted | [D07](documentation-tasks/D07.md) |
| D08 | Error, Panic, and Exception Boundary Contract | accepted | [D08](documentation-tasks/D08.md) |
| D09 | Concurrency, Runtime, and Shutdown Specification | accepted | [D09](documentation-tasks/D09.md) |
| D10 | Build, Packaging, Versioning, and Provenance Specification | accepted | [D10](documentation-tasks/D10.md) |
| D11 | Engine Integration Specification and Two-Module Verification | accepted | [D11](documentation-tasks/D11.md) |
| D12 | Proof Obligations and Actual Verification Specification | accepted | [D12](documentation-tasks/D12.md) |
| D13 | Performance, Memory, and Developer Experience Methodology | accepted | [D13](documentation-tasks/D13.md) |
| D14 | Database Driver Capabilities and Adaptation Specification | accepted | [D14](documentation-tasks/D14.md) |
| D15 | Connection Pool, Transaction, and Recovery Contract | accepted | [D15](documentation-tasks/D15.md) |
| D16 | Native Query Semantics and ORM Scope | accepted | [D16](documentation-tasks/D16.md) |
| D17 | AOT Query Capture, Generation, and Safe Dynamic APIs | accepted | [D17](documentation-tasks/D17.md) |
| D18 | Server Lifecycle and Adaptation Specification | accepted | [D18](documentation-tasks/D18.md) |
| D19 | Protocol, Observability, and Security Specification | accepted | [D19](documentation-tasks/D19.md) |
| D20 | Production-Grade Reference Application and Acceptance Design | accepted | [D20](documentation-tasks/D20.md) |
| D21 | Extension Boundaries for Future Engines and Mobile Platforms | accepted | [D21](documentation-tasks/D21.md) |
| D22 | Preparation of ABI, Memory, and Resource Development Tasks | accepted | [D22](documentation-tasks/D22.md) |
| D23 | Preparation of Generator and Analyzer Development Tasks | accepted | [D23](documentation-tasks/D23.md) |
| D24 | Preparation of Callback, Async, and Runtime Tasks | accepted | [D24](documentation-tasks/D24.md) |
| D25 | Preparation of Build, Packaging, and Independent Release Tasks | accepted | [D25](documentation-tasks/D25.md) |
| D26 | Preparation of Engine, Proof, Testing, and Benchmark Tasks | accepted | [D26](documentation-tasks/D26.md) |
| D27 | Preparation of Complete Database Implementation Tasks | accepted | [D27](documentation-tasks/D27.md) |
| D28 | Preparation of Strongly Typed Fluent and Native ORM Implementation Tasks | accepted | [D28](documentation-tasks/D28.md) |
| D29 | Preparation of Server and Protocol Implementation Tasks | accepted | [D29](documentation-tasks/D29.md) |
| D30 | Preparation of End-to-End, Long-Running-Load, and Domain Release Tasks | accepted | [D30](documentation-tasks/D30.md) |
| D31 | Global Traceability, Version Compatibility, and Future Engine Task Specification | accepted | [D31](documentation-tasks/D31.md) |
| D32 | Independent Cross-Review and Delivery Readiness Review | accepted | [D32](documentation-tasks/D32.md) |

## Delivery

| ID | Task | Recorded state | Packet |
| --- | --- | --- | --- |
| A01 | ABI Descriptions, Layout Probes, and Version Reads | planned_candidate | [A01](tasks/A01.md) |
| A02 | Status, Capability, and Compatibility Negotiation Entry Points | planned_candidate | [A02](tasks/A02.md) |
| A03 | Synchronous Handles and Resource Leases | planned_candidate | [A03](tasks/A03.md) |
| A04 | Owned Buffers and Async Leases | planned_candidate | [A04](tasks/A04.md) |
| A05 | Controlled Error and Panic Conversion Boundaries | planned_candidate | [A05](tasks/A05.md) |
| A06 | Callback Registration, Revocation, and Draining | planned_candidate | [A06](tasks/A06.md) |
| A07 | Task Async Bridge and Cancellation State Machine | planned_candidate | [A07](tasks/A07.md) |
| A08 | Optional Executors, Capacity, and Shutdown | planned_candidate | [A08](tasks/A08.md) |
| A09 | Binding Contract IR and Input Validation | planned_candidate | [A09](tasks/A09.md) |
| A10 | C# LibraryImport Binding Emission | planned_candidate | [A10](tasks/A10.md) |
| A11 | Rust Exports and ABI Consistency Checks | planned_candidate | [A11](tasks/A11.md) |
| A12 | ABI, Lifetime, and AOT Analyzers | planned_candidate | [A12](tasks/A12.md) |
| A13 | MSBuild and Cargo Reproducible Build Graph | planned_candidate | [A13](tasks/A13.md) |
| A14 | Linux Native Artifacts and AOT Package Verification | planned_candidate | [A14](tasks/A14.md) |
| A15 | Windows Native Artifacts and AOT Package Verification | planned_candidate | [A15](tasks/A15.md) |
| A16 | Independent NuGet/Crate Releases and Provenance Records | planned_candidate | [A16](tasks/A16.md) |
| A17 | Actual Synchronous Engine Integration Verification | planned_candidate | [A17](tasks/A17.md) |
| A18 | Actual Async Engine Integration Verification | planned_candidate | [A18](tasks/A18.md) |
| A19 | Executable Lifetime and Async Models | planned_candidate | [A19](tasks/A19.md) |
| A20 | Cross-Language ABI and Resource Property and Fuzz Testing | planned_candidate | [A20](tasks/A20.md) |
| A21 | Three-Path Benchmark and Resource Observation Tools | planned_candidate | [A21](tasks/A21.md) |
| A22 | ABI/API Upgrades and Compatibility Testing | planned_candidate | [A22](tasks/A22.md) |
| A23 | Thread-Affinity and Special-Platform Integration Probes | planned_candidate | [A23](tasks/A23.md) |
| A24 | Engine Integration Scaffolding and Conformance Entry Points | planned_candidate | [A24](tasks/A24.md) |
| B01 | Data Interfaces and Dynamic Metadata Boundaries | planned_candidate | [B01](tasks/B01.md) |
| B02 | Rust PostgreSQL Execution Adapter | planned_candidate | [B02](tasks/B02.md) |
| B03 | Rust SQLite Execution Adapter | planned_candidate | [B03](tasks/B03.md) |
| B04 | Required Rust Database Host and Lifecycle | planned_candidate | [B04](tasks/B04.md) |
| B05 | Rust Transactions, Pool Recovery, and Unknown | planned_candidate | [B05](tasks/B05.md) |
| B06 | Rust Bounded Result Batches and Streams | planned_candidate | [B06](tasks/B06.md) |
| B07 | Rust Fallible Parameter Codecs and Boundary Values | planned_candidate | [B07](tasks/B07.md) |
| B08 | Rust Migration Execution and Version Ledger | planned_candidate | [B08](tasks/B08.md) |
| B09 | Minimal Query Bindings and Metadata Definitions | planned_candidate | [B09](tasks/B09.md) |
| B10 | Optional Static Descriptor and DTO Generation | planned_candidate | [B10](tasks/B10.md) |
| B11 | Rust SeaQuery Deep Binding and Capability Checks | planned_candidate | [B11](tasks/B11.md) |
| B12 | Static C# DTO Materialization and Exception Cleanup | planned_candidate | [B12](tasks/B12.md) |
| B13 | Strongly Typed Runtime Fluent Native Queries | planned_candidate | [B13](tasks/B13.md) |
| B14 | Rust Explicit Relationship CRUD and Optimistic Concurrency | planned_candidate | [B14](tasks/B14.md) |
| B15 | C# Server Application, Strongly Typed Handlers, and Static Registration | planned_candidate | [B15](tasks/B15.md) |
| B16 | Bounded Streams and Budgets for Rust Body and C# Leases | planned_candidate | [B16](tasks/B16.md) |
| B17 | Required Rust Server Host and Handler Boundaries | planned_candidate | [B17](tasks/B17.md) |
| B18 | Native Tonic gRPC and C# Static Protobuf Mapping | planned_candidate | [B18](tasks/B18.md) |
| B19 | Native rmcp and C# Static Tools and JSON Mapping | planned_candidate | [B19](tasks/B19.md) |
| B20 | Diagnostic Correlation, Overall Deadlines, and Shutdown Coordination | planned_candidate | [B20](tasks/B20.md) |
| B21 | General-Purpose Idempotent Task Reference Service | planned_candidate | [B21](tasks/B21.md) |
| B22 | End-to-End Fault, Crash, and Long-Term Resource Verification | planned_candidate | [B22](tasks/B22.md) |
| B23 | Domain Full-Workload Performance and Memory Report | planned_candidate | [B23](tasks/B23.md) |
| B24 | Domain Compatibility Matrix, Independent Packages, and Release Acceptance | planned_candidate | [B24](tasks/B24.md) |
