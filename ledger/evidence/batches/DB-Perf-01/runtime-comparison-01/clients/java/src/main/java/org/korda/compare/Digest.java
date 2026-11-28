package org.korda.compare;

import java.math.BigDecimal;
import java.nio.ByteBuffer;
import java.nio.CharBuffer;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
import static org.korda.compare.Models.*;

/** Canonical FNV-1a; this is the original contract, not Java object hashes. */
final class Digest {
    private long value = 0xcbf29ce484222325L;
    // Per worker, allocated before measurement. No new UTF-8 byte array per field.
    private final ByteBuffer utf8 = ByteBuffer.allocate(4096);
    private final java.nio.charset.CharsetEncoder encoder = StandardCharsets.UTF_8.newEncoder()
        .onMalformedInput(CodingErrorAction.REPORT).onUnmappableCharacter(CodingErrorAction.REPORT);
    void reset() { value=0xcbf29ce484222325L; }
    long value() { return value; }
    private void octet(int b) { value ^= b&255; value *= 0x100000001b3L; }
    void integer(long x) { for(int i=0;i<8;i++){octet((int)x);x>>>=8;} }
    void bool(boolean x) { octet(x?1:0); }
    void nullableInteger(Long x) { bool(x!=null);if(x!=null)integer(x); }
    void money(BigDecimal x) { integer(x.movePointRight(2).longValueExact()); }
    void nullableMoney(BigDecimal x) { bool(x!=null);if(x!=null)money(x); }
    void text(String s) {
        if(s==null){integer(-1);return;}
        utf8.clear();encoder.reset();
        var result=encoder.encode(CharBuffer.wrap(s),utf8,true);
        if(result.isError()||result.isOverflow())throw new IllegalArgumentException("UTF-8 exceeds fixed 4096-byte field contract");
        result=encoder.flush(utf8);
        if(result.isError()||result.isOverflow())throw new IllegalArgumentException("Invalid UTF-8 field");
        integer(utf8.position());
        for(int i=0;i<utf8.position();i++)octet(utf8.get(i));
    }
    void settings(Settings s){text(s.channel());bool(s.gift());}
    void order(Order o){integer(o.tenantId());integer(o.id());integer(o.createdAt());nullableInteger(o.customerId());
        money(o.total());text(o.note());integer(o.version());settings(o.settings());text(o.internalMemo());}
    void line(OrderLine l){integer(l.id());integer(l.tenantId());integer(l.orderId());text(l.product());integer(l.quantity());}
}
