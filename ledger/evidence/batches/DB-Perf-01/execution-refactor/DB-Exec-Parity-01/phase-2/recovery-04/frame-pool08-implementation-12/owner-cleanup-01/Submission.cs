using Korda.Data;
using Korda.Interop.Abi;

namespace Korda.Query.Internal;

internal sealed partial class QueryCommand
{
    private const int SingleRootScratchBytes = 4096;

    // QueryBinding holds exclusive admission throughout encoding and submission.
    // A private root cannot gain another origin owner here. Shared snapshots and
    // captured values retain the complete graph/owner binding path below.
    private bool TryEncodeSingleRoot(Span<byte> scratch, out int length)
    {
        length = 0;
        if (_dependencies.Count != 0) return false;
        foreach (var origin in _origins)
            if (origin.Identity.References != 1 || origin.Identity.Capture is not null) return false;
        var size = checked(56 + _written);
        if (_environment.MaxDepth < 1 || size > _environment.MaxEnvelopeBytes || _recordCount > 2 * _environment.MaxNodes) Capacity();
        if (size > scratch.Length) return false;
        var bytes = scratch[..size]; bytes[..56].Clear();
        DbWire.U32(bytes, 0, 0x4351574e); DbWire.U32(bytes, 4, 1); DbWire.U32(bytes, 8, (uint)size);
        DbWire.U32(bytes, 12, 1); DbWire.U32(bytes, 20, (uint)_recordCount);
        DbWire.U32(bytes, 32, (uint)(24 + _written)); DbWire.U32(bytes, 40, _model.TableId);
        DbWire.U32(bytes, 44, (uint)_recordCount); DbWire.U32(bytes, 48, (uint)_slots.Count);
        _records.AsSpan(0, _written).CopyTo(bytes[56..]);
        // Each local scalar record creates a distinct origin. Only imports or
        // clones can share it; equal values and repeated parameter IDs do not.
        for (var i = 0; i < _origins.Count; i++) DbWire.U32(bytes, 56 + _origins[i].Offset, checked((uint)i + 1));
        length = size; return true;
    }

    private EncodedCommand Encode()
    {
        var blocks = new List<QueryCommand>();
        var indices = new Dictionary<QueryCommand, int>(ReferenceEqualityComparer.Instance);
        var visiting = new HashSet<QueryCommand>(ReferenceEqualityComparer.Instance);
        void Visit(QueryCommand command, int depth)
        {
            if (indices.ContainsKey(command)) return;
            if (depth > _environment.MaxDepth || !visiting.Add(command)) Capacity();
            foreach (var dependency in command._dependencies) if (dependency.Snapshot is { } snapshot) Visit(snapshot, depth + 1);
            visiting.Remove(command); indices.Add(command, blocks.Count); blocks.Add(command);
            if (blocks.Count > _environment.MaxNodes + 1) Capacity();
        }
        Visit(this, 1);
        var size = 32; var records = 0;
        foreach (var block in blocks)
        {
            size = checked(size + 24 + block._written); records = checked(records + block._recordCount);
            if (size > _environment.MaxEnvelopeBytes || records > 2 * _environment.MaxNodes) Capacity();
        }
        var owners = new List<QueryCommandDependency>();
        var ownerIndices = new Dictionary<(nint, uint), uint>();
        var origins = new Dictionary<QueryOrigin, uint>(ReferenceEqualityComparer.Instance);
        uint Owner(RetainedQueryOwner owner, uint kind)
        {
            var key = (owner.Pointer, kind);
            if (ownerIndices.TryGetValue(key, out var found)) return found;
            if (owners.Count >= _environment.MaxNodes + 1) Capacity();
            var index = checked((uint)owners.Count); owners.Add(new() { Owner = owner.Pointer, Kind = kind }); ownerIndices.Add(key, index); return index;
        }
        foreach (var block in blocks)
            foreach (var origin in block._origins)
                if (!origins.ContainsKey(origin.Identity)) origins.Add(origin.Identity, checked((uint)origins.Count + 1));
        var bindings = new List<(uint Origin, uint Owner, uint RetainedOrigin)>();
        foreach (var origin in origins)
            if (origin.Key.Capture is { } retained)
            {
                var kind = retained.Owner.Owner.Kind == DatabaseOwnerKind.Plan ? 2u : 3u;
                bindings.Add((origin.Value, Owner(retained.Owner, kind), retained.Origin));
            }
        size = checked(size + 12 * bindings.Count);
        if (size > _environment.MaxEnvelopeBytes) Capacity();
        var bytes = new byte[size];
        DbWire.U32(bytes, 0, 0x4351574e); DbWire.U32(bytes, 4, 1); DbWire.U32(bytes, 8, (uint)bytes.Length);
        DbWire.U32(bytes, 12, (uint)blocks.Count); DbWire.U32(bytes, 16, (uint)indices[this]); DbWire.U32(bytes, 20, (uint)records);
        DbWire.U32(bytes, 24, (uint)bindings.Count);
        var position = 32;
        foreach (var binding in bindings)
        {
            DbWire.U32(bytes, position, binding.Origin); DbWire.U32(bytes, position + 4, binding.Owner);
            DbWire.U32(bytes, position + 8, binding.RetainedOrigin); position += 12;
        }
        foreach (var block in blocks)
        {
            DbWire.U32(bytes, position, (uint)(24 + block._written)); DbWire.U32(bytes, position + 4, Owner(block._root, 1));
            DbWire.U32(bytes, position + 8, block._model.TableId); DbWire.U32(bytes, position + 12, (uint)block._recordCount);
            DbWire.U32(bytes, position + 16, (uint)block._slots.Count); position += 24;
            block._records.AsSpan(0, block._written).CopyTo(bytes.AsSpan(position));
            foreach (var fixup in block._fixups)
            {
                var dependency = block._dependencies[fixup.Dependency];
                var index = dependency.Snapshot is { } snapshot ? checked((uint)indices[snapshot]) : Owner(dependency.Owner!, dependency.Kind);
                DbWire.U32(bytes, position + fixup.Offset, index);
            }
            foreach (var origin in block._origins)
                DbWire.U32(bytes, position + origin.Offset, origins[origin.Identity]);
            position += block._written;
        }
        return new(bytes, owners.ToArray(), origins);
    }

