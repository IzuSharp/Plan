package org.korda.compare;

import com.fasterxml.jackson.core.JsonFactory;
import com.fasterxml.jackson.core.JsonToken;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.LinkedHashMap;
import java.util.Map;

/** A campaign owner's explicit, executable-bound admission; never created by this client. */
final class FormalAdmission {
    final String path,policySha256,executableSha256;
    private FormalAdmission(String path,String policySha256,String executableSha256){
        this.path=path;this.policySha256=policySha256;this.executableSha256=executableSha256;
    }
    static FormalAdmission load(Options options,boolean nativeAot)throws Exception{
        if(options.formalAdmission==null)return null;
        if(!nativeAot||options.verifyOnly||options.emptyDriver||options.allowJitDiagnostic)
            throw new IllegalArgumentException("Formal admission requires the real Native Image workload, without verification-only, empty-driver or diagnostic flags");
        if(!options.verify)throw new IllegalArgumentException("Formal admission requires --verify: all 35 cases separately from the 64-operation warmup");
        Path file=options.formalAdmission;
        if(Files.size(file)>65536)throw new IllegalArgumentException("Admission document exceeds 64 KiB");
        byte[] bytes=Files.readAllBytes(file);
        if(bytes.length>65536)throw new IllegalArgumentException("Admission document exceeds 64 KiB");
        var values=new LinkedHashMap<String,Object>();
        try(var parser=new JsonFactory().createParser(bytes)){
            if(parser.nextToken()!=JsonToken.START_OBJECT)throw new IllegalArgumentException("Admission must be a JSON object");
            while(parser.nextToken()!=JsonToken.END_OBJECT){
                if(parser.currentToken()!=JsonToken.FIELD_NAME)throw new IllegalArgumentException("Invalid admission property");
                String name=parser.currentName();
                if(values.containsKey(name))throw new IllegalArgumentException("Duplicate admission property: "+name);
                JsonToken token=parser.nextToken();
                if(token==null)throw new IllegalArgumentException("Incomplete admission document");
                Object value=switch(token){
                    case VALUE_STRING->parser.getText();
                    case VALUE_TRUE->true;
                    case VALUE_FALSE->false;
                    case VALUE_NULL->null;
                    case VALUE_NUMBER_INT,VALUE_NUMBER_FLOAT->parser.getDecimalValue();
                    case START_OBJECT,START_ARRAY->{parser.skipChildren();yield "structured evidence retained in the policy file";}
                    default->throw new IllegalArgumentException("Invalid admission value: "+name);
                };
                values.put(name,value);
            }
            if(parser.nextToken()!=null)throw new IllegalArgumentException("Trailing content after admission object");
        }
        require(values,"Schema","DB-Runtime-Compare-01.java-admission.v1");
        require(values,"ApprovedForFormalMeasurement",true);
        String executable=Database.sha256(Path.of("/proc/self/exe"));
        require(values,"ExecutableSha256",executable);
        require(values,"ContractSha256",Contract.MANIFEST_SHA256);
        require(values,"Provider",options.provider);
        require(values,"Case","mixed");require(values,"Mode","prepared");require(values,"SessionMode","persistent");
        if(!options.caseName.equals("mixed")||!options.mode.equals("prepared")||!options.session.equals("persistent"))
            throw new IllegalArgumentException("Formal comparison requires mixed/prepared/persistent");
        int concurrency=options.provider.equals("sqlite")?4:8;
        int rate=options.provider.equals("sqlite")?3000:3600;
        number(values,"Concurrency",concurrency,options.concurrency);
        number(values,"RequestsPerSecond",rate,options.rate);
        number(values,"QueueCapacity",64,options.queueCapacity);
        number(values,"Seconds",1800,options.seconds);
        number(values,"WarmupPerWorker",64,options.warmup);
        number(values,"IdleSeconds",15,options.idleSeconds);
        number(values,"CSharpGcBudgetMiB",192,192);
        require(values,"CgroupRequired",false);
        require(values,"JavaMemoryCapBytes",null);
        String policyHash=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
        return new FormalAdmission(file.toString(),policyHash,executable);
    }
    private static void require(Map<String,Object> values,String key,Object expected){
        if(!values.containsKey(key)||!java.util.Objects.equals(values.get(key),expected))
            throw new IllegalArgumentException("Admission does not match the frozen campaign: "+key);
    }
    private static void number(Map<String,Object> values,String key,double frozen,double actual){
        if(!(values.get(key) instanceof Number value)||value.doubleValue()!=frozen||actual!=frozen)
            throw new IllegalArgumentException("Admission/command differs from the frozen campaign: "+key);
    }
    Map<String,Object> receipt(){
        return Json.map("Schema","DB-Runtime-Compare-01.java-admission.v1","Path",path,"PolicySha256",policySha256,
            "ExecutableSha256",executableSha256,"ContractSha256",Contract.MANIFEST_SHA256,
            "CSharpGcBudgetMiB",192,"CSharpGcBudgetSemantics","Requested GC budget; no hard RSS or process-memory guarantee",
            "CgroupRequired",false,"JavaMemoryCapBytes",null,
            "Scope","Campaign-owner approval bound to the actual executable, original contract and exact 30-minute cell parameters; does not certify an unsuccessful run");
    }
}
