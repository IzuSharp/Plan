"""One-time scoped continuation of the existing 114 task packets.
Preimages are checked against merged main. No new graph or product authorization.
Run with Plan and NativeWeave-Design sibling directories.
"""
from pathlib import Path
import hashlib,json,os,subprocess
P=Path.cwd();D=P.parent/'NativeWeave-Design';REV='0.2.0';CV='0.2.0-draft'
BASE='da9e4a6337a5af0ec3d5e40a4695a2760d6ac5f5'
DESIGN='8f7f80d10943b9ca6f5c26df563f14423d7d85ab'
assert subprocess.check_output(['git','-C',str(D),'rev-parse','HEAD'],text=True).strip()==DESIGN
for name in subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],text=True).splitlines():
 if (P/name).read_bytes()!=subprocess.check_output(['git','show',BASE+':'+name]):raise SystemExit('Preimage drift: '+name)
updated={'C-BUILD-001','C-ENGINE-001','C-DB-001','C-TX-001','C-QUERY-001','C-QUERYGEN-001','C-SERVER-001','C-REFERENCE-001'}
graphs={g:json.loads((P/f'{g}-graph.json').read_text()) for g in ('research','documentation','delivery')}
nodes={n['id']:n for g in graphs.values() for n in g['nodes']}
assert len(nodes)==114
R={
'R03':'比较稳定C ABI与native直接/批量操作；Rust AST/Value/trait私有布局不跨ABI；布局、版本、所有权分别验证。',
'R04':'验证LibraryImport/UCO/函数指针、native线程回调和AOT；薄绑定仍须保证GCHandle与异常边界。',
'R05':'比较现成生成器和最小绑定输入；生成ABI glue不等于重写领域引擎；分开动态metadata与编译native能力。',
'R06':'可选static descriptor/DTO生成、增量稳定性和诊断；不以SG/完整LINQ捕获为唯一查询路线，不在SG调用Cargo。',
'R07':'可变native builder的单writer admission不同于SafeHandle物理寿命；验证cross-query owner/dispose/inflight lease。',
'R08':'ForeignHandler注册代际、注销及body/context退休；回调只进入有界dispatcher，不执行任意用户同步代码。',
'R09':'Future/Task完成桥、response-head/body分离，close deadline不是quiescence；保留迟到完成和取消竞争。',
'R10':'Rust AST/value/batch与DTO复制成本；protocol credit不能释放managed仍持有的字节预算。',
'R13':'维护者native构建与普通C#消费分离；无Cargo/CI的RID-free本地开发和显式RID AOT都必须验证。',
'R14':'固定commit/crate checksum/Cargo.lock/features/patch queue；稳定升级、安全修复和差分/性能回归，不自动升级生产。',
'R15':'形式化适用边界，response-head permit早释反例；有限模型不是weak-memory、whole-RSS或运行证明。',
'R16':'原生对照差分、SQLite silent no-op/值窄化panic、混合owner、巨大值、decoder异常和真实AOT负例。',
'R17':'直接builder/batch/static fast path与原生/managed AOT完整负载比较；度量FFI/alloc/copy/RSS和工程成本。',
'R18':'source-driven接入梯度：公开API、source-informed Adapter、上游扩展、受控Fork；动态metadata与native能力分开，小Core。',
'R19':'Rust SQLx PostgreSQL执行、取消/ReadyForQuery与Unknown提交恢复；managed驱动只作对照，不是产品后端。',
'R20':'Rust SQLx SQLite worker/队列/锁/progress取消，条数和bytes分开；公开接口不足可评估源码扩展，不伪造即时取消。',
'R21':'效果/协议/本地生命周期独立状态、SQLx池归还和cleanup；Drop排队rollback不等于服务端确认。',
'R22':'native Value到SQLx Arguments必须fallible；unsigned窄化、编码错误、NULL/precision、SQLite text-decimal、大字段边界。',
'R23':'普通typed Fluent优先；比较direct native builder、batch和可选static metadata；不要求任意IQueryable/Expression.Compile或C#SQL引擎。',
'R24':'SQL三值逻辑和backend能力；SQLite忽略row-lock/SELECT INTO/SEARCH CYCLE必须拒绝；CTE/window/join/aggregate差分。',
'R25':'SeaQuery动态AST/identifier/value/CRUD/CTE/window与SeaORM静态Entity边界，比较SQLx执行；普通新实体不默认编译Rust。',
'R26':'Kestrel现代Native AOT能力等价基线；保留独立无DB示例，源码可绑定不等于Server有实测收益。',
'R27':'Hyper Service/Body、Tower/Axum、Actix worker affinity、Pingora代理接缝；C#是handler层，不重写网络核心。',
'R28':'所选gRPC/MCP/TLS的静态注册/DTO与错误；协议包选择不阻塞无关Server/DB工作。',
'R29':'Tower ResponseFuture许可不覆盖body；Hyper H2credit不覆盖retained bytes；waiters/chunks/close预算分别验证。',
'R30':'跨语言诊断关联、bounded telemetry和credentials/参数脱敏，诊断队列不能破坏预算。',
'R31':'Rust DB+C#业务参考服务；保留原子幂等/outbox/Unknown；普通新实体复用nativehash与干净消费者验证。'}
for id,scope in R.items():
 n=nodes[id];n['questions']=[scope]+n.get('questions',[]);n['source_driven_amendment']=scope
 if id in ('R19','R23','R25'):n['questions']=[scope]
 if id in ('R23','R25'):
  n['alternatives']=['预编译SeaQuery动态native builder + SQLx','batch与可选static fast path','专用SeaORM静态Entity及native构建代价','managed外部对照；不重写完整C#SQL Provider']
  for repo in ['https://github.com/SeaQL/sea-query','https://github.com/SeaQL/sea-orm','https://github.com/transact-rs/sqlx']:
   if not any(x['repository']==repo for x in n['source_targets']):n['source_targets'].append({'repository':repo,'read_state':'target_not_yet_read','pin_required':True})
 if id=='R27':
  for repo in ['https://github.com/tower-rs/tower','https://github.com/tokio-rs/axum','https://github.com/actix/actix-web','https://github.com/cloudflare/pingora']:
   if not any(x['repository']==repo for x in n['source_targets']):n['source_targets'].append({'repository':repo,'read_state':'target_not_yet_read','pin_required':True})
 if id in ('R25','R27'):
  path=f"NativeWeave-Design:docs/research/topics/{id}/source-driven-{'seaquery' if id=='R25' else 'server'}.md"
  n.setdefault('initial_seed_refs',[]).append(path);n['status']='partially_evidenced'
  if path not in n['outputs']:n['outputs'].append(path)
