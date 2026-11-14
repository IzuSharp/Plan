#!/usr/bin/env python3
"""Refine existing tasks for the public API design; never grant acceptance or Delivery authorization.

Run after domain inputs are integrated. This writes current candidate revisions only;
new exact independent reviews and binding attestations are separate steps.
"""
from pathlib import Path
import hashlib
import json
import subprocess

P = Path(__file__).resolve().parents[1]
D = P.parent / 'NativeWeave-Design'
REVISION = '0.4.0'

def read(path): return json.loads(path.read_text())
def dump(path, data): path.write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n')
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

TASK_SURFACE = {
 'A01': 'Internal fixed-layout C ABI, generated layouts and bootstrap descriptions; expose no raw handles or pointers to application code.',
 'A02': 'AbiVersion, EngineCapability, EngineInfo, EngineDescriptor, EngineLoadOptions and EngineCatalog metadata/capability/preflight behavior.',
 'A03': 'Internal SafeHandle/resource admission and parent-child leases underpin every public owner; no public copyable owning struct.',
 'A04': 'NativeBuffer, NativeBufferReader and maintainer NativeBufferFactory; scoped reads, explicit copies, async staging and release.',
 'A05': 'NativeEngineException, EngineLoadException and EngineLoadFailure; preserve native diagnostics and represent absent pre-native fields honestly.',
 'A06': 'Internal static callback registration/revocation/draining; public C# handlers require no unmanaged function pointers or GCHandle management.',
 'A07': 'Internal Task bridge consumed by exact domain Async methods; cancellation, terminal result and native quiescence remain separate.',
 'A08': 'Internal Engine-local executor/admission/close primitives; no mandatory global runtime or generic public scheduler.',
 'A09': 'Versioned binding description and operation/payload inventory; all public symbols map through it without copying domain algorithms.',
 'A10': 'Generated C# LibraryImport/reverse-entry declarations, static metadata and XML documentation; no unbounded reflection binder.',
 'A11': 'Generated Rust exports and layout/version tests for the exact managed/native operation catalog.',
 'A12': 'Stable actionable analyzer IDs for lifetime, raw pointer escape, unrooted callback, unsupported AOT shape and API/XML inconsistency.',
 'A13': 'Actual product adoption of the API standard, SDK/language pin, XML/reference/consumer pipeline and package dependency boundaries.',
 'A14': 'Linux package native assets and first-use loading diagnostics; actual linux-x64 product/AOT consumer, no user Cargo requirement.',
 'A15': 'Windows package native assets and first-use loading diagnostics; actual win-x64 product/AOT consumer, no user Cargo requirement.',
 'A16': 'Independent facade/native NuGet graph, manifest/assets/provenance and genuinely pristine no-Rust installation/build/run/publish.',
 'A17': 'Public synchronous Engine consumer using scoped buffer ownership and actual native algorithm; no fixture substitution.',
 'A18': 'Public asynchronous Engine consumer using cancellation/streaming and actual native retirement; no fixture substitution.',
 'A19': 'Executable models cover each public owner state and visible cancellation/close result without claiming model checking proves the product.',
 'A20': 'Differential/property/fuzz checks cover exact public/native codecs, malformed inputs, callback races and resource release.',
 'A21': 'Measure public facade FFI/allocation/copy/pin/runtime/diagnostic costs and installation/developer effort against comparable direct native/.NET paths.',
 'A22': 'Managed API baselines, source/binary/default/behavior compatibility, native ABI/domain version matrix and Obsolete migration policy.',
 'A23': 'Affinity-capability consumption and future platform conformance; no unsupported public GUI/GPU/mobile surface announced.',
 'A24': 'EnginePackage/manifest maintainer SPI and scaffold explicitly adopting the versioned standard, reference/docs/samples/CI in each new repository.',
 'B01': 'Canonical NativeWeave.Data descriptors, codecs/parameters/rows/errors and Database source/session interfaces; other tasks implement shared declarations.',
 'B02': 'PostgreSqlDataSource/UsePostgreSql behavior over SQLx PostgreSQL; parameter, error, pool/session and capability mapping use B01 definitions.',
 'B03': 'SqliteDataSource/UseSqlite behavior over SQLx SQLite; path/options/worker/NULL/dialect capability limits are explicit.',
 'B04': 'DataSourceBuilder/DataSource/DataSession lifecycle, factories, optional AddNativeWeaveDatabase DI and independent provider assets.',
 'B05': 'DataTransaction/savepoint/commit-result/cleanup APIs preserve unknown remote outcome, poisoned session handling and bounded close.',
 'B06': 'Typed QueryAsync/streaming/batches, cardinality methods and early-disposal behavior with bounded native row leases.',
 'B07': 'ValueCodec<T>/Codecs/parameter encoding and fallible native conversions; canonical definitions stay with B01, no parallel binder model.',
 'B08': 'MigrationPlan/MigrationRunner/schema capability facade, ordered checksummed ledger, lock/transaction limits and explicit scripts.',
 'B09': 'Minimal metadata/query operation bindings using B01 types and exact native expression/node IDs; no managed SQL AST.',
 'B10': 'Optional static Entity/DTO descriptor and mapper generation; ordinary managed source additions require no Rust rebuild or manual duplicate registration.',
 'B11': 'SeaQuery native AST/dialect/capability operations for filter/join/projection/group/aggregate/order/pagination/upsert/returning as specified.',
 'B12': 'Projection<T>/RowMaterializer<T>/owned DTO creation, nullability/cardinality and mapper-exception cleanup over B06 buffers.',
 'B13': 'NativeWeave.Query strongly typed Fluent surface, composable native expressions, deterministic unsupported boundaries and complete consumer examples.',
 'B14': 'Explicit relationship load/link/unlink/CRUD and optimistic concurrency; native execution, no lazy proxies or hidden tracker graph.',
 'B15': 'NativeServer/NativeServerBuilder/NativeServerApplication routing, RequestContext, typed handlers/results, middleware/filters/auth and static JSON.',
 'B16': 'Borrowed request/response Streams, owned chunks/SSE and retained-byte credits; exact advance/copy/dispose semantics and size limits.',
 'B17': 'Required Rust host implements exact startup/listener/TLS/HTTP1/2/shutdown/route/dispatch APIs; no Kestrel network implementation.',
 'B18': 'Optional static C# gRPC mapping exposes four cardinalities through Tonic on B17; status/trailers/deadline/flow-control semantics.',
 'B19': 'Optional MCP tools/resources/prompts/transports and static JSON mapping through rmcp on B17, with explicit auth/session/cancellation limits.',
 'B20': 'ILogger/ActivitySource/Meter integration, correlation/overall deadlines, scoped service ownership and whole-stack shutdown.',
 'B21': 'Actual reference application consumes the complete API from packed NuGet artifacts; minimum and advanced Entity/DTO/Handler examples.',
 'B22': 'Actual end-to-end public API failure/crash/cancellation/restart/retirement tests and long-term resource evidence.',
 'B23': 'Comparable full workload measurements including typed Fluent/DI/JSON/streaming cost and optional protocol/native binary closure.',
 'B24': 'Final provider/server/protocol package closure, API/docs/compatibility/RID matrix, pristine no-Rust consumers and versioned release documentation.'
}

