using System.Runtime.InteropServices;
using NativeWeave.Data;
using NativeWeave.Interop.Abi;
using NativeWeave.Query.Internal;

unsafe
{
    var module = NativeLibrary.Load(Path.GetFullPath(args[0]));
    var calls = new NativeCalls("query.binding.fixture", name => NativeLibrary.TryGetExport(module, name, out var p) ? p : 0);
    var open = (delegate* unmanaged[Cdecl]<nint*, nint*, uint>)NativeLibrary.GetExport(module, "nw_test_open_v1");
    var live = (delegate* unmanaged[Cdecl]<uint, ulong>)NativeLibrary.GetExport(module, "nw_test_live_v1");
    nint nativeSource = 0, nativeSession = 0;
    if (open(&nativeSource, &nativeSession) != 0) throw new InvalidOperationException("fixture open failed");
    var identity = new SourceBinding(calls, 1);
    var sourceOwner = new DatabaseOwner(identity, DatabaseOwnerKind.Source, nativeSource);
    var sessionOwner = new DatabaseOwner(identity, DatabaseOwnerKind.Session, nativeSession);
    var builder = new TableBuilder<Row>("ownership_probe");
    var id = builder.Column("id", Codecs.Int64, new() { IsPrimaryKey = true });
    var table = builder.Build(row => new Row(row.Get(id)), (row, value) => row.Set(id, value.Id));
    bool admittedAfterDispose = false, createdAfterDispose = false;
    ulong before = live(1), during;
    using (var earlier = sourceOwner.Borrow(DatabaseOwnerKind.Source))
    {
        sourceOwner.Dispose();
        during = live(1);
        Console.WriteLine($"after_dispose physical_owners={during} safehandle_is_closed={sourceOwner.IsClosed}");
        try { using var late = sourceOwner.Borrow(DatabaseOwnerKind.Source); admittedAfterDispose = true; }
        catch (ObjectDisposedException) { }
        try { using var lateModel = MetadataBindings.RegisterModel(sourceOwner, table); createdAfterDispose = true; }
        catch (ObjectDisposedException) { }
    }
    ulong afterEarlier = live(1);
    sessionOwner.Dispose();
    ulong final = live(1);
    Console.WriteLine($"prior_lease_keeps_physical_owner={during == before}; new_lease_after_dispose={admittedAfterDispose}; new_native_model_after_dispose={createdAfterDispose}; after_prior_lease={afterEarlier}; final_owners={final}");
    NativeLibrary.Free(module);
    if (final != 0) throw new InvalidOperationException("probe leaked native owner");
    if (admittedAfterDispose || createdAfterDispose) return 1;
    return 0;
}
internal sealed record Row(long Id);
