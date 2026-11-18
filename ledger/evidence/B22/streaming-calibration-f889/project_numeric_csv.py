#!/usr/bin/env python3
"""Lossless JSON scalar CSV projection for the allowlisted B22 telemetry files."""
from pathlib import Path
import csv,hashlib,json,collections,sys

SOURCES=('resources.jsonl','operations.jsonl','service/observations.jsonl','trace-receipt.json.samples.jsonl')
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def pointer(path):return ''.join('/'+str(x).replace('~','~0').replace('/','~1') for x in path)
def flatten(value,path=(),containers=None):
    result={}
    if isinstance(value,(dict,list)) and value:
        containers.setdefault(pointer(path),set()).add('object' if isinstance(value,dict) else 'array')
        items=value.items() if isinstance(value,dict) else enumerate(value)
        for k,v in items:result.update(flatten(v,(*path,k),containers))
    else:result[pointer(path)]=value
    return result

def project(source,output):
    output.mkdir(parents=True,exist_ok=False)
    schema={'schemaVersion':1,'sourceDirectory':str(source),'encoding':'Each present cell contains the exact JSON scalar (or empty-container literal); an empty CSV cell means missing, distinct from null. Column headers are RFC6901 JSON pointers. row_index retains the original zero-based JSONL row. Files split only by original top-level field set to avoid sparse repeated-key rows.','verification':'Every projected row is decoded and compared against all original typed flattened values; no scalar is rounded or omitted. Original container kinds and row indices retain shape and order. Original JSONL bytes/hashes remain separately identified.','files':{}}
    for relative in SOURCES:
        path=source/relative
        if not path.exists():continue
        original=[json.loads(line)for line in path.read_text().splitlines()]
        groups=collections.defaultdict(list)
        for index,value in enumerate(original):groups[tuple(sorted(value))].append((index,value))
        file_meta={'sha256':digest(path),'bytes':path.stat().st_size,'rows':len(original),'groups':[]}
        verified={}
        for number,(keys,rows) in enumerate(sorted(groups.items()),1):
            containers={};flat=[(i,flatten(value,containers=containers))for i,value in rows]
            columns=sorted({k for _,v in flat for k in v})
            target=output/(relative.replace('/','-').replace('.jsonl','')+f'.{number:02}.csv')
            with target.open('w',newline='')as f:
                writer=csv.writer(f,lineterminator='\n');writer.writerow(['row_index',*columns])
                for i,v in flat:writer.writerow([i,*[json.dumps(v[c],ensure_ascii=False,separators=(',',':'),allow_nan=False)if c in v else ''for c in columns]])
            with target.open(newline='')as f:
                for row in csv.DictReader(f):
                    i=int(row.pop('row_index'));decoded={k:json.loads(v)for k,v in row.items()if v!=''}
                    expected=flatten(original[i],containers={})
                    assert decoded==expected and all(type(decoded[k])is type(expected[k])for k in decoded)
                    assert i not in verified;verified[i]=True
            kinds={c:sorted({type(v[c]).__name__ for _,v in flat if c in v})for c in columns}
            file_meta['groups'].append({'path':target.name,'sha256':digest(target),'bytes':target.stat().st_size,'rows':len(flat),'topLevelKeys':list(keys),'containerKinds':{k:sorted(v)for k,v in sorted(containers.items())},'columnValueTypes':kinds})
        assert sorted(verified)==list(range(len(original)))
        file_meta['allRowsAndScalarTypesRoundTrip']=True;schema['files'][relative]=file_meta
    (output/'schema.json').write_text(json.dumps(schema,indent=2)+'\n')
    print(json.dumps({'source':str(source),'projection':str(output),'rows':sum(v['rows']for v in schema['files'].values()),'bytes':sum(p.stat().st_size for p in output.iterdir()),'allRoundTrips':True}))

if __name__=='__main__':project(Path(sys.argv[1]),Path(sys.argv[2]))
