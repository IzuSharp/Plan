#!/usr/bin/env python3
"""One-time localized continuation, not a new graph or blanket product approval."""
from pathlib import Path
import hashlib,json,os,re,subprocess
P=Path.cwd();D=P.parent/'NativeWeave-Design';BASE='f082d4542dcbb59dad344ae2ab7b4a1126a30988'
DESIGN=os.environ['NW_DESIGN_COMMIT'];assert subprocess.check_output(['git','-C',str(D),'rev-parse','HEAD'],text=True).strip()==DESIGN
for name in subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],text=True).splitlines():
    if (P/name).read_bytes()!=subprocess.check_output(['git','show',BASE+':'+name]):raise RuntimeError('Preimage drift '+name)
def put(p,s):
    p=P/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s.rstrip()+'\n')
def dump(p,o):put(p,json.dumps(o,ensure_ascii=False,indent=2))
reg=json.loads((D/'docs/contracts/registry.json').read_text());cversions={c['id']:c['version'] for c in reg['contracts']}
graphs={k:json.loads((P/(k+'-graph.json')).read_text()) for k in ['research','documentation','delivery']}
nodes={n['id']:n for g in graphs.values() for n in g['nodes']};assert len(nodes)==114
notes={
'R01':'Rust1.100真实release/compiler/Cargo及源码、两OS13项unit/13项command已记录；继续缺失.NET/编译器范围，不重复成功Rust probes。',
'R03':'extern custom不是P/Invoke；内部never/Allocator不改变固定C ABI。构建实际layout/错误/owned-buffer探针，不伪造C-ABI已接受。',
'R04':'Rust1.100+C#静态LibraryImport的Windows/Linux真实AOT ABI切片；保持回调、borrowed length和SafeHandle寿命前置。',
'R07':'DropGuard仅简化同步局部rollback；Box/Arc map不用于已发布句柄，allocator owner不能早于所有lease释放。',
'R09':'DropGuard/Drop不会await；不删除create/start/take_result/retire或取消静默规则。',
'R10':'稳定Allocator作用于自身分配，不控制SeaQuery嵌套String/Vec或整个RSS；grow成功旧pointer失效，错误保留。',
'R11':'allocator方法和Drop不得unwind；catch_unwind不覆盖abort/OOM；never仅内部类型，不跨ABI。',
'R13':'Rust/Cargo1.100，Cargo JSON compiler-artifact定位，worktree缓存与目标资产分开；保留clean no-Rust/AOT矩阵。',
'R14':'Cargo unused-dependencies有target/dev/feature边界；min-publish-age不审计已锁定/无timestamp依赖，7day是政策不是安全证明。',
'R17':'Box/Arc map指针相同只为当前实现观察；PGO和cache收益须完整负载，不发布target-cpu=native。',
'R18':'最新stable机制只缩减必要glue，不新增全局allocator/Tokio；保留独立Engine源码/patch升级责任。',
'R22':'现有SeaQuery/SQLx closure须用1.100真实编译；fallible Arguments::add/整数窄化，不能拿MSRV元数据当通过。',
'R25':'结合SeaORM dynamic补充，对比普通动态metadata路线；不逐entity Cargo、不完整C#SQL Provider；Rust升级不自动换库。',
'R27':'在1.100实际执行native Service/Body生命周期切片，避免仅有抽象模型；Rust Server仍需Kestrel比较。',
'D01':'把新R01准确工具链/目标事实纳入；13Rust测试不是C#AOT或平台生产认证。',
'D02':'落实repr(C)、状态、大小/offset与borrow/owner，禁止custom/Rust ABI；从R03/R04可执行探针形成规范。',
'D07':'原始所有者/allocator释放和failed-grow安全；外层Vec不是whole-RSS预算。',
'D10':'C-BUILD新version；Cargo JSON/独立worktree缓存/锁文件/age与lint边界，普通消费仍不需要Rust。',
'D11':'C-ENGINE新version；DropGuard和map仅局部内部，不替换quiescence。',
'D16':'修正SQL3VL nullable NOT比较的过宽禁令，区别C#补偿；保留NaN/自定义比较限制。',
'D32':'用户允许PR5/PR2严格自审合并，但独立审查未发生；记录后续精确snapshot复审，不阻塞可执行独立研究，也不接受未完成产品。',
'A03':'未来实施可用Rust1.100 owner-aware Vec/Box；仍要接受的Buffer/ABI规范，allocator不可unwind、grow失效明确。',
'A05':'局部DropGuard只做nonblocking no-panic回滚；不以新语法删callback静默状态。',
'A13':'cargo build/test --locked；从JSON找cdylib，不能猜1.100改变的中间目录；rust-version和toolchain分别记录。',
'A14':'实际Linux1.100 native/AOT包验证；目标ABI/CPU，不能外推Windows。',
'A15':'实际Windows1.100 native/AOT包验证；证据LF/CRLF原始hash分别记录。',
'A16':'NuGet maintainer原生产物与普通消费隔离，RID-free开发/无Rust机器仍须实测。',
'A22':'never/Infallible coherence、Box allocator推断和Cargo布局变更进入升级负例，源锁及完整闭包。',
'A24':'脚手架使用1.100稳定能力和小Core；异质Engine，不把PGO/分配器profile强加所有模块。',
'B07':'显式fallible绑定，不用Arc::new_in等仍nightly扩展；大小/NULL/窄化失败必须发生在DB发送前。',
'B11':'保留SeaQuery1.0.2主体pin；binder0.9.1需单独compat验证，不能混用crate与Git证据。',
'B17':'实际native Service/Body probe独立于数据库；仍需正式已接受Core契约后转生产。'}
affected=set(notes)
for n in nodes.values():
    if any(c['version']!=cversions[c['id']] for c in n['contract_inputs']):affected.add(n['id'])
