#!/usr/bin/env python3
"""Build only; never runs a benchmark. Honors existing proxy and OS CA trust."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import urllib.parse
import xml.etree.ElementTree as ET

p = argparse.ArgumentParser()
p.add_argument('--toolchains', type=Path, required=True, help='Task-owned Java toolchain directory')
p.add_argument('--native', action='store_true')
args = p.parse_args()
base = args.toolchains.resolve()
project = Path(__file__).resolve().parent
def input_hashes():
    files=[project/'pom.xml',*sorted((project/'src').rglob('*'))]
    return {str(f.relative_to(project)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files if f.is_file()}
before_inputs=input_hashes()
started_utc=datetime.now(timezone.utc).isoformat()
jdk = base / 'graalvm-community-25.6.5.1+2.1'
maven = base / 'apache-maven-3.10.2/bin/mvn'
trust = base / 'environment-cacerts'
if not trust.exists():
    shutil.copyfile(jdk / 'lib/security/cacerts', trust)
    for i, cert in enumerate(Path('/usr/local/share/ca-certificates').glob('*.crt')):
        subprocess.run([str(jdk/'bin/keytool'), '-importcert', '-noprompt', '-alias', f'environment-ca-{i}',
                        '-file', str(cert), '-keystore', str(trust), '-storepass', 'changeit'], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
env = os.environ.copy()
env['JAVA_HOME'] = str(jdk)
env['PATH'] = str(jdk/'bin') + ':' + env['PATH']
env['MAVEN_OPTS'] = '-Xmx768m -Djavax.net.ssl.trustStore=' + str(trust)
# Proxy ports may be short lived in a managed executor. Read the current environment per invocation.
settings = ET.Element('settings')
proxy = urllib.parse.urlsplit(env.get('HTTPS_PROXY') or env.get('https_proxy') or '')
if proxy.hostname:
    q = ET.SubElement(ET.SubElement(settings, 'proxies'), 'proxy')
    for key, value in [('id','environment'), ('active','true'), ('protocol','http'), ('host',proxy.hostname),
                       ('port',str(proxy.port or 80)), ('nonProxyHosts','localhost|127.*')]:
        ET.SubElement(q, key).text = value
    if proxy.username: ET.SubElement(q, 'username').text = urllib.parse.unquote(proxy.username)
    if proxy.password: ET.SubElement(q, 'password').text = urllib.parse.unquote(proxy.password)
with tempfile.NamedTemporaryFile(prefix='maven-settings-', suffix='.xml', dir=base) as f:
    ET.ElementTree(settings).write(f, encoding='utf-8', xml_declaration=True)
    f.flush()
    command = [str(maven), '-s', f.name, '-B', '-ntp', '-U', '-Dmaven.repo.local='+str(base/'m2'), '-DskipTests']
    if args.native: command.append('-Pnative')
    command += ['package', 'dependency:build-classpath', '-Dmdep.outputFile=target/runtime-classpath.txt']
    subprocess.run(command, cwd=project, env=env, check=True)
if before_inputs!=input_hashes():
    raise SystemExit('Source changed during build; this executable has no frozen-source acceptance identity. Rebuild the final source.')
cp = (project/'target/runtime-classpath.txt').read_text().strip().split(os.pathsep)
lock = {'directPins': {'jooq':'3.21.10','postgresql':'42.7.15','sqlite-jdbc':'3.51.3.0','jackson-core':'2.23.0'},
        'resolvedRuntimeArtifacts': [{'name':Path(x).name, 'sha256':hashlib.sha256(Path(x).read_bytes()).hexdigest()} for x in cp]}
(project/'dependency-lock.json').write_text(json.dumps(lock, indent=2)+'\n')
receipt={'nativeImage':args.native,'startedUtc':started_utc,'finishedUtc':datetime.now(timezone.utc).isoformat(),'buildScriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'sourceHashes':before_inputs,'mavenCommand':command,'jdkReleaseSha256':hashlib.sha256((jdk/'release').read_bytes()).hexdigest(),'jdkVersion':subprocess.check_output([str(jdk/'bin/java'),'-version'],stderr=subprocess.STDOUT,text=True),
         'jarSha256':hashlib.sha256((project/'target/runtime-comparison-java-1.0.0.jar').read_bytes()).hexdigest(),
         'runtimeArtifactHashes':lock['resolvedRuntimeArtifacts']}
if args.native:
    receipt['executableSha256']=hashlib.sha256((project/'target/runtime-comparison-java').read_bytes()).hexdigest()
    receipt['nativeImageVersion']=subprocess.check_output([str(jdk/'bin/native-image'),'--version'],stderr=subprocess.STDOUT,text=True)
    metadata=base/'m2/org/graalvm/buildtools/graalvm-reachability-metadata/1.1.19'
    receipt['reachabilityMetadataArchives']={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(metadata.glob('*.zip')) if f.is_file()}
    receipt['buildFlags']=['--gc=serial','-O3','-march=x86-64','-J-Xmx3g','--parallelism=2','--enable-monitoring=jfr']
(project/'build-identity.json').write_text(json.dumps(receipt,indent=2)+'\n')
