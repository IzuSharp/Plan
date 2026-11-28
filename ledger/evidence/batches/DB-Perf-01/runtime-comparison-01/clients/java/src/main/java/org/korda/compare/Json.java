package org.korda.compare;

import com.fasterxml.jackson.core.JsonFactory;
import com.fasterxml.jackson.core.JsonGenerator;
import java.io.IOException;
import java.io.OutputStream;
import java.math.BigDecimal;
import java.math.BigInteger;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.LinkedHashMap;
import java.util.Map;

/** Explicit JSON serialization avoids reflective bean discovery in Native Image. */
final class Json {
    static Map<String,Object> map(Object... pairs){var result=new LinkedHashMap<String,Object>();for(int i=0;i<pairs.length;i+=2)result.put((String)pairs[i],pairs[i+1]);return result;}
    static void create(Path path,Object value)throws IOException{
        if(path.getParent()!=null)Files.createDirectories(path.getParent());
        try(OutputStream out=Files.newOutputStream(path,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE);var g=new JsonFactory().createGenerator(out)){g.useDefaultPrettyPrinter();write(g,value);}
    }
    static String text(Object value)throws IOException{var out=new java.io.StringWriter();try(var g=new JsonFactory().createGenerator(out)){write(g,value);}return out.toString();}
    private static void write(JsonGenerator g,Object value)throws IOException{
        if(value==null)g.writeNull();
        else if(value instanceof String v)g.writeString(v);
        else if(value instanceof Boolean v)g.writeBoolean(v);
        else if(value instanceof BigInteger v)g.writeNumber(v);
        else if(value instanceof BigDecimal v)g.writeNumber(v);
        else if(value instanceof Integer v)g.writeNumber(v);
        else if(value instanceof Long v)g.writeNumber(v);
        else if(value instanceof Double v)g.writeNumber(v);
        else if(value instanceof Float v)g.writeNumber(v);
        else if(value instanceof Map<?,?> m){g.writeStartObject();for(var entry:m.entrySet()){g.writeFieldName((String)entry.getKey());write(g,entry.getValue());}g.writeEndObject();}
        else if(value instanceof Iterable<?> list){g.writeStartArray();for(var item:list)write(g,item);g.writeEndArray();}
        else if(value instanceof long[] list){g.writeStartArray();for(long item:list)g.writeNumber(item);g.writeEndArray();}
        else if(value instanceof Object[] list){g.writeStartArray();for(var item:list)write(g,item);g.writeEndArray();}
        else throw new IllegalArgumentException("Unregistered JSON value: "+value.getClass().getName());
    }
}