# Only actual dependency-version propagation, not wholesale task rewriting.
while True:
    more={n['id'] for n in nodes.values() if any(d in affected for d in n['start_dependencies']+n['acceptance_dependencies']+[x['task_id'] for x in n['conditional_dependencies']])}
    if more<=affected:break
    affected|=more
for id in affected:nodes[id]['revision']='0.2.1'
nodes['R01']['status']='partially_evidenced'
ref='NativeWeave-Design:docs/research/topics/R01/rust-1.100.md'
nodes['R01'].setdefault('initial_seed_refs',[]).append(ref)
nodes['R01']['outputs'].append(ref)
# R01 already owns its topic directory. Experimental shared scripts are integrator artifacts, not hidden task ownership.
for n in nodes.values():
    if n['id'] not in affected:continue
    n['dependency_pins']={d:nodes[d]['revision'] for d in n['start_dependencies']+n['acceptance_dependencies']}
    for c in n['contract_inputs']:c['version']=cversions[c['id']]
    for c in n['conditional_dependencies']:c['revision']=nodes[c['task_id']]['revision']
    text=(P/n['prompt']).read_text().replace('Revision: **0.2.0**','Revision: **0.2.1**')
    if n['id']=='R01':text=text.replace('State: **planned**','State: **partially_evidenced**')
    for c in n['contract_inputs']:
        text=re.sub(re.escape(c['id'])+r'@\d+\.\d+\.\d+-draft',c['id']+'@'+c['version'],text)
    pins=', '.join(d+'@'+v for d,v in sorted(n['dependency_pins'].items())) or '无'
    text=text.replace('任务依赖revision 0.2.0。','精确依赖revision：'+pins+'。')
    for c in n['conditional_dependencies']:
        text=re.sub(re.escape(c['task_id'])+r'@0\.2\.0:',c['task_id']+'@'+c['revision']+':',text)
    if n['id'] in notes:
        n['rust1100_impact']=notes[n['id']]
        text+='\n## Rust1.100局部修订（2026-11-12）\n\n'+notes[n['id']]+'\n依据：Design docs/research/topics/R01/rust-1.100.md及精确source-driven-baseline.json。原有正确性、平台与独立产品接受门禁不变；当前用户授权按真实门禁实际执行，不重复成功研究。\n'
    put(n['prompt'],text);n['packet_sha256']=hashlib.sha256((P/n['prompt']).read_bytes()).hexdigest()
for n in nodes.values():
    for component in (n.get('release_scope') or {}).get('components',[]):
        component['revision']=nodes[component['task_id']]['revision']
