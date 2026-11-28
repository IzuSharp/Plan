package org.korda.compare;

import java.math.BigDecimal;

final class Models {
    record Settings(String channel, boolean gift) {}
    record TextRow(long id, String note) {}
    record MoneyRow(long id, BigDecimal total) {}
    record JsonRow(long id, Settings settings) {}
    record Order(long tenantId, long id, long createdAt, Long customerId, BigDecimal total,
                 String note, long version, Settings settings, String internalMemo) {
        Order withNote(String value) { return new Order(tenantId,id,createdAt,customerId,total,value,version,settings,internalMemo); }
        Order mutated() { return new Order(tenantId,id,createdAt,customerId,total,"perf-mutated",2,settings,internalMemo); }
    }
    record JoinRow(long id, String name) {}
    record CustomerTotal(Long customerId, long count, BigDecimal total) {}
    record ProductTotal(String product, Long quantity) {}
    record RankRow(long id, long rank) {}
    record RunningRow(long id, Long quantity) {}
    record DetailRow(long orderId, String name, String product, long quantity) {}
    record OrderLine(long id, long tenantId, long orderId, String product, long quantity) {}
    record OperationResult(long rows, long digest) {}

    static Order seedOrder(long id) {
        Long customer = id%7==0 ? null : id%10<7 ? 1+id%8 : 9+id%248;
        return new Order(1,id,1_700_000_000L+id/4,customer,
            BigDecimal.valueOf(100+(1009+id*37)%100000,2),id%5==0?null:"note-"+id%16,
            1,new Settings(id%2==0?"web":"store",id%11==0),"m".repeat(id%17==0?2048:32));
    }
}
