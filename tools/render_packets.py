#!/usr/bin/env python3
"""Render existing graph semantics into the existing 114 packets and 10 fragments.
This does not create tasks, reset status, or supply new architecture."""
from pathlib import Path
import json,hashlib
p=Path(__file__).resolve().parents[1]
load=lambda f:json.loads(Path(f).read_text())
dump=lambda f,x:Path(f).write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n")
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
graphs={k:load(p/(k+'-graph.json')) for k in ['research','documentation','delivery']}
nodes={n['id']:n for g in graphs.values() for n in g['nodes']}
ver=graphs['delivery']['revision']
registry=load(p.parent/'NativeWeave-Design/docs/contracts/registry.json')
contracts={c['id']:c for c in registry['contracts']}
fragments={'D22':('interop-foundation',['A01','A02','A03','A04','A05']),'D23':('generation',['A09','A10','A11','A12']),'D24':('async-runtime',['A06','A07','A08']),'D25':('build-release',['A13','A14','A15','A16']),'D26':('verification-engines',['A17','A18','A19','A20','A21','A23']),'D27':('database',[f'B{i:02d}' for i in range(1,9)]),'D28':('orm',[f'B{i:02d}' for i in range(9,15)]),'D29':('server',[f'B{i:02d}' for i in range(15,21)]),'D30':('end-to-end',[f'B{i:02d}' for i in range(21,25)]),'D31':('evolution',['A22','A24'])}
(p/'fragments').mkdir(exist_ok=True)
mirrored=['title','boundary_and_ownership','native_reuse','csharp_surface','implementation_steps','error_cancellation_resources_concurrency','specific_acceptance','write_scopes','dependency_rationale','verification_matrix']
for did,(name,ids) in fragments.items():
 content={'schema_version':'1.0.0','documentation_task_id':did,'revision':ver,'role':'Detailed implementation instructions for existing tasks; delivery-graph.json is the sole scheduling graph.','delivery_task_ids':ids,'design_inputs':[{'id':ref,'outputs':nodes[ref]['outputs']} for ref in nodes[did]['research_refs']+nodes[did]['documentation_refs']],'task_details':{id:{k:nodes[id][k] for k in mirrored} for id in ids},'worktree_policy':'One branch/worktree per task, exact owned scopes; root solution/Cargo workspace registration is an A13 integration patch under the small workspace-manifest lock. No global worker lock.','phase_authorization':'No product writes or A/B execution authorized in this research/design turn.'}
 if did=='D31':content['evolution_rules']=['Four independent identities: source/crate, C ABI, C# API and domain semantics; record relation rather than merge versions.','Any changed accepted input invalidates dependent review by exact hash/revision snapshot; re-review affected slice, not every unrelated task.','Controlled fork requires upstream base/patch queue/license/security owner/exit condition and direct-native regression oracles.','New Engine uses existing schema/contracts and a scoped task/fragment amendment in the existing three graphs, no fourth workflow.','No automatic production dependency promotion; security exception records reason and exact update evidence.']
 dump(p/'fragments'/f'{name}.json',content)
# Render all 114 self-contained packets from current task semantics; no obsolete appended policy text survives.
def bullets(items):
 if isinstance(items,str):return items+'\n'
 return '\n'.join('- '+('; '.join(str(v) for v in x) if isinstance(x,list) else str(x)) for x in items)+'\n'
def reference_table(n):
 rows=['| 输入 | 精确要求 |','| --- | --- |']
 rows += [f'| {id} | task revision {v}；来源和接受证据由三图绑定 |' for id,v in n['dependency_pins'].items()]
 rows += [f'| {c["id"]} | {c["version"]}；`{contracts[c["id"]]["spec_path"]}`；SHA-256 `{contracts[c["id"]]["content_sha256"]}`；以同内容接受记录为准 |' for c in n['contract_inputs']]
 return '\n'.join(rows)
