(async function uploadAtomic(limit=6){
 const root=load("uploadRoot"),manifest=load("uploadManifest"),receipts=load("uploadReceipts");
 const complete=new Set(receipts.blobs.map(x=>x.path));
 const batch=manifest.files.filter(f=>!complete.has(f.path)).slice(0,limit);
 const quote=s=>"'"+s.replace(/'/g,"'\\''")+"'";
 let persistence=Promise.resolve();
 const persist=()=>{
  store("uploadReceipts",receipts);
  const snapshot=JSON.stringify(receipts,null,2)+"\n";
  persistence=persistence.then(async()=>{
   const code="from pathlib import Path\nimport sys,json,hashlib,os,datetime\np=Path(sys.argv[1]);s=sys.argv[2];tmp=p.with_suffix('.tmp');tmp.write_text(s);os.replace(tmp,p)\nm=p.parent/'blob-publication-manifest-04.json';mb=m.read_bytes();manifest=json.loads(mb);receipt=json.loads(s);done={x['path'] for x in receipt['blobs']};pending=[x for x in manifest['files'] if x['path'] not in done]\nstate={'task':'DB-Exec-Parity-01','updatedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'completed':len(done),'total':len(manifest['files']),'remaining':len(pending),'remainingBytes':sum(x['bytes'] for x in pending),'nextPath':pending[0]['path'] if pending else None,'manifestSha256':hashlib.sha256(mb).hexdigest(),'receiptsSha256':hashlib.sha256(s.encode()).hexdigest(),'remotePublication':False,'scope':'create_blob only; no tree, commit, ref or branch changed'}\np=p.parent/'blob-upload-resume-04.json';t=p.with_suffix('.tmp');t.write_text(json.dumps(state,indent=2)+'\\n');os.replace(t,p)";
   const r=await tools.exec_command({cmd:"taskset -c 8 nice -n 19 python3 -c "+quote(code)+" "+quote(root+"/blob-upload-receipts-04.json")+" "+quote(snapshot),max_output_tokens:1000});
   if(r.exit_code!==0)throw new Error("atomic receipt write failed: "+r.output);
  });
  return persistence;
 };
 const one=async(f)=>{
  try {
   const n=786429,p=f.sourcePath||(root+"/"+f.path);
   const rs=await Promise.allSettled(Array.from({length:Math.ceil(f.bytes/n)},(_,i)=>(async()=>{
    const offset=i*n,len=Math.min(n,f.bytes-offset);
    const script="import base64\nwith open("+JSON.stringify(p)+",'rb') as f:\n f.seek("+offset+")\n print(base64.b64encode(f.read("+len+")).decode())";
    const r=await tools.exec_command({cmd:"taskset -c 8 nice -n 19 python3 -c "+quote(script),max_output_tokens:400000,yield_time_ms:10000});
    const s=r.output.trim();
    if(r.exit_code!==0||s.length!==4*Math.ceil(len/3)||!/^[A-Za-z0-9+/]+={0,2}$/.test(s))throw new Error("chunk "+i+" bad length "+s.length);
    return s;
   })()));
   const failures=rs.filter(x=>x.status==="rejected");
   if(failures.length)throw new Error("read chunks: "+failures.map(x=>String(x.reason)).join(";"));
   const content=rs.map(x=>x.value).join("");
   if(content.length!==4*Math.ceil(f.bytes/3))throw new Error("joined length mismatch");
   const result=await tools.mcp__codex_apps__github_create_blob({repository_full_name:"IzuSharp/Plan",encoding:"base64",content});
   if(result.isError||result.structuredContent?.sha!==f.gitBlobSha)throw new Error("GitHub blob result mismatch "+JSON.stringify(result));
   receipts.blobs.push({path:f.path,bytes:f.bytes,sha:result.structuredContent.sha,createdInThisSession:true,chunkBytes:n,verification:"GitHub SHA equals local manifest Git blob SHA",remotePublication:false});
   await persist();
   return true;
  }catch(error){
   receipts.attempts.push({path:f.path,phase:"read-create-persist-blob",passed:false,error:String(error)});
   await persist();throw error;
  }
 };
 for(let i=0;i<batch.length;i+=2){
  const pair=batch.slice(i,i+2), results=await Promise.allSettled(pair.map(one));
  if(results.some(x=>x.status==="rejected")){text({failedPair:pair.map(x=>x.path),errors:results.filter(x=>x.status==="rejected").map(x=>String(x.reason))});break;}
 }
 if(batch.length===0) await persist();
 await persistence;
 const done=new Set(receipts.blobs.map(x=>x.path));
 text({receiptBlobs:receipts.blobs.length,totalFiles:manifest.files.length,remainingFiles:manifest.files.filter(f=>!done.has(f.path)).length,remainingParts:manifest.files.filter(f=>f.path.endsWith(".bin")&&!done.has(f.path)).length});
})