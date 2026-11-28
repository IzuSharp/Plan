#!/usr/bin/env python3
"""Compile the unchanged Xerial JNI wrapper against an existing exact SQLite engine."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

p=argparse.ArgumentParser()
p.add_argument('--toolchains',type=Path,required=True,help='Task Java toolchain directory')
p.add_argument('--sqlite-prefix',type=Path,required=True,help='Existing baseline prefix with include/sqlite3.h and lib/libsqlite3.so')
args=p.parse_args()
base=args.toolchains.resolve();sqlite=args.sqlite_prefix.resolve()
jdk=base/'graalvm-community-25.6.5.1+2.1';src=base/'xerial-sqlite-3.51.3.0';out=base/'sqlite-jni';headers=out/'headers'
revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=src,text=True).strip()
if revision!='bf18ce13f938411a4cc1b417b1ce5fbb95c09db6':raise SystemExit('Unexpected Xerial source revision')
headers.mkdir(parents=True,exist_ok=True)
jars=[base/'m2/org/xerial/sqlite-jdbc/3.51.3.0/sqlite-jdbc-3.51.3.0.jar',base/'m2/org/slf4j/slf4j-api/2.0.17/slf4j-api-2.0.17.jar']
javac=[str(jdk/'bin/javac'),'-cp',':'.join(map(str,jars)),'-d',str(out/'header-classes'),'-h',str(headers),str(src/'src/main/java/org/sqlite/core/NativeDB.java')]
subprocess.run(javac,check=True)
shutil.copyfile(headers/'org_sqlite_core_NativeDB.h',headers/'NativeDB.h')
cc=['gcc','-shared','-fPIC','-Os','-fvisibility=hidden','-I'+str(jdk/'include'),'-I'+str(jdk/'include/linux'),'-I'+str(headers),'-I'+str(sqlite/'include'),str(src/'src/main/java/org/sqlite/core/NativeDB.c'),'-L'+str(sqlite/'lib'),'-Wl,-rpath,'+str(sqlite/'lib'),'-Wl,--no-undefined','-lsqlite3','-pthread','-lm','-o',str(out/'libsqlitejdbc.so')]
subprocess.run(cc,check=True)
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
record={'sourceCommit':revision,'nativeDbC':sha(src/'src/main/java/org/sqlite/core/NativeDB.c'),'javacCommand':javac,'ccCommand':cc,
        'jniSha256':sha(out/'libsqlitejdbc.so'),'sqliteSha256':sha(sqlite/'lib/libsqlite3.so'),
        'scope':'Unmodified Xerial NativeDB.c thin JNI wrapper; dynamically links exact baseline SQLite; SQLite source and compile options unchanged'}
(out/'build-receipt.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
