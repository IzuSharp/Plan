# 图校验与接受证据格式 v1

`tools/validate_graphs.py`仅用Python标准库。实际执行结果在同目录`graph-validation.json`；针对门禁的有限错误注入在`mutation-checks.json`。这不是产品实现或AOT测试。

## 检查范围

- 三张独立图版本、ID唯一、引用存在、图类型、start与acceptance依赖无环、精确任务revision和契约version。
- repository-qualified路径安全、输出必须被所有者范围**包含**、不同任务写范围不得重叠、当前可启动集合和局部资源冲突。
- prompt/packet的实际字节与`packet_sha256`匹配。节点接受内容digest包含packet hash；改正文使旧证据失效。
- proposed契约允许暂缺spec。accepted契约必须有实际spec文件、内容hash、有效证据、绑定该版本/hash的独立Review与已接受精确依赖。
- accepted、delivered、complete、completed、done、verified全部执行终结门禁，不能用别名逃过检查。
- 运行证据必须显式passed、checks完成且failed=0、未超时、退出码0、有真实本地日志文件/hash及合法带时区起止时间；AOT还要publish/执行标志、命令、目标RID、实际制品字节hash。
- 必需平台按OS、arch、RID和kind匹配。win-arm64不能代替win-x64。模型验证按model_check记录，不冒充AOT应用。
- 依赖快照绑定revision、内容hash、source_commit及验收证据hash。上游实现或证据变动会使下游旧验收失效。
- 可选分支选择状态及版本进入subject快照。条件start边约束开始并在接受时复查，条件acceptance边约束最终接受；未选分支不成为依赖。B24按release_scope逐组件验收，不外推未选包。
- required_selection_groups仅用于Delivery：同一组任务必须属于selection_inputs、具备selection_required，minimum_selected=1。所有selection_inputs需selected/excluded，组内至少一个selected；未决定/全部排除不能使组合ready或终结接受。允许B15/B17同时selected，不设默认host。
- proposed release_scope也检查组件revision、引用和when条件；必需Rust Database B04不能使用when=selected而从scope漏掉。
- B18/B19的protocol_host_profiles必须完整列出host选择；启用的profile只引用现有contract_inputs中的精确accepted协议契约。缺Rust adapter设计的null条目不能放行；选中协议至少在一个选中host启用。双host可显式只启用Kestrel协议，未启用profile的条件start边不生效；没有第二套approved布尔接受系统。

## 输入位置

本地应有同级`Plan/`和`NativeWeave-Design/`。路径使用`Plan:ledger/...`、`NativeWeave-Design:docs/...`或产品的`NativeWeave:...`，不接受绝对路径、`..`、反斜杠或越过仓库根的链接。候选输出可以还不存在；**接受证据引用的文件必须实际存在且hash匹配**。

运行：

```bash
python3 tools/validate_graphs.py --root . --output verification/graph-validation.json
python3 tools/mutation_checks.py
python3 tools/host_selection_checks.py
```

## Manifest引用与内容

契约`evidence`和`reviews`，任务`acceptance_evidence`和`independent_reviewers`均存引用对象：`manifest_path`及完整`sha256`。这两个字段指向真实JSON字节；不能把非空字符串当作证据。

证据manifest遵从`schemas/evidence-manifest-v1.schema.json`，至少包含schema_version、is_template=false、subject、status=passed、kind、recorded_at、producer、artifact.path/sha256。允许source_read、official_documentation、design_analysis、static_review，以及适用的实际run kinds。source_read只能支撑读取结论，不推导编译运行。

运行manifest额外记录source_commit、command、exit_code、toolchain、platform（os/arch）、checks（completed=true、timed_out=false、failed=0）、logs.stdout与logs.stderr的path/sha256，以及started_at/finished_at。root Design的evidence-policy还要求更丰富的CPU/ABI/链接器、输入/种子、警告与测试数量；结构工具不代替实质审查这些内容。

native_aot_run的`aot`含published=true、executed=true、runtime_mode=native_aot、target_rid、binary.path/sha256、publish_command、run_command。AOT制品和原始日志需要被审查者下载到本地证据目录后校验；不能只给不可核查的URL然后声称通过。

contract subject精确包含kind=contract、id、version、content_sha256。task subject由`Validator.task_subject(task_id,node)`生成，包含task revision、节点/packet内容digest、当前产品source_commit、依赖快照与选择快照。`node_digest`不含状态、接受记录、实施授权记录或source_commit以避免自引用；产品source_commit单独进入subject并进入下游依赖快照。

Review manifest包含schema_version=1.0.0、is_template=false、同一subject、verdict=accepted、author、非作者的reviewer、reviewed_at、blocking_findings=[]和全部reviewed_evidence_sha256。当前author/producer/reviewer不能为null、布尔、对象、空白或unassigned等占位值。

产品任务从planned_candidate提升为planned时，需实施授权记录指向task_id、task_revision、task_content_sha256和verdict=authorize_implementation。它表示既定独立审查门禁通过、任务范围具备执行条件，**不是要求用户重复授权每个常规任务**。发布和权限操作仍按实际任务与用户授权判断。

## 明确限制

工具校验本地结构、hash、状态和相互绑定。它不能认证某字符串背后的人确实独立，也不能仅凭自报manifest证明命令真的执行；恶意伪造完整日志/二进制/身份仍需可信CI、实际GitHub Review或独立重放发现。它也不检查源码机制是否正确、测试oracle是否可靠、所有线程交错或业务语义是否覆盖。

JSON Schema是可交换形状；Python工具实现当前关键语义检查，不是通用JSON Schema解释器。生产CI还可使用独立schema校验器，再进行必要的语义/来源审查。任何本地校验错误使工具返回的ready集合为空；对独立topic不要把结构工具的错误误解释为所有研究必须停工，先局部修复对应图变更。

正式接受需要真实证据与独立实质Review共同成立，不能把绿色结构检查当产品验收。

`host_selection_checks.py`的隔离fixture仅替换与选择无关的证据/授权验证，用于让正负选择门禁有可观察结果；不向ledger写fixture接受或授权记录。它同时检查真实48个候选任务未被授权，默认再运行完整Validator。`--policy-only`只适用于配对Design尚在准备时的代码审查，输出显式full_graph_checked=false，不能替代合并前完整检查。原有14个mutation与4个Rust1.100回归保留。

## 协议host范围的规范绑定

协议spec使用且只能使用一个以下形状的代码块。下面只是格式说明，不表示任何契约已经接受；当前D19的Kestrel接缝只能声明B15，B17须有新的相应设计后另行接受。

````text
```json nativeweave-protocol-host-profiles-v1
{"host_task_ids":["B15"]}
```
````

host_task_ids必须非空、唯一且为合法B任务ID。validator先要求现有contract_inputs的精确契约通过原来的spec hash/证据/独立Review检查，再读取同一spec的匹配字节。无声明、重复/无效声明、不含请求host或篡改正文hash时不放行。它不接受Plan中填approved=true，不把Kestrel-only已接受契约自动推广到Rust。协议矩阵属于node digest，所选host属于selection snapshot，二者改变都会使旧任务接受subject失效。