mandate='C# 是强类型应用层；数据库/ORM 查询关系和 Server 网络协议运行时必须由成熟 Rust 引擎实现。Kestrel/托管驱动只比较。普通 Entity/DTO/Handler 使用维护者预编译 native 模块，正常 dotnet build/run 与 AOT；不重写 C# SQL AST/方言/完整 LINQ，不引入强制巨型 Core runtime。'
for kind,g in graphs.items():
 for n in g['nodes']:
  id=n['id'];s=f'# {id} — {n["title"]}\n\n任务修订 **{ver}**。所属图 `{kind}-graph.json`；当前状态、精确来源 Commit 与接受记录以图为准。本文是现有114份独立任务说明之一。\n\n## 目标与阶段\n\n{mandate}\n\n当前只执行 Research/Documentation 与 Design 研究原型；未来 Delivery 实施仍需明确阶段授权。设计接受不冒充产品、长负载或发布通过。\n\n## 输入、依赖和版本\n\n{reference_table(n)}\n\n开始依赖：{", ".join(n["start_dependencies"]) or "无任务完成前置"}。接受依赖：{", ".join(n["acceptance_dependencies"]) or "无额外任务完成前置"}。研究引用：{", ".join(n["research_refs"]) or "本项实际源码"}。规范引用：{", ".join(n["documentation_refs"]) or "本项输出/registry"}。引用提供追溯，未列为依赖的引用不制造全局等待。\n\n## 文件所有权\n\n'+bullets(n['write_scopes'])
  if kind=='delivery':
   s+=f'\n独立 Worktree/分支：`{n["parallel_worktree"]}`。只改上述 scope；根 solution/Cargo workspace/共享构建文件由 A13 整合补丁，禁止抢写其他模块或锁住全部 worker。\n\n## 模块与接口\n\n{n["boundary_and_ownership"]}\n\nC# 接口：\n\n'+bullets(n['csharp_surface'])+'\nRust 原生复用：\n\n'+bullets(n['native_reuse'])+'\n## 实施步骤\n\n'+'\n'.join(f'{i+1}. {v}' for i,v in enumerate(n['implementation_steps']))+'\n\n## 错误、取消、内存与并发\n\n'+bullets(n['error_cancellation_resources_concurrency'])+'\n## 验收要求\n\n'+bullets(n['specific_acceptance'])+'\n'+bullets(list(n['verification_matrix'].values()))+f'\n依赖理由：{n["dependency_rationale"]}\n\n## 交付与审查\n\n提交真实产品变更、对应测试/日志/制品 SHA、原生与 C# 输入身份、失败记录及独立技术审查；证据写入 Plan:ledger/evidence/{id}/。既有 Design 实验是实现 oracle，不能复制其 passed 当作本项通过。只有当前图的实现授权、相关契约和局部依赖成立才可执行。\n'
  elif kind=='research':
   s+='\n## 已有成果与研究范围\n\n先阅读现有报告/evidence/coverage，按 takeover audit 区分状态滞后与真实缺口；完整成果只复核，不重做。\n\n'+bullets(n['outputs'])+'\n研究问题：\n\n'+bullets(n.get('questions',[]))+'\n源码机制：\n\n'+bullets(n.get('symbol_targets',[]))+'\n## 实际执行与异常路径\n\n'+bullets(n.get('failure_paths',[]))+'\n1. 固定实际源码/版本/commit/crate checksum/features；仅列真正读过的符号与范围。\n2. 区分上游测试已读、研究实验已运行、产品验证待实现；正常/失败/关键边界建立可追溯结论。\n3. 适当实验保存完整命令、输入/输出 hash、目标平台、实际运行及保留失败；未执行不得标通过。\n4. 明确技术决定、替代方案取舍和剩余产品义务，直接修正旧冲突，不只叠加附录。\n5. 接受前独立技术审查精确输出，修复阻断，再绑定当前 graph subject 与真实证据。\n\n## 完成依据\n\n'+str(n.get('verification','固定源码与必要实验及独立审查。'))+'\n\n当前实质成果以 report.md/evidence.json/coverage.json 为准；后续只在来源或接口变化时重开受影响范围。研究阶段不依赖未来产品先实现。\n'
  else:
   s+='\n## 规范范围与具体输出\n\n'+n['specific_scope']+'\n\n'+bullets(n['outputs'])+'\n## 编制与接受步骤\n\n1. 读相关已存在研究与固定源码/实验，复用成功结果；区分本文新决定与历史观察。\n2. 给出明确 Rust/C# 接口、原生成熟能力复用、ABI/状态机/所有权/线程/取消/错误/释放和平台规则。\n3. 定义普通预编译消费、静态 AOT 映射、必要实现例子与可执行测试验收，不让产品实现成为设计的循环前置。\n4. 将真实未来义务落入现有 Delivery IDs、文件 scope、局部依赖和 Worktree；fragment 只细化现有图。\n5. 独立审查规范与研究/契约/任务一致性，修复全部阻断，绑定精确 hash/version/来源。\n\n## 审查证据\n\n契约输出：'+(', '.join(n.get('contract_outputs',[])) or '无独立契约；现有任务详细说明/整体独立审查')+'。registry 和图保存当前正式接受证据；此 packet 不自授接受。产品长期负载、真实发布和生产支持依旧由 Delivery 证明。\n'
  file=p/n['prompt'];file.parent.mkdir(parents=True,exist_ok=True);file.write_text(s);n['packet_sha256']=sha(file)
for kind,g in graphs.items():dump(p/(kind+'-graph.json'),g)
# Canonical inventory remains exactly 114 IDs.
s='# NativeWeave 任务索引\n\n现有三图：34 Research、32 Documentation、48 未来 Delivery。修订0.3.0；状态/接受以图为准，产品实施当前未授权。\n'
for kind,g in graphs.items():
 s+=f'\n## {kind}\n\n| ID | 任务 | 独立说明 |\n| --- | --- | --- |\n'
 for n in g['nodes']:s+=f'| {n["id"]} | {n["title"]} | [{n["id"]}]({n["prompt"]}) |\n'
(p/'task-index.md').write_text(s)
print('updated 114 nodes/packets, 10 required fragments; no product files written')
