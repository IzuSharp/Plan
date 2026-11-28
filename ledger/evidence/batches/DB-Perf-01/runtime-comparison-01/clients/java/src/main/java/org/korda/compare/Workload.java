package org.korda.compare;

import com.fasterxml.jackson.core.JsonFactory;
import com.fasterxml.jackson.core.JsonToken;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Objects;
import org.jooq.Cursor;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.Record;
import org.jooq.Record1;
import org.jooq.ResultQuery;
import org.jooq.Select;
import org.jooq.Table;
import org.jooq.conf.ParamType;
import static org.jooq.impl.DSL.*;
import static org.korda.compare.Models.*;

/** Thread confined, genuine jOOQ Fluent graph -> JDBC -> typed owned DTOs. */
final class Workload implements AutoCloseable {
    private static final Table<Record> ORDERS=table(name("orders")), CUSTOMERS=table(name("customers")), LINES=table(name("order_lines"));
    private static final Field<Long> TENANT=field(name("orders","TenantId"),Long.class),ID=field(name("orders","Id"),Long.class),
        CREATED=field(name("orders","CreatedAt"),Long.class),CUSTOMER=field(name("orders","CustomerId"),Long.class),VERSION=field(name("orders","Version"),Long.class),
        CUSTOMER_ID=field(name("customers","Id"),Long.class),LINE_ID=field(name("order_lines","Id"),Long.class),
        LINE_TENANT=field(name("order_lines","TenantId"),Long.class),LINE_ORDER=field(name("order_lines","OrderId"),Long.class),QUANTITY=field(name("order_lines","Quantity"),Long.class);
    private static final Field<String> NOTE=field(name("orders","Note"),String.class),SETTINGS=field(name("orders","Settings"),String.class),
        MEMO=field(name("orders","InternalMemo"),String.class),CUSTOMER_NAME=field(name("customers","Name"),String.class),PRODUCT=field(name("order_lines","Product"),String.class);
    private static final Field<BigDecimal> TOTAL=field(name("orders","Total"),BigDecimal.class);
    private static final Field<?>[] WIDE={TENANT,ID,CREATED,CUSTOMER,TOTAL,NOTE,VERSION,SETTINGS,MEMO};
    private static final JsonFactory JSON=new JsonFactory();
    final Options options;
    final Connection connection;
    final DSLContext dsl;
    final Digest digest=new Digest();
    private final ResultQuery<?>[] prepared=new ResultQuery<?>[35];
    final long[] caseStarted=new long[35],caseSucceeded=new long[35],caseFailed=new long[35],caseRows=new long[35];
    final Map<String,Object> diagnosticSql=new LinkedHashMap<>();
    final Map<String,Object> bindValues=new LinkedHashMap<>();

    Workload(Options options,Connection connection,DSLContext dsl){
        this.options=options;this.connection=connection;this.dsl=dsl;
        for(int i=0;i<35;i++){
            if(i>=30&&i<=33)continue;
            ResultQuery<?> q=build(i);
            diagnosticSql.put(Contract.NAMES[i],q.getSQL(ParamType.INDEXED));
            bindValues.put(Contract.NAMES[i],q.getBindValues());
            if(options.mode.equals("prepared")&&i!=29)prepared[i]=q;
        }
        diagnosticSql.put("write-find",findQuery().getSQL(ParamType.INDEXED));
        diagnosticSql.put("write-controls",options.provider.equals("sqlite")?"BEGIN IMMEDIATE; COMMIT/ROLLBACK":"JDBC setAutoCommit(false); READ COMMITTED; commit/rollback; setAutoCommit(true)");
        diagnosticSql.put("write-update",dsl.update(ORDERS).set(NOTE,"perf-mutated").set(VERSION,2L).where(TENANT.eq(1L).and(ID.eq(1024L))).getSQL(ParamType.INDEXED));
        diagnosticSql.put("partial-update",dsl.update(ORDERS).set(NOTE,(String)null).where(TENANT.eq(1L).and(ID.eq(1024L))).getSQL(ParamType.INDEXED));
        diagnosticSql.put("stale-update",dsl.update(ORDERS).set(NOTE,"stale-write").where(TENANT.eq(1L).and(ID.eq(1024L)).and(VERSION.eq(1L))).getSQL(ParamType.INDEXED));
    }

