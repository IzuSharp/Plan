# Candidate5 GitHub CI failure — observed

Run: https://github.com/IzuSharp/NativeWeave/actions/runs/44912217954

The run completed with **failure**, not cancellation. Attempt 1 used source aaf5dafc241f036b184c46265e87c042787120e8, tree ed5a72cac3f240feb0730e1329816e58b66f723c. Both archive source receipts match this identity.

The first failing command is Data.NativeHost-aot-restore (exit 1, NU1004) in build job 136870347433, step 9. The Host test and Database.DependencyInjection projects selected the ordinary NuGet lock during the separate AOT restore because they lacked the plural RuntimeIdentifiers fallback. Their committed AOT locks already contained the required RID and pinned SDK compiler/linker entries. The 21 preceding recorded commands passed and their archived log hashes match; the last was Host JIT.

Candidate6 already contains the reviewed selector repair for both failing projects and the analogous Migrations test selector. The exact candidate6 source binding is recorded separately. No lock regeneration or disabled locked restore is involved. Candidate6 runtime and full CI acceptance remain separate pending evidence.

All four security jobs succeeded. Final Verify failed because the build gate failed. The downloaded 105359-byte artifact 14710629007 matches GitHub digest sha256:6e902d2b4d2241b1a20cba75dd6ae57a770a03e1f5fccee7f8fe352a2470a5ef.

Safe review inputs are failure-observation.json and Data.NativeHost-aot-restore.sanitized.log. Original ZIP and extracted raw logs remain preserved locally.
