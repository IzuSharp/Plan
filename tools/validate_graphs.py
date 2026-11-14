#!/usr/bin/env python3
"""NativeWeave three-graph structural and local-evidence consistency validator.

No network, no dependencies. It validates local manifests and hashes, not human
identity or whether an asserted command really ran. Acceptance still requires
independent review of source, logs and platform execution evidence.
"""
from __future__ import annotations
import argparse
from datetime import datetime
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath

VERSION = '1.0.0'
TERMINAL = {'accepted', 'delivered', 'complete', 'completed', 'done', 'verified'}
STATUSES = {
 'research': {'planned','in_progress','partially_evidenced','review_ready','accepted','failed','blocked'} | TERMINAL,
 'documentation': {'draft_ready','drafting','partially_evidenced','review_ready','accepted','failed','blocked'} | TERMINAL,
 'delivery': {'planned_candidate','planned','in_progress','partially_verified','review_ready','accepted','failed','blocked'} | TERMINAL,
}
READY_STATES = {'research': {'planned'}, 'documentation': {'draft_ready'}, 'delivery': {'planned'}}
REPOS = {'Plan','NativeWeave-Design','NativeWeave'}
SHA256 = re.compile(r'^[0-9a-f]{64}$')
GITSHA = re.compile(r'^[0-9a-f]{40}$')
PLACEHOLDERS = {'','unassigned','todo','tbd','placeholder','template','unknown'}
NODE_FIELDS = {'id','title','phase','status','owner_role','start_dependencies','acceptance_dependencies','contract_inputs','research_refs','documentation_refs','outputs','write_scopes','resource_locks','prompt','acceptance_evidence','independent_reviewers','revision','author','packet_sha256','dependency_pins','conditional_dependencies','selection_inputs'}
RUN_KINDS = {'experiment_run','native_aot_run','build_run','model_check','conformance_run'}
EVIDENCE_KINDS = RUN_KINDS | {'source_read','official_documentation','design_analysis','static_review'}
ARCHITECTURE_POLICY = {
 'database_engine':'Rust', 'orm_query_relations_engine':'Rust', 'server_engine':'Rust',
 'server_host_task':'B17', 'server_application_task':'B15', 'kestrel_role':'comparison_only',
 'ordinary_entity_requires_rust_rebuild':False, 'managed_sql_ast_or_dialect':False,
 'full_linq_compatibility_goal':False, 'mandatory_global_runtime':False,
}
FRAGMENT_MIRROR_FIELDS = {
 'title','boundary_and_ownership','native_reuse','csharp_surface','implementation_steps',
 'error_cancellation_resources_concurrency','specific_acceptance','write_scopes',
 'dependency_rationale','verification_matrix',
 'api_design_inputs','api_design_input_sha256','api_contract_types',
 'api_surface_responsibility','documentation_owner_role','documentation_outputs',
}


def canonical_digest(value):
 return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()


def node_digest(node):
 excluded={'status','acceptance_evidence','independent_reviewers','implementation_authorization','source_commit'}
 return canonical_digest({k:v for k,v in node.items() if k not in excluded})


def valid_identity(value):
 return isinstance(value,str) and value.strip().lower() not in PLACEHOLDERS


def scope_contains(owner,output):
 ro,po=path_parts(owner);rt,pt=path_parts(output)
 return ro==rt and (po.rstrip('/')==pt.rstrip('/') or (po.endswith('/') and pt.startswith(po)))


def path_parts(scope):
 if not isinstance(scope,str) or ':' not in scope:
  raise ValueError('path must be repository-qualified: Repository:relative/path')
 repo,path=scope.split(':',1)
 p=PurePosixPath(path)
 if repo not in REPOS or not path or p.is_absolute() or '..' in p.parts or '\\' in path or path.startswith('./'):
  raise ValueError('unsafe or unknown repository path: '+scope)
 if str(p).rstrip('/') != path.rstrip('/'):
  raise ValueError('noncanonical path: '+scope)
 return repo,path


def scopes_overlap(a,b):
 ra,pa=path_parts(a);rb,pb=path_parts(b)
 if ra!=rb: return False
 if pa.rstrip('/')==pb.rstrip('/'): return True
 return (pa.endswith('/') and pb.startswith(pa)) or (pb.endswith('/') and pa.startswith(pb))


def cycles(nodes,edges):
 color={}; stack=[]; found=[]
 def walk(v):
  color[v]=1;stack.append(v)
  for w in edges(v):
   if w not in nodes: continue
   if color.get(w,0)==0: walk(w)
   elif color.get(w)==1:
    found.append(stack[stack.index(w):]+[w])
  stack.pop();color[v]=2
 for v in nodes:
  if not color.get(v): walk(v)
 return found


