# DB-Go-01 cleanup inventory addendum

Observed: 2026-11-26T14:19:01.804657+00:00.

This is a read-only post-campaign addendum. No file was deleted. The frozen cleanup helper and original inventory were not modified. Telemetry payloads and token contents are not included.

## Task-created Go telemetry outside the explicit cache roots

Go 1.27.4 created **9 files, 114,690 bytes**, under `/home/agent/.config/go/telemetry/local`: seven versioned tool counters, the empty `upload.token` rate-limit marker and the two-byte `weekends` helper. Exact device/inode, birth time, modification time, ownership and SHA-256 values are recorded in the JSON addendum.

The official task-local SDK was installed at `2026-11-26T12:34:53.140738+00:00`. The telemetry wrapper directories and first counter/helper were born at approximately `2026-11-26T12:35:53.953564Z`; the remaining versioned files were created between 12:42 and 12:45 UTC. The pre-install environment audit found no usable Go compiler in the inspected locations. All counters name the installed Go 1.27.4 Linux amd64 version and the task date.

The pinned Go source independently explains these paths: `internal/telemetry/dir.go` initializes the default from `os.UserConfigDir()/go/telemetry`; `internal/counter/file.go` constructs the versioned counter names and creates `weekends` only when absent; `start.go` creates an empty `upload.token` marker. These files are independent of GOCACHE and GOMODCACHE. The earlier statement that all Go setup writes were task-local therefore needs this explicit telemetry exception.

| Exact filename in telemetry/local | Bytes | Modified UTC | SHA-256 |
|---|---:|---|---|
| `asm@go1.27.4-go1.27.4-linux-amd64-2026-11-26.v1.count` | 16384 | 2026-11-26T12:45:27.777914+00:00 | `83939b521e28b560bfacb9c7890c9c26128dfa66a7d56c4166c537ce73b06dd0` |
| `cgo@go1.27.4-go1.27.4-linux-amd64-2026-11-26.v1.count` | 16384 | 2026-11-26T12:45:41.474736+00:00 | `849aeb90be7458e1d838e04e1c5cbc90ffddfec8b0383d06b5706d13a0d666f3` |
| `compile@go1.27.4-go1.27.4-linux-amd64-2026-11-26.v1.count` | 16384 | 2026-11-26T12:45:27.754555+00:00 | `2129e713e49e6443c6b26d700d5105e57303af816a232d5dda66f9cf3f83a2c1` |
| `go@go1.27.4-go1.27.4-linux-amd64-2026-11-26.v1.count` | 16384 | 2026-11-26T12:35:53.959345+00:00 | `605912ed05d1ecbf163303409ce52516f3ccf203c0d0883d9b9d0f7740ee0c85` |
| `gofmt@go1.27.4-go1.27.4-linux-amd64-2026-11-26.v1.count` | 16384 | 2026-11-26T12:42:47.180699+00:00 | `58766fa06532dd489c2b804f3463b9feb0f6be4093c2b7d6e04aa15ab3e10eb6` |
| `link@go1.27.4-go1.27.4-linux-amd64-2026-11-26.v1.count` | 16384 | 2026-11-26T12:45:50.749546+00:00 | `1552fa35438f25c00f9c5c89395b95bb6552bd3da07dd6d75cab873cc6b5b5cb` |
| `upload.token` | 0 | 2026-11-26T12:35:53.959345+00:00 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `vet@go1.27.4-go1.27.4-linux-amd64-2026-11-26.v1.count` | 16384 | 2026-11-26T12:45:51.185186+00:00 | `9c2f6edd96cda5b7222aff3536241b4c9a79751a5d0670fe66e33a30f0a0f3e5` |
| `weekends` | 2 | 2026-11-26T12:35:53.953564+00:00 | `06e9d52c1720fca412803e3b07c4b228ff113e303f4c7ab94665319d832bbfb7` |

The default `~/.cache/go-build`, `~/.cache/go-toolchains`, `~/go/pkg/mod`, `~/.config/go/env`, and telemetry `mode` paths were absent. The sibling telemetry `upload` directory was empty and was created during the same first Go invocation. No other shared cache content was scanned.

## Separate, narrow cleanup recommendation

The root agent can remove the nine exact files after immediately rechecking their inode, regular-file type, ownership and hashes. Do not run Go commands during removal. If a file changed or a new counter/configuration file appears, preserve it and re-audit. These are rebuildable tool telemetry artifacts; retain the metadata and omission record rather than treating them as benchmark evidence.

After file cleanup, the root may use empty-only `rmdir` operations on these task-created wrappers, in this order:

1. `/home/agent/.config/go/telemetry/local`
2. `/home/agent/.config/go/telemetry/upload`
3. `/home/agent/.config/go/telemetry`
4. `/home/agent/.config/go`

Use matching inode checks and leave any nonempty directory untouched. `/home/agent/.config` remains. Never use a recursive deletion against shared user configuration. This separate action does not expand the frozen cleanup helper roots.

## Refreshed worktree and temporary scope

There are **62 registered worktrees**: Korda 52, Korda-Design 4, and Plan 6. The two additions relative to the original 60-worktree inventory are the current-root `DB-Go-01-korda` and `DB-Go-01-plan` worktrees. Both are already inside the helper's fixed current-root deletion scope.

The **32 task temporary paths are unchanged** from the original inventory; no additional task temporary root was found. The current workspace has the expected `worktrees` directory alongside the original evidence and the current Go comparison directory.

## Frozen file verification and draft PR scope

- `final_cleanup.py`: `79088224364dd5b1321e83c30aa462a2e3bd79efc7e1a692b3638257b4cdabb7`; matches the frozen template.
- `cleanup-inventory.json`: `ff44db8a718951a07c15d00035c5ea516ddd0b0af3628d532c8c57e9ef87f71b`; matches the frozen template.

The latest instruction is to retain both Go PRs as drafts and not merge them. Cleanup does not require a merge: the helper accepts fixed-commit report/archive URLs on the draft branches once remote byte readback and all other archival gates are satisfied. The earlier merged Korda/Design/Plan receipts remain records of the completed prior campaign.

The root must still generate the final read-only cleanup plan after all result archival and source changes are finished. This appendix does not authorize premature deletion.