    private ResultQuery<?> build(int i){
        var tenant=TENANT.eq(1L);
        return switch(i){
            case 0->dsl.select(ID.as("value")).from(ORDERS).where(tenant).orderBy(ID.asc().nullsLast()).limit(val(32L));
            case 1->dsl.select(ID,NOTE).from(ORDERS).where(tenant).orderBy(ID.asc().nullsLast()).limit(val(32L));
            case 2->dsl.select(ID,TOTAL).from(ORDERS).where(tenant).orderBy(ID.asc().nullsLast()).limit(val(32L));
            case 3->dsl.select(ID,SETTINGS).from(ORDERS).where(tenant).orderBy(ID.asc().nullsLast()).limit(val(32L));
            case 4->dsl.select(WIDE).from(ORDERS).where(tenant).orderBy(ID.asc().nullsLast()).limit(val(32L));
            case 5->dsl.select(ID.as("value")).from(ORDERS).where(tenant.and(CUSTOMER.eq(2L))).orderBy(ID.asc().nullsLast()).limit(val(32L));
            case 6->dsl.select(ID.as("value")).from(ORDERS).where(tenant.and(CREATED.ge(1_700_000_100L)).and(CREATED.lt(1_700_000_200L))).orderBy(ID.asc().nullsLast()).limit(val(32L));
            // The unused left-join projection and match marker are removed; returned DTO/NULL semantics are unchanged.
            case 7->dsl.select(ID,CUSTOMER_NAME).from(ORDERS).leftJoin(CUSTOMERS).on(CUSTOMER.eq(CUSTOMER_ID)).where(tenant).orderBy(ID.asc().nullsLast()).limit(val(32L));
            case 8->dsl.select(ID,CUSTOMER_NAME).from(ORDERS).join(CUSTOMERS).on(CUSTOMER.eq(CUSTOMER_ID)).where(tenant).orderBy(ID.asc().nullsLast()).limit(val(32L));
            case 9->dsl.select(ID.as("value")).from(ORDERS).where(tenant.and(NOTE.isNull())).orderBy(ID.asc().nullsLast()).limit(val(32L));
            case 10->dsl.select(ID.as("value")).from(ORDERS).where(tenant.and(NOTE.like("%note-1%",'\\'))).orderBy(ID.asc().nullsLast()).limit(val(32L));
            case 11->dsl.select(CUSTOMER,count().cast(Long.class).as("Count"),sum(TOTAL).as("Total")).from(ORDERS).where(tenant).groupBy(CUSTOMER).having(count().gt(3)).orderBy(CUSTOMER.asc().nullsLast());
            case 12->dsl.select(PRODUCT,sum(QUANTITY).cast(Long.class).as("Quantity")).from(LINES).where(LINE_TENANT.eq(1L)).groupBy(PRODUCT).having(sum(QUANTITY).cast(Long.class).gt(10L)).orderBy(PRODUCT.asc().nullsLast());
            // SQL SUM remains NULL for an empty input; there is deliberately no COALESCE.
            case 13->dsl.select(sum(TOTAL).as("value")).from(ORDERS).where(TENANT.eq(-1L));
            case 14->dsl.select(ID.as("value")).from(ORDERS).where(tenant.and(CREATED.gt(1_700_000_128L).or(CREATED.eq(1_700_000_128L).and(TENANT.gt(1L).or(TENANT.eq(1L).and(ID.gt(512L))))))).orderBy(CREATED.asc().nullsLast(),TENANT.asc().nullsLast(),ID.asc().nullsLast()).limit(val(32L));
            case 15->dsl.select(ID.as("value")).from(ORDERS).where(tenant).orderBy(CREATED.asc().nullsLast(),TENANT.asc().nullsLast(),ID.asc().nullsLast()).limit(val(32L)).offset(val(768L));
            case 16->dsl.select(CUSTOMER_ID.as("value")).from(CUSTOMERS).where(exists(dsl.select(ID).from(ORDERS).where(tenant.and(ID.ge(32L))))).orderBy(CUSTOMER_ID.asc().nullsLast()).limit(val(1L));
            case 17->dsl.select(CUSTOMER_ID.as("value")).from(CUSTOMERS).where(CUSTOMER_ID.in(dsl.select(CUSTOMER).from(ORDERS).where(tenant.and(ID.gt(128L))))).orderBy(CUSTOMER_ID.asc().nullsLast()).limit(val(32L));
            case 18->cte(false,18);
            case 19->dsl.select(ID,rowNumber().over().partitionBy(CUSTOMER).orderBy(CREATED.asc().nullsLast(),ID.asc().nullsLast()).cast(Long.class).as("Rank")).from(ORDERS).where(tenant).orderBy(ID.asc().nullsLast()).limit(val(32L));
            case 20,21,22,23->cte(true,i);
            case 24->dsl.select(LINE_ID,sum(QUANTITY).over().orderBy(LINE_ID.asc().nullsLast()).rowsBetweenUnboundedPreceding().andCurrentRow().cast(Long.class).as("Quantity")).from(LINES).where(LINE_TENANT.eq(1L)).orderBy(LINE_ID.asc().nullsLast()).limit(val(32L));
            case 25->dsl.select(ID.as("OrderId"),CUSTOMER_NAME,PRODUCT,QUANTITY).from(ORDERS).join(CUSTOMERS).on(CUSTOMER.eq(CUSTOMER_ID)).join(LINES).on(TENANT.eq(LINE_TENANT).and(ID.eq(LINE_ORDER))).where(tenant).orderBy(ID.asc().nullsLast(),LINE_ID.asc().nullsLast()).limit(val(32L));
            case 26->dsl.select(ID.as("value")).from(ORDERS).where(tenant.and(ID.notIn(dsl.select(LINE_ORDER).from(LINES).where(LINE_TENANT.eq(1L).and(QUANTITY.ge(5L)))))).orderBy(ID.asc().nullsLast()).limit(val(32L));
            // This case intentionally uses NULLS FIRST, exactly as queries-v3.json.
            case 27->dsl.select(ID.as("value")).from(ORDERS).where(tenant).orderBy(CUSTOMER.asc().nullsFirst(),ID.asc().nullsLast()).limit(val(32L));
            // This workload case explicitly tests raw SQL in every route.
            case 28->dsl.resultQuery("SELECT \"Id\",\"Note\" FROM orders WHERE \"TenantId\"=? ORDER BY \"Id\" LIMIT ?",1L,32L);
            case 29->relatedQuery();
            // The query still selects all 1024 complete orders. The consumer stops after three.
            case 34->dsl.select(WIDE).from(ORDERS).where(tenant).orderBy(ID.asc().nullsLast()).limit(val(1024L));
            default->throw new IllegalArgumentException("No read query: "+i);
        };
    }

