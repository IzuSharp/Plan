using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
foreach (var type in new[] { typeof(object), typeof(Plain), typeof(Padded), typeof(References), typeof(decimal), typeof(byte), typeof(Padded?) })
    Console.WriteLine($"{type}: public RuntimeHelpers.SizeOf={RuntimeHelpers.SizeOf(type.TypeHandle)}");
public sealed class Plain { public Padded Value { get; set; } }
[StructLayout(LayoutKind.Sequential, Size = 65536)] public struct Padded { public int A { get; set; } }
public struct References { public object? A; public int B; }
