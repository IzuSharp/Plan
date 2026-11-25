# Source-location correction and publication recovery

The owner's repository split places implementation and benchmarks in Korda, and
plans, measured evidence and recovery records in Plan. Automatic approval review
rejected two attempts to upload new full implementation snapshots to Plan: a
temporary tree request containing DbWire/codec/control-record source, and a blob
request containing a complete earlier campaign controller. Neither request
changed a branch reference. The rejected uploads are not retried through another
transport.

This correction replaces **93 newly added source/build-input copies (52 unique
contents)** with source-reference JSON records. Eleven references, covering seven
unique contents, already bind to published Korda commits. The other 82 references
cover 45 unique historical variants, now prepared under Korda's immutable
`benchmarks/db-perf/reproduction-inputs/by-sha256/<sha256>/<filename>` archive.
Their commit/tree fields remain explicitly pending until the actual Korda
publication is verified. These archive files are historical reproduction inputs;
they do not participate in the current consumer or production build.

The complete local recovery snapshot remains reachable at Plan commit
`b279f42674eb3e8db48b423482f38c6b955c4d82`. That local commit is not described as a
published remote commit. The new safe publication tree preserves every file
already present in remote Plan commit
`ba380202e7b36cbfe8dcd4bc2cfa0afe86048d92`; pre-existing remote implementation
evidence is not deleted or rewritten by this correction.

Raw measurement counts, logs, command receipts and original build receipts are
unchanged. Original checkpoint indexes are preserved byte-for-byte under
`original-indexes/`; the current `checkpoints/*/files.json` indexes now resolve the
source-reference records. Historical paths inside original receipts remain an
accurate record of the original run. Resolve those paths through
[source-references.json](source-references.json) to locate the immutable Korda
source. A reference carries the original Plan path, original Git blob, exact
SHA-256, byte length and fixed or pending Korda destination.

Run `python3 tools/verify_db_perf.py --korda-source <existing-Korda-checkout>` to
check all currently fixed source bytes against their exact Git commit and tree.
Pending bindings are allowed for this in-progress recovery checkpoint; they block
accepted state. The gate does not execute performance measurements. This
correction creates no new performance result: long-test credit stays **0/8**, and
framework-wide zero allocation remains unproved.
