using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using System.Reflection;
using System.Runtime.Loader;
using System.Text;
var refs = ((string)AppContext.GetData("TRUSTED_PLATFORM_ASSEMBLIES")!).Split(Path.PathSeparator).Select(path => MetadataReference.CreateFromFile(path)).ToArray();
const int nesting = 70, count = 60;
var text = new StringBuilder("public static class Container { public static System.Type[] Types() => new System.Type[] { ");
string prefix = string.Join(".", Enumerable.Range(0, nesting).Select(i => "N" + i.ToString("D3") + new string('x', 496)));
for (int i=0; i<count; i++) text.Append("typeof(").Append(prefix).Append(".T").Append(i).Append("),");
text.Append("}; ");
for (int i=0; i<nesting; i++) text.Append(i == 0 ? "private class N" : "public class N").Append(i.ToString("D3")).Append(new string('x',496)).Append(" { ");
for (int i=0; i<count; i++) text.Append("public class T").Append(i).Append(" { public int Value {get;set;} } ");
for (int i=0; i<nesting+1; i++) text.Append("} ");
var compilation=CSharpCompilation.Create("IdentityFixture",[CSharpSyntaxTree.ParseText(text.ToString())],refs,new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary,optimizationLevel:OptimizationLevel.Release));
using var image=new MemoryStream(); var emit=compilation.Emit(image);
if(!emit.Success) { Console.WriteLine(string.Join("\n",emit.Diagnostics.Where(x=>x.Severity==DiagnosticSeverity.Error))); return; }
image.Position=0; var assembly=AssemblyLoadContext.Default.LoadFromStream(image);
var types=(Type[])assembly.GetType("Container")!.GetMethod("Types")!.Invoke(null,null)!;
long before=GC.GetAllocatedBytesForCurrentThread();
long chars=0;
foreach(var type in types) { chars+=type.FullName!.Length; _=type.Assembly.GetName().Name; }
long allocated=GC.GetAllocatedBytesForCurrentThread()-before;
Console.WriteLine($"types={types.Length}; max_identity_chars={types.Max(t=>t.FullName!.Length)}; retained_name_chars={chars}; UTF16_payload_min={2*chars}; allocated={allocated}; startup_cap={4*1024*1024}");
GC.KeepAlive(types);
