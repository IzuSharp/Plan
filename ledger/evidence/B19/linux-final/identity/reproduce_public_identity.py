#!/usr/bin/env python3
"""Generate the exact B19 public identity fixture; optionally run a frozen product."""
import argparse, hashlib, json, os, shutil, subprocess
from pathlib import Path

HEADER = 'using System.Text.Json.Serialization;\nusing NativeWeave.Server.Mcp;\nContainer.Run();\ninternal partial class Container {\ninternal static void Run() {\nvar input=Context.Default.Root;\nint g0=GC.CollectionCount(0), g1=GC.CollectionCount(1), g2=GC.CollectionCount(2);\nlong before=GC.GetAllocatedBytesForCurrentThread();\nvar registry=new McpRegistry();\nregistry.AddTool("identity", "identity scratch witness", input, input, static (Root value,McpCallContext _) => Task.FromResult(McpToolResult<Root>.Success(value)));\nlong allocated=GC.GetAllocatedBytesForCurrentThread()-before;\nlong characters=0; foreach(var property in input.Properties) characters+=property.PropertyType.FullName!.Length;\nConsole.WriteLine($"Public AddTool accepted; types={input.Properties.Count + 2}; properties={input.Properties.Count * 2}; selected_fullname_chars={characters}; cached_UTF16_payload_min={characters * 2}; AddTool_allocated={allocated}; startup_cap={4*1024*1024}");\nvar observed=input.Properties.Select(p=>new WeakReference<string>(p.PropertyType.FullName!)).ToArray();\nConsole.WriteLine($"Collections during AddTool: {GC.CollectionCount(0)-g0}/{GC.CollectionCount(1)-g1}/{GC.CollectionCount(2)-g2}");\nGC.Collect(); GC.WaitForPendingFinalizers(); GC.Collect();\nConsole.WriteLine($"Names still strongly reachable after forced GC: {observed.Count(w=>w.TryGetTarget(out _))}/{observed.Length}");\nGC.KeepAlive(registry); GC.KeepAlive(input);\n}\n'
PROJECT = '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net11.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable><TreatWarningsAsErrors>false</TreatWarningsAsErrors><IsAotCompatible>false</IsAotCompatible></PropertyGroup><ItemGroup><Reference Include="input/*.dll"/><Analyzer Include="analyzer/*.dll"/></ItemGroup></Project>\n'

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def source(reject=False):
    header = HEADER
    if reject:
        call = 'registry.AddTool("identity", "identity scratch witness", input, input, static (Root value,McpCallContext _) => Task.FromResult(McpToolResult<Root>.Success(value)));'
        replacement = 'try { ' + call + ' } catch (ArgumentException error) {\n' + \
            'long rejectedBytes = GC.GetAllocatedBytesForCurrentThread()-before;\n' + \
            'if (!error.Message.Contains("NWAPI-S004",StringComparison.Ordinal) || error.Message.Length>1024 || rejectedBytes>=4*1024*1024) throw new InvalidOperationException("Unbounded identity rejection", error);\n' + \
            'Console.WriteLine($"Identity rejected before private name expansion; allocated={rejectedBytes}; diagnostic_chars={error.Message.Length}; dynamic={System.Runtime.CompilerServices.RuntimeFeature.IsDynamicCodeSupported}");\nreturn; }\n' + \
            'if (registry is not null) throw new InvalidOperationException("Expected identity admission rejection.");'
        header = header.replace(call, replacement)
    prefix = '.'.join('N'+str(i).zfill(3)+'x'*496 for i in range(70))
    parts = [header, 'private sealed class Root {\n']
    parts.extend(f'public {prefix}.T{i}? P{i} {{get;set;}}\n' for i in range(60))
    parts.append('}\n[JsonSerializable(typeof(Root))]\nprivate partial class Context : JsonSerializerContext;\n')
    parts.extend(('private' if i==0 else 'public')+' class N'+str(i).zfill(3)+'x'*496+' {\n' for i in range(70))
    parts.extend(f'public sealed class T{i} {{ public int Value {{get;set;}} }}\n' for i in range(60))
    parts.extend('}\n' for _ in range(71))
    return ''.join(parts)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--inputs', type=Path)
    parser.add_argument('--analyzer', type=Path)
    parser.add_argument('--sdk', default='dotnet')
    parser.add_argument('--expect', choices=['accept','reject'], default='accept')
    parser.add_argument('--aot', action='store_true')
    parser.add_argument('--generate-only', action='store_true')
    args=parser.parse_args()
    output=args.output.resolve(); output.mkdir(parents=True,exist_ok=False)
    (output/'Program.cs').write_text(source(args.expect=='reject'))
    (output/'Probe.csproj').write_text(PROJECT)
    result={'expect':args.expect,'source_sha256':digest(output/'Program.cs'),'source_bytes':(output/'Program.cs').stat().st_size,'project_sha256':digest(output/'Probe.csproj'),'commands':[]}
    if args.generate_only:
        print(json.dumps(result)); return
    if args.inputs is None or args.analyzer is None: parser.error('--inputs and --analyzer are required to run')
    for sub in ['input','analyzer']: (output/sub).mkdir()
    for path in args.inputs.glob('*.dll'): shutil.copy2(path,output/'input'/path.name)
    shutil.copy2(args.analyzer,output/'analyzer'/args.analyzer.name)
    result['input_sha256']={str(path.relative_to(output)):digest(path) for sub in ['input','analyzer'] for path in (output/sub).glob('*.dll')}
    def run(name,argv):
        log=output/(name+'.log')
        with log.open('w') as stream: completed=subprocess.run(argv,cwd=output,stdout=stream,stderr=subprocess.STDOUT)
        result['commands'].append({'name':name,'argv':argv,'exit_code':completed.returncode,'log':log.name,'sha256':digest(log)})
        (output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
        if completed.returncode: raise RuntimeError(name+' failed: '+str(log))
        return log.read_text()
    flags=['-p:UseSharedCompilation=false','-nr:false','-m:1']
    run('restore',[args.sdk,'restore','Probe.csproj','--ignore-failed-sources',*flags])
    run('build',[args.sdk,'build','Probe.csproj','-c','Release','--no-restore',*flags])
    text=run('jit',[args.sdk,str(output/'bin/Release/net11.0/Probe.dll')])
    if args.expect=='accept' and 'Names still strongly reachable after forced GC: 60/60' not in text: raise RuntimeError('Original retention witness did not reproduce')
    if args.expect=='reject' and 'Identity rejected before private name expansion' not in text: raise RuntimeError('Bounded rejection did not execute')
    if args.aot:
        run('restore-aot',[args.sdk,'restore','Probe.csproj','-r','linux-x64','-p:PublishAot=true','--ignore-failed-sources',*flags])
        run('publish-aot',[args.sdk,'publish','Probe.csproj','-c','Release','-r','linux-x64','-p:PublishAot=true','--no-restore','-o',str(output/'aot'),*flags])
        text=run('aot',[str(output/'aot/Probe')])
        if args.expect=='reject' and ('dynamic=False' not in text or 'Identity rejected before private name expansion' not in text): raise RuntimeError('AOT bounded rejection did not execute')
    result['status']='passed'; (output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':'passed','result':str(output/'result.json'),'sha256':digest(output/'result.json')}))
if __name__=='__main__': main()
