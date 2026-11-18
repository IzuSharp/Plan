# B21 Linux independent source review

**Decision:** no open source-review blockers for Linux B21 integration validation. The complete packaged JIT/AOT/TLS/provider matrix is a separate in-progress acceptance gate.

## Exact scope and identity

- Integrated commit: `acb5be54f6a6af4e26048af6f98553a4ac7e41ad`.
- Integrated tree: `65b47ef06e247f5bd53e630ac13760811df0a2f2`.
- Implementation commit: `074b771c118afb37c0d0400726653a3d7dc84f14`; tree `9ad107873af6248cf3419dd6486d4f5e5326c252`.
- Application subtree: `77383c7ba506b420880f1b6eaf8fdc017fa30468`.
- Design pin: `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`.
- Source manifest: `source-manifest.json`; SHA-256 `5d5e067e5855d663d82e55cb81af8d84a90a7ccd5f7aae4f562f0bc5ef5b169d`; 20 tracked app/guide/sample files.

The manifest hashes exact Git blobs and excludes itself, these external review artifacts, generated output and private configuration. Every included file is byte-identical between the implementation commit and the integrated commit, and the checked-out files matched those blobs. Scope includes `src/Reference.TaskService/`, `docs/guides/reference-taskservice.md` and `samples/api/reference-taskservice/`.

Reviewer `/root/task07_requirements` did not author the implementation; `/root/b21_service` did. The reviewer authored the separate PostgreSQL test oracle, which is explicitly excluded from independent code approval below.

## Findings and dispositions

| ID | Disposition | Correction reviewed |
| --- | --- | --- |
| B21-R1 | Resolved | Upload binding becomes admitted only after BeginTransaction confirms. Positively pre-admission failures may release upload protection. Admitted transactions release markers only after the actual retirement join observes TransactionOutcome.RolledBack; Unknown and rollback-unconfirmed records remain protected. |
| B21-R2 | Resolved | Old inactive orphan parts and temporary manifests are eligible after the configured grace period. The unmanifested-part cleanup skips parts with a final manifest; ordinary manifest processing still applies, and complete hash-bearing uncertain manifests continue to protect blobs. Reference checks still precede immutable-blob deletion. |
| B21-R3 | Resolved | ProtectCommit writes and flushes .json.new, atomically moves it to the final identity, then fsyncs the directory before COMMIT. The caller enrolls protection before that call. Confirmed rollback removes complete/temporary records; old unpublished recovery temporaries receive grace cleanup. Complete uncertain records remain protected. |
| B21-R4 | Resolved | Bounded per-phase cursors persist in atomic maintenance.json and wrap on a short/empty page. Database scan positions advance only after confirmed commit. Protected entries are revisited on subsequent sweeps without blocking later work. The disk admission reserves 8 KiB for complete plus temporary progress metadata. |
| B21-R5 | Resolved | Thirty-two application protection slots are reserved before mutation DB admission and retained through native plus filesystem obligations. Completed tasks are removed. After handlers stop, the top-level finally joins sources and owned application cleanup on normal and exceptional exits before releasing owner.lock. HTTP paths retain their finite 100 ms session closure and do not retain RequestContext or DI scope. |
| B21-R6 | Resolved | Metadata publication/removal is synchronized with quota observation. The scan tolerates files already removed, while full active reservations conservatively cover not-yet-written upload bytes and metadata. It does not drop arbitrary I/O failures or weaken the disk bound. |

The detailed initial issue, severity, source paths and symbols are preserved in `review.json`. No open source findings remain.

## Correctness and ownership assessment

Authentication derives tenant/principal identity from configured opaque bearer credentials; clients do not supply trusted scopes. The application hashes fixed v1 field framing, stores explicit response versions and original serialized bytes, and uses the same native transaction for the operation result, business mutation and outbox. PostgreSQL reads the conflict winner in a separate typed statement; SQLite uses Immediate writer admission. Missing recovery rows remain unconfirmed.