    private ResultQuery<?> cte(boolean set,int index){
        Select<Record1<Long>> source;
        if(!set)source=dsl.select(ID.as("Id")).from(ORDERS).where(TENANT.eq(1L).and(ID.gt(16L)));
        else{
            Select<Record1<Long>> a=dsl.select(ID.as("Id")).from(ORDERS).where(TENANT.eq(1L).and(ID.le(16L)));
            Select<Record1<Long>> b=dsl.select(ID.as("Id")).from(ORDERS).where(TENANT.eq(1L).and(ID.ge(9L)).and(ID.le(24L)));
            source=switch(index){case 20->a.unionAll(b);case 21->a.union(b);case 22->a.intersect(b);case 23->a.except(b);default->throw new IllegalArgumentException();};
        }
        var c=name("selected_order_ids").fields("Id").as(source);
        var id=field(name("selected_order_ids","Id"),Long.class);
        var q=dsl.with(c).select(id.as("value")).from(c).orderBy(id.asc().nullsLast());
        return set?q:q.limit(val(32L));
    }
    private ResultQuery<?> relatedQuery(){
        // Equivalent bounded-key SQL optimization: one IN query, then all input groups retained.
        Long[] keys=new Long[32];for(int i=0;i<keys.length;i++)keys[i]=(long)i+1;
        return dsl.select(LINE_ID,LINE_TENANT,LINE_ORDER,PRODUCT,QUANTITY).from(LINES)
            .where(LINE_TENANT.eq(1L).and(LINE_ORDER.in(keys))).orderBy(LINE_ORDER.asc().nullsLast(),LINE_ID.asc().nullsLast());
    }
    private ResultQuery<?> findQuery(){return dsl.select(WIDE).from(ORDERS).where(TENANT.eq(1L).and(ID.eq(1024L))).limit(val(2L));}

