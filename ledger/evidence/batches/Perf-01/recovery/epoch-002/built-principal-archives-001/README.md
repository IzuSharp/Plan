# Actual principal binary archive readback

Status: **saved, retrieved and verified** at `2026-11-21T02:22:12.134193+00:00`. No performance or long-duration credit.

Two narrowly selected archives retain the actual completed before/common producer outputs. Each archive was saved as a user-owned durable file, retrieved to a new directory and checked against its original SHA-256. Every payload member was then rehashed against its embedded sanitized identity manifest.

| Role | Archive | Archive bytes | Verified payload files | SHA-256 |
| --- | --- | ---: | ---: | --- |
| before | NativeWeave-Perf-01-epoch002-before-principal-001.tar.gz | 99608131 | 61 | `846e726d61ffb90ee09c53ac4e7e47c25959df8003f87626420ddb49afba00ed` |
| common | NativeWeave-Perf-01-epoch002-common-principal-001.tar.gz | 25775472 | 21 | `86d0c8519ddab31580ffb67a36126d93fe806c8ecac3f3eeee996db66ec05e81` |

The before archive contains selected project packages, principal AOT/client/shared/codec publish outputs and stable native assets. The common archive contains direct Rust and managed comparators and the fixed synthetic codec corpus. Three reused before prerequisites are referenced by exact identity without duplicating payload in the common archive. Each archive also contains one `IDENTITY.json` member.

Member names use project-relative roles. Private control maps, environment files, TLS material, full caches and build intermediates are excluded. Existing selected publish bytes, including debug files, are preserved unchanged. The public [before](../built-before-001/README.md) and [common](../built-common-001/README.md) projections retain their actual build source/package identities.

Retention: user-owned durable files remain until removed by their owner; no automatic expiry was provided. Resolve the exact filenames and archive digests above when recovering them. Private provider identifiers stay in the local delivery receipt and are not published. Public curated Git evidence remains separately available in this repository.

The adjacent [readback.json](readback.json) preserves the actual successful retrieval and complete member-check counts. This does not archive the entire private runtime admission closure or transfer acceptance from the lost epoch.
