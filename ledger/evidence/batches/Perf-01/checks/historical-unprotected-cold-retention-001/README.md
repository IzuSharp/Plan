# Historical unprotected payload retention 001 — actual storage result

The actual lossless retention completed successfully. **483 unused historical compiled files were archived and removed from their former locations.** Their original **4,640,235,640 bytes** are represented by **1,651,272,305 gzip bytes**. The completed producer records matching full decoded byte counts and SHA-256 values for every file before removal. This is storage maintenance and grants **zero performance, functional or 30-minute-test credit**.

## Recorded result

| Item | Actual value |
|---|---:|
| Retention interval, UTC | 2026-11-20 17:54:40.013775 to 18:04:35.192670 |
| Selected files / recorded verified removals | 483 / 483 |
| Original bytes | 4,640,235,640 |
| Gzip bytes | 1,651,272,305 |
| Nominal original minus gzip bytes | 2,988,963,335 |
| Observed free bytes before / after | 1,384,419,328 / 4,285,296,640 |
| Observed free-space increase | 2,900,877,312 bytes |
| Incomplete or unremoved selected files | 0 |
| Owned retention commands / exit status | 1 / 0 |
| Temporary safety checks | 7 passed; 0 failed |

The observed free-space change is a filesystem observation; it is not equated with the nominal byte difference. All 483 entries record a compressed hash, matching original/decoded hashes and byte counts, a verification timestamp preceding removal, and a restoration path, mode and modification time. The owner recorded normal process-group and adopted-descendant retirement, without cleanup signals or cleanup errors.

The seven existing temporary tests covered corrupt-archive rejection, live descriptor and mapping rejection, byte/mode/time preservation, fresh restore destinations, protected future inputs, and special-permission rejection. The test framework reported 0.080 seconds; the owned command took 273,299,965 ns. These are storage tests, not product regressions or benchmarks.

## Restoration and identity

The private archive retains all 483 compressed entries and their exact restoration map. The existing restore entrypoint requires a fresh destination, the exact source hash `a73e9ff02f650290495e08c2044edca60a5c887ccf814c0f008eaac4a3bc074e`, and the actual final manifest hash `4869f7e682b1b2bba5e79345396e653340ab130154bf490d15ad69b4352bdb11`. The original removal locations are not overwritten automatically. This maintenance run did not perform a full-bundle restore; the completed archive producer verified every full decoded payload before removal, and the temporary tests exercised restoration boundaries. No new expiry or remote archive publication is claimed here.

The public [summary.json](summary.json) binds the source index, selected inputs, dependency closure, temporary-check source and receipts, finite owner and actual archive manifest. It publishes numerical totals and hashes; private workspace paths, process identities and per-file operational catalogs remain outside this projection. The selected future execution inputs, sources, controls and package archives remain hot. Earlier failed, invalid, accepted and pending measurement states are unchanged.

## Separate Git object compaction

A later successful Git object compaction recorded unchanged ref digests and requested retention of unreachable objects, without a prune or reset request. Its observed free space changed from **4,285,235,200 to 4,314,693,632 bytes**. That separate **29,458,432-byte** observation is not included in the archive byte totals. Its exact receipt hash and unchanged ref digest are included in the summary.

This checklist is a projection of completed metadata. No archive/member payload was replayed or rehashed while writing it, and it provides no new measurement or optional-cache retention decision.
