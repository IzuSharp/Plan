package org.korda.compare;

import java.nio.file.Path;
import java.util.Arrays;

final class Options {
    String provider="",connection="",mode="prepared",session="persistent",caseName="mixed";
    int concurrency=1,warmup=64,queueCapacity=64;
    double seconds=1800,rate=0,idleSeconds=15;
    boolean verify,verifyOnly,emptyDriver,allowJitDiagnostic;
    int[] active=java.util.stream.IntStream.range(0,35).toArray();
    Path output,sqliteNativeLibrary,sqliteJniDirectory,formalAdmission;
    static Options parse(String[] args){
        var p=new Options();
        for(int i=0;i<args.length;i++){
            String key=args[i];
            if(key.equals("--verify")){p.verify=true;continue;}
            if(key.equals("--verify-only")){p.verify=true;p.verifyOnly=true;continue;}
            if(key.equals("--empty-driver")){p.emptyDriver=true;continue;}
            if(key.equals("--allow-jit-diagnostic")){p.allowJitDiagnostic=true;continue;}
            if(++i>=args.length)throw new IllegalArgumentException("Missing option value: "+key);
            String value=args[i];
            switch(key){
                case "--provider"->p.provider=value;
                case "--connection"->p.connection=value;
                case "--mode"->p.mode=value;
                case "--session"->p.session=value;
                case "--case"->{p.caseName=value;p.active=value.equals("mixed")?java.util.stream.IntStream.range(0,35).toArray():new int[]{Contract.index(value)};}
                case "--cases"->{p.caseName="custom";p.active=Arrays.stream(value.split(",")).map(String::trim).mapToInt(Contract::index).toArray();}
                case "--concurrency"->p.concurrency=Integer.parseInt(value);
                case "--warmup"->p.warmup=Integer.parseInt(value);
                case "--queue-capacity"->p.queueCapacity=Integer.parseInt(value);
                case "--seconds"->p.seconds=Double.parseDouble(value);
                case "--rate","--arrival-rate"->p.rate=Double.parseDouble(value);
                case "--idle-seconds"->p.idleSeconds=Double.parseDouble(value);
                case "--output"->p.output=Path.of(value);
                case "--formal-admission"->p.formalAdmission=Path.of(value).toAbsolutePath().normalize();
                case "--sqlite-native-library"->p.sqliteNativeLibrary=Path.of(value).toAbsolutePath();
                case "--sqlite-jni-directory"->p.sqliteJniDirectory=Path.of(value).toAbsolutePath();
                case "--rows","--batch-rows"->{if(Integer.parseInt(value)!=32)throw new IllegalArgumentException("This frozen manifest requires 32 rows/batch");}
                case "--tenants"->{if(Integer.parseInt(value)!=8)throw new IllegalArgumentException("This frozen manifest requires 8 tenants");}
                case "--orders-per-tenant"->{if(Integer.parseInt(value)!=1024)throw new IllegalArgumentException("This frozen manifest requires 1024 orders/tenant");}
                default->throw new IllegalArgumentException("Unknown option: "+key);
            }
        }
        if(!p.provider.equals("sqlite")&&!p.provider.equals("postgresql"))throw new IllegalArgumentException("--provider sqlite|postgresql required");
        if(p.connection.isBlank())throw new IllegalArgumentException("--connection required; initializer is deliberately external");
        if(p.provider.equals("sqlite")&&(p.sqliteNativeLibrary==null||p.sqliteJniDirectory==null))
            throw new IllegalArgumentException("SQLite requires --sqlite-native-library and --sqlite-jni-directory; bundled engine fallback is prohibited");
        if(!p.mode.equals("prepared")&&!p.mode.equals("dynamic"))throw new IllegalArgumentException("--mode prepared|dynamic required");
        if(!p.session.equals("persistent"))throw new IllegalArgumentException("Only the frozen persistent-session comparison is implemented");
        if(p.concurrency<1||p.concurrency>256||p.queueCapacity<1||p.queueCapacity>65536||p.warmup<1||p.warmup>100000
            ||p.active.length<1||!Double.isFinite(p.seconds)||p.seconds<=0||p.seconds>86400||!Double.isFinite(p.rate)||p.rate<0||p.rate>1_000_000
            ||(!p.verifyOnly&&p.rate==0)||!Double.isFinite(p.idleSeconds)||p.idleSeconds<0||p.idleSeconds>300)
            throw new IllegalArgumentException("Invalid bounded offered-load options");
        if(p.verifyOnly&&p.emptyDriver)throw new IllegalArgumentException("A correctness probe cannot use the empty driver");
        return p;
    }
    int index(long iteration){return active[(int)(iteration%active.length)];}
}