def add_output(node, value):
    if value not in node['outputs']: node['outputs'].append(value)
    if not any(value == scope or (scope.endswith('/') and value.startswith(scope)) for scope in node['write_scopes']):
        node['write_scopes'].append(value)

def main():
    graphs = {k: read(P/(k+'-graph.json')) for k in ('research','documentation','delivery')}
    nodes = {n['id']: n for g in graphs.values() for n in g['nodes']}
    registry = read(D/'docs/contracts/registry.json')
    standard = 'NativeWeave-Design:docs/standards/csharp-public-api-and-documentation.md'
    common = [standard, 'NativeWeave-Design:docs/api/README.md', 'NativeWeave-Design:docs/api/documentation-system.md', 'NativeWeave-Design:docs/api/public-api.json']
    for contract in registry['contracts']:
        contract['version'] = REVISION
        contract['content_sha256'] = digest(D/contract['spec_path'])
        contract['status'] = 'proposed'
        contract['specification_status'] = 'public_api_refinement_pending_exact_independent_acceptance'
        contract['evidence'] = []; contract['reviews'] = []; contract['reviewers'] = []
        contract.pop('source_commit', None)
        domain = 'database' if contract['documentation_task_id'] in {'D14','D15','D16','D17'} else 'server' if contract['documentation_task_id'] in {'D18','D19'} else 'interop'
        contract['api_specification_inputs'] = common + [f'NativeWeave-Design:docs/api/{domain}.md',f'NativeWeave-Design:docs/api/{domain}-coverage.json',f'NativeWeave-Design:experiments/public-api/NativeWeave.Api.Design/{domain.title()}.cs']
        if contract['documentation_task_id'] in {'D10','D11','D20','D21'}:
            contract['api_specification_inputs'].append('NativeWeave-Design:docs/api/nuget-and-consumption.md')
        if contract['documentation_task_id'] in {'D12','D13','D20'}:
            contract['api_specification_inputs'] += ['NativeWeave-Design:docs/api/database.md','NativeWeave-Design:docs/api/server.md']
        contract['api_specification_inputs'] = list(dict.fromkeys(contract['api_specification_inputs']))
        contract['author'] = '/root/database_api' if domain == 'database' else '/root/server_api' if domain == 'server' else '/root/interop_api' if contract['documentation_task_id'] in {'D01','D03','D10','D11'} else '/root'
        contract['version_note'] = '0.4.0 public API refinement. Earlier accepted snapshots remain historical; native ABI wire v1 is unchanged unless an explicit operation extension says otherwise.'
        for dep in contract['dependencies']: dep['version'] = REVISION
    registry['status'] = 'public_api_refinement_review_ready'
    dump(D/'docs/contracts/registry.json', registry)
    # Source studies are delta outputs of existing Research topics.
    additions = {
      'R01': ['docs/api/foundation-sources.json'],
      'R18': ['docs/api/interop-sources.json'],
      'R25': ['docs/api/database-sources.json'],
      'R27': ['docs/api/server-sources.json'],
      'D10': ['docs/api/nuget-and-consumption.md'],
      'D11': ['docs/api/interop.md','docs/api/interop-coverage.json'],
      'D12': ['docs/api/documentation-system.md'],
      'D13': ['docs/api/foundation-coverage.json'],
      'D14': ['docs/api/database.md','docs/api/database-coverage.json'],
      'D18': ['docs/api/server.md','docs/api/server-coverage.json'],
      'D20': ['docs/api/getting-started.md','docs/api/guides.md'],
      'D31': ['docs/api/README.md','docs/api/public-api.json','docs/api/reference.md','docs/standards/csharp-public-api-and-documentation.md','templates/public-api/AGENTS.fragment.md','templates/public-api/adoption-checklist.md','templates/public-api/api-change-template.md','docs/decisions/ADR-0004-csharp-public-api-and-documentation.md'],
    }
    for identity, paths in additions.items():
        for path in paths: add_output(nodes[identity], 'NativeWeave-Design:'+path)
        nodes[identity]['revision'] = REVISION
    # The isolated interface/generator/consumer experiment remains in the existing R06 scope.
    files = subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','experiments/public-api'],cwd=D,text=True).splitlines()
    for path in sorted(set(files)):
        if (D/path).is_file(): add_output(nodes['R06'],'NativeWeave-Design:'+path)
    nodes['R06']['revision'] = REVISION
    for n in graphs['documentation']['nodes']: n['revision'] = REVISION
    for n in graphs['delivery']['nodes']:
        identity = n['id']; n['revision'] = REVISION
        domain = 'database' if identity.startswith('B') and int(identity[1:]) <= 14 else 'server' if identity.startswith('B') and int(identity[1:]) <= 20 else 'interop'
        domains = ['database','server','interop'] if identity in {'A13','A16','A21','A22','A24','B21','B22','B23','B24'} else [domain]
        n['api_design_inputs'] = common + ['NativeWeave-Design:docs/api/nuget-and-consumption.md'] + [f'NativeWeave-Design:docs/api/{x}.md' for x in domains]
        n['api_surface_responsibility'] = TASK_SURFACE[identity]
        n['documentation_owner_role'] = 'delivery/'+identity
        prefix = 'Public API refinement 0.4.0: '
        n['implementation_steps'] = [x for x in n['implementation_steps'] if not x.startswith(prefix)]
        n['implementation_steps'] += [prefix+TASK_SURFACE[identity], prefix+'Implement the pinned exact declarations and semantic/native operation mapping; update XML, generated API Reference, guides and minimal/advanced consumer source in the same task. For internal-only scopes document applicability and expose no accidental public plumbing.']
        n['specific_acceptance'] = [x for x in n['specific_acceptance'] if not x.startswith(prefix)]
        n['specific_acceptance'] += [prefix+'Compile exact signatures/overloads/nullability/generics and relevant generated consumers; run required actual product AOT rows, API compatibility and XML/reference/symbol coverage checks. Design stub execution is never a passed product row.', prefix+'Review installation/import/configuration/disposal/error experience, capability/native-operation correspondence and allocation/copy/FFI/runtime cost. This task owns its documentation; A16/B24 own final pristine package consumption.']
        n['verification_matrix']['api_and_documentation'] = 'Exact API/consumer compilation, current stable source comparison, XML/reference completeness, compatibility and independent usability review; justified applicability for internal-only work.'
    for kind,g in graphs.items():
        g['revision'] = REVISION
        g['amendment'] = 'Complete C# public API, native mappings, consumer experience and continuous documentation; existing IDs/edges and product authorization preserved.'
        if kind != 'delivery':
            g['graph_status'] = 'public_api_refinement_review_ready'
            for n in g['nodes']:
                n['status'] = 'review_ready'; n['acceptance_evidence'] = []; n['independent_reviewers'] = []; n.pop('source_commit',None)
        for n in g['nodes']:
            for c in n['contract_inputs']: c['version'] = REVISION
            n['dependency_pins'] = {k:nodes[k]['revision'] for k in n['dependency_pins']}
            for dep in n.get('conditional_dependencies',[]): dep['revision'] = nodes[dep['task_id']]['revision']
            for dep in n.get('release_scope',{}).get('components',[]): dep['revision'] = nodes[dep['task_id']]['revision']
            for profile in n.get('protocol_host_profiles',[]):
                if profile.get('contract_input'): profile['contract_input']['version'] = REVISION
        if kind == 'delivery': g['architecture_policy']['version'] = REVISION
        dump(P/(kind+'-graph.json'),g)
    print(json.dumps({'contracts_refined':21,'delivery_refined':48,'graphs':3,'acceptance_granted':False,'product_implementation_authorized':False}))

if __name__ == '__main__': main()
