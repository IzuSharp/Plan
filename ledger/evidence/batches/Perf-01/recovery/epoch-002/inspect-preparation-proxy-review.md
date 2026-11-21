# Inspect preparation proxy inheritance: independent addendum

**ACCEPT exact prepared source `04d1a63d41f6a1d3cf42ba679494ff20361a6870` for execution.**
This narrow source review adds to the [external-cache review](inspect-preparation-cache-review.md).
It runs no restore, build, target-module import, profile or workload.

| Input | SHA-256 |
| --- | --- |
| Current profile source index | `43d088bace6f72d8e7fa59318aa9ae777d1020245b050173f415d135f13251bf` |
| Current `profile.py` | `d068a7bb4a6572d7f2ade52de335063f4da3ba3c8d48ecfded2f43db8ef060ad` |
| Prior external-cache source index | `ccea3bd075bbd088b5d013cd8f86ffdcbd8afdc4a882293aad2edb8df82e923d` |

The only execution delta copies the eight existing tool-provided environment
keys `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `NO_PROXY` and their lowercase
forms, when present, into the temporary **Inspect preparation** environment.
The added record contains sorted key names only. No value, endpoint or
credential is introduced or published. Independent inspection of the original
`Run.command` and finite owner's receipt construction confirms that they do
not serialize this inherited environment mapping. The reviewer did not read
proxy values.

The same `finally` restores the original environment object before every
Inspect probe and on preparation failure. The external-only fallback view,
fresh writable cache, copied same-role project feed, native identities,
command arguments, owner and bounds are unchanged. No audit, TLS or package
source setting is disabled. No other profile branch, workload, formal
measurement configuration or timing statistic changes. All four indexed file
hashes match; the caller parses as Python AST without import.

Root reported a separate NU1900 fallback-only diagnostic restore failure and
a successful diagnostic restore using the inherited proxy keys. This review
does not independently audit or transfer those outcomes to this new profiler
source. The executor must preserve them and obtain actual receipts for the
new invocation. Source acceptance grants no runtime or performance credit.
