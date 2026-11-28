using System.Text;

// FNV-1a over typed canonical fields, never CLR object hash codes.
// Int64: eight little-endian bytes. String: signed byte length then UTF-8; NULL length=-1.
// Money: exact signed cents as Int64. Boolean: one byte 0/1. No row separators.
internal struct Digest
{
    internal ulong Value;
    internal static Digest Create() => new() { Value = 14695981039346656037UL };
    private void Byte(byte value) { Value ^= value; Value *= 1099511628211UL; }
    internal void Integer(long value)
    {
        var bits = unchecked((ulong)value);
        for (var i = 0; i < 8; i++) { Byte((byte)bits); bits >>= 8; }
    }
    internal void Boolean(bool value) => Byte(value ? (byte)1 : (byte)0);
    internal void Money(decimal value) => Integer(checked((long)(value * 100m)));
    internal void Text(string? value)
    {
        if (value is null) { Integer(-1); return; }
        var bytes = Encoding.UTF8.GetByteCount(value);
        Integer(bytes);
        if (bytes > 4096) throw new InvalidOperationException("The fixed workload's UTF-8 field bound was exceeded.");
        Span<byte> buffer = stackalloc byte[4096];
        var written = Encoding.UTF8.GetBytes(value.AsSpan(), buffer);
        for (var i = 0; i < written; i++) Byte(buffer[i]);
    }
}

internal readonly record struct OperationResult(long Rows, ulong Digest, long Suspensions);
internal delegate void RowDigest<in T>(ref Digest digest, T value);