    void warmup(){
        if(options.verify)for(int i=0;i<35;i++)executeValidated(i);
        for(int i=0;i<options.warmup;i++)executeValidated(options.index(i));
    }
    OperationResult scheduled(long job){
        int i=options.index(job);caseStarted[i]++;
        try{var r=executeValidated(i);caseSucceeded[i]++;caseRows[i]+=r.rows();return r;}
        catch(RuntimeException error){caseFailed[i]++;throw error;}
    }
    OperationResult executeValidated(int i){
        try{
            OperationResult r=options.emptyDriver?new OperationResult(Contract.ROWS[i],Contract.DIGESTS[i]):execute(i);
            if(r.rows()!=Contract.ROWS[i]||r.digest()!=Contract.DIGESTS[i])throw Oracle.fail("Expected "+Contract.ROWS[i]+"/"+Long.toUnsignedString(Contract.DIGESTS[i],16)+"; observed "+r.rows()+"/"+Long.toUnsignedString(r.digest(),16),Contract.NAMES[i]);
            return r;
        }catch(RuntimeException e){Oracle.observe(e,Contract.NAMES[i]);throw e;}
    }
    private OperationResult execute(int i){
        digest.reset();
        if(i>=30&&i<=33)return transaction(i);
        if(i==29)return related();
        ResultQuery<?> q=prepared[i]!=null?prepared[i]:build(i);
        long count=0;
        try(Cursor<?> cursor=q.fetchLazy()){
            while(cursor.hasNext()){
                Record row=cursor.fetchNext();
                hashRow(i,row);count++;
                if(i==34&&count==3)break;
            }
        }
        return new OperationResult(count,digest.value());
    }
    private BigDecimal money(Record row,int column){
        BigDecimal raw=row.get(column,BigDecimal.class);
        if(raw==null)return null;
        return (options.provider.equals("sqlite")?raw.movePointLeft(2):raw).setScale(2,RoundingMode.UNNECESSARY);
    }
    private static long integer(Record row,int column){return Objects.requireNonNull(row.get(column,Long.class),"Non-null Int64 column is NULL");}
    private static String requiredText(Record row,int column){return Objects.requireNonNull(row.get(column,String.class),"Non-null string column is NULL");}
    private static Settings settings(String value){
        try(var parser=JSON.createParser(value)){
            if(parser.nextToken()!=JsonToken.START_OBJECT)throw new IllegalArgumentException("Settings must be a JSON object");
            String channel=null;Boolean gift=null;
            while(parser.nextToken()!=JsonToken.END_OBJECT){
                if(parser.currentToken()!=JsonToken.FIELD_NAME)throw new IllegalArgumentException("Expected JSON property");
                String key=parser.currentName();JsonToken token=parser.nextToken();
                if(key.equals("Channel")){if(token!=JsonToken.VALUE_STRING)throw new IllegalArgumentException("Channel must be a string");channel=parser.getText();}
                else if(key.equals("Gift")){if(token!=JsonToken.VALUE_TRUE&&token!=JsonToken.VALUE_FALSE)throw new IllegalArgumentException("Gift must be boolean");gift=parser.getBooleanValue();}
                else parser.skipChildren();
            }
            if(channel==null||gift==null||parser.nextToken()!=null)throw new IllegalArgumentException("Invalid Settings fields");
            return new Settings(channel,gift);
        }catch(IOException e){throw new UncheckedIOException(e);}
    }
    private Order order(Record r){return new Order(integer(r,0),integer(r,1),integer(r,2),r.get(3,Long.class),
        Objects.requireNonNull(money(r,4)),r.get(5,String.class),integer(r,6),settings(requiredText(r,7)),requiredText(r,8));}
    private void hashRow(int i,Record r){
        switch(i){
            case 1,28->{var v=new TextRow(integer(r,0),r.get(1,String.class));digest.integer(v.id());digest.text(v.note());}
            case 2->{var v=new MoneyRow(integer(r,0),Objects.requireNonNull(money(r,1)));digest.integer(v.id());digest.money(v.total());}
            case 3->{var v=new JsonRow(integer(r,0),settings(requiredText(r,1)));digest.integer(v.id());digest.settings(v.settings());}
            case 4,34->digest.order(order(r));
            case 7,8->{var v=new JoinRow(integer(r,0),r.get(1,String.class));digest.integer(v.id());digest.text(v.name());}
            case 11->{var v=new CustomerTotal(r.get(0,Long.class),integer(r,1),money(r,2));digest.nullableInteger(v.customerId());digest.integer(v.count());digest.nullableMoney(v.total());}
            case 12->{var v=new ProductTotal(requiredText(r,0),r.get(1,Long.class));digest.text(v.product());digest.nullableInteger(v.quantity());}
            case 13->digest.nullableMoney(money(r,0));
            case 19->{var v=new RankRow(integer(r,0),integer(r,1));digest.integer(v.id());digest.integer(v.rank());}
            case 24->{var v=new RunningRow(integer(r,0),r.get(1,Long.class));digest.integer(v.id());digest.nullableInteger(v.quantity());}
            case 25->{var v=new DetailRow(integer(r,0),requiredText(r,1),requiredText(r,2),integer(r,3));digest.integer(v.orderId());digest.text(v.name());digest.text(v.product());digest.integer(v.quantity());}
            default->digest.integer(integer(r,0));
        }
    }
    private OperationResult related(){
        var groups=new ArrayList<ArrayList<OrderLine>>(32);
        for(int i=0;i<32;i++)groups.add(new ArrayList<>());
        long rows=0;
        try(Cursor<?> cursor=relatedQuery().fetchLazy()){
            while(cursor.hasNext()){
                Record r=cursor.fetchNext();var line=new OrderLine(integer(r,0),integer(r,1),integer(r,2),requiredText(r,3),integer(r,4));
                if(line.tenantId()!=1||line.orderId()<1||line.orderId()>32)throw Oracle.fail("Related key is outside the bounded input","related");
                groups.get(Math.toIntExact(line.orderId()-1)).add(line);rows++;
            }
        }
        for(int i=0;i<32;i++){
            var group=groups.get(i);group.sort(Comparator.comparingLong(OrderLine::id));
            digest.integer(i+1);digest.integer(group.size());for(var child:group)digest.line(child);
        }
        return new OperationResult(rows,digest.value());
    }