    internal unsafe DatabaseOwner Seal(uint terminal)
    {
        ValidateSeal(terminal); using var gates = LockOrigins(false);
        Span<byte> scratch = stackalloc byte[SingleRootScratchBytes];
        Span<QueryCommandDependency> root = stackalloc QueryCommandDependency[1];
        scoped ReadOnlySpan<byte> command; scoped ReadOnlySpan<QueryCommandDependency> dependencies;
        EncodedCommand? encoded = null;
        if (gates.Origins.Length == 0 && TryEncodeSingleRoot(scratch, out var length))
        {
            root[0] = new() { Owner = _root.Pointer, Kind = 1 };
            command = scratch[..length]; dependencies = root;
        }
        else
        {
            encoded = Encode(); command = encoded.Value.Bytes; dependencies = encoded.Value.Dependencies;
        }
        using var session = _session.Borrow(DatabaseOwnerKind.Session); nint result = 0; var error = BindingChecks.Error();
        fixed (byte* bytes = command)
        fixed (QueryCommandDependency* owners = dependencies)
            BindingChecks.Status(Calls.Compile(session.Pointer, BindingChecks.View(bytes, command.Length), owners,
                (uint)dependencies.Length, terminal, &result, &error), error);
        if (result == 0) throw new BindingFailure(NativeStatus.ContractViolation, 0, 0, 0);
        DatabaseOwner plan;
        try
        {
            // Keep the raw result unadopted until allocating metadata is ready.
            var metadata = Metadata();
            plan = new(Source, DatabaseOwnerKind.Plan, result) { QueryPlan = metadata };
        }
        catch { Source.Calls.nw_db_owner_release_v1(result); throw; }
        try { if (encoded is { } complete) PublishOrigins(plan, complete, gates); }
        catch { plan.Dispose(); throw; }
        _sealed = true; return plan;
    }

