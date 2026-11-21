# Independent review of the complementary native close tests

Reviewer: `perf01_grpc_review`, a separate source-review agent. This is not a
GitHub account approval and does not waive repository checks.

The reviewer accepted the actual `cad8acabfdb11dda9e365701cebceb8d12578f36`
diff against `483c3b8c80c1d2bfbbf8d1130eaef48239b9c853`:

- Only the native host engine and its native test file changed.
- All new engine fields, initialization, gate type and network-join handshake
  are under `cfg(test)`. The published production polling repair is unchanged.
- The native test file is byte-identical to the separately reviewed
  `f5acae7096d6ffa832c63e1a73f52fa39406a20d` pre-repair regression source.
- The existing managed HTTP/1.1 and HTTP/2 regressions remain unchanged.
- Finish is created and started through the actual ABI, with the request-local
  operation count intact. The empty trailer input is the real four-byte encoded
  empty header block. The test uses actual sockets and complete declared bodies.
- The worker gate is released before waiting for terminal delivery. The failure
  cleanup saves the absent terminal and exited-worker observation, completes the
  otherwise stranded test operation only for teardown, retires its owners, and
  still fails on the original observation. It does not alter production behavior.

The root subsequently published the exact tested tree
`7f803d4f9e57fef1d8cfdef69c505d67f84614c9` as
`2f40348c3db80a4fbee7a99e721b374a597b16df` and fetched both changed files back.
The publication identity and observed 23/23 Debug and Release results are in
[the checklist](checklist.json). The reviewer did not execute builds or tests;
those results belong to the separately recorded finite executions.

The earlier independent production-drain review remains in
[server-close-drain-source-review.md](../server-close-drain-source-review.md).
The requestless TLS reload-versus-close limitation is unchanged and is not
claimed fixed by these request-tail changes. Final assembled application/package
checks and formal performance/long-run acceptance remain separate obligations.