    private Order find(String caseId){
        try(Cursor<?> cursor=findQuery().fetchLazy()){
            if(!cursor.hasNext())throw Oracle.fail("Fixed write key returned no rows",caseId);
            Order row=order(cursor.fetchNext());
            if(cursor.hasNext())throw Oracle.fail("Fixed write key returned more than one row",caseId);
            return row;
        }
    }
    private static void requireSame(Order actual,Order expected,String name,String stage){
        if(!actual.equals(expected))throw Oracle.fail(stage+": full order differs from the fixed contract",name);
    }
    private OperationResult transaction(int index){
        String name=Contract.NAMES[index];boolean sqlite=options.provider.equals("sqlite"),active=false;
        Throwable primary=null;
        Order original;
        try{
            if(sqlite)dsl.execute("BEGIN IMMEDIATE");
            else{connection.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);connection.setAutoCommit(false);}
            active=true;
            original=find(name);requireSame(original,Models.seedOrder(1024),name,"original");digest.order(original);
            int changed;
            if(index==32)changed=dsl.update(ORDERS).set(NOTE,(String)null).where(TENANT.eq(1L).and(ID.eq(1024L))).execute();
            else if(index==33)changed=dsl.update(ORDERS).set(NOTE,"perf-mutated").set(VERSION,2L).where(TENANT.eq(1L).and(ID.eq(1024L)).and(VERSION.eq(1L))).execute();
            else changed=dsl.update(ORDERS).set(NOTE,"perf-mutated").set(VERSION,2L).where(TENANT.eq(1L).and(ID.eq(1024L))).execute();
            if(changed!=1)throw Oracle.fail("Mutation did not affect exactly one order",name);
            if(index==33){
                int stale=dsl.update(ORDERS).set(NOTE,"stale-write").where(TENANT.eq(1L).and(ID.eq(1024L)).and(VERSION.eq(1L))).execute();
                if(stale!=0)throw Oracle.fail("Stale optimistic write was accepted",name);
                digest.bool(true);if(sqlite)dsl.execute("ROLLBACK");else connection.rollback();active=false;
            }else{
                Order check=find(name);requireSame(check,index==32?original.withNote(null):original.mutated(),name,"mutated");digest.order(check);
                if(index==31){if(sqlite)dsl.execute("ROLLBACK");else connection.rollback();active=false;}
                else{
                    int restored=index==32?dsl.update(ORDERS).set(NOTE,original.note()).where(TENANT.eq(1L).and(ID.eq(1024L))).execute()
                        :dsl.update(ORDERS).set(NOTE,original.note()).set(VERSION,original.version()).where(TENANT.eq(1L).and(ID.eq(1024L))).execute();
                    if(restored!=1)throw Oracle.fail("Restore did not affect exactly one order",name);
                    if(sqlite)dsl.execute("COMMIT");else connection.commit();active=false;
                }
            }
        }catch(RuntimeException|SQLException error){
            primary=error;Oracle.observe(error,name);throw error instanceof RuntimeException r?r:new DatabaseFailure(error);
        }finally{
            try{
                if(active){if(sqlite)dsl.execute("ROLLBACK");else connection.rollback();}
                if(!sqlite&&!connection.getAutoCommit())connection.setAutoCommit(true);
            }catch(RuntimeException|SQLException cleanup){
                var violation=Oracle.fail("Transaction did not retire cleanly",name,cleanup);
                if(primary!=null)primary.addSuppressed(violation);else throw violation;
            }
        }
        Order persisted=find(name);requireSame(persisted,original,name,"persisted");digest.order(persisted);
        return new OperationResult(index==33?2:3,digest.value());
    }
    static final class DatabaseFailure extends RuntimeException { DatabaseFailure(Throwable error){super(error);} }
    @Override public void close() throws SQLException {connection.close();if(!connection.isClosed())throw Oracle.fail("Connection remained open after close",null);}
}
