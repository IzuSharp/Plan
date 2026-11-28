package org.korda.compare;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicLongArray;

/** Port of Shared/OfferedLoad.cs: absolute arrivals, bounded FIFO, no capacity wait, full drain. */
final class OfferedLoad {
    private static final class Job {long index,planned;}
    private static final class Queue {
        final long[] indices,due;
        int head,tail,count;boolean complete;
        Queue(int capacity){indices=new long[capacity];due=new long[capacity];}
        synchronized boolean offer(long index,long planned){
            if(complete)throw new IllegalStateException("Offer after completion");
            if(count==indices.length)return false;
            indices[tail]=index;due[tail]=planned;tail=(tail+1)%indices.length;count++;notify();return true;
        }
        synchronized boolean take(Job target)throws InterruptedException{
            while(count==0&&!complete)wait();
            if(count==0)return false;
            target.index=indices[head];target.planned=due[head];head=(head+1)%indices.length;count--;return true;
        }
        synchronized void complete(){complete=true;notifyAll();}
    }
    static final class WorkerState {
        long started,succeeded,failed,rows,digest;
        final long[] service=new long[8192],response=new long[8192],allResponse=new long[8192],queue=new long[8192];
        final String[] errorNames=new String[16];final long[] errorCounts=new long[16];
        String firstError;
    }
    final Options options;final Workload[] operations;final WorkerState[] workers;final Queue queue;
    final Thread[] consumers;final Thread producer;
    final CountDownLatch ready,start=new CountDownLatch(1);
    final long planned;
    long began,deadline,offeredEnd,drained,attempted,sent,rejected,oracleBefore;
    Long allocatedAtOfferedEnd;
    Map<String,Object> gcAtOfferedEnd;
    volatile Throwable fatal;volatile boolean truncated;
    final long[] plannedBySecond;
    final AtomicLongArray sentBySecond,startedBySecond,succeededBySecond,failedBySecond,rejectedBySecond,rowsBySecond;

