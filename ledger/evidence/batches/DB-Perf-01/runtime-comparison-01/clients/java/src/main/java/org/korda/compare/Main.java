package org.korda.compare;

import java.math.BigInteger;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.Map;

public final class Main {
    public static void main(String[] args)throws Exception{
        System.setProperty("org.jooq.no-logo","true");System.setProperty("org.jooq.no-tips","true");
        Options options=null;
        try{
            options=Options.parse(args);
            boolean nativeAot="runtime".equals(System.getProperty("org.graalvm.nativeimage.imagecode"));
            if(!nativeAot&&!options.verifyOnly&&!options.allowJitDiagnostic)throw new IllegalArgumentException("Formal comparison requires a native executable; JIT is available only for explicit diagnostics");
            if(!options.verifyOnly&&options.formalAdmission==null&&!options.allowJitDiagnostic)
                throw new IllegalArgumentException("Offered-load measurement requires --formal-admission; finite correctness uses --verify-only");
            var receipt=run(options,nativeAot);
            if(options.output!=null)Json.create(options.output,receipt);
            System.out.println("DB_PERF_JAVA_RECEIPT "+Json.text(receipt));
            Oracle.requireClean();
            if(receipt.get("Failed") instanceof Number n&&n.longValue()>0)
                throw new IllegalStateException("Completed receipt records "+n.longValue()+" business errors; this command is not a successful cell");
        }catch(Throwable error){
            if(Oracle.failures.get()!=0){
                var failure=Json.map("Schema","DB-Perf-01.oracle-failure.v1","OracleFailures",Oracle.failures.get(),"FirstOracleFailure",Oracle.first.get(),"Scope","Process-lifetime sticky oracle failures; no correctness, SLO or timing credit");
                System.err.println("DB_PERF_ORACLE_FAILURE "+Json.text(failure));
                if(options!=null&&options.output!=null)Json.create(Path.of(options.output+".oracle-failure.json"),failure);
            }
            error.printStackTrace(System.err);System.exit(2);
        }
    }
    private static Map<String,Object> run(Options options,boolean nativeAot)throws Exception{
        var admission=FormalAdmission.load(options,nativeAot);
        ProcessStats.initialize();
        var database=new Database(options);var workers=new Workload[options.concurrency];
        Throwable primary=null;
        try{
            for(int i=0;i<workers.length;i++)workers[i]=database.open();
            Oracle.phase="warmup";
            var warmThreads=new Thread[workers.length];var warmErrors=new Throwable[workers.length];
            for(int i=0;i<workers.length;i++){int index=i;warmThreads[i]=new Thread(()->{try{workers[index].warmup();}catch(Throwable e){warmErrors[index]=e;}},"db-perf-warmup-"+i);warmThreads[i].start();}
            for(var t:warmThreads)t.join();for(var e:warmErrors)if(e!=null)throw new IllegalStateException("Warmup failed",e);
            Oracle.requireClean();
            var expected=new LinkedHashMap<String,Object>();for(int i=0;i<35;i++)expected.put(Contract.NAMES[i],Json.map("Rows",Contract.ROWS[i],"Digest",new BigInteger(Long.toUnsignedString(Contract.DIGESTS[i])),"DigestHex",Long.toUnsignedString(Contract.DIGESTS[i],16)));
            var common=Json.map("SchemaVersion",1,"Task","DB-Runtime-Compare-01","Route",nativeAot?"independent-java-jooq-native-image":"java-jooq-jit-diagnostic-only","NativeAot",nativeAot,
                "JavaVersion",System.getProperty("java.runtime.version"),"JavaVendor",System.getProperty("java.vendor"),"VmVersion",System.getProperty("java.vm.version"),
                "GcContract",nativeAot?"Serial GC selected at Native Image build; no Java memory cap imposed":"JIT diagnostic; actual collectors reported in GcIdentity; no Native Image GC claim","GcIdentity",ProcessStats.gc(),
                "ExecutableSha256",admission!=null?admission.executableSha256:Database.sha256(Path.of("/proc/self/exe")),"PackageVersion","jOOQ/"+org.jooq.Constants.VERSION+";sqlite-jdbc/3.51.3.0;pgJDBC/42.7.15;jackson-core/2.23.0",
                "Provider",options.provider,"Database",database.identity,"BackendPids",database.backendPids,"ContractSha256",Contract.MANIFEST_SHA256,
                "Case",options.caseName,"ActualCaseIds",Arrays.stream(options.active).mapToObj(i->Contract.NAMES[i]).toList(),"Mode",options.mode,"SessionMode",options.session,
                "QueryReuseContract",options.mode.equals("prepared")?"One jOOQ Fluent query graph per worker reused; no retained JDBC statements; pgJDBC prepareThreshold=0; related and transaction graphs rebuilt per operation":"Build a jOOQ Fluent query graph and execute it per operation; same DTO contract",
                "TransactionContract",options.provider.equals("sqlite")?"BEGIN IMMEDIATE; WAL/FULL/foreign_keys=ON/busy_timeout=5000; full row reads, actual updates, restored commit or rollback":"READ COMMITTED read-write JDBC transactions; full row reads, actual updates, restored commit or rollback",
                "Concurrency",options.concurrency,"WarmupPerWorker",options.warmup,"PremeasurementVerifiedCasesPerWorker",options.verify?35:0,"RequestedRows",32,"BatchRows",32,"Tenants",8,"OrdersPerTenant",1024,
                "ActualDiagnosticSql",workers[0].diagnosticSql,"DiagnosticBindValues",workers[0].bindValues,"ExpectedResults",expected,"EmptyDriver",options.emptyDriver,
                "Scheduling","Fixed absolute offered rate; preallocated bounded FIFO; nonwaiting capacity admission; full drain; blocking JDBC on dedicated platform workers",
                "NativeAllocationBytes",null,"NativeAllocationScope","Not instrumented; no zero-allocation claim","ActualStreamSuspensions",null,
                "AllocationAttribution","Whole-process ThreadMXBean allocated-byte counter when supported; includes jOOQ, JDBC, JSON, DTO and harness; null means unavailable; no framework-only attribution",
                "MeasurementKind",options.verifyOnly?"finite-correctness":admission!=null?"admitted-formal-campaign":"explicit-diagnostic",
                "FormalAdmission",admission==null?null:admission.receipt(),
                "TimingComparisonEligible",false,"TimingComparisonIneligibilityReasons",new String[]{options.verifyOnly?"Finite correctness probe; no offered-load measurement":admission==null?"No campaign-owner formal admission":"Admitted operation has not yet completed and reconciled"});
            if(options.verifyOnly){common.put("VerificationOnly",true);common.put("VerifiedCasesPerWorker",35);common.put("OracleFailures",Oracle.failures.get());return common;}

            Oracle.phase="offered";
            var load=new OfferedLoad(options,workers);
            var processBefore=ProcessStats.read();var gcBefore=ProcessStats.gc();Long allocatedBefore=ProcessStats.allocatedBytes();
            String startedUtc=Instant.now().toString();load.start();load.join();
            Long allocatedAfter=ProcessStats.allocatedBytes();var gcAfter=ProcessStats.gc();String finishedUtc=Instant.now().toString();var processAfter=ProcessStats.read();
            var schedule=load.receipt();long success=load.succeeded(),failed=load.failed(),rows=load.rows();
            Long allocated=allocatedBefore==null||allocatedAfter==null?null:allocatedAfter-allocatedBefore;
            double user=(double)processAfter.get("UserCpuSeconds")-(double)processBefore.get("UserCpuSeconds"),system=(double)processAfter.get("SystemCpuSeconds")-(double)processBefore.get("SystemCpuSeconds");
            common.putAll(Json.map("StartedUtc",startedUtc,"FinishedUtc",finishedUtc,"SteadyStartMonotonicNs",load.began,"SteadyEndMonotonicNs",load.drained,
                "EffectiveSeconds",(load.drained-load.began)/1e9,"Planned",load.planned,"Started",schedule.get("Started"),"Completed",success,"Failed",failed,"Rejected",load.rejected,"Retries",0,"Rows",rows,
                "AllocatedBefore",allocatedBefore,"AllocatedAfter",allocatedAfter,"AllocatedBytes",allocated,"BytesPerSuccessfulOperation",allocated==null?null:success==0?0.0:allocated/(double)success,
                "BytesPerRow",allocated==null?null:rows==0?0.0:allocated/(double)rows,"ProcessBefore",processBefore,"ProcessAfter",processAfter,
                "UserCpuSeconds",user,"SystemCpuSeconds",system,"CpuSecondsPerSuccessfulOperation",success==0?0.0:(user+system)/success,
                "GcBefore",gcBefore,"GcAfter",gcAfter,"OfferedLoad",schedule,"OracleFailuresBefore",load.oracleBefore,"OracleFailuresAfter",Oracle.failures.get(),"OracleFailures",Oracle.failures.get(),"FirstOracleFailure",Oracle.first.get()));
            var perCase=new ArrayList<Map<String,Object>>();
            for(int i=0;i<35;i++){
                long begun=0,done=0,bad=0,count=0;for(var w:workers){begun+=w.caseStarted[i];done+=w.caseSucceeded[i];bad+=w.caseFailed[i];count+=w.caseRows[i];}
                perCase.add(Json.map("Name",Contract.NAMES[i],"Started",begun,"Succeeded",done,"Failed",bad,"Rows",count));
            }
            common.put("Cases",perCase);
            long[] histogram=load.merge(0);common.put("Latencies",Json.map("P50MicrosecondsUpper",OfferedLoad.quantile(histogram,success,.5),"P95MicrosecondsUpper",OfferedLoad.quantile(histogram,success,.95),"P99MicrosecondsUpper",OfferedLoad.quantile(histogram,success,.99),"Method","base-2 histogram, 128 subdivisions per exponent, upper bound (<0.782% relative bin width)","Histogram",histogram));
            Oracle.phase="drain";closeAll(workers);
            common.put("ApplicationConnectionsReturnedToZero",true);
            if(options.idleSeconds>0){
                var before=ProcessStats.read();String idleStart=Instant.now().toString();long began=System.nanoTime();
                Thread.sleep((long)(options.idleSeconds*1000));long end=System.nanoTime();var after=ProcessStats.read();
                common.put("Idle",Json.map("StartedUtc",idleStart,"FinishedUtc",Instant.now().toString(),"RequestedSeconds",options.idleSeconds,"ObservedSeconds",(end-began)/1e9,"Before",before,"After",after,
                    "Scope","After worker/connection drain; no forced GC; outside effective duration and raw allocation boundary"));
            }
            boolean eligible=admission!=null&&failed==0&&Oracle.failures.get()==0&&!load.truncated&&success>0;
            common.put("TimingComparisonEligible",eligible);
            var reasons=new ArrayList<String>();
            if(admission==null)reasons.add("No campaign-owner formal admission");
            if(failed!=0)reasons.add("Business errors were recorded");
            if(Oracle.failures.get()!=0)reasons.add("Process-lifetime oracle failures were recorded");
            if(load.truncated)reasons.add("Per-second evidence was truncated");
            if(success==0)reasons.add("No successful operation was observed");
            common.put("TimingComparisonIneligibilityReasons",reasons);
            return common;
        }catch(Exception|Error error){primary=error;throw error;}
        finally{
            try{closeAll(workers);}catch(RuntimeException cleanup){if(primary!=null)primary.addSuppressed(cleanup);else throw cleanup;}
        }
    }
    private static void closeAll(Workload[] workers){
        Oracle.Violation aggregate=null;
        for(int i=0;i<workers.length;i++){
            var worker=workers[i];if(worker==null)continue;workers[i]=null;
            try{worker.close();}catch(Exception cleanup){
                var error=Oracle.fail("Connection did not retire cleanly",null,cleanup);
                if(aggregate==null)aggregate=error;else aggregate.addSuppressed(error);
            }
        }
        if(aggregate!=null)throw aggregate;
    }
}