nodes['R01']['initial_seed_note']='历史版本观察不是永久latest或稳定性结论。重新核验官方stable/preview与实际AOT支持，保留原日期和纠正关系。'
Dsc={
'D01':'稳定工具链/平台矩阵；有限Linux SQLite原型不是正式Windows/Linux支持，逐项核验当前特性状态。',
'D02':'私有native类型不跨ABI；direct/batch领域边界不改变Core布局/所有权，capability/version明确拒绝。',
'D03':'最小glue与校验，不在managed重写领域引擎；SG不得Cargo或假设能读取其他SG本轮输出。',
'D04':'保留lease，明确native可变builder单writer admission与SafeHandle的区别。',
'D05':'保留callback quiescence，ForeignHandler/body/context退休及注册代际，不以Task完成替代。',
'D06':'保留create/start/take_result/retire，分开response-head/body和deadline/真实回收。',
'D07':'类型长度ownership与bounded批次，retained bytes不由protocol credit自动释放。',
'D08':'panic containment/poisoned builder，fallible binder/UnsupportedCapability；catch不恢复abort或silent no-op。',
'D09':'无全局Tokio；Engine-local与worker-affine策略、线程/runtime/关闭所有权。',
'D10':'维护者预编译native和NuGet消费，不默认每entity Cargo；pins/锁闭包/patch/差分/升级。',
'D11':'完整source-driven梯度、小Core/领域Adapter，至少两个异质真实Engine验证，未来领域仅边界。',
'D12':'保留model/property/fuzz/race/AOT，区分恢复原型、author-side模型和独立Review。',
'D13':'native direct/batch/static fast path及原生/managed AOT完整成本；数值门槛有基线。',
'D14':'Rust DB mandatory，动态SeaQuery+SQLx与专用SeaORM比较；metadata/codec分开，typed batches/fallible binder。',
'D15':'保留Unknown/effect/protocol/local lifetime与fixed session lease；移除必需SeaORM trait/model编译前置。',
'D16':'SQL语义typed Fluent直接复用SeaQuery；不要求全LINQ/C# null补偿；CTE/window/join及backend拒绝。',
'D17':'可选static descriptor/DTO增量生成，手写static同等路径；不默认schema-specific Rust或C#SQL Provider。',
'D18':'原生Service/Body/connection+C#handler，ResponseFuture/body许可与H2retained bytes分开，Kestrel对照。',
'D20':'Rust DB必需，同nativehash新增C#entity；保留幂等/outbox/Unknown/close，不默认逐schema SeaORM构建。',
'D22':'细化既有ABI/lifetime/error，领域native对象不泄漏到Core。',
'D23':'细化薄绑定与metadata/DTO，不预设完整查询编译器。',
'D24':'异步桥与body/retirement验证，不自动共享runtime。',
'D25':'维护者build、clean no-Rust/RID-free消费及AOT发布完整矩阵。',
'D26':'异质Engine、差分/fuzz/race/成本，补silent-no-op与body许可负例。',
'D27':'B01–B08 Rust驱动/host/池/事务/codec/流/迁移，B04必需而非可选。',
'D28':'B09–B14 metadata/可选SG/native builder/binder/DTO/Fluent/关系，删除全LINQ与重复C#SQL任务。',
'D29':'原生Server成熟接缝和body预算，Kestrel对照/可选协议保持局部依赖。',
'D30':'B21–B24必须包含B04；PG/SQLite故障、no-Rust consumer、Windows/Linux AOT及完整负载。',
'D31':'源码/内部seam/patch/ABI/行为追溯，在既有三图内维护。',
'D32':'独立检查精确新commit/packet/contract hash；PR2–4旧Review不接受本轮修改。'}
for id,scope in Dsc.items():nodes[id]['specific_scope']=scope;nodes[id]['source_driven_amendment']=scope
# Same B IDs, corrected native implementation ownership.
B={
'B01':('Data接口与动态metadata边界','Data.Abstractions','Table<TEntity>, Column<TEntity,TValue>, DataSource/Session, typed descriptors','定义接口/limits/profile，static C#metadata和DTO；执行只到Rust；业务metadatahash不代表native已编译实体。','metadata/version/capability mismatch, malformed长度/null/shape','跨实体/类型负例，双侧descriptor golden，无managed产品provider','interfaces'),
'B02':('Rust PostgreSQL执行Adapter','Data.Postgres','SQLx Pg adapter; bounded physical Session lease','复用SQLx连接/协议/执行，SeaQuery+fallible参数binder；不重写PG协议或发布Npgsql产品后端。','断线、未消费结果、timeout、COMMIT响应丢失','真实PG执行/错误/stream/cancel/quarantine及Windows/Linux AOT','postgres'),
'B03':('Rust SQLite执行Adapter','Data.Sqlite','SQLx SQLite worker; native cancellation flag','复用worker/队列，不无条件Task.Run；WAL/FK/busy profile；取消标志与真正worker退休分开。','busy/progress中断、ack丢失、worker未退出、巨大cell','实库故障/worker退出，queue条数与bytes分开，AOT','sqlite'),
'B04':('必需Rust Database Host与生命周期','Data.NativeHost','Engine-local host, SessionExecutor, create/start/take_result/retire','拥有连接lease和bounded Engine-local runtime/持久池；query/cursor/tx持父lease，通过driver接口组合provider/tx，禁止循环依赖。','并发误用、close pending、parent先dispose、迟到callback','双provider组合，SafeHandle与single-writer区分，取消/retire竞态及native tools','host'),
'B05':('Rust事务、池恢复与Unknown','Data.Transactions','TxLifecycle/Outcome/ConnectionDisposition/LocalLifetime','按D15状态机；commit入线后断开不覆盖效果；Drop排队rollback不是确认；未知协议隔离。','lost commit reply、rollback未确认、reset失败','PG/SQLite故障、模型/性质、AOT及幂等恢复','transactions'),
'B06':('Rust有界结果批次与流','Data.Streaming','CursorFetch, OwnedRowBatch, bounded value chunks','row+byte预算推进SQLx流，单fetch/单未takebatch；cancel/break/decoder异常关闭cursor并保留cleanup owners。','单cell超budget、slow consumer、fetch_all全量分配、重复take','巨大值/early break/decoder throw/RSS长跑和AOT','streaming'),
'B07':('Rust fallible参数codec与边界值','Data.Codecs','LogicalValue tags; checked encode/decode; typed null','传播每个Arguments::add错误；u64窄化不unwrap；enum使用已支持整数/文本metadata，新native codec另发profile。','NaN、precision loss、unknown tag、invalid UTF8、u64溢出','逐类型双库往返/负例/fuzz/AOT，不默认stringify','codecs'),
'B08':('Rust迁移执行与版本ledger','Data.Migrations','Migration ID/hash/provider/from-to/transaction mode','显式部署；事务DDL与ledger原子，非事务DDL阶段恢复；不以启动schema-sync替代审核迁移。','同ID异hash、并发migration、权限失败/中断','双库迁移竞争、崩溃重入、兼容窗口','migrations'),
'B09':('最小查询绑定与metadata定义','Query.Binding','Versioned operation/metadata descriptors and native owner IDs','仅native操作/值/类型/owner契约；比较direct/batch，不实现完整C#SQL AST/优化器/方言。','mixed owner、unknown opcode/capability、length overflow','双侧编码与capability负例，direct/batch同源语义','binding'),
'B10':('可选静态descriptor与DTO生成','Query.Generator','Incremental descriptors; static constructors','static C#metadata/constructor/diagnostics，手写static同等可用；SG不联网/Cargo/依赖其他SG本轮输出，不捕获任意LINQ。','unsupported codec/constructor、不稳定输出、动态AOT依赖','增量/诊断/golden、新实体同nativehash、generated/manual AOT parity',None),
'B11':('Rust SeaQuery深度绑定与能力检查','Query.Native','Native CRUD/Condition/Expr and fallible binder','复用native AST/方言，先查backend能力；拒绝SQLite silent no-op，fallible binder与多named-window扩展单独评估。','row-lock/SELECT INTO/SEARCH CYCLE被忽略、CTE panic、编码失败','CRUD/join/CTE/window/group/subquery差分和真实双库结果','query'),
'B12':('静态C# DTO物化与异常清理','Data.Materialization','Static typed readers and projection constructors','native typed batch经shape/null/codec检查后直接构造DTO；constructor异常finally释放并关闭cursor；不做managed ORM身份图。','NULL到非空、窄化、constructor throw、retained buffer','手写static oracle/wrong shape/cleanup/AOT；生成器自己的任务验证同oracle parity',None),
'B13':('强类型runtime Fluent原生查询','Query.Fluent','Native-backed Query<TEntity> and scoped expression proxies','普通C#调用native builder；direct参考，batch优化须测；SQL三值语义，无IQueryable/Expression.Compile/SQL emitter。','single-writer竞态、seal后修改、cross-query expression、非法动态字段','typed编译负例，runtime predicates变化同nativehash，direct/batch成本',None),
'B14':('Rust显式关系CRUD与乐观并发','Orm.Relations','Metadata joins; NotSet/Null/Value changesets; version CAS','复用SeaQuery/SQLx实现显式Rust关系/CRUD/CAS；不把SeaQuery称完整ORM，不暗加EF tracking/lazy graph save；SeaORM专用profile独立。','tenant谓词遗漏、left join null-marker、CAS冲突、partial changeset','关系/跨tenant/CAS差分、原子事务/异常、AOT组合','relations')}
for id,(title,module,api,method,fail,verify,native) in B.items():
 n=nodes[id];n.update(title=title,module=module,candidate_api=api,method=method,failure_paths=[fail],specific_verification=[verify],selection_required=False,selection_status='not_applicable')
 n['outputs']=[f'NativeWeave:src/{module}/',f'NativeWeave:tests/{module}/',f'Plan:ledger/evidence/{id}/']
 if native:n['outputs'].append(f'NativeWeave:native/database/{native}/')
 n['write_scopes']=list(n['outputs'])