    internal unsafe nint Render()
    {
        ValidateSeal(8);
        Span<byte> scratch = stackalloc byte[SingleRootScratchBytes];
        Span<QueryCommandDependency> root = stackalloc QueryCommandDependency[1];
        scoped ReadOnlySpan<byte> command; scoped ReadOnlySpan<QueryCommandDependency> dependencies;
        if (TryEncodeSingleRoot(scratch, out var length))
        {
            root[0] = new() { Owner = _root.Pointer, Kind = 1 };
            command = scratch[..length]; dependencies = root;
        }
        else
        {
            var encoded = Encode(); command = encoded.Bytes; dependencies = encoded.Dependencies;
        }
        using var session = _session.Borrow(DatabaseOwnerKind.Session); nint result = 0; var error = BindingChecks.Error();
        fixed (byte* bytes = command)
        fixed (QueryCommandDependency* owners = dependencies)
            BindingChecks.Status(Calls.Render(session.Pointer, BindingChecks.View(bytes, command.Length), owners,
                (uint)dependencies.Length, &result, &error), error);
        if (result == 0) throw new BindingFailure(NativeStatus.ContractViolation, 0, 0, 0);
        return result;
    }

    internal unsafe DatabaseOwner CreateCte(DatabaseOwner declaredModel, uint tableId, bool recursive)
    {
        BindingChecks.SameSource(Source, declaredModel); ValidateSeal(8);
        _environment.Require("db.cte.v1"); if (recursive) _environment.Require("db.recursive-cte.v1");
        var model = declaredModel.QueryModel ?? throw new ArgumentException("Missing CTE declaration metadata.");
        using var gates = LockOrigins(true); var encoded = Encode(); using var session = _session.Borrow(DatabaseOwnerKind.Session);
        using var declared = declaredModel.Borrow(DatabaseOwnerKind.Model); nint result = 0; var error = BindingChecks.Error();
        fixed (byte* bytes = encoded.Bytes)
        fixed (QueryCommandDependency* dependencies = encoded.Dependencies)
            BindingChecks.Status(Calls.Cte(session.Pointer, BindingChecks.View(bytes, encoded.Bytes.Length), dependencies,
                (uint)encoded.Dependencies.Length, declared.Pointer, tableId, recursive ? 1u : 0u, &result, &error), error);
        if (result == 0) throw new BindingFailure(NativeStatus.ContractViolation, 0, 0, 0);
        DatabaseOwner cte;
        try
        {
            var metadata = new QueryCteMetadata(model.Table, Metadata());
            cte = new(Source, DatabaseOwnerKind.Cte, result) { QueryCte = metadata };
        }
        catch { Source.Calls.nw_db_owner_release_v1(result); throw; }
        try { PublishOrigins(cte, encoded, gates); return cte; }
        catch { cte.Dispose(); throw; }
    }

    private OriginGates LockOrigins(bool all)
    {
        if (!all && !_dependencies.Any(dependency => dependency.Snapshot is not null)
            && !_origins.Any(origin => origin.Identity.Capture is null && origin.Identity.References > 1)) return OriginGates.Empty;
        var origins = new HashSet<QueryOrigin>(ReferenceEqualityComparer.Instance);
        var visited = new HashSet<QueryCommand>(ReferenceEqualityComparer.Instance);
        void Visit(QueryCommand command, bool snapshot)
        {
            if (!visited.Add(command)) return;
            foreach (var origin in command._origins)
                if (origin.Identity.Capture is null && (all || snapshot || origin.Identity.References > 1)) origins.Add(origin.Identity);
            foreach (var dependency in command._dependencies) if (dependency.Snapshot is { } child) Visit(child, true);
        }
        Visit(this, false); return new(origins.OrderBy(origin => origin.Sequence).ToArray());
    }

    private static void PublishOrigins(DatabaseOwner result, EncodedCommand encoded, OriginGates gates)
    {
        RetainedQueryOwner? retained = null;
        try
        {
            foreach (var origin in gates.Origins)
                if (origin.Capture is null)
                {
                    retained ??= new(result, result.Kind);
                    origin.Publish(retained, encoded.Origins[origin]);
                }
        }
        finally { retained?.Release(); }
    }

    private sealed class OriginGates : IDisposable
    {
        internal static readonly OriginGates Empty = new([]);
        private readonly QueryOrigin[] _origins;
        internal QueryOrigin[] Origins => _origins;
        private int _entered;
        internal OriginGates(QueryOrigin[] origins)
        {
            _origins = origins;
            try { foreach (var origin in origins) { Monitor.Enter(origin.Gate); _entered++; } }
            catch { Dispose(); throw; }
        }
        public void Dispose() { while (_entered != 0) Monitor.Exit(_origins[--_entered].Gate); }
    }

    private readonly record struct EncodedCommand(byte[] Bytes, QueryCommandDependency[] Dependencies, IReadOnlyDictionary<QueryOrigin, uint> Origins);
}
