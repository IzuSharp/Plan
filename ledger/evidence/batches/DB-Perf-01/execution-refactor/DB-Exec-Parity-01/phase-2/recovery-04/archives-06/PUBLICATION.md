# Archive06 publication checkpoint

The earlier README is retained as the original preparation record. Its statements
that packing and stream verification are pending are superseded by
`archive-completion-validation-02.json` and `resume-closure-02.json`.

The six frozen payload groups have passed the recorded stream and identity checks:
21 ordered parts, 71,202,192 compressed bytes, 1,908 members and 202,602,754 expanded
bytes. No full extraction or new product, database, diagnostic or performance run
was performed for this publication continuation. Existing source and payload bytes
remain unchanged.

All 21 content-addressed part uploads returned the expected Git blob identities.
The bounded metadata is frozen by `publication/primary-manifest.json`; the matching
primary upload receipts and state are preserved next to it. Creating these blobs
does not publish a branch or prove remote byte readback. The root task separately
owns the tree, commit, branch update, review and actual remote-byte validation.
Only its later publication and readback receipt can establish those outcomes.

Restore with the existing `restore_archive06.py` and the prerequisite archives
specified in the unchanged README. Its default operation stream-checks the saved
payload; extraction requires an explicit destination with adequate free space.
Historical reconstructed generated files remain marked byte-identical
reconstructions and are not silently substituted for their current source views.

This archive closes the rejected frame08 experiment and preserves the independent
owner cleanup. It adds no performance acceptance, parity claim, new experiment or
long measurement. Public NuGet publication and AOT consumption evidence is outside
this frozen archive and is recorded separately by the root task.