for k,g in graphs.items():g['revision']='0.2.1';dump(k+'-graph.json',g)
# Localized policy corrections replace stale contradictory statements.
p=P/'execution-policy.md';s=p.read_text().replace('本政策规划未来实施，不授权本次研究会话开始完整产品开发。','本政策管理实际并行执行。2026-11-12用户已授权按现有真实门禁推进实施；不再需要逐步询问。')
a=s.index('纯C# Data/Query/Kestrel');b=s.index('\n\n',a)
s=s[:a]+'Database底层必需Rust；不存在产品纯C#Data/Query fallback。Kestrel、独立研究/fixture和无数据库应用不等待全部Interop实现。正式native产品功能只依赖所需accepted契约/实现，不制造全局等待，也不把研究探针当阶段A生产验收。'+s[b:]
a=s.index('B04原生PostgreSQL');b=s.index('\n\n',a)
s=s[:a]+'B04是必需Rust Database Host，B02/B03是Rust providers。B17原生Server、B18 gRPC、B19 MCP才是独立可选路线。选择状态进入对应B21–B24验收快照；新增组合必须复验，不能复用旧组合报告。'+s[b:]
s=s.replace('不授权大规模产品实现。','实施授权以当前用户请求和精确任务门禁为准；不得把候选任务直接标为已验收。')
s+='''

## 本轮文档合并例外与后续执行

用户当前明确授权Design PR5/Plan PR2在真实独立Reviewer不可用时，严格自审、可执行检查通过、无未解决文档阻断项后合并；如实标记self-review并保留D32独立复审。此例外不绕过GitHub强制规则，不将作者冒充独立Reviewer，不自动接受技术契约或Delivery终结态。

合并后直接从ready/continuable开始实际源码/编译工作。Research/Documentation下的小型可执行fixture可以作为已有研究任务输出，不伪装成已满足A01/B01等全部产品前置。产品实施任务仍须自己的精确accepted契约、依赖与授权记录；这是真实技术门禁，不是要求用户再次批准。
''';put('execution-policy.md',s)
put('acceptance-register.md','''# 当前接受状态与历史证据

精确任务状态/revision/hash以三图为准，契约以Design registry为准，配对输入见source-driven-baseline.json。不要继续把初始0.1.1提示词或全部0.1.0契约当当前状态；历史启动记录保留在Git。

当前34R/32D/48候选Delivery ID不变。R01/R25/R27有部分证据，可继续研究而非被错误永久blocked；其余任务按图状态推进。契约仍proposed，文档合并不自动产生生产accepted。已有原始Linux/SQLite C#AOT实验和新增Windows/Linux Rust1.100 API实验分别保留，不能互相替代，也不代表完整产品验收。

用户对Design PR5/Plan PR2允许严格自审合并的范围见execution-policy.md。独立复审仍待D32；不能虚构Review。正式产品终结态继续校验独立Review、真实AOT/平台/故障/资源证据。下一批实际fixture按已有R/D任务执行以补齐前置，不重复总规划。
''')
for path in ['README.md','AGENTS.md','documentation-policy.md','prompts/independent-review.md']:
    s=(P/path).read_text();s+='''

## 2026-11-12 Rust1.100连续执行授权

当前稳定Rust/Cargo1.100研究与真实两OS测试见Design R01。Design PR5/Plan PR2可按用户明确例外经严格self-review和真实检查合并，独立审查未完成必须保留D32复审；不绕过GitHub门禁或伪造accepted契约。普通技术任务不再逐个询问。按图ready/continuable实际执行；没有accepted前置的Delivery保持候选，先执行已有R/D的真实源码/编译fixture。旧“仅规划、当前全面不授权执行”指的是历史启动轮，不覆盖此次授权。
''';put(path,s)
# Preserve accepted gates; expose resumable R/D separately from new start readiness.
p=P/'tools/validate_graphs.py';s=p.read_text();needle=' def run(self):\n'
method=''' def continuable(self):
  result={'research':[],'documentation':[],'delivery':[]}
  if self.errors:return result
  states={'research':{'in_progress','partially_evidenced','review_ready'},'documentation':{'drafting','partially_evidenced','review_ready'}}
  for nid,n in self.nodes.items():
   kind=self.kind[nid]
   if n.get('status') not in states.get(kind,set()):continue
   if any(self.nodes.get(d,{}).get('status') not in TERMINAL for d in n.get('start_dependencies',[])):continue
   result[kind].append(nid)
  return result

'''
assert needle in s;s=s.replace(needle,method+needle)
s=s.replace("'ready':ready,'blocked':blocked","'ready':ready,'continuable':self.continuable(),'blocked':blocked")
# Registry paths are local to Design, while evidence manifest paths are repository qualified.
s=s.replace("raw=self.require_file_hash(c.get('spec_path'),c.get('content_sha256'),where+'/spec')","spec_ref=c.get('spec_path')\n  if isinstance(spec_ref,str) and ':' not in spec_ref:spec_ref='NativeWeave-Design:'+spec_ref\n  raw=self.require_file_hash(spec_ref,c.get('content_sha256'),where+'/spec')")
put('tools/validate_graphs.py',s)
base=json.loads((P/'source-driven-baseline.json').read_text())
base.update(design_amendment_commit=DESIGN,contract_registry_sha256=hashlib.sha256((D/'docs/contracts/registry.json').read_bytes()).hexdigest(),task_revision_policy='0.2.1 only for affected packets and actual dependency-pin propagation; others remain0.2.0',review_status='self_review_user_exception_independent_followup_pending',user_execution_authorization='conditional on existing task gates; no repeated user confirmation',rust_toolchain='1.100.0')
base.pop('task_revision',None)
dump('source-driven-baseline.json',base)
dump('verification/rust1100-impact.json',{'design_commit':DESIGN,'plan_input':os.environ.get('GITHUB_SHA'),'affected_task_ids':sorted(affected),'unaffected_task_ids':sorted(set(nodes)-affected),'counts':{k:len(g['nodes']) for k,g in graphs.items()},'review':'self-review, not independent','formal_delivery_auto_accepted':False})
# Keep original index links/titles; only state entry and revision note change.
s=(P/'task-index.md').read_text().replace('source-driven revision 0.2.0','source-driven Rust1.100 revision').replace('| R01 | [稳定工具链与现代语言机制](research-tasks/R01.md) | planned |','| R01 | [稳定工具链与现代语言机制](research-tasks/R01.md) | partially_evidenced |')
put('task-index.md',s+'\nTask revisions are exact per graph; unaffected packets were not rewritten. R/D continuation is distinct from product acceptance.\n')
print(json.dumps({'affected_packets':len(affected),'preserved_packets':len(nodes)-len(affected),'design_commit':DESIGN,'independent_review':False}))
