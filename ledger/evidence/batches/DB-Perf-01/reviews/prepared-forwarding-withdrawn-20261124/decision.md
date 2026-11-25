# DB-Perf-01: PreparedQuery forwarding withdrawal

The [PreparedQuery forwarding experiment](https://github.com/IzuSharp/Korda/pull/37#issuecomment-7142236185) was withdrawn and is not retained. A SQLite process exited with code `-6`; the cause remains undetermined. No claim is made that the patch caused the failure. See the public [failure report](https://github.com/IzuSharp/Korda/pull/37#issuecomment-7143231640) and [withdrawal decision](https://github.com/IzuSharp/Korda/pull/37#issuecomment-7143778377).

The public withdrawal decision keeps these outcomes distinct:

| Outcome | Count |
| --- | ---: |
| Successful short-test processes | 19 |
| Failed short-test processes | 1 |
| Unstarted matrix cells | 4 |
| Separate successful diagnostic processes | 2 |

The two diagnostic processes did not reproduce the failure and do not replace the failed result. This experiment did not change the formal candidate identified publicly as `3d5`. [Source](https://github.com/IzuSharp/Korda/pull/37#issuecomment-7143778377)

This decision record assigns **0 formal long-run credit** to the withdrawn experiment. That accounting concerns this experiment only.

Detailed experiment records are retained, but this minimal decision record does not provide them or claim that their raw counters have been published. It therefore establishes no performance benefit for the withdrawn experiment.