# Handwritten static materialization does not wait for optional code generation.
nodes['B12']['start_dependencies']=[x for x in nodes['B12']['start_dependencies'] if x!='B10']
if 'B09' not in nodes['B12']['start_dependencies']:nodes['B12']['start_dependencies'].append('B09')
for id in ('B21','B22','B23','B24'):
 n=nodes[id];n['conditional_dependencies']=[x for x in n['conditional_dependencies'] if x['task_id']!='B04'];n['selection_inputs']=[x for x in n['selection_inputs'] if x!='B04']
 for x in n['conditional_dependencies']:x['reason']='仅选中的可选Rust Server/协议包进入组合；Database Rust host B04始终必需。'
 if 'B04' not in n['acceptance_dependencies'] and 'B04' not in n['start_dependencies']:n['acceptance_dependencies'].append('B04')
 n['method']=n['method'].replace('纯C#','外部managed对照')+'；产品Database始终Rust，新普通实体复用预编译native资产。'
 n['specific_verification'].append('Required Rust DB; same native hash after supported entity changes; clean no-Rust and RID-free consumer; Windows/Linux Native AOT.')
for id in ('A13','A14','A15','A16','A22','A24'):
 nodes[id]['specific_verification'].append('维护者native构建/普通消费分开；source/closure/patch pins；same-native-hash entity；clean no-Rust/RID-free运行与升级ABI/行为差分。')