class Validator:
 def __init__(self, plan_root):
  self.plan=Path(plan_root).resolve(); self.bundle=self.plan.parent
  self.errors=[];self.warnings=[];self.graphs={};self.nodes={};self.kind={};self.contracts={};self.conflicts=[]
  self.checked_contracts=set();self.checking_contracts=set()

 def err(self,code,msg): self.errors.append({'code':code,'message':msg})
 def warn(self,code,msg): self.warnings.append({'code':code,'message':msg})
 def resolve(self,value):
  repo,p=path_parts(value);base=self.plan if repo=='Plan' else self.bundle/repo
  result=(base/p).resolve()
  if not result.is_relative_to(base.resolve()): raise ValueError('path escapes repository')
  return result
 def read_json(self,path,code='JSON'):
  try: return json.loads(Path(path).read_text())
  except (ValueError,OSError) as e: self.err(code,f'{path}: {e}');return None
 def require_file_hash(self,ref,sha,where):
  if not isinstance(sha,str) or not SHA256.fullmatch(sha):
   self.err('HASH_REQUIRED',f'{where}: valid sha256 required');return None
  try: p=self.resolve(ref)
  except (ValueError,TypeError) as e: self.err('PATH',f'{where}: {e}');return None
  if not p.is_file(): self.err('FILE_MISSING',f'{where}: {ref}');return None
  raw=p.read_bytes()
  if hashlib.sha256(raw).hexdigest()!=sha:
   self.err('HASH_MISMATCH',f'{where}: {ref}');return None
  return raw

 def manifest(self,record,where):
  if not isinstance(record,dict): self.err('MANIFEST',f'{where}: record must be object');return None
  raw=self.require_file_hash(record.get('manifest_path'),record.get('sha256'),where)
  if raw is None:return None
  try: obj=json.loads(raw)
  except (ValueError,UnicodeError): self.err('MANIFEST_JSON',where);return None
  if not isinstance(obj,dict) or obj.get('schema_version')!=VERSION:
   self.err('MANIFEST_SCHEMA',f'{where}: schema_version must be {VERSION}');return None
  if obj.get('is_template') is not False:
   self.err('TEMPLATE_EVIDENCE',f'{where}: is_template must be explicitly false');return None
  return obj

 def evidence(self,records,subject,where):
  out=[]
  if not isinstance(records,list) or not records:
   self.err('EVIDENCE_REQUIRED',where);return out
  for i,r in enumerate(records):
   key=f'{where}/evidence/{i}';m=self.manifest(r,key)
   if m is None:continue
   if m.get('subject')!=subject:self.err('EVIDENCE_SUBJECT',key)
   if m.get('status')!='passed':self.err('EVIDENCE_NOT_PASSED',key)
   if m.get('kind') not in EVIDENCE_KINDS:self.err('EVIDENCE_KIND',key)
   if not valid_identity(m.get('producer')):self.err('EVIDENCE_PRODUCER',key)
   if not m.get('recorded_at'):self.err('EVIDENCE_DATE',key)
   artifact=m.get('artifact',{})
   self.require_file_hash(artifact.get('path'),artifact.get('sha256'),key+'/artifact')
   if m.get('kind') in RUN_KINDS:
    if not m.get('command') or type(m.get('exit_code')) is not int or m.get('exit_code')!=0:self.err('RUN_COMMAND',key)
    if not isinstance(m.get('toolchain'),dict) or not m['toolchain']:self.err('RUN_TOOLCHAIN',key)
    if not isinstance(m.get('platform'),dict) or not m['platform'].get('os') or not m['platform'].get('arch'):self.err('RUN_PLATFORM',key)
    if not GITSHA.fullmatch(str(m.get('source_commit',''))):self.err('RUN_COMMIT',key)
    if subject.get('source_commit') and m.get('source_commit')!=subject['source_commit']:self.err('RUN_COMMIT_STALE',key)
   if m.get('kind') in RUN_KINDS:
    logs=m.get('logs')
    if not isinstance(logs,dict) or set(logs)!={'stdout','stderr'}:self.err('RUN_LOGS',key)
    else:
     for stream,record in logs.items():
      self.require_file_hash(record.get('path'),record.get('sha256'),key+'/'+stream)
    try:
     start=datetime.fromisoformat(m['started_at'].replace('Z','+00:00'));end=datetime.fromisoformat(m['finished_at'].replace('Z','+00:00'))
     if start.tzinfo is None or end.tzinfo is None or end<start:raise ValueError('invalid time interval')
    except (KeyError,ValueError,TypeError,AttributeError):self.err('RUN_TIMES',key)
    checks=m.get('checks',{})
    if checks.get('completed') is not True or checks.get('timed_out') is not False or type(checks.get('failed')) is not int or checks.get('failed')!=0:
     self.err('RUN_CHECKS_INCOMPLETE',key)
    for alias in ('tests_failed','failed_tests','failures'):
     if alias in m and m[alias] not in (0,[]):self.err('RUN_CONTRADICTION',key+':'+alias)
    if m.get('timed_out') is True:self.err('RUN_CONTRADICTION',key+':timed_out')
    if m.get('kind')=='native_aot_run':
     aot=m.get('aot',{})
     if aot.get('published') is not True or aot.get('executed') is not True or aot.get('runtime_mode')!='native_aot':
      self.err('AOT_NOT_EXECUTED',key)
     if not aot.get('publish_command') or not aot.get('run_command'):self.err('AOT_COMMANDS',key)
     rid=aot.get('target_rid','')
     platform=m.get('platform',{})
     if not isinstance(rid,str) or (platform.get('os')=='Windows' and not rid.startswith('win-')) or (platform.get('os')=='Linux' and not rid.startswith('linux-')) or not rid.endswith('-'+str(platform.get('arch'))):
      self.err('AOT_TARGET',key)
     binary=aot.get('binary',{})
     self.require_file_hash(binary.get('path'),binary.get('sha256'),key+'/aot-binary')
   out.append((r.get('sha256'),m))
  return out

 def reviews(self,records,subject,author,evidence_hashes,where):
  if not valid_identity(author):self.err('AUTHOR_REQUIRED',where)
  if not isinstance(records,list) or not records:
   self.err('INDEPENDENT_REVIEW_REQUIRED',where);return
  for i,r in enumerate(records):
   key=f'{where}/review/{i}';m=self.manifest(r,key)
   if m is None:continue
   if m.get('subject')!=subject:self.err('REVIEW_SUBJECT',key)
   if m.get('verdict')!='accepted' or m.get('blocking_findings')!=[]:self.err('REVIEW_BLOCKED',key)
   reviewer=m.get('reviewer')
   if not valid_identity(reviewer) or reviewer==author:self.err('REVIEW_NOT_INDEPENDENT',key)
   if m.get('author')!=author:self.err('REVIEW_AUTHOR',key)
   if not m.get('reviewed_at'):self.err('REVIEW_DATE',key)
   reviewed=m.get('reviewed_evidence_sha256',[])
   if not isinstance(reviewed,list) or not evidence_hashes or not set(evidence_hashes).issubset(set(reviewed)):
    self.err('REVIEW_EVIDENCE_BINDING',key)

 def load(self):
  for kind in ('research','documentation','delivery'):
   graph=self.read_json(self.plan/(kind+'-graph.json'))
   if not isinstance(graph,dict):continue
   self.graphs[kind]=graph
   if graph.get('schema_version')!=VERSION:self.err('SCHEMA_VERSION',kind)
   if graph.get('graph_kind')!=kind:self.err('GRAPH_KIND',kind)
   if not isinstance(graph.get('nodes'),list):self.err('NODES_REQUIRED',kind);continue
   for n in graph['nodes']:
    if not isinstance(n,dict):self.err('NODE_OBJECT',kind);continue
    missing=NODE_FIELDS-set(n)
    if missing:self.err('NODE_FIELDS',f'{n.get("id")}: missing {sorted(missing)}')
    nid=n.get('id')
    if not isinstance(nid,str) or not re.fullmatch(r'(R|D|A|B)\d{2,}',nid):self.err('ID_FORMAT',str(nid));continue
    if nid in self.nodes:self.err('DUPLICATE_ID',nid);continue
    self.nodes[nid]=n;self.kind[nid]=kind
    if n.get('status') not in STATUSES[kind]:self.err('STATE',f'{nid}: {n.get("status")}')
    expected={'research':'R','documentation':'D','delivery':('A','B')}[kind]
    if not nid.startswith(expected):self.err('ID_GRAPH',nid)
    if n.get('revision')!='0.1.0' and not re.fullmatch(r'\d+\.\d+\.\d+(?:-[\w.]+)?',str(n.get('revision',''))):self.err('REVISION',nid)
    for field in ('start_dependencies','acceptance_dependencies','contract_inputs','research_refs','documentation_refs','outputs','write_scopes','resource_locks','acceptance_evidence','independent_reviewers'):
     if not isinstance(n.get(field),list):self.err('FIELD_ARRAY',f'{nid}:{field}')
    prompt=n.get('prompt')
    if not isinstance(prompt,str) or '..' in PurePosixPath(prompt).parts or PurePosixPath(prompt).is_absolute() or not (self.plan/prompt).is_file():
     self.err('PROMPT_MISSING',nid)
    if isinstance(prompt,str) and (self.plan/prompt).is_file():
     self.require_file_hash('Plan:'+prompt,n.get('packet_sha256'),nid+'/packet')
    if kind=='delivery':
     if not isinstance(n.get('verification_requirements'),list) or not n['verification_requirements']:self.err('VERIFICATION_REQUIREMENTS',nid)
     if n.get('selection_status') not in {'undecided','selected','excluded','not_applicable'}:self.err('SELECTION_STATE',nid)
    for s in n.get('write_scopes',[])+n.get('outputs',[]):
     try:path_parts(s)
     except (ValueError,TypeError) as e:self.err('PATH',f'{nid}: {e}')
    for out in n.get('outputs',[]):
     try:
      if not any(scope_contains(s,out) for s in n.get('write_scopes',[])):self.err('OUTPUT_NOT_OWNED',f'{nid}: {out}')
     except (ValueError,TypeError):pass
  registry=self.read_json(self.bundle/'NativeWeave-Design/docs/contracts/registry.json','CONTRACT_REGISTRY')
  if isinstance(registry,dict):
   for c in registry.get('contracts',[]):
    if not isinstance(c,dict):self.err('CONTRACT_OBJECT','registry');continue
    key=(c.get('id'),c.get('version'))
    if None in key or key in self.contracts:self.err('CONTRACT_ID',str(key));continue
    self.contracts[key]=c

 def references(self):
  for nid,n in self.nodes.items():
   for field in ('start_dependencies','acceptance_dependencies','research_refs','documentation_refs','cross_review_by'):
    values=n.get(field,[])
    if not isinstance(values,list):continue
    if len(values)!=len(set(values)):self.err('DUPLICATE_EDGE',f'{nid}:{field}')
    for dep in values:
     if dep not in self.nodes:self.err('MISSING_DEPENDENCY',f'{nid}:{field}->{dep}')
     elif field=='research_refs' and self.kind[dep]!='research':self.err('CROSS_GRAPH_TYPE',f'{nid}:{field}->{dep}')
     elif field=='documentation_refs' and self.kind[dep]!='documentation':self.err('CROSS_GRAPH_TYPE',f'{nid}:{field}->{dep}')
   all_deps=n.get('start_dependencies',[])+n.get('acceptance_dependencies',[])
   pins=n.get('dependency_pins')
   if not isinstance(pins,dict) or set(pins)!=set(all_deps):self.err('DEPENDENCY_PINS',nid)
   else:
    for dep,rev in pins.items():
     if dep in self.nodes and rev!=self.nodes[dep].get('revision'):self.err('DEPENDENCY_VERSION',f'{nid}->{dep}@{rev}')
   seen_conditionals=set()
   for conditional in n.get('conditional_dependencies',[]):
    dep=conditional.get('task_id');condition=conditional.get('condition',{})
    if dep not in self.nodes or condition.get('task_id') not in self.nodes:self.err('MISSING_CONDITIONAL_DEPENDENCY',nid)
    elif conditional.get('revision')!=self.nodes[dep].get('revision'):self.err('CONDITIONAL_VERSION',nid)
    if conditional.get('gate') not in {'start','acceptance'} or condition.get('selection_status')!='selected':self.err('CONDITIONAL_SCHEMA',nid)
    if 'protocol_profile_selected' in condition and (condition['protocol_profile_selected'] is not True or not n.get('protocol_host_profiles')):
     self.err('CONDITIONAL_PROTOCOL_PROFILE',nid)
    selector=condition.get('task_id')
    if selector not in n.get('selection_inputs',[]) or not self.nodes.get(selector,{}).get('selection_required'):self.err('CONDITIONAL_SELECTION_REFERENCE',nid)
    edge=(conditional.get('gate'),dep,selector)
    if edge in seen_conditionals:self.err('DUPLICATE_CONDITIONAL_EDGE',nid)
    seen_conditionals.add(edge)
   for selection in n.get('selection_inputs',[]):
    if selection not in self.nodes or not self.nodes[selection].get('selection_required'):self.err('SELECTION_REFERENCE',nid)
   groups=n.get('required_selection_groups',[]);seen_groups=set()
   if not isinstance(groups,list):self.err('SELECTION_GROUP_SCHEMA',nid);groups=[]
   for group in groups:
    if not isinstance(group,dict):self.err('SELECTION_GROUP_SCHEMA',nid);continue
    group_id=group.get('id');members=group.get('task_ids')
    if not isinstance(group_id,str) or not group_id or group_id in seen_groups:self.err('SELECTION_GROUP_ID',nid)
    else:seen_groups.add(group_id)
    if self.kind[nid]!='delivery' or group.get('minimum_selected')!=1 or type(group.get('minimum_selected')) is not int or not isinstance(members,list) or not members or any(not isinstance(d,str) for d in members):
     self.err('SELECTION_GROUP_SCHEMA',nid);continue
    if len(members)!=len(set(members)):self.err('SELECTION_GROUP_SCHEMA',nid)
    for member in members:
     if member==nid or member not in n.get('selection_inputs',[]) or not self.nodes.get(member,{}).get('selection_required'):
      self.err('SELECTION_GROUP_REFERENCE',nid+':'+str(member))
   profiles=n.get('protocol_host_profiles')
   if profiles is not None:
    if not isinstance(profiles,list) or not profiles or self.kind[nid]!='delivery' or not n.get('selection_required'):
     self.err('PROTOCOL_PROFILE_SCHEMA',nid);profiles=[]
    hosts=[]
    for profile in profiles:
     if not isinstance(profile,dict):self.err('PROTOCOL_PROFILE_SCHEMA',nid);continue
     host=profile.get('host_task_id')
     if not isinstance(host,str):self.err('PROTOCOL_PROFILE_HOST',nid);continue
     hosts.append(host)
     if host not in n.get('selection_inputs',[]) or not self.nodes.get(host,{}).get('selection_required'):self.err('PROTOCOL_PROFILE_HOST',nid)
     if profile.get('selection_status') not in {'selected','excluded','undecided'}:self.err('PROTOCOL_PROFILE_SCHEMA',nid)
     contract=profile.get('contract_input')
     if contract is not None and (not isinstance(contract,dict) or contract not in n.get('contract_inputs',[])):
      self.err('PROTOCOL_PROFILE_CONTRACT',nid)
    if len(hosts)!=len(set(str(h) for h in hosts)) or set(hosts)!=set(n.get('selection_inputs',[])):
     self.err('PROTOCOL_PROFILE_COVERAGE',nid)
   scope=n.get('release_scope')
   if scope:
    for component in scope.get('components',[]):
     dep=self.nodes.get(component.get('task_id'))
     if not dep:self.err('RELEASE_COMPONENT_MISSING',nid);continue
     if component.get('revision')!=dep.get('revision'):self.err('RELEASE_COMPONENT_VERSION',nid)
     if component.get('when') not in {'always','selected'}:self.err('RELEASE_COMPONENT_CONDITION',nid)
     if component.get('when')=='selected' and (not dep.get('selection_required') or dep['id'] not in n.get('selection_inputs',[])):
      self.err('RELEASE_SELECTION_REFERENCE',nid+':'+dep['id'])
   for c in n.get('contract_inputs',[]):
    if not isinstance(c,dict) or c.get('required_status')!='accepted' or not c.get('version'):
     self.err('CONTRACT_PIN',nid);continue
    if (c.get('id'),c.get('version')) not in self.contracts:self.err('CONTRACT_MISSING',f'{nid}: {c}')
  for label,fields in [('start',('start_dependencies',)),('acceptance',('start_dependencies','acceptance_dependencies'))]:
   for path in cycles(self.nodes,lambda v:[d for f in fields for d in self.nodes[v].get(f,[])]+[c['task_id'] for c in self.nodes[v].get('conditional_dependencies',[]) if label=='acceptance' or c.get('gate')=='start']+(self.active_release_components(self.nodes[v]) if label=='acceptance' else [])):
    self.err('DEPENDENCY_CYCLE',label+': '+' -> '.join(path))
  ckeys=set(self.contracts)
  for key,c in self.contracts.items():
   for dep in c.get('dependencies',[]):
    if not isinstance(dep,dict) or (dep.get('id'),dep.get('version')) not in ckeys:self.err('CONTRACT_DEPENDENCY',f'{key}: {dep}')
  for path in cycles(ckeys,lambda k:[(d.get('id'),d.get('version')) for d in self.contracts[k].get('dependencies',[]) if isinstance(d,dict)]):
   self.err('CONTRACT_CYCLE',str(path))

 def contract_accepted(self,key):
  c=self.contracts.get(key)
  return bool(c and c.get('status')=='accepted' and key in self.checked_contracts)

 def declared_contract_host_profiles(self,key):
  """Read the hashed declaration even while a complete design awaits review."""
  contract=self.contracts.get(key)
  if not contract:return set()
  ref=contract.get('spec_path')
  if isinstance(ref,str) and ':' not in ref:ref='NativeWeave-Design:'+ref
  raw=self.require_file_hash(ref,contract.get('content_sha256'),'protocol-host-scope/'+key[0]+'@'+key[1])
  if raw is None:return set()
  try:
   blocks=re.findall(r'^```json nativeweave-protocol-host-profiles-v1\r?\n(.*?)^```[ \t]*\r?$',raw.decode('utf-8'),re.M|re.S)
   if len(blocks)!=1:return set()
   declaration=json.loads(blocks[0]);hosts=declaration.get('host_task_ids')
   if not isinstance(declaration,dict) or not {'host_task_ids'}.issubset(declaration) or not set(declaration).issubset({'host_task_ids','profiles'}):return set()
   if not isinstance(hosts,list) or not hosts or any(not isinstance(h,str) or not re.fullmatch(r'B\d{2,}',h) for h in hosts) or len(hosts)!=len(set(hosts)):return set()
   if 'profiles' in declaration:
    profiles=declaration['profiles'];supported={'grpc':'native-tonic','mcp':'native-rmcp'}
    if not isinstance(profiles,dict) or not profiles or any(name not in supported or backend!=supported[name] for name,backend in profiles.items()):return set()
   return set(hosts)
  except (UnicodeError,ValueError,TypeError,AttributeError):return set()

 def contract_host_profiles(self,key):
  """Acceptance-sensitive callers still require the original full contract gate."""
  if not self.contract_accepted(key):return set()
  return self.declared_contract_host_profiles(key)

 def architecture(self):
  """The current mission fixes Rust engines; only concrete native composition varies."""
  graph=self.graphs.get('delivery',{});policy=graph.get('architecture_policy')
  if not isinstance(policy,dict):self.err('ARCHITECTURE_POLICY_REQUIRED','delivery');return
  if policy.get('version')!=graph.get('revision'):self.err('ARCHITECTURE_POLICY_VERSION','delivery')
  for field,expected in ARCHITECTURE_POLICY.items():
   actual=policy.get(field)
   if type(actual) is not type(expected) or actual!=expected:
    self.err('ARCHITECTURE_POLICY',field)
  phase_authorized=policy.get('delivery_execution_authorized')
  if type(phase_authorized) is not bool:self.err('PHASE_AUTHORIZATION_POLICY','delivery')
  for nid,n in self.nodes.items():
   if n.get('required_selection_groups'):
    self.err('LEGACY_HOST_SELECTION_GROUP',nid)
   if any(h in n.get('selection_inputs',[]) for h in ('B04','B15','B17')):
    self.err('LEGACY_HOST_SELECTION_INPUT',nid)
   if any(c.get('condition',{}).get('task_id') in {'B04','B15','B17'} for c in n.get('conditional_dependencies',[])):
    self.err('OPTIONAL_NATIVE_ENGINE_DEPENDENCY',nid)
   if n.get('protocol_host_profiles') is not None:
    self.err('LEGACY_HOST_PROFILE_MATRIX',nid)
   if self.kind.get(nid)!='delivery':continue
   authorization=n.get('implementation_authorization',{})
   if not isinstance(authorization,dict):self.err('IMPLEMENTATION_AUTHORIZATION_SCHEMA',nid);authorization={}
   if phase_authorized is False and (authorization.get('status')!='not_authorized' or authorization.get('approval_record') is not None):
    self.err('CURRENT_PHASE_PRODUCT_AUTHORIZATION',nid)
   if phase_authorized is False and n.get('status') in TERMINAL|{'in_progress','partially_verified'}:
    self.err('CURRENT_PHASE_PRODUCT_EXECUTION',nid)
   if nid.startswith('B'):
    number=int(nid[1:]);expected='mandatory_rust_database' if number<=14 else 'mandatory_rust_server' if number<=20 else 'mandatory_rust_database_and_server'
    if n.get('native_backend_policy')!=expected:self.err('NATIVE_BACKEND_POLICY',nid)
  for nid,module in [('B04','Data.NativeHost'),('B15','Server.Application'),('B17','Server.Native')]:
   n=self.nodes.get(nid,{})
   if n.get('selection_required') is not False or n.get('selection_status')!='not_applicable':
    self.err('REQUIRED_NATIVE_ROLE_OPTIONAL',nid)
   if n.get('module')!=module:self.err('NATIVE_ROLE_MODULE',nid)
  app=self.nodes.get('B15',{});host=self.nodes.get('B17',{})
  if 'B17' not in app.get('acceptance_dependencies',[]):self.err('APPLICATION_NATIVE_HOST_ACCEPTANCE','B15')
  if 'NativeWeave:src/Server.Application/' not in app.get('write_scopes',[]):self.err('APPLICATION_SCOPE','B15')
  if 'NativeWeave:native/server/host/' not in host.get('write_scopes',[]):self.err('RUST_HOST_SCOPE','B17')
  for nid,n in self.nodes.items():
   if nid!='B17' and any(scope_contains(s,'NativeWeave:native/server/host/') for s in n.get('write_scopes',[])):
    self.err('DUPLICATE_PRODUCTION_HOST',nid)
  def ancestors(nid,seen=None):
   seen=set() if seen is None else seen
   for dep in self.nodes.get(nid,{}).get('start_dependencies',[])+self.nodes.get(nid,{}).get('acceptance_dependencies',[]):
    if dep not in seen:seen.add(dep);ancestors(dep,seen)
   return seen
  for nid in ('B18','B19','B20'):
   if 'B17' not in ancestors(nid):self.err('SERVER_HOST_DEPENDENCY',nid)
  for nid in ('B21','B22','B23','B24'):
   if not {'B04','B17'}.issubset(ancestors(nid)):self.err('INTEGRATION_NATIVE_ENGINES_REQUIRED',nid)
  components=self.nodes.get('B24',{}).get('release_scope',{}).get('components',[])
  for nid in ('B04','B15','B17'):
   selected=[c for c in components if c.get('task_id')==nid]
   if len(selected)!=1 or selected[0].get('when')!='always':self.err('RELEASE_NATIVE_ROLE_REQUIRED',nid)
  protocol_keys=set()
  for nid in ('B18','B19'):
   pins=[c for c in self.nodes.get(nid,{}).get('contract_inputs',[]) if c.get('id')=='C-PROTOCOL-001']
   if len(pins)!=1:self.err('PROTOCOL_CONTRACT_REQUIRED',nid)
   protocol_keys.update((c['id'],c['version']) for c in pins)
  for key in protocol_keys:
   if self.declared_contract_host_profiles(key)!={'B17'}:
    self.err('PROTOCOL_SPEC_RUST_HOST_ONLY',key[0]+'@'+key[1])

 def public_api(self):
  """Validate each existing Delivery's exact API input and documentation owner."""
  standard=self.resolve('NativeWeave-Design:docs/standards/csharp-public-api-and-documentation.md')
  match=re.search(r'^Version: (\d+\.\d+\.\d+)\.',standard.read_text(),re.MULTILINE) if standard.is_file() else None
  for kind,g in self.graphs.items():
   if not match or g.get('public_api_standard_version')!=match.group(1):self.err('API_STANDARD_VERSION',kind)
  verified=set()
  for nid,n in self.nodes.items():
   if self.kind.get(nid)!='delivery':continue
   paths=n.get('api_design_inputs');pins=n.get('api_design_input_sha256')
   if not isinstance(paths,list) or not paths or len(paths)!=len(set(paths)) or not all(isinstance(p,str) and p.startswith('NativeWeave-Design:') for p in paths):
    self.err('API_INPUTS_REQUIRED',nid);continue
   if not isinstance(pins,dict) or set(pins)!=set(paths):
    self.err('API_INPUT_PINS',nid);continue
   for path in paths:
    key=(path,pins[path])
    if key not in verified:
     self.require_file_hash(path,pins[path],nid+'/api-input');verified.add(key)
   if not isinstance(n.get('api_surface_responsibility'),str) or not n['api_surface_responsibility'].strip():self.err('API_SURFACE_RESPONSIBILITY',nid)
   if n.get('documentation_owner_role')!='delivery/'+nid:self.err('API_DOCUMENTATION_OWNER',nid)
   if not isinstance(n.get('api_contract_types'),list):self.err('API_TYPE_POLICIES',nid)
   outputs=n.get('documentation_outputs')
   if not isinstance(outputs,list) or len(outputs)<2:self.err('API_DOCUMENTATION_OUTPUTS',nid)
   else:
    for path in outputs[:2]:
     if not isinstance(path,str) or not any(scope_contains(scope,path) for scope in n.get('write_scopes',[])):self.err('API_DOCUMENTATION_NOT_OWNED',nid)
   matrix=n.get('verification_matrix',{})
   if not isinstance(matrix,dict) or not matrix.get('api_and_documentation'):self.err('API_VERIFICATION_REQUIRED',nid)

 def fragments(self):
  """Fragments mirror existing task detail; they cannot form a fourth graph."""
  files=sorted((self.plan/'fragments').glob('*.json'));owners=set();covered=[]
  for path in files:
   f=self.read_json(path,'FRAGMENT_JSON')
   if not isinstance(f,dict):continue
   where=path.relative_to(self.plan).as_posix();did=f.get('documentation_task_id')
   if not isinstance(did,str):self.err('FRAGMENT_OWNER',where);continue
   owner=self.nodes.get(did,{})
   if f.get('schema_version')!=VERSION:self.err('FRAGMENT_SCHEMA',where)
   if self.kind.get(did)!='documentation' or did in owners:self.err('FRAGMENT_OWNER',where)
   owners.add(did)
   if f.get('revision')!=owner.get('revision'):self.err('FRAGMENT_REVISION',where)
   if 'Plan:'+where not in owner.get('outputs',[]):self.err('FRAGMENT_OUTPUT',where)
   if 'nodes' in f or 'edges' in f:self.err('FRAGMENT_SCHEDULING_GRAPH',where)
   ids=f.get('delivery_task_ids');details=f.get('task_details')
   if not isinstance(ids,list) or any(not isinstance(n,str) for n in ids) or not isinstance(details,dict):
    self.err('FRAGMENT_TASKS',where);continue
   if len(ids)!=len(set(ids)) or set(details)!=set(ids):self.err('FRAGMENT_TASKS',where)
   covered.extend(ids)
   for nid,detail in details.items():
    if self.kind.get(nid)!='delivery' or not isinstance(detail,dict):self.err('FRAGMENT_TASK_REFERENCE',where+':'+nid);continue
    if set(detail)!=FRAGMENT_MIRROR_FIELDS:self.err('FRAGMENT_FIELDS',where+':'+nid)
    for field,value in detail.items():
     if field not in self.nodes[nid] or value!=self.nodes[nid][field]:self.err('FRAGMENT_MIRROR',where+':'+nid+':'+field)
   inputs=f.get('design_inputs')
   if not isinstance(inputs,list):self.err('FRAGMENT_DESIGN_INPUTS',where);continue
   source_ids=[]
   for source in inputs:
    if not isinstance(source,dict):self.err('FRAGMENT_DESIGN_INPUTS',where);continue
    sid=source.get('id')
    if not isinstance(sid,str):self.err('FRAGMENT_DESIGN_INPUTS',where);continue
    source_ids.append(sid)
    if sid not in self.nodes or self.kind.get(sid) not in {'research','documentation'} or source.get('outputs')!=self.nodes.get(sid,{}).get('outputs'):
     self.err('FRAGMENT_SOURCE_MIRROR',where+':'+str(sid))
   expected=set(owner.get('research_refs',[])+owner.get('documentation_refs',[]))
   if len(source_ids)!=len(set(source_ids)) or set(source_ids)!=expected:self.err('FRAGMENT_SOURCE_COVERAGE',where)
  expected_owners={f'D{i:02}' for i in range(22,32)}
  if owners!=expected_owners or len(files)!=10:self.err('FRAGMENT_OWNER_COVERAGE','D22-D31')
  delivery={n for n in self.nodes if self.kind[n]=='delivery'}
  if set(covered)!=delivery or len(covered)!=len(set(covered)):self.err('FRAGMENT_DELIVERY_COVERAGE','48 existing tasks')

 def check_contract(self,key):
  if key in self.checked_contracts:return True
  if key in self.checking_contracts:return False
  c=self.contracts.get(key)
  if not c or c.get('status')!='accepted':return False
  self.checking_contracts.add(key);before=len(self.errors);where=f'contract/{key[0]}@{key[1]}'
  spec_ref=c.get('spec_path')
  if isinstance(spec_ref,str) and ':' not in spec_ref:spec_ref='NativeWeave-Design:'+spec_ref
  raw=self.require_file_hash(spec_ref,c.get('content_sha256'),where+'/spec')
  if raw is not None and not raw.strip():self.err('EMPTY_SPEC',where)
  subject={'kind':'contract','id':key[0],'version':key[1],'content_sha256':c.get('content_sha256')}
  ev=self.evidence(c.get('evidence'),subject,where)
  self.reviews(c.get('reviews'),subject,c.get('author'),[h for h,m in ev],where)
  for dep in c.get('dependencies',[]):
   dk=(dep.get('id'),dep.get('version'))
   if not self.check_contract(dk):self.err('CONTRACT_DEPENDENCY_NOT_ACCEPTED',f'{where}: {dk}')
  self.checking_contracts.remove(key)
  if len(self.errors)==before:self.checked_contracts.add(key);return True
  return False

 def active_release_components(self,n):
  return [c['task_id'] for c in n.get('release_scope',{}).get('components',[])
          if c.get('when')=='always' or (c.get('when')=='selected' and self.nodes.get(c.get('task_id'),{}).get('selection_status')=='selected')]

 def active_dependencies(self,n,gate):
  result=list(n.get(gate+'_dependencies',[]))
  if gate=='acceptance':result.extend(self.active_release_components(n))
  for c in n.get('conditional_dependencies',[]):
   cond=c['condition']
   profile_active=not cond.get('protocol_profile_selected') or any(p['host_task_id']==cond['task_id'] and p['selection_status']=='selected' for p in n.get('protocol_host_profiles',[]))
   if c.get('gate')==gate and profile_active and self.nodes.get(cond['task_id'],{}).get('selection_status')==cond['selection_status']:result.append(c['task_id'])
  return list(dict.fromkeys(result))

 def active_start_dependencies(self,n):return self.active_dependencies(n,'start')
 def active_acceptance_dependencies(self,n):return self.active_dependencies(n,'acceptance')

 def selection_issues(self,n):
  issues=[]
  for member in n.get('selection_inputs',[]):
   if self.nodes.get(member,{}).get('selection_status') not in {'selected','excluded'}:
    issues.append(('SELECTION_UNRESOLVED',member))
  for group in n.get('required_selection_groups',[]):
   selected=sum(self.nodes.get(member,{}).get('selection_status')=='selected' for member in group['task_ids'])
   if selected<group['minimum_selected']:issues.append(('SELECTION_GROUP_UNSATISFIED',group['id']))
  return issues

 def protocol_profile_issues(self,n):
  if 'protocol_host_profiles' not in n or n.get('selection_status')!='selected':return []
  issues=[];enabled=0
  for profile in n['protocol_host_profiles']:
   host=profile['host_task_id'];global_choice=self.nodes[host].get('selection_status');choice=profile['selection_status']
   if global_choice=='selected':
    if choice=='undecided':issues.append(('PROTOCOL_PROFILE_UNRESOLVED',host))
    elif choice=='selected':
     enabled+=1;contract=profile.get('contract_input')
     if contract is None:issues.append(('PROTOCOL_PROFILE_DESIGN_MISSING',host))
     elif not self.contract_accepted((contract['id'],contract['version'])):issues.append(('PROTOCOL_PROFILE_CONTRACT_UNACCEPTED',host))
     elif host not in self.contract_host_profiles((contract['id'],contract['version'])):issues.append(('PROTOCOL_PROFILE_HOST_NOT_IN_CONTRACT',host))
   elif choice=='selected':issues.append(('PROTOCOL_PROFILE_HOST_UNSELECTED',host))
  if not enabled:issues.append(('PROTOCOL_PROFILE_EMPTY',n['id']))
  return issues

 def task_subject(self,nid,n):
  deps=self.active_start_dependencies(n)+self.active_acceptance_dependencies(n)
  return {'kind':'task','id':nid,'revision':n.get('revision'),'content_sha256':node_digest(n),'source_commit':n.get('source_commit'),
   'dependency_snapshot':{d:{'revision':self.nodes[d].get('revision'),'content_sha256':node_digest(self.nodes[d]),'source_commit':self.nodes[d].get('source_commit'),'acceptance_evidence_sha256':[e.get('sha256') for e in self.nodes[d].get('acceptance_evidence',[])],'independent_review_sha256':[r.get('sha256') for r in self.nodes[d].get('independent_reviewers',[])]} for d in deps if d in self.nodes},
   'selection_snapshot':{d:{'revision':self.nodes[d].get('revision'),'selection_status':self.nodes[d].get('selection_status'),'content_sha256':node_digest(self.nodes[d])} for d in n.get('selection_inputs',[]) if d in self.nodes},
   'contract_snapshot':{pin['id']+'@'+pin['version']:{'spec_path':self.contracts.get((pin['id'],pin['version']),{}).get('spec_path'),'content_sha256':self.contracts.get((pin['id'],pin['version']),{}).get('content_sha256'),'evidence_sha256':[e.get('sha256') for e in self.contracts.get((pin['id'],pin['version']),{}).get('evidence',[])],'review_sha256':[r.get('sha256') for r in self.contracts.get((pin['id'],pin['version']),{}).get('reviews',[])]} for pin in n.get('contract_inputs',[])}}

 def check_release_scope(self,nid,n):
  scope=n.get('release_scope')
  if not scope:return
  if scope.get('status')!='accepted' or not scope.get('components'):self.err('RELEASE_SCOPE_UNACCEPTED',nid)
  for component in scope.get('components',[]):
   dep=self.nodes.get(component.get('task_id'),{})
   if component.get('revision')!=dep.get('revision'):self.err('RELEASE_COMPONENT_VERSION',nid)
   if component.get('when')=='selected' and dep.get('selection_status')=='undecided':self.err('RELEASE_SELECTION_UNRESOLVED',nid)
   if component.get('when')=='always' or dep.get('selection_status')=='selected':
    if dep.get('status') not in TERMINAL:self.err('RELEASE_COMPONENT_NOT_ACCEPTED',nid+':'+str(component.get('task_id')))

 def check_acceptance(self):
  for key in self.contracts:self.check_contract(key)
  for nid,n in self.nodes.items():
   if n.get('status') not in TERMINAL:continue
   subject=self.task_subject(nid,n)
   if not GITSHA.fullmatch(str(n.get('source_commit',''))):self.err('TASK_COMMIT',nid)
   ev=self.evidence(n.get('acceptance_evidence'),subject,nid)
   self.reviews(n.get('independent_reviewers'),subject,n.get('author'),[h for h,m in ev],nid)
   for dep in self.active_start_dependencies(n)+self.active_acceptance_dependencies(n):
    if self.nodes.get(dep,{}).get('status') not in TERMINAL:self.err('DEPENDENCY_NOT_ACCEPTED',f'{nid}->{dep}')
   for c in n.get('contract_inputs',[]):
    if not self.contract_accepted((c.get('id'),c.get('version'))):self.err('CONTRACT_NOT_ACCEPTED',f'{nid}: {c.get("id")}@{c.get("version")}')
   if self.kind[nid]=='delivery':
    if n.get('selection_required') and n.get('selection_status')!='selected':self.err('UNSELECTED_OPTION',nid)
    for code,detail in self.selection_issues(n)+self.protocol_profile_issues(n):self.err(code,nid+':'+detail)
    self.authorization(nid,n)
    self.check_release_scope(nid,n)
    for req in n.get('verification_requirements',[]):
     if not any(m.get('kind')==req.get('kind') and m.get('platform',{}).get('os')==req.get('os') and m.get('platform',{}).get('arch')==req.get('arch') and (not req.get('target_rid') or m.get('aot',{}).get('target_rid')==req['target_rid']) and m.get('status')=='passed' for h,m in ev):
      self.err('PLATFORM_EVIDENCE_MISSING',f'{nid}: {req}')

 def authorization(self,nid,n):
  a=n.get('implementation_authorization')
  if not isinstance(a,dict) or a.get('status')!='authorized' or not isinstance(a.get('approval_record'),dict):
   self.err('IMPLEMENTATION_NOT_AUTHORIZED',nid);return False
  m=self.manifest(a['approval_record'],nid+'/implementation-authorization')
  if m is None:return False
  if m.get('task_id')!=nid or m.get('task_revision')!=n.get('revision') or m.get('task_content_sha256')!=node_digest(n) or m.get('verdict')!='authorize_implementation':
   self.err('IMPLEMENTATION_AUTH_SUBJECT',nid);return False
  return True

 def ownership(self):
  allnodes=list(self.nodes.items())
  for i,(a,na) in enumerate(allnodes):
   for b,nb in allnodes[i+1:]:
    overlaps=[]
    for x in na.get('write_scopes',[]):
     for y in nb.get('write_scopes',[]):
      try:
       if scopes_overlap(x,y):overlaps.append([x,y])
      except (ValueError,TypeError):pass
    if overlaps:
     conflict={'tasks':[a,b],'paths':overlaps};self.conflicts.append(conflict)
     self.err('WRITE_SCOPE_CONFLICT',json.dumps(conflict,ensure_ascii=False))
  # resource_locks are explicit local resources. They create scheduling conflicts,
  # not invalid graphs and never a global lock for every worker.

 def ready(self):
  ready={k:[] for k in ('research','documentation','delivery')};blocked={}
  for nid,n in self.nodes.items():
   kind=self.kind[nid]; reasons=[]
   if n.get('status') not in READY_STATES[kind]:reasons.append('state='+str(n.get('status')))
   for dep in self.active_start_dependencies(n):
    if self.nodes.get(dep,{}).get('status') not in TERMINAL:reasons.append('dependency='+dep)
   if kind=='delivery':
    for code,detail in self.selection_issues(n)+self.protocol_profile_issues(n):reasons.append(code+'='+detail)
    for c in n.get('contract_inputs',[]):
     if not self.contract_accepted((c.get('id'),c.get('version'))):reasons.append('contract='+str(c.get('id'))+'@'+str(c.get('version')))
    if n.get('selection_required') and n.get('selection_status')!='selected':reasons.append('optional route undecided')
    if n.get('status')=='planned':
     before=len(self.errors)
     if not self.authorization(nid,n):reasons.append('implementation authorization missing/invalid')
     # Readiness missing auth is blocked rather than graph-format failure.
     del self.errors[before:]
   if reasons:blocked[nid]=reasons
   else:ready[kind].append(nid)
  if self.errors:
   ready={k:[] for k in ready}
   self.warnings.append({'code':'READY_FAIL_CLOSED','message':'Validation errors make every executable ready set empty.'})
  ids_ready=[i for v in ready.values() for i in v]
  resource_conflicts=[]
  for i,a in enumerate(ids_ready):
   for b in ids_ready[i+1:]:
    shared=sorted(set(self.nodes[a].get('resource_locks',[])) & set(self.nodes[b].get('resource_locks',[])))
    if shared:resource_conflicts.append({'tasks':[a,b],'resources':shared})
  return ready,blocked,resource_conflicts

 def continuable(self):
  result={'research':[],'documentation':[],'delivery':[]}
  if self.errors:return result
  states={'research':{'in_progress','partially_evidenced','review_ready'},'documentation':{'drafting','partially_evidenced','review_ready'}}
  for nid,n in self.nodes.items():
   kind=self.kind[nid]
   if n.get('status') not in states.get(kind,set()):continue
   if any(self.nodes.get(d,{}).get('status') not in TERMINAL for d in n.get('start_dependencies',[])):continue
   result[kind].append(nid)
  return result

 def run(self):
  self.load()
  if not self.errors:
   self.references();self.ownership();self.architecture();self.fragments();self.public_api()
  if not self.errors:self.check_acceptance()
  if self.errors:
   ready={k:[] for k in ('research','documentation','delivery')};blocked={k:['validation errors'] for k in self.nodes};resources=[]
   self.warn('READY_FAIL_CLOSED','Validation errors make every executable ready set empty.')
  else:ready,blocked,resources=self.ready()
  return {'validator_version':VERSION,'ok':not self.errors,'counts':{k:sum(v==k for v in self.kind.values()) for k in ('research','documentation','delivery')},'errors':self.errors,'warnings':self.warnings,'write_conflicts':self.conflicts,'ready':ready,'continuable':self.continuable(),'blocked':blocked,'resource_conflicts':resources,'accepted_contracts':len(self.checked_contracts),'limitations':['Local structure, hashes and manifest bindings are checked; this does not authenticate reviewer identity or prove commands truly executed.','An empty or proposed contract registry never authorizes delivery.','The initial delivery graph is a candidate decomposition, not accepted implementation instructions.']}


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output',type=Path);args=ap.parse_args()
 result=Validator(args.root).run();text=json.dumps(result,ensure_ascii=False,indent=2)
 if args.output:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(text+'\n')
 print(text);return 0 if result['ok'] else 1
if __name__=='__main__':sys.exit(main())
