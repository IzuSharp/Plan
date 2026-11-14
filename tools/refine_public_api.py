#!/usr/bin/env python3
"""Refine existing tasks for the public API design; never grant acceptance or Delivery authorization.

Run after domain inputs are integrated. This writes current candidate revisions only;
new exact independent reviews and binding attestations are separate steps.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
from validate_graphs import node_digest

P = Path(__file__).resolve().parents[1]
D = P.parent / 'NativeWeave-Design'
REVISION = '0.4.0'
STANDARD_VERSION = re.search(r'^Version: (\d+\.\d+\.\d+)\.',
    (D/'docs/standards/csharp-public-api-and-documentation.md').read_text(), re.MULTILINE).group(1)
PRIOR_MANIFEST = P / 'ledger/public-api-2026-11-14/prior-acceptance.json'

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
 'B08': 'Migration/MigrationBundle, MigrationOptions and DatabaseAdministration migration/schema APIs; ordered checksummed ledger, lock/transaction limits and explicit scripts.',
 'B09': 'Minimal metadata/query operation bindings using B01 types and exact native expression/node IDs; no managed SQL AST.',
 'B10': 'Facade-transitive model generator emits Table/Column/RowMaterializer descriptors from WeaveTable/WeaveColumn/WeaveKey/WeaveVersion; explicit exclusion retains the equivalent manual static path. Ordinary managed source additions require no Rust rebuild or duplicate registration.',
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

# Replace provisional names where the original task used illustrative API shapes.
# Preserve each task's existing native execution, error, resource and test detail.
SURFACE_CORRECTIONS = {
 'A02': 'AbiVersion, EngineCapability, EngineInfo, EngineDescriptor.Inspect, EngineLoadOptions and EngineCatalog provide immutable bootstrap/capability metadata; Engine instances remain independently owned.',
 'B01': 'Canonical NativeWeave.Data Table<TEntity>, Column<TEntity,TValue>, ValueCodec<T>, RowReader, RowWriter, RowMaterializer<T>, Projection<T>, EntityKey<TEntity>, Changes<TEntity>, ConcurrencyCheck<TEntity>, Relation<TParent,TChild>, SqlCommand and SqlParameters declarations; canonical Database source/session/result declarations are implemented by their owning B tasks. Exact names, signatures and semantics are fixed by Database.cs and database.md.',
 'B02': 'NativeWeave.Database.PostgreSql.PostgreSqlDataSource.Create and Engine, PostgreSqlOptions and DataSourceBuilder.UsePostgreSql; common DataSession/query API, native SQLx PostgreSQL execution and explicit TLS/capability options.',
 'B03': 'NativeWeave.Database.Sqlite.SqliteDataSource.Create and Engine, SqliteOptions and DataSourceBuilder.UseSqlite; file/WAL/FK/busy-timeout/begin-mode semantics use the common DataSession/query API.',
 'B04': 'DataSourceBuilder.Build, DataSource.OpenSessionAsync and CloseAsync/Dispose/DisposeAsync, DataSession and AddNativeWeaveDatabase; independent provider factories, explicit ownership and no global initialization or public Rust runtime.',
 'B05': 'DataSession.BeginTransactionAsync, DataTransaction and Savepoint; TransactionOutcome/TransactionState/DatabaseCloseResult snapshots preserve Unknown and local cleanup separately. CommitAsync succeeds only for Committed; DatabaseException, CommitOutcomeUnknownException and DatabaseCleanupException retain their specified distinctions. DisposeAsync joins actual local safety; no business-delegate replay.',
 'B06': 'DataSession.QueryAsync/StreamAsync/ScalarAsync, Query<TEntity> and QuerySelection<T> terminal/cardinality methods and IAsyncEnumerable<T>; bounded owned rows, one active fetch and exact early-disposal/cancellation cleanup. Native cursor handles remain internal.',
 'B07': 'ValueCodec<T>, Codecs and static RowReader/RowWriter accessors implement the canonical B01 declarations, exact db-wire scalar registry and fallible conversions; configured nullable/enum/JSON codecs are statically reachable. No object[] or auto-stringify fallback.',
 'B08': 'Migration, MigrationBundle, MigrationOptions, MigrationStatus, MigrationReport, SchemaColumn, SchemaTable and DatabaseAdministration.MigrateAsync/GetMigrationStatusAsync/ValidateMigrationsAsync/GetTablesAsync; explicit SQL scripts, checksums, ordered native ledger and provider transaction/locking limits.',
 'B10': 'The default facade-transitive Roslyn generator processes attributed C# models and emits statically referenced Table/Column metadata and RowMaterializer/EntityWriter methods. WeaveTable/WeaveColumn/WeaveKey/WeaveVersion/WeaveIgnore are fixed public attributes. Explicitly excluding generators requires the documented equivalent manual static descriptors, never rd.xml, runtime discovery or a Rust rebuild.',
 'B12': 'Projection<T>, RowMaterializer<T>, EntityWriter<T>, non-generic ref-struct RowReader/RowWriter, ResultColumn<T> and ResultField use typed codecs and owned DTO construction. No identity map, reflection setter, arbitrary runtime generic instantiation or managed relation graph.',
 'B13': 'NativeWeave.Query Query<TEntity>, QuerySelection<T>, SqlExpression<T>, SqlPredicate, typed parameter/alias/join/CTE/window/group/order/pagination/aggregate/set-operation surfaces and async terminals; exact Database.cs signatures and database.md native-token ownership rules. Generated and manual static metadata are equivalent AOT-safe paths.',
 'B14': 'Relation<TParent,TChild>, EntityKey<TEntity>, Changes<TEntity>, ConcurrencyCheck<TEntity>, LoadRelatedAsync and typed foreign-key changes through UpdateAsync/UpdateCheckedAsync, plus checked CRUD/bulk operations; nullable foreign keys, composite keys, explicit relation loading, NotSet versus NULL and optimistic concurrency remain distinct. Native SQLx/SeaQuery owns execution and grouping.',
 'B15': ['NativeServer.CreateBuilder, NativeServerBuilder, NativeServerApplication, ServerRoutes/RouteGroupBuilder/ServerEndpointBuilder, RequestContext, ServerRequest/ServerResponse, ServerResult/Results and typed handler/filter/middleware/auth interfaces.', 'Source-generated endpoint registration and static JsonTypeInfo metadata avoid arbitrary Delegate binding, runtime expression compilation and per-handler Cargo builds.', 'One rooted native dispatch/control bridge schedules bounded managed work; business delegates do not execute synchronously under native locks.'],
 'B16': ['ServerRequest.Body/ReadChunkAsync, BodyChunk, ServerResponse.Body/WriteAsync and Results.Stream/ServerSentEvents with ServerEvent expose the declared borrowed-stream and owned-chunk rules.', 'Native read/write operations, explicit reservation/credit ownership and finite request/retirement budgets implement bounded flow control; no raw body handle escapes.'],
 'B18': ['GrpcMarshaller<T>, GrpcMethod<TRequest,TResponse>, GrpcMethodOptions, GrpcCallContext, GrpcMetadata, GrpcException and IGeneratedGrpcService.', 'MapGrpc/MapGrpcUnary/MapGrpcServerStreaming/MapGrpcClientStreaming/MapGrpcDuplex preserve four cardinalities, typed callbacks, exact status/trailers/deadline rules and separate HTTP versus binary metadata.', 'Tonic RawCodec and one mandatory B17 HTTP2/TLS/runtime own transport and protocol execution; host_task_id remains B17.'],
 'B19': ['McpRegistry.AddTool/AddResource/AddPrompt, McpCallContext, McpToolResult<T>, McpTextResource/McpPromptMessage and McpEndpointOptions; MapMcp(routes, pattern, registry, options) is the exact public entry point.', 'Static JsonTypeInfo and typed C# callbacks reuse one precompiled rmcp ForeignMcp/Tower service on B17. Pre-parse authentication and all automatic protocol methods obey the same bounded native gate and cancellation/retirement contract.']
}

DOMAIN_ACCEPTANCE = {
 'B01': 'Verify identical generated/manual table and column identities, exact CLR-name preservation and explicit store-name overrides; validate nullable/composite keys, configured codec identity and cross-entity type safety before native side effects.',
 'B05': 'Verify COMMIT admission and Unknown independently from local release, savepoint LIFO and caller-owned transaction preservation, including cancellation after remote commit admission and cleanup quarantine.',
 'B07': 'Run golden and malformed db-wire scalar/profile/null-bit vectors, canonical metadata/parameter IDs, configured decimal/enum/JSON codecs and fallible native argument conversion with no lossy default coercion.',
 'B10': 'From one installed facade, add and change attributed Entity/DTO source, verify default CLR spelling plus explicit WeaveColumn/WeaveVersion mappings against the manual static descriptor, then build and Native AOT publish without rd.xml, runtime code generation or any Rust rebuild. Test explicit generator exclusion as the advanced manual path.',
 'B11': 'Verify JOIN reserve/commit/abort and HasMatch, source-bound projection/CTE registration, mutable selection clone -> seal operation 8 -> import kind 2 -> clause 9/14, with reverse-order finally release, window/Over snapshots, parameter identity across clone/combine/subqueries, and atomic failed native clause mutation.',
 'B13': 'Compile and execute the specified filter/join/group/aggregate/window/CTE/set-operation/parameter/locking/pagination/DTO paths; reject wrong entity/value/nullability/arithmetic consumers at their documented boundary. No managed SQL AST or runtime expression compiler may replace native tokens.',
 'B14': 'Verify independent insert and update payloads for Upsert (kind 4 field 8 carries the update values), exact required/forbidden fields for mutation kinds 0..6, CAS row counts and nullable/composite relation keys. Cover BulkResult/BulkProgress, All-operation savepoint rollback, partial committed batches, caller-owned transaction state and unknown outcomes without inventing success.',
 'B15': 'Verify finite typed handler/binder/JSON paths, starting/completed/disposable ordering and exception isolation, stream ownership at execution admission, final-status validation including bodyless responses, and deterministic trusted-forwarding rules.',
 'B16': 'Verify separate borrowed Stream versus owned BodyChunk lifetimes, native write reservation and managed credit rollback, bounded copy and retained-allocation release, exactly-once cleanup despite user callback/disposable failures, and cancellation distinct from retirement.',
 'B17': 'Verify host fault notification, sticky request cancellation and native retirement using actual Rust networking. Preserve final versus informational response rules, correct HEAD/204/205/304 framing, and the native outer protocol admission gate.',
 'B18': 'Verify all four cardinalities and message boundaries, whole-call deadlines, raw binary gRPC metadata independently from HTTP header text, trailer/status propagation and retention/retirement under cancellation on the same B17 host.',
 'B19': 'Verify nw_server_mcp_gate_resume_create and dispatch kinds 2/3 on the same request ticket, with one request_take/scope/completion and an explicit managed allow/deny continuation before rmcp parsing or automatic method dispatch. Apply the same authority/session policy to tools/resources/prompts and native lists; reject invalid Host/Origin/schema input before side effects and release cancelled gate ownership.'
}

FINAL_REVIEW_ACCEPTANCE = {
 'B01': 'Own kind23 canonical relation descriptor and parent-key db-wire definitions; golden and malformed shape/null/codec-config cases must agree with B07 and B09 without parallel primitives.',
 'B07': 'Validate kind23 and parent-key canonical bytes including ordered composite components, nullable child-key flags and exact configured codec/collation compatibility; reject malformed or lossy conversion before native effects.',
 'B09': 'Bind the post-Build source-bound nw_db_relation_register_v1(source,parent_model,child_model,kind23,&relation) and nw_db_relation_load_create_v1(session,relation,parent_key,child_projection_id,&op), unified take_owner kind2/fetch/close/retire, kind23 fields1..8 with both model hashes/table IDs/ordered columns/child NULL flags/relation hash; no mutation of frozen Table identities or invented managed relationship plan.',
 'B11': 'Nullable expression lifting uses native unary operation4 with unchanged owner, codec/configuration and SQL value; only nullability metadata widens. Verify native nullable-FK equality under SQL three-valued logic.',
 'B13': 'Compile nonnullable parent-key to nullable child-FK JOINs using AsNullable/AsNullableReference; reject nullable-to-nonnullable projection and invalid repeated or reversed lifting. Do not replace NULL with a sentinel: actual PostgreSQL/SQLite parent key0 must not match a NULL child FK. Check wrong-owner and JOIN commit/abort alias dependencies.',
 'B14': 'Verify post-Build Relation registration by source generation plus canonical description hash, ordered parent/child model and column identities, exact parent-key payload, compatible nullable FK codecs, capability checks, query/cursor retirement and reverse release of both model/projection leases. The load is one child SELECT with ordered parent-key kind4 parameters; any NULL component does not match. No implicit parent-existence check, ordering or tenant filter is added. Cover bounded concurrent cache deduplication, source-close dropping cache roots before waiting, and cancellation/decode-failure cleanup.',
 'B15': 'Before completion callbacks and disposal, automatically finish every successful incomplete HTTP response from MapRaw, generated void/Task, custom results and middleware short circuit. Cover untouched200 and preserved201; failure must not send a second final response.',
 'B16': 'Payload credit uses one atomic nonwaiting request/global backing-capacity grant; lack of credit returns resource_limit and rolls back every partial grant/queue reservation. Cover128x32KiB retained input chunks exhausting4MiB before a positive output write, cross-request global exhaustion for reads/writes, cancellation/untaken/never-started rollback and taken chunks outliving dispatch. Only bounded queue/socket/protocol backpressure may wait; no payload-credit retry loop.',
 'B17': 'Verify nonwaiting request/global native payload admission under full retained inbound credit, with cleanup preserving counters until last owner release; queue and network waits remain bounded and cancellable.',
 'B18': 'Split comma-coalesced -bin HTTP wire fields boundedly in the Rust Adapter before per-segment Tonic decoding: test OWS, empty/invalid base64, duplicate order,200entries,bytes and decode-overlap caps. Reject every prohibited raw HTTP operation and inherited/endpoint ServerFilter on gRPC routes; authentication and authorization denial use framed gRPC16/7.',
 'B19': 'MCP AwaitingGate has only the documented pre-parse HTTP denial exception. After Allow, rmcp owns protocol output and raw response/body/filter operations remain forbidden.',
 'B22': 'Assemble raw/void/custom/short-circuit automatic HTTP completion, all gRPC binary metadata and route restrictions, nullable-FK relation/query cases, and request/global retained-byte exhaustion with immediate resource_limit. Do not substitute a timeout for a liveness witness.'
}

TRACEABILITY_DESIGN_INPUTS = [
 'tools/verify_public_api.py','tools/verify_contract_acceptance.py','tools/contract_acceptance_checks.py',
 '.gitattributes','.github/workflows/public-api-design.yml','.github/workflows/english-translation.yml']
TRACEABILITY_PLAN_INPUTS = [
 'tools/prepare_acceptance.py','tools/refine_public_api.py','tools/render_packets.py',
 'tools/review_bindings.py','tools/validate_graphs.py','tools/verify_completion.py',
 'tools/verify_public_api_history.py','tools/verify_public_api_plan.py','tools/binding_attestation_checks.py',
 'tools/mutation_checks.py','tools/host_selection_checks.py','schemas/graph-v1.schema.json',
 '.github/workflows/native-slices-final-check.yml','public-api-acceptance-workflow.md',
 'api-execution-requirements.md','AGENTS.md']

def design_inputs(domains):
    common = [
        'docs/standards/csharp-public-api-and-documentation.md',
        'docs/api/README.md', 'docs/api/documentation-system.md',
        'docs/api/public-api.json', 'docs/api/reference.md',
        'docs/api/foundation-sources.json', 'docs/api/foundation-coverage.json',
        'docs/api/nuget-and-consumption.md', 'docs/api/getting-started.md',
        'docs/api/guides.md', 'experiments/public-api/abi/nativeweave_api_v1.h'
    ]
    for domain in domains:
        common += [f'docs/api/{domain}.md', f'docs/api/{domain}-coverage.json',
                   f'docs/api/{domain}-sources.json', f'docs/api/{domain}-symbol-policies.json',
                   f'experiments/public-api/NativeWeave.Api.Design/{domain.title()}.cs',
                   f'experiments/public-api/NativeWeave.Api.Consumers/{domain.title()}Examples.cs']
    if 'database' in domains:
        common.append('experiments/public-api/NativeWeave.Api.Consumers/DatabaseAdvancedExamples.cs')
    if 'server' in domains:
        common.append('experiments/public-api/abi/nativeweave_server_api_v1.h')
    paths = ['NativeWeave-Design:'+path for path in dict.fromkeys(common)]
    for path in paths:
        assert (D/path.split(':',1)[1]).is_file(), ('missing integrated API input',path)
    return paths

def preserve_prior_acceptance():
    """Snapshot exact old indices before any state transition; never rewrite evidence."""
    sources = {'Plan':'352bd56dad9804dab1b3de358c404987c26f3e4f',
               'NativeWeave-Design':'a0f6bca1f55ddf456fe931886da8be19e94a1413'}
    selected = {'Plan':['source-driven-baseline.json','research-graph.json',
                        'documentation-graph.json','delivery-graph.json','ledger/completion-acceptance.json'],
                'NativeWeave-Design':['docs/contracts/registry.json','docs/contracts/acceptance-index.json']}
    rows=[]
    directory=PRIOR_MANIFEST.parent/'prior'
    for repository,paths in selected.items():
        root=P if repository=='Plan' else D
        for path in paths:
            raw=subprocess.check_output(['git','show',sources[repository]+':'+path],cwd=root)
            snapshot=directory/repository/path
            if snapshot.exists():
                assert snapshot.read_bytes()==raw, ('immutable prior snapshot changed',snapshot)
            else:
                snapshot.parent.mkdir(parents=True,exist_ok=True);snapshot.write_bytes(raw)
            rows.append({'repository':repository,'source_commit':sources[repository],
                         'path':path,'sha256':hashlib.sha256(raw).hexdigest(),
                         'snapshot_path':snapshot.relative_to(P).as_posix()})
    result={'schema_version':'1.0.0','kind':'immutable_prior_public_api_acceptance_snapshot',
            'sources':sources,'files':rows,
            'accepted_history_pair':{'Plan':'dacaab7fc346da5b649e943a4d937a756345c492',
                                     'NativeWeave-Design':'4c5c385779b753a4f06e59d07f80ad27ca10a841'},
            'immutable_evidence_prefixes':{'Plan':['ledger/acceptance/','ledger/english-translation/'],
              'NativeWeave-Design':['verification/design-acceptance/','verification/english-translation/','docs/traceability/reviews/final-2026-11-13/','docs/traceability/reviews/english-translation/']},
            'scope':'Earlier Accepted states apply only to these exact bytes and their historical records. Public API 0.4.0 requires new actual independent review and binding; no native experiment or product acceptance is claimed.',
            'product_implementation_authorized':False}
    if PRIOR_MANIFEST.exists():assert read(PRIOR_MANIFEST)==result
    else:dump(PRIOR_MANIFEST,result)

def add_output(node, value):
    if value not in node['outputs']: node['outputs'].append(value)
    if not any(value == scope or (scope.endswith('/') and value.startswith(scope)) for scope in node['write_scopes']):
        node['write_scopes'].append(value)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-design-registry',action='store_true',
                        help='Explicitly update the paired Design registry as well as Plan candidates.')
    args=parser.parse_args()
    assert args.write_design_registry, 'Pair refinement changes Design registry; coordinate that owned path and pass --write-design-registry.'
    graphs = {k: read(P/(k+'-graph.json')) for k in ('research','documentation','delivery')}
    nodes = {n['id']: n for g in graphs.values() for n in g['nodes']}
    original_digests={identity:node_digest(node) for identity,node in nodes.items()}
    registry = read(D/'docs/contracts/registry.json')
    assert set(TASK_SURFACE)=={n['id'] for n in graphs['delivery']['nodes']}
    assert all(n['status']=='planned_candidate' and n['implementation_authorization']=={'status':'not_authorized','approval_record':None} for n in graphs['delivery']['nodes'])
    assert not any(c['version']==REVISION and c['status']=='accepted' for c in registry['contracts']), 'Do not reset accepted 0.4.0 inputs; create an explicitly reviewed new revision.'
    preserve_prior_acceptance()
    inventory=read(D/'docs/api/public-api.json')
    design_inputs(['database','server','interop'])  # preflight before writing candidates
    for contract in registry['contracts']:
        contract['version'] = REVISION
        contract['content_sha256'] = digest(D/contract['spec_path'])
        contract['status'] = 'proposed'
        contract['specification_status'] = 'public_api_refinement_pending_exact_independent_acceptance'
        contract['evidence'] = []; contract['reviews'] = []; contract['reviewers'] = []
        contract.pop('source_commit', None)
        domain = 'database' if contract['documentation_task_id'] in {'D14','D15','D16','D17'} else 'server' if contract['documentation_task_id'] in {'D18','D19'} else 'interop'
        domains=['database','server','interop'] if contract['documentation_task_id'] in {'D10','D12','D13','D20','D21'} else [domain]
        contract['api_specification_inputs'] = design_inputs(domains)
        contract['api_refinement_integrator']='/root'
        # Retain the existing attributable author; do not manufacture a reviewer or
        # retroactively attribute inherited work to a freshly named agent.
        contract['version_note'] = '0.4.0 public API refinement. Earlier accepted snapshots remain historical; native ABI wire v1 is unchanged unless an explicit operation extension says otherwise.'
        for dep in contract['dependencies']: dep['version'] = REVISION
    registry['status'] = 'public_api_refinement_review_ready'
    dump(D/'docs/contracts/registry.json', registry)
    # Old accepted indices are preserved by the prior snapshot. Current indices
    # must not present the old revision's acceptance as this candidate's state.
    candidate_index={'schema_version':'1.0.0','state':'review_ready_not_accepted',
        'api_refinement_version':REVISION,'product_implementation_authorized':False,
        'subjects':[],'binding_attestations':[],
        'prior_acceptance_manifest':'Plan:ledger/public-api-2026-11-14/prior-acceptance.json',
        'scope':'Candidate only. Actual independent technical review and fresh exact bindings are required before any subject is accepted.'}
    dump(D/'docs/contracts/acceptance-index.json',candidate_index)
    dump(P/'ledger/completion-acceptance.json',candidate_index)
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
    for path in TRACEABILITY_DESIGN_INPUTS:add_output(nodes['D31'],'NativeWeave-Design:'+path)
    for path in TRACEABILITY_PLAN_INPUTS:add_output(nodes['D31'],'Plan:'+path)
    add_output(nodes['D32'],'Plan:ledger/public-api-2026-11-14/review-readiness.md')
    # The isolated interface/generator/consumer experiment remains in the existing R06 scope.
    files = subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','experiments/public-api','verification/public-api'],cwd=D,text=True).splitlines()
    for path in sorted(set(files)):
        if (D/path).is_file(): add_output(nodes['R06'],'NativeWeave-Design:'+path)
    nodes['R06']['revision'] = REVISION
    for n in graphs['documentation']['nodes']: n['revision'] = REVISION
    for n in graphs['delivery']['nodes']:
        identity = n['id']; n['revision'] = REVISION
        domain = 'database' if identity.startswith('B') and int(identity[1:]) <= 14 else 'server' if identity.startswith('B') and int(identity[1:]) <= 20 else 'interop'
        domains = ['database','server','interop'] if identity in {'A13','A16','A21','A22','A24','B21','B22','B23','B24'} else [domain]
        n['api_design_inputs'] = design_inputs(domains)
        n['api_design_input_sha256'] = {path:digest(D/path.split(':',1)[1]) for path in n['api_design_inputs']}
        n['api_contract_types'] = sorted(name for name,policy in inventory['semantic_policies'].items() if identity in policy['tasks'])
        n['api_surface_responsibility'] = TASK_SURFACE[identity]
        n['documentation_owner_role'] = 'delivery/'+identity
        n['api_refinement_author']='/root/recover_plan'
        if identity in SURFACE_CORRECTIONS:
            n['csharp_surface']=SURFACE_CORRECTIONS[identity]
            n['candidate_api']=SURFACE_CORRECTIONS[identity]
        module=next(scope for scope in n['write_scopes'] if scope.startswith('NativeWeave:src/')).split('/')[1]
        slug=module.lower().replace('.','-')
        guide=f'NativeWeave:docs/guides/{slug}.md'
        sample=f'NativeWeave:samples/api/{slug}/'
        for scope in (guide,sample):
            if scope not in n['write_scopes']:n['write_scopes'].append(scope)
        n['documentation_outputs']=[guide,sample,
            'XML comments in the task-owned source modules; A13 composes generated API Reference from those assemblies without manual edits to another task\'s source.']
        prefix = 'Public API refinement 0.4.0: '
        n['implementation_steps'] = [x for x in n['implementation_steps'] if not x.startswith(prefix)]
        n['implementation_steps'] += [prefix+TASK_SURFACE[identity], prefix+'Use api_design_inputs and api_design_input_sha256 from the exact pinned Design commit; implement the declared member/type policies and native operation mapping. Update task-owned XML, generated API Reference contribution, guide and minimal/advanced consumer source together. For internal-only scopes document applicability and expose no accidental public plumbing.']
        n['specific_acceptance'] = [x for x in n['specific_acceptance'] if not x.startswith(prefix)]
        n['specific_acceptance'] += [prefix+'Compile exact signatures/overloads/nullability/generics and relevant generated consumers; run required actual product AOT rows, API compatibility and XML/reference/symbol coverage checks. Design stub execution is never a passed product row.', prefix+'Review installation/import/configuration/disposal/error experience, capability/native-operation correspondence and allocation/copy/FFI/runtime cost. This task owns its documentation; A16/B24 own final pristine package consumption.']
        if identity in DOMAIN_ACCEPTANCE:n['specific_acceptance'].append(prefix+DOMAIN_ACCEPTANCE[identity])
        if identity in FINAL_REVIEW_ACCEPTANCE:n['specific_acceptance'].append(prefix+FINAL_REVIEW_ACCEPTANCE[identity])
        n['verification_matrix']['api_and_documentation'] = 'Exact API/consumer compilation, current stable source comparison, XML/reference completeness, compatibility and independent usability review; justified applicability for internal-only work.'
    for kind,g in graphs.items():
        g['revision'] = REVISION
        g['public_api_standard_version'] = STANDARD_VERSION
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
    # A source topic whose content is inherited can still acquire a changed
    # dependency pin. Advance exactly the affected transitive subjects rather
    # than changing semantics under an unchanged revision.
    while True:
        changed=False
        for n in nodes.values():
            n['dependency_pins']={k:nodes[k]['revision'] for k in n['dependency_pins']}
            for dep in n.get('conditional_dependencies',[]):dep['revision']=nodes[dep['task_id']]['revision']
            for dep in n.get('release_scope',{}).get('components',[]):dep['revision']=nodes[dep['task_id']]['revision']
            if n['revision']!=REVISION and node_digest(n)!=original_digests[n['id']]:
                n['revision']=REVISION;changed=True
        if not changed:break
    for kind,g in graphs.items():dump(P/(kind+'-graph.json'),g)
    baseline=read(P/'source-driven-baseline.json')
    baseline['completion_stage']='review_ready'
    baseline['review_status']='public_api_0_4_0_refinement_pending_actual_independent_review_and_exact_binding'
    baseline['api_refinement']={
      'version':REVISION,'state':'review_ready_not_accepted',
      'prior_acceptance_manifest':PRIOR_MANIFEST.relative_to(P).as_posix(),
      'workflow':'public-api-acceptance-workflow.md',
      'candidate_inputs_require_committed_design_pin':True,
      'task_revision_policy':'Existing source studies are inherited; changed outputs, API obligations and dependency bindings receive new exact review. No original accepted evidence is rewritten.',
      'product_implementation_authorized':False}
    dump(P/'source-driven-baseline.json',baseline)
    print(json.dumps({'contracts_refined':21,'delivery_refined':48,'graphs':3,'acceptance_granted':False,'product_implementation_authorized':False}))

if __name__ == '__main__': main()
