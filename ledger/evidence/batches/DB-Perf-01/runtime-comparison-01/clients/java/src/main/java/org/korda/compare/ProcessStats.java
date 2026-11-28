package org.korda.compare;

import java.io.IOException;
import java.lang.management.ManagementFactory;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.Map;

final class ProcessStats {
    private static long ticks;
    static void initialize()throws Exception{
        var p=new ProcessBuilder("getconf","CLK_TCK").start();String value=new String(p.getInputStream().readAllBytes()).trim();
        if(p.waitFor()!=0)throw new IOException("getconf CLK_TCK failed");ticks=Long.parseLong(value);
        // Warm management providers outside the measurement boundaries.
        allocatedBytes();gc();read();
    }
    static Long allocatedBytes(){
        try{
            if(ManagementFactory.getThreadMXBean() instanceof com.sun.management.ThreadMXBean bean
                &&bean.isThreadAllocatedMemorySupported()){
                if(!bean.isThreadAllocatedMemoryEnabled())bean.setThreadAllocatedMemoryEnabled(true);
                long n=bean.getTotalThreadAllocatedBytes();return n<0?null:n;
            }
        }catch(UnsupportedOperationException|LinkageError e){return null;}
        return null;
    }
    static Map<String,Object> gc(){
        var perCollector=new LinkedHashMap<String,Object>();long count=0,time=0;boolean valid=true;
        for(var bean:ManagementFactory.getGarbageCollectorMXBeans()){
            long n=bean.getCollectionCount(),ms=bean.getCollectionTime();perCollector.put(bean.getName(),Json.map("Count",n,"CollectionMilliseconds",ms));
            if(n<0||ms<0)valid=false;else{count+=n;time+=ms;}
        }
        return Json.map("Collections",valid?count:null,"CollectionMilliseconds",valid?time:null,"Collectors",perCollector,
            "Scope","Process counters; collection time is not a validated stop-the-world pause histogram");
    }
    static Map<String,Object> read()throws IOException{
        String stat=Files.readString(Path.of("/proc/self/stat"));String[] fields=stat.substring(stat.lastIndexOf(')')+2).trim().split("\\s+");
        long user=Long.parseLong(fields[11]),system=Long.parseLong(fields[12]);
        var status=new LinkedHashMap<String,Long>();
        for(String line:Files.readAllLines(Path.of("/proc/self/status"))){int colon=line.indexOf(':');if(colon>0&&line.substring(0,colon).startsWith("Vm")){String[] parts=line.substring(colon+1).trim().split("\\s+");status.put(line.substring(0,colon),Long.parseLong(parts[0])*1024);}}
        Long pss=null;try{for(String line:Files.readAllLines(Path.of("/proc/self/smaps_rollup")))if(line.startsWith("Pss:"))pss=Long.parseLong(line.substring(4).trim().split("\\s+")[0])*1024;}catch(IOException ignored){}
        return Json.map("UserCpuSeconds",user/(double)ticks,"SystemCpuSeconds",system/(double)ticks,"RssBytes",status.get("VmRSS"),"PeakRssBytes",status.get("VmHWM"),"PssBytes",pss,
            "JavaHeapUsedBytes",Runtime.getRuntime().totalMemory()-Runtime.getRuntime().freeMemory(),"JavaHeapCommittedBytes",Runtime.getRuntime().totalMemory(),"JavaHeapMaximumBytes",Runtime.getRuntime().maxMemory());
    }
}
