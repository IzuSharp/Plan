# Perf-01 final before HTTP calibration: v5r1

These are byte-identical copies of the completed, small metadata files from
`ROOT/perf01-evidence/calibration/before-http-v5r1`. The protocol reviewer copied
them on CPU 8 while root continued the separate gRPC calibration. No raw request,
client-operation, result-histogram, or resource ledger was scanned for this copy.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `selection.json` | 2,107 | `d652f232f69d17ed7e9f2e1028401e3809b8ac28f3ad784c8bf6d038be079db6` |
| `controller.json` | 47,236 | `b1ae28ecd3f4bbc7e44dacd90f3ce91f1efeb467f758c983521a391ba2e6965f` |

Selection completed at **2026-11-19T13:29:01.677586+00:00**. The largest
consistently passing sampled offered rate was **1,088 calls/s**, with 64 client
workers. The policy's 500/s cap selects **500 calls/s for both paired long HTTP
runs**. This selection does not itself grant any 30-minute credit.

| Fresh confirmation | Offered / successful logical checks | p99 arrival latency | Server RSS maximum |
| --- | ---: | ---: | ---: |
| `13-confirmation-0-1088` | 65,390 / 65,390 | 285.246995 ms | 70,557,696 bytes |
| `14-confirmation-1-1088` | 65,390 / 65,390 | 274.753607 ms | 71,626,752 bytes |
| `15-confirmation-2-1088` | 65,390 / 65,390 | 280.616883 ms | 70,520,832 bytes |

Each row is a separate 60-second scheduled process with `exit_code=0`,
`valid=true`, and `qualifies=true` in the copied controller. Counts include
successful expected probes; the raw result separately distinguishes ordinary
business calls. The table repeats recorded controller metadata, not a new raw
correctness or percentile recomputation.

The higher sampled points at 1,152, 1,280, 1,536, and 2,048 calls/s failed with
`generator saturation: in-flight capacity`. Those cells remain invalid and
**do not establish the server's capacity ceiling**. The passing 1,088/s result
is a measured stable point under the frozen complete generator/service setup.

The before producer remains clean main
`ea5fa528035d025bd7a28698ee7c71194432236c`, using the unchanged common Native AOT
client. Producer and client build manifests both have SHA-256
`818643898f04803f3070cb55f6bf0894dc23c1f9c21ff7d556a8e99b6b96d8c3`.
The short profile SHA-256 is
`19490e76a164d65098868f3cd51d576ba8bc22a581a57b563dc27786a336ae16`;
the policy SHA-256 is
`0c7cd866b1ad0fc86d647e31dd1b6fe0b148d2e7ca54d83b7286cec09f11cafc`.
Full command arrays, result and plan hashes, earlier failed points, source pins,
and timestamps remain in the copied controller. TLS file paths/hashes are
metadata only; no key or certificate contents were copied.

Controller and other generator RSS are not fields in this small calibration
controller. Their existing result fields and sampled evidence are described in
[`../../protocol-controller-memory-review.md`](../../protocol-controller-memory-review.md).
No controller-memory value is inferred from the server RSS above.
