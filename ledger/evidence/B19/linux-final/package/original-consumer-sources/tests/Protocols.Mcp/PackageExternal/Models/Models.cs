using System.Runtime.InteropServices;
using System.Text.Json.Serialization;

namespace ExternalModels;

#pragma warning disable CS0169, CS0649
[StructLayout(LayoutKind.Sequential, Size = 512)]
internal struct Padding { internal int Value; }

public sealed class ExternalInput
{
    private Padding _first;
    // PRIVATE_FIELD_EDIT
    public int Value { get; set; }
    public int Touch() => _first.Value;
}
#pragma warning restore CS0169, CS0649

public sealed record ExternalOutput(int Value);

[JsonSerializable(typeof(ExternalInput))]
[JsonSerializable(typeof(ExternalOutput))]
[JsonSourceGenerationOptions(PropertyNamingPolicy = JsonKnownNamingPolicy.CamelCase)]
public partial class ExternalJson : JsonSerializerContext;
