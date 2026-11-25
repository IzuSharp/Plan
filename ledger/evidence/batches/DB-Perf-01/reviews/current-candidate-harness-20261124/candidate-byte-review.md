# DB-Perf-01 当前普通 CI 候选包：实际字节独立核对

结论：两个授权的当前 artifact 各下载一次，ZIP、nupkg、完整 unsigned member 集合、每个成员和实际 ELF native payload 全部匹配冻结 request、producer release manifest 与 GitHub artifact digest。此报告不构成公开 NuGet 包或新的 AOT/数据库执行验证。

## 固定生产身份

- 普通 CI：`45438460386`，GitHub API observed completed/success，head `cf7c080aeef01e3b012d0564e6f930b77e9c697f`。
- 实际 clean package producer 是 PR merge commit `3d5ba3f9884308caa691718f73a74aa42be19d94`。GitHub Git object API 返回其 tree 为 `74a76bc5d00671a48221d0ed19002a3ffffd319f`，与 cf7c080 的固定 tree 完全相同；它仍不是一次正常合并 main 的证明。
- 当前 activation `d665c0c9629922cfff0e48fa535d6f21393f8162` 的 request 使用 frozen harness `da153c22ef1093fccc3233ec76bfda96e6cc59df`，request SHA `189fc14ab799b152256c2d92c497c507a6ded2431cad8bdbd362bdc7538adfab`。
- 两个 provider 均为独立 `0.1.0-ci.1` 包，无 NuGet 依赖条目；两个 nuspec 的 repository commit 均对应实际 producer。

## 实际包及原生 payload

| 项目 | PostgreSQL | SQLite |
| --- | --- | --- |
| Artifact ID | 14943151333 | 14942282883 |
| ZIP bytes | 1,430,406 | 2,037,450 |
| ZIP SHA-256 | `6bb86cde0f2e86b53d5dc74cf4e52cd8761d77be0c7323ecb6183c30ef46ab75` | `52e970d42635320ee8a25349cb002fa017ce2a0460473b9e123394fa8b4ad01f` |
| nupkg SHA-256 | `c9a35d9d1bc2a3bc47a771120481f857ecdc381d99efb95387d1d1890020d94c` | `7bd4b5458226b02ce5fed07651fdd3f2816650e404266d3f525d61d9eb3735ed` |
| native SHA-256 | `73f725104fb1bee5fc86a9bc371e556ea8358ac3a2d774c4823185e6da8984c6` | `970a8868290cec37c353bbd8e48bb7bf4ef18cfa1da9e495fc06d7eb08d71d40` |
| 完整 unsigned 包成员 | 41 | 40 |

每个 archive 均检查了重复成员、路径逃逸及 ZIP CRC。包中的成员名称集合与 release.json 精确一致，81个成员逐个 SHA-256 相符；没有 `.signature.p7s`。native 文件从包中实际提取并核验 ELF magic，未加载或执行。ZIP 两次读取及 stat 稳定性也保存在 JSON 内。

## 候选消费证据的边界

每个 artifact 还保留 scaffold/original/edited 三阶段各 publish/execute 的六条命令日志，合计12份。这次将全部日志重新哈希，与 package consumer receipt 的逐命令 SHA 和 exit0 对照。两库记录均为 Native AOT、ProjectReferences=0；DTO 修改改变 Models 和可执行文件记录的 SHA，原生 SHA保持相同且与实际包 payload匹配。

这些 artifact **没有保存那六个 consumer ELF 本体**。本次因此只核验已保留的 CI 执行记录及原生包字节，不把记录中的 consumer ELF SHA 伪称为本次独立逐字节复核，不新建或执行消费者。

## 公开发布仍须另行验证

这两个 `0.1.0-ci.1` 为普通 CI 的 unsigned 候选。当前 PR #37 仍 draft/open；正常合并、main checks、自动 preview、从 NuGet 取回实际已发布 signed nupkg 并执行源码树外 PackageReference Native AOT 都没有由本次核对完成。后续须保留实际公开 archive 自身 SHA，并按发布规则绑定生产输入与 unsigned成员；不能用本地候选文件冒充公开下载。

## 本地恢复位置与复核命令

所有文件仅在 `/tmp/dbperf-current-candidates-45438460386`：

- 原始 archives：`postgresql.zip`、`sqlite.zip`。
- nupkg：`postgresql/artifact/feed/Korda.Database.PostgreSql.0.1.0-ci.1.nupkg`；`sqlite/artifact/feed/Korda.Database.Sqlite.0.1.0-ci.1.nupkg`。
- native：各 provider 的 `native/libnw_database_*.so`。
- release与原始日志：各 provider 的 `artifact/`，原 archive 成员按原路径保留。
- API元数据及下载 file_id：`provenance.json`；不保存临时签名下载URL。
- 完整核验数据：`candidate-byte-review.json`。

```sh
python /tmp/dbperf-current-candidates-45438460386/verify-candidates.py
```

该脚本只读核对现有 archive；只为本审查目录补齐字节完全一致的提取文件和本地核验 JSON，不触发构建、执行、数据库、Git、远端写入或其他 campaign。