    OfferedLoad(Options options,Workload[] operations){
        this.options=options;this.operations=operations;queue=new Queue(options.queueCapacity);
        planned=(long)Math.ceil(options.seconds*options.rate);
        int n=(int)Math.ceil(options.seconds)+301;
        plannedBySecond=new long[n];sentBySecond=new AtomicLongArray(n);startedBySecond=new AtomicLongArray(n);succeededBySecond=new AtomicLongArray(n);
        failedBySecond=new AtomicLongArray(n);rejectedBySecond=new AtomicLongArray(n);rowsBySecond=new AtomicLongArray(n);
        for(int s=0;s<Math.ceil(options.seconds);s++)plannedBySecond[s]=Math.min(planned,(long)Math.ceil((s+1)*options.rate))-Math.min(planned,(long)Math.ceil(s*options.rate));
        workers=new WorkerState[operations.length];consumers=new Thread[operations.length];ready=new CountDownLatch(operations.length+1);
        for(int i=0;i<operations.length;i++){
            int index=i;workers[i]=new WorkerState();consumers[i]=new Thread(()->consume(index),"db-perf-jooq-"+i);consumers[i].start();
        }
        producer=new Thread(this::produce,"db-perf-arrivals");producer.start();
        try{ready.await();}catch(InterruptedException e){Thread.currentThread().interrupt();throw new IllegalStateException(e);}
    }
    void start(){oracleBefore=Oracle.failures.get();began=System.nanoTime();deadline=began+(long)(options.seconds*1e9);start.countDown();}
    void join()throws InterruptedException{
        producer.join();for(var thread:consumers)thread.join();drained=System.nanoTime();
        if(fatal!=null)throw new IllegalStateException("Offered-load scheduler did not complete",fatal);
    }
    private static void waitUntil(long due)throws InterruptedException{
        for(;;){long left=due-System.nanoTime();if(left<=0)return;if(left>2_000_000)Thread.sleep(1);else for(int i=0;i<32;i++)Thread.onSpinWait();}
    }
    private void produce(){
        ready.countDown();
        try{
            start.await();
            for(long i=0;i<planned;i++){
                long due=began+(long)(i*(1e9/options.rate));waitUntil(due);attempted++;long now=System.nanoTime();
                if(queue.offer(i,due)){sent++;record(sentBySecond,now,1);}else{rejected++;record(rejectedBySecond,now,1);}
            }
            waitUntil(deadline);offeredEnd=System.nanoTime();allocatedAtOfferedEnd=ProcessStats.allocatedBytes();gcAtOfferedEnd=ProcessStats.gc();
        }catch(Throwable e){fatal=e;}finally{queue.complete();}
    }
    private void consume(int index){
        var worker=workers[index];var job=new Job();ready.countDown();
        try{
            start.await();
            while(queue.take(job)){
                long b=System.nanoTime();worker.started++;record(startedBySecond,b,1);add(worker.queue,b-job.planned);
                try{
                    var result=operations[index].scheduled(job.index);long end=System.nanoTime();
                    worker.succeeded++;worker.rows+=result.rows();worker.digest^=result.digest();
                    add(worker.service,end-b);add(worker.response,end-job.planned);add(worker.allResponse,end-job.planned);
                    record(succeededBySecond,end,1);record(rowsBySecond,end,result.rows());
                }catch(Exception e){
                    long end=System.nanoTime();worker.failed++;add(worker.allResponse,end-job.planned);record(failedBySecond,end,1);
                    if(worker.firstError==null)worker.firstError=stack(e);
                    String name=e.getClass().getName();int slot=0;
                    while(slot<15&&worker.errorNames[slot]!=null&&!worker.errorNames[slot].equals(name))slot++;
                    if(worker.errorNames[slot]==null)worker.errorNames[slot]=slot==15?"other-error-types":name;
                    worker.errorCounts[slot]++;
                }
            }
        }catch(Throwable e){fatal=e;queue.complete();}
    }
    private void record(AtomicLongArray values,long now,long amount){
        long second=(now-began)/1_000_000_000L;if(second<0||second>=values.length()){truncated=true;return;}values.addAndGet((int)second,amount);
    }
    private static void add(long[] histogram,long ns){
        long value=Math.max(1,ns);int exponent=63-Long.numberOfLeadingZeros(value);long lower=1L<<exponent;
        int fraction=(int)(((double)(value-lower)*128)/lower);histogram[exponent*128+fraction]++;
    }
    long[] merge(int kind){var result=new long[8192];for(var w:workers){long[] a=switch(kind){case 0->w.service;case 1->w.response;case 2->w.allResponse;default->w.queue;};for(int i=0;i<a.length;i++)result[i]+=a[i];}return result;}
    long succeeded(){long n=0;for(var w:workers)n+=w.succeeded;return n;}
    long failed(){long n=0;for(var w:workers)n+=w.failed;return n;}
    long rows(){long n=0;for(var w:workers)n+=w.rows;return n;}
    Map<String,Object> receipt(){
        long started=0;for(var w:workers)started+=w.started;long success=succeeded(),failed=failed();
        if(attempted!=planned||attempted!=sent+rejected||started!=sent||started!=success+failed)throw new IllegalStateException("Offered-load operation accounting does not reconcile");
        var seconds=new ArrayList<Map<String,Object>>();
        int count=Math.min(plannedBySecond.length,(int)Math.ceil((drained-began)/1e9)+1);
        for(int i=0;i<count;i++)seconds.add(Json.map("Second",i,"Planned",plannedBySecond[i],"Sent",sentBySecond.get(i),"Started",startedBySecond.get(i),"Succeeded",succeededBySecond.get(i),"Failed",failedBySecond.get(i),"Rejected",rejectedBySecond.get(i),"Rows",rowsBySecond.get(i)));
        var errorClasses=new LinkedHashMap<String,Object>();var errors=new ArrayList<String>();
        for(var w:workers){if(w.firstError!=null)errors.add(w.firstError);for(int i=0;i<16;i++)if(w.errorNames[i]!=null)errorClasses.merge(w.errorNames[i],w.errorCounts[i],(a,b)->(long)a+(long)b);}
        return Json.map("RequestsPerSecond",options.rate,"OfferedSeconds",options.seconds,"QueueCapacity",options.queueCapacity,
            "StartedTicks",began,"DeadlineTicks",deadline,"OfferedEndTicks",offeredEnd,"DrainedTicks",drained,"TimerFrequency",1_000_000_000L,
            "AllocatedAtOfferedEnd",allocatedAtOfferedEnd,"GcAtOfferedEnd",gcAtOfferedEnd,
            "Planned",planned,"Attempted",attempted,"Sent",sent,"Started",started,"Completed",success+failed,"Succeeded",success,"Failed",failed,"Rejected",rejected,"Retries",0,
            "Rows",rows(),"Suspensions",null,"SuccessServiceHistogram",merge(0),"SuccessScheduledHistogram",merge(1),"AllCompletedScheduledHistogram",merge(2),"StartDelayHistogram",merge(3),
            "Seconds",seconds,"TimeSeriesTruncated",truncated,"ErrorClasses",errorClasses,"Errors",errors,
            "OracleFailuresBefore",oracleBefore,"OracleFailuresAfter",Oracle.failures.get(),"OracleFailures",Oracle.failures.get(),"FirstOracleFailure",Oracle.first.get());
    }
    static double quantile(long[] histogram,long total,double q){
        if(total==0)return 0;long wanted=(long)Math.ceil(total*q),count=0;
        for(int i=0;i<histogram.length;i++){count+=histogram[i];if(count>=wanted){double lower=Math.scalb(1.0,i/128);return(lower+lower*((i%128+1)/128.0))/1000;}}
        throw new IllegalArgumentException("Histogram population differs from counter");
    }
    static String stack(Throwable e){var w=new java.io.StringWriter();e.printStackTrace(new java.io.PrintWriter(w));return w.toString();}
}