nodes['B17']['method']='复用Hyper Service/Body/connection/Tokio及Tower/Axum，比较Actix worker-affine与Pingora proxy；一个ForeignService接C#runtime handler/route，不重写网络核心。B17仍可选未选定，Kestrel AOT完整对照。'
nodes['B17']['specific_verification'].append('ResponseFuture/body许可、H2credit/retained bytes分开，callback retirement、TLS失败、shutdown_timeout不释放roots。')
for id in ('B16','B20','B22'):nodes[id]['specific_verification'].append('head完成但body仍活跃、slow reader/巨大chunk、completion/cancel/close竞争和callback roots；channel条数不是RSS上界。')
for g in graphs.values():
 g['graph_status']='source-driven-revision-proposed';g['revision']=REV;g['amendment']='Existing task IDs and gates retained; no product implementation authorization.'
 for n in g['nodes']:
  n['revision']=REV
  for c in n['contract_inputs']:
   if c['id'] in updated:c['version']=CV
  n['dependency_pins']={x:REV for x in n['start_dependencies']+n['acceptance_dependencies']}
  for c in n['conditional_dependencies']:c['revision']=REV
COMMON='''NativeWeave独立于ArcForges，ArcForges只参考格式。C#是应用开发层，正式消费必须Native AOT。Database底层必须Rust，managed驱动只作源码/基准对照；Rust Server可选且需证据。优先源码驱动深度复用；普通新实体使用预编译native能力，不默认Cargo/CI。自然typed Fluent优先，不要求完整IQueryable/EF，不在C#重写SQL AST/方言。SG可选生成static metadata/DTO，不是唯一查询路径。Core只提供可组合ABI/lifetime/buffer/error/async，无巨型runtime。保留严格安全和生产验收，不授权大规模产品实现。'''
BASE_TEXT='''## 当前输入与继续规则

启动PR #1已合并，不再从旧bootstrap分支重启。历史main：Design `baa953772d2a771bb4da3aff0cf4b4be6fc811a1`，Plan `da9e4a6337a5af0ec3d5e40a4695a2760d6ac5f5`。读取source-driven-baseline.json中的精确Design修订和当前Plan snapshot，分别记录design_commit/plan_commit；两个仓库不是原子更新，不能混用旧packet与新spec。

核对Task ID/revision/packet_sha256，从该snapshot建独立task/<ID>-<topic>分支。只补缺失研究，先读已提交report/evidence/follow-up；不要重复已有成果。技术决定、实现验证、生产接受分开。缺少真实subagent工具时不得模拟委派或独立Review。
'''
EVIDENCE='''## 证据、验证和独立接受

逐条记录repo/full commit/path/symbol/line ranges，跟踪正常、错误、取消、释放及测试；声明覆盖缺口和许可证/维护风险。下载不等于阅读，读测试不等于执行。区分source-confirmed/executed/inferred/pending/rejected；代码样例标记draft/compiled/executed/native-aot-executed。

产品验收保留对应Windows/Linux真实构建、PublishAot=true后执行、故障/竞态/性质/fuzz/适用模型、旧新版本、资源和完整负载。JIT不是AOT；有限模型不能证明weak-memory、whole-RSS或完整活性。保存命令/exit/stdout/stderr/OS/arch/toolchain/source+artifact hash/seed/oracle。平台缺失记blocked，不宣称未测的更快/零复制/完整能力。

提交独立Draft PR，由未主导修改的真实审查者检查精确新hash和证据；PR2–4旧Review不能替代本轮。现有校验器不认证reviewer身份或命令真实性。局部accepted满足各自门禁，不等全部研究，也不绕过Required Checks。本轮研究原型不是产品实现授权。
'''
def bullets(xs):return '\n'.join('- '+str(x) for x in xs) or '- 无。'
for kind,g in graphs.items():
 for n in g['nodes']:
  id=n['id'];text=f"# {id} — {n['title']}\n\nRevision: **{REV}**. State: **{n['status']}**.\n\n"+BASE_TEXT+'\n## 项目边界\n\n'+COMMON+'\n\n'
  text+='## 独占输出与并行范围\n\n'+bullets(n['outputs'])+'\n\nwrite_scopes：\n'+bullets(n['write_scopes'])+'\n\n共享图、registry和根索引由整合者处理；不要复制公共接口绕过依赖，无全局单任务锁。\n\n'
  text+='## 精确依赖\n\n开始：'+(', '.join(n['start_dependencies']) or '无')+'；接受：'+(', '.join(n['acceptance_dependencies']) or '无')+'。任务依赖revision '+REV+'。Research/Documentation引用不自动成为等待。\n\n契约：\n'+bullets([f"{c['id']}@{c['version']} requires {c['required_status']}" for c in n['contract_inputs']])+'\n\n'
  if n['conditional_dependencies']:text+='仅选中才生效：\n'+bullets([f"{c['task_id']}@{c['revision']}: {c['reason']}" for c in n['conditional_dependencies']])+'\n\n'
  if kind=='research':
   text+='## 研究问题与候选比较\n\n'+bullets(n['questions'])+'\n\n'+bullets(n['alternatives'])+'\n\n## 源码入口和异常路径\n\n'+bullets([x['repository'] for x in n['source_targets']])+'\n\n关键符号：'+('; '.join(n['symbol_targets']))+'\n\n'+bullets(n['failure_paths'])+'\n\n验证重点：'+n['verification']+'\n\n'
   text+='已有种子（不代表全任务完成）：\n'+bullets(n.get('initial_seed_refs',[]))+'\n\n'+n.get('initial_seed_note','')+'\n\n'
   text+='输出report/evidence/coverage：比较/来源/限制、API/状态机/不变量、成本及Design/Plan影响。仅补缺失调用链；跟进放在原R目录，不新建体系。交叉审查接口：'+', '.join(n.get('cross_review_by',[]))+'。\n\n'
  elif kind=='documentation':
   text+='## 具体编制责任\n\n'+n['specific_scope']+'\n\nResearch输入：'+', '.join(n['research_refs'])+'。\n\n'
   for rid in n['research_refs']:
    if rid in nodes:text+=f"### {rid} — {nodes[rid]['title']}\n"+bullets(nodes[rid].get('questions',[]))+'\n固定来源见实际R evidence；引用不等于已读。\n\n'
   text+='输出契约：'+', '.join(n.get('contract_outputs',[]))+'，版本以registry为准，不自动accepted。\n\n形成需求/非目标、固定源码、候选/理由、模块/API/ABI、正常异常/ownership/并发状态机、不变量、代码状态、构建/AOT/发布、性能内存、平台兼容、故障矩阵和具体Codex验收。保留正确正文，替换冲突假设，不只加原则段落。\n\n'
  else:
   text+='## 实施范围与方法\n\n模块：`'+n['module']+'`；研究：'+', '.join(n['research_refs'])+'；Design：'+', '.join(n['documentation_refs'])+'。\n\n候选API（未编译，以accepted契约为准）：\n```text\n'+n['candidate_api']+'\n```\n\n'+n['method']+'\n\n## 异常与具体验收\n\n'+bullets(n['failure_paths'])+'\n\n'+bullets(n['specific_verification'])+'\n\n运行矩阵：'+json.dumps(n['verification_requirements'],ensure_ascii=False)+'。\n\n'
   text+='planned_candidate不是实施授权：任务须planned，精确契约accepted、必要局部依赖有证据且implementation_authorization获准。代码/测试/fixtures和完整日志hash进入本任务ledger；未运行不accepted。可选Server/协议局部选择，Database native必需。\n\n'
  text+=EVIDENCE+'\n正式入口IzuSharp/NativeWeave-Design和IzuSharp/Plan；本轮不在IzuSharp/NativeWeave写完整产品实现。报告实际研究/编制/验证和准确PR/commit，不重复总规划。\n'
  (P/n['prompt']).write_text(text);n['packet_sha256']=hashlib.sha256(text.encode()).hexdigest()
