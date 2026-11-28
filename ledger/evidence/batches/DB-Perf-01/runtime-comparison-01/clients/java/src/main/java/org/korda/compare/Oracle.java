package org.korda.compare;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;

final class Oracle {
    static final AtomicLong failures=new AtomicLong();
    static final AtomicReference<Map<String,Object>> first=new AtomicReference<>();
    static volatile String phase="setup";
    static final class Violation extends RuntimeException { Violation(String message,Throwable cause){super(message,cause);} }
    static Violation fail(String message,String caseId){return fail(message,caseId,null);}
    static Violation fail(String message,String caseId,Throwable cause){
        long n=failures.incrementAndGet();
        var record=new LinkedHashMap<String,Object>();
        record.put("Sequence",n);record.put("Phase",phase);record.put("CaseId",caseId);record.put("Message",message);
        record.put("InnerError",cause==null?null:cause.toString());record.put("ObservedTicks",System.nanoTime());record.put("TimerFrequency",1_000_000_000L);
        first.compareAndSet(null,record);
        return new Violation(message,cause);
    }
    static void observe(Throwable error,String name){
        if(error instanceof Violation)return;
        if(error instanceof IllegalArgumentException||error instanceof IllegalStateException||error instanceof ArithmeticException
            ||error instanceof NullPointerException||error instanceof ClassCastException||error instanceof java.io.UncheckedIOException
            ||error instanceof org.jooq.exception.MappingException||error instanceof org.jooq.exception.DataTypeException)
            fail("Materialization/execution contract failed",name,error);
    }
    static void requireClean(){if(failures.get()!=0)throw new IllegalStateException("A sticky oracle failure invalidates this run");}
}
