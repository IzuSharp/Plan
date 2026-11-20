# Perf-01 exact SDK/Design restoration

**Cutoff: 2026-11-20 21:34:27 UTC.** The first ON build failed. Its whole failed
role was preserved, exact inputs were restored, and a fresh build started. The
[curated record](checkpoint.json) contains necessary identities and receipt hashes.

All events occurred on 2026-11-20 UTC:

| Event | Actual interval | Result |
| --- | --- | --- |
| First ON build | 21:10:45–21:19:53 | Failed before any managed build |
| SDK restoration | 21:27:05–21:27:31 | Original checksums/version matched |
| Design restoration | 21:27:43–21:27:58 | Locked commit/tree matched; clean |
| Failed-role preservation | 21:30:23–21:30:24 | 2,584 files / 883,420,344 bytes preserved |
| Fresh ON build | Started 21:34:19 | Pending at this checkpoint |

The native producer completed, but packages could not find `dotnet` for its SDK
version command. The disappearance cause is unknown. Both owners retired without
signals or remaining children. Official SDK 11.0.100 archive, executable and
original dependency hashes matched; its original physical location was restored.

Independent local source/configuration review conditionally accepted preserving
the failed role and running all eight producers anew. Old bytes and failed status
remain unchanged. No partial producer is reused. Completed before/common builds
and before gRPC functional evidence retain their original identities. No restoration or build was executed by this curation.

**No fresh ON completion is claimed. Performance credit remains zero; all ten
fresh 30-minute segments are outstanding.** Internal inventories stay local. After verified publication, Git retention lasts
while repository history is retained; no full-raw remote archive is claimed.