for name,g in graphs.items():(P/f'{name}-graph.json').write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n')
baseline={'design_main':'baa953772d2a771bb4da3aff0cf4b4be6fc811a1','plan_main':BASE,'design_pr':5,'design_amendment_commit':DESIGN,'task_revision':REV,'contract_registry_sha256':hashlib.sha256((D/'docs/contracts/registry.json').read_bytes()).hexdigest(),'review_status':'independent_review_pending','product_implementation_authorized':False}
(P/'source-driven-baseline.json').write_text(json.dumps(baseline,indent=2)+'\n')
index='# NativeWeave task index — source-driven revision 0.2.0\n\nExisting 34 Research, 32 Documentation, 48 candidate Delivery IDs retained. Exact paired Design commit: source-driven-baseline.json. No product implementation authorized.\n\n'
for kind,g in graphs.items():
 index+='## '+kind+'\n\n| ID | Task / packet | State |\n|---|---|---|\n'
 for n in g['nodes']:index+=f"| {n['id']} | [{n['title']}]({n['prompt']}) | {n['status']} |\n"
 index+='\n'
(P/'task-index.md').write_text(index.rstrip()+'\n')
for path in ['README.md','AGENTS.md','execution-policy.md','documentation-policy.md','research-policy.md','milestones.md','acceptance-register.md','prompts/independent-review.md']:
 p=P/path;s=p.read_text()
 if path=='README.md':
  a=s.index('## 首次启动输入定位');b=s.index('## 三张图的职责',a)
  s=s[:a]+BASE_TEXT+'\n'+COMMON+'\n\n修订proposed；34R/32D/48Delivery保留，21契约仍未接受，产品未授权。R25/R27部分源码/实验进入follow-up；其他任务沿既有证据继续。\n\n'+s[b:]
  s=s.replace('查询IR/LINQ捕获/SQL方言/static mapper/动态安全API/关系','薄绑定metadata/可选static生成/Rust builder与binder/static DTO/runtime Fluent/显式关系')
 s=s.replace('纯C#路线不等待未选择native分支','无数据库C#应用不等待未选Server；Database Rust host必需').replace('纯C#组合不等待未选native','无数据库C#组合不等待未选Server')
 s+='\n\n## Source-driven amendment (2026-11-12)\n\n'+COMMON+'\n\n读取source-driven-baseline.json、同ID新packet和Design ADR-0002。独立Review检查新hash、backend拒绝、fallible binder、无逐实体Cargo、Server body/retirement、三图和未完成验证。旧Review不接受新内容；不增加规划层。\n'
 p.write_text(s)
print('Revised',len(nodes),'existing packets; same three graphs; no product authorization.')
