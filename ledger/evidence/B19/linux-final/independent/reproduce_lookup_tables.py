#!/usr/bin/env python3
"""Regenerate the exact compact-table JIT/AOT allocation witness source."""
import argparse,hashlib,json
from pathlib import Path
PREFIX = 'using System.Runtime.CompilerServices;\nusing System.Reflection;\nConsole.WriteLine($"Runtime={Environment.Version}; dynamic={RuntimeFeature.IsDynamicCodeSupported}");\nMeasure("direct32", P32.Proof, typeof(T32_0032));\nMeasure("direct256", P256.Proof, typeof(T256_0256));\nMeasure("direct2048", P2048.Proof, typeof(T2048_2048));\nMeasure("indirect", Indirect.Proof, typeof(Indirect.Target));\nMeasure("indirect2048", IndirectMany.Proof, typeof(IndirectMany.Target));\nstatic void Measure(string label, Func<Type,(int,int)> proof, Type selected)\n{\n    GC.Collect(); GC.WaitForPendingFinalizers();\n    long before = GC.GetAllocatedBytesForCurrentThread();\n    var first = proof(selected);\n    long firstBytes = GC.GetAllocatedBytesForCurrentThread() - before;\n    before = GC.GetAllocatedBytesForCurrentThread();\n    var second = proof(selected);\n    long secondBytes = GC.GetAllocatedBytesForCurrentThread() - before;\n    Console.WriteLine($"{label}: first={firstBytes}; second={secondBytes}; result={first.Item1}/{second.Item1}");\n}\ninternal static class Indirect\n{\n    internal class Target { }\n    [MethodImpl(MethodImplOptions.NoInlining)]\n    internal static (int,int) Proof(Type type)\n    {\n        var definition = type.IsGenericType ? type.GetGenericTypeDefinition() : type;\n        string? name = definition.FullName;\n        string? assembly = definition.Assembly.GetName().Name;\n        if (assembly == "Probe" && name == "Indirect+Target") return (1,2);\n        return (-1,-1);\n    }\n}\n'
INDIRECT_HEADER = '\ninternal static class IndirectMany { internal sealed class Target {} [MethodImpl(MethodImplOptions.NoInlining)] internal static (int,int) Proof(Type type) { var definition = type.IsGenericType ? type.GetGenericTypeDefinition() : type; string? name=definition.FullName; string? assembly=definition.Assembly.GetName().Name;\n'
PROJECT = '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net11.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable><TreatWarningsAsErrors>false</TreatWarningsAsErrors><IsAotCompatible>true</IsAotCompatible></PropertyGroup></Project>\n'

def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    path=args.output.resolve();path.mkdir(parents=True,exist_ok=False)
    parts=[PREFIX]
    for n in (32,256,2048):
        parts.append(f'internal static class P{n} {{ [MethodImpl(MethodImplOptions.NoInlining)] internal static (int,int) Proof(Type type) {{ var definition = type.IsGenericType ? type.GetGenericTypeDefinition() : type;\n')
        parts.extend(f'if (definition == typeof(T{n}_{i:04d})) return (1,2);\n' for i in range(n+1))
        parts.append('return (-1,-1); }}\n')
        parts.extend(f'internal sealed class T{n}_{i:04d} {{ }}\n' for i in range(n+1))
    parts.append(INDIRECT_HEADER)
    parts.extend(f'if (assembly == "Probe" && name == "Unrelated+T{i:04d}") return (1,2);\n' for i in range(2048))
    parts.append('if (assembly == "Probe" && name == "IndirectMany+Target") return (1,2); return(-1,-1); } }\n')
    (path/'Program.cs').write_text(''.join(parts));(path/'Probe.csproj').write_text(PROJECT)
    print(json.dumps({'source_sha256':hashlib.sha256((path/'Program.cs').read_bytes()).hexdigest(),'source_bytes':(path/'Program.cs').stat().st_size}))
if __name__=='__main__':main()
