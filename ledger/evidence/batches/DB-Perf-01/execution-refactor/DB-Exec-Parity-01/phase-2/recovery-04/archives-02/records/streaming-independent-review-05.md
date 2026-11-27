# Independent streaming-archive review and contained-path correction

The `/root/worker_boundary_review` agent independently read the frozen verifier without running tests, measurements or large I/O. It found no material defect in per-part EOF validation, whole compressed/tar hashes including padding, member size/hash/mode validation, or the explicit per-member overlay rule.

It identified a restore containment ordering defect: the old verifier called `target.parent.mkdir(...)` before checking whether a pre-existing parent symlink resolved outside the destination. Such a link could cause an outside subdirectory to be created before the verifier rejected the member. This did not affect the already completed byte verification of the four evidence packages, or restoration into a new empty destination.

The archive author preserved that verifier as `writer-v4.py`, moved the resolved-parent check before directory creation, and retained a second check afterwards. A tiny owned temporary fixture demonstrated the old side effect, confirmed rejection without external directory creation after the correction, and passed normal restoration. `records/contained-path-selfcheck.json` binds both verifier hashes and the actual results. This is a correctness control, not a performance measurement. No evidence payload was recompressed or changed.

The review also clarified two contracts now stated in the README. Restoration commits one verified member at a time; failure later in a stream can leave earlier verified members or temporary files. Source capture uses cooperative sealing plus per-file identity checks and content hashes, rather than a simultaneous snapshot of every selected file. These limitations were not converted into broader guarantees.

The independent review preceded the correction. The tiny regression control was executed by the archive author; it is not represented as an independent execution by the reviewer. The read-only review request and all local operations paused for the root agent's ordinary-measurement quiet window; the correction/control ran only after the explicit quiet-end notification.
