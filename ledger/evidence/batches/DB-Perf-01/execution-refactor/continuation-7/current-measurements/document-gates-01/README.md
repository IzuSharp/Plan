# Document/history checks before the final campaign

Design `python3 tools/verify_db_rename.py` passed, including its immutable
Fluent/C++/scope history chain. The observation records the actual tool chunks;
no unrecorded stdout hash is invented.

A current-tree invocation of Plan `tools/verify_db_perf.py --korda-source ...`
failed at its old `validate_history` allowlist. That gate is tied to the
pre-repository-rename DB-Perf history and rejects later unrelated workflow URL
maintenance already present on this branch. The failure remains recorded.
The existing CI deliberately runs this unchanged gate at exact immutable Plan
`38f8ce8a01f88e6e4c4459926f197c5438c2f6fc`; that actual frozen invocation passed
with 13 record controls and four source-reference controls. Its historical
state/counts were not relabelled to this campaign. No verifier, historical
acceptance or CI selection was changed to make the check pass.

Current performance acceptance remains the separate unchanged four-cell
arithmetic and final source/owner auditor, not these documentation checks.