Lists filter the tenant and use `(created_at,item_id)` with a unique tie-breaker. Cursors bind tenant/principal under HMAC. Operation recovery checks tenant/principal/semantic scope. Downloads first authorize a persisted attachment reference, so shared content hashes cannot grant cross-tenant access. Attachment binding checks the expected item version after idempotency lookup.

Outbox claims are bounded and finish their source transaction before external publication. Stable event IDs and a separate persistent consumer transaction distinguish duplicate delivery attempts from one durable effect. Attempt CAS prevents stale worker acknowledgments from overwriting newer claims. Failed/uncertain deliveries stay observable and protect their operation history.

Uploads use 32 KiB chunks and finite active/disk reservations without retaining a DB session during the client body. The file and relevant directories are flushed before DB reference binding. Immutable blobs, staging/recovery protection and grace collection preserve the selected local storage ordering. Unknown records are never deleted solely because a lookup is absent.

HTTP handlers use a finite 100 ms session-close wait. Native Pending owners remain retained, and the additional 32 application retirement obligations stay bounded after native permits release. The application captures transaction/blob identity, not an ended request context or DI scope. Process shutdown joins those obligations before relinquishing the blob-root lock. The application and linked examples consume packed APIs and static metadata; no managed substitute engine or new public/native ABI was introduced.

## Evidence actually inspected

The retained final-source result reports **21 passing focused regressions**. I checked all 9 recorded source hashes against the reviewed commit: **zero mismatches**. Canonical, minimum and advanced build logs each contain zero warnings and zero errors. The minimum sample records successful create, stable replay, typed listing, actual native SQLite/Server loading, absence of unused PostgreSQL assets and released shutdown owners.

The focused regression data includes scan progress beyond 100 protected records, preserved unresolved recovery, grace collection of four old temporary artifacts, and 16 concurrent stale attachment CAS failures whose known-rollback markers were retired before process exit. The reviewer inspected the retained author-run results and source binding; the reviewer did not rerun those author-owned checks. Evidence paths and SHA-256 values appear in `review.json`.

## Separately authored PostgreSQL oracle correction

The reviewer-authored oracle fix is `f43698ae74e2efbb97e55d41350abbdeddce9f1c`, integrated as `275ee8ffddbaa4db6f30f4f4420056d36b3a5776`. It is **not independent code review**. It removes an invalid `sslmode` URI override and uses the application’s explicit local TLS option.

A real packaged pilot-003 run passed both conflict-snapshot and discarded-COMMIT-acknowledgement cases under `task07-toolchain/logs/b21-proxy-product-diagnosis-004/`. The conflict had an independently observed PostgreSQL transaction lock wait, `INSERT 0 0`, identical confirmed responses and one durable operation/item/outbox effect. A dropped actual COMMIT plus idle acknowledgement produced 503 `outcome_unknown`; authorized recovery and same-key replay returned the durable original bytes.

One intervening SQLx column-origin catalog query is recorded explicitly. The source path is native `Session::describe_typed` → SQLx `prepare_with` → SQLx 0.9.0 `src/connection/resolve.rs`, `ColumnResolver::push_column`/`fill_cache`. The oracle permits at most one complete known `pg_catalog.pg_attribute` query shape with at most eleven numeric OID/attribute pairs; it records the exact statement hash and permits no other SQL before the next business operations SELECT. It does not claim literal wire adjacency or ignore arbitrary SELECTs. The initial timeout-query inference was rejected by the trace and is not used.

The successful diagnostic used the earlier immutable pilot-003 product. The final oracle adds an explicit metadata-count result field after that run without changing the algorithm. The parent is running the final integrated product matrix; this review does not substitute the earlier diagnostic for those rows.

## Acceptance limits

This source review does not establish B22 crash/fault or long-duration acceptance, B23 performance benefits, B24 release composition, other platforms, or power-loss durability. The local filesystem has one process owner and explicit offline maintenance. Seven-day replay is not permanent duplicate prevention. Outbox publication has a 15-second admission token and a separate existing 30-second native consumer COMMIT deadline; shutdown does not promise to finish within the admission-token duration.

The parent owns Plan integration and full B21 acceptance. No Plan file was modified by this review.
