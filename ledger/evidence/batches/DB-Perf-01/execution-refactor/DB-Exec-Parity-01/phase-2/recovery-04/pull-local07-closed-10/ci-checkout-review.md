# Plan checkout transport review 07

**Recommend a narrow transport change: add `filter: blob:none` to the seven existing pinned checkout steps, retaining `fetch-depth: 0`, every ref/path/command and all existing gates.** This is supported by the pinned action implementation and the observed fetch bottleneck. It is not yet a measured CI speedup or a successful post-change CI result. No workflow was edited or triggered by this review.

## Observed cancellation

Run `45984275158`, job `140455763686`, head `ded73d7cd90cb692bea554c5e780df0ca9e05e3f`: the six Plan checkout steps take **294 + 246 + 232 + 238 + 293 + 237 = 1,540 seconds (25 min 40 sec)**. The frozen Design checkout takes one second. Each Plan log shows an unfiltered full-refspec fetch (`+refs/heads/*` and `+refs/tags/*`) before selecting its pinned commit. The completed frozen gates have success results. The combined historical gate starts at 11:07:42 and is cancelled at 11:11:57; final schema validation is skipped and later artifact/post-job cleanup runs.

Job start 10:41:57 and logged cancellation 11:11:57 match the configured 30-minute timeout. **Timeout attribution is an inference from those times and the unchanged workflow**; no annotation endpoint was available. Job final completion includes cleanup and is later than the cancellation.

## Why the exact input works

The workflow pins actions/checkout to `11d5960a326750d5838078e36cf38b85af677262`. Its `action.yml` declares `filter`; `input-helper.ts` reads it; `git-source-provider.ts` forwards it into the same all-history fetch branch when fetch depth is zero; `git-command-manager.ts` adds the filter flag without changing the refspec or depth. The frozen refs, all commits and trees, and normal full working-directory checkout are retained. This is independent of shallow-history restrictions. See the official pinned files retained under `upstream/` and linked in `summary.json`.

`blob:none` defers file-content objects until needed. Thus the five historical Plan checkouts can avoid pre-downloading later archive payloads reachable only through other/current branches. Git checkout fetches the contents needed for the chosen historical tree, and history gates can obtain specifically requested older blobs on demand. It does not prune historical commits or alter verifier bytes.

## Practical limits and security

The first checkout selects current HEAD, whose working tree includes the archives and whose existing upload step includes them; those bytes will still be fetched/materialized. This change chiefly removes repeated unrelated historical-clone payload transfer. It does not promise a precise saved byte count or duration. A gate that reads additional historical contents can still trigger network I/O.

The pinned action removes authentication after checkout when `persist-credentials: false`; preserve that setting. Read-only GitHub repository metadata confirms Plan and Korda-Design are public in this review, so post-checkout lazy retrieval does not inherently require keeping a token. Retrieval/network failure must continue to fail the original gate, not be ignored.

Keep the 30-minute timeout, contents-read permission, all refs/paths, action pins, frozen verifier commands, and artifact paths unchanged. This proposal adds no benchmark, profile, calibration, stress test or database execution. After root reviews a seven-line-only diff, normal CI must demonstrate all pre-existing gates and final schema validation succeeding; absent that result, do not call the delivery blocker resolved.

Official semantics: https://git-scm.com/docs/git-clone and https://git-scm.com/docs/partial-clone . Evidence: `observations/recovery/archive04-ci-cancelled-01/{job.log,receipt.json}`. Source and input hashes, exact checkout durations, and official pinned URLs are in `summary.json`.
