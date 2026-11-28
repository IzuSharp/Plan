package org.korda.compare;

import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Properties;
import org.jooq.SQLDialect;
import org.jooq.conf.ParamType;
import org.jooq.conf.RenderQuotedNames;
import org.jooq.conf.StatementType;
import org.jooq.impl.DSL;

final class Database {
    final Options options;
    final Map<String,Object> identity=new LinkedHashMap<>();
    final ArrayList<Long> backendPids=new ArrayList<>();
    Database(Options options){this.options=options;}
    Workload open()throws Exception{
        Connection c;
        if(options.provider.equals("sqlite")){
            System.setProperty("org.sqlite.lib.path",options.sqliteJniDirectory.toString());
            var config=new org.sqlite.SQLiteConfig();config.enforceForeignKeys(true);config.setBusyTimeout(5000);
            config.setJournalMode(org.sqlite.SQLiteConfig.JournalMode.WAL);config.setSynchronous(org.sqlite.SQLiteConfig.SynchronousMode.FULL);
            c=new org.sqlite.JDBC().connect(options.connection.startsWith("jdbc:")?options.connection:"jdbc:sqlite:"+options.connection,config.toProperties());
        }else{
            var properties=new Properties();properties.setProperty("prepareThreshold","0");properties.setProperty("connectTimeout","30");
            properties.setProperty("ApplicationName","DB-Runtime-Compare-01-java");
            String url=options.connection.startsWith("jdbc:")?options.connection:"jdbc:"+options.connection;
            // JDBC URLs carry host/database/options; credentials may also be supplied as environment variables.
            String user=System.getenv("PGUSER"),password=System.getenv("PGPASSWORD");
            if(user!=null)properties.setProperty("user",user);if(password!=null)properties.setProperty("password",password);
            c=new org.postgresql.Driver().connect(url,properties);
        }
        if(c==null)throw new IllegalArgumentException("Driver did not accept connection URL");
        try{
            var settings=new org.jooq.conf.Settings().withRenderSchema(false).withRenderFormatted(false).withRenderQuotedNames(RenderQuotedNames.ALWAYS)
                .withExecuteLogging(false).withParamType(ParamType.INDEXED).withStatementType(StatementType.PREPARED_STATEMENT)
                .withQueryTimeout(options.provider.equals("sqlite")?5:30);
            var dsl=DSL.using(c,options.provider.equals("sqlite")?SQLDialect.SQLITE:SQLDialect.POSTGRES,settings);
            var metadata=dsl.fetch("SELECT schema_version,tenants,orders_per_tenant FROM db_perf_metadata");
            if(metadata.size()!=1||metadata.get(0).get(0,Long.class)!=1L||metadata.get(0).get(1,Long.class)!=8L||metadata.get(0).get(2,Long.class)!=1024L)
                throw Oracle.fail("Dataset metadata differs from fixed v3 oracle","dataset");
            identity.put("DatabaseVersion",c.getMetaData().getDatabaseProductVersion());identity.put("DriverVersion",c.getMetaData().getDriverVersion());
            if(options.provider.equals("sqlite")){
                identity.put("SQLiteVersion",dsl.fetchValue("SELECT sqlite_version()"));identity.put("SQLiteSourceId",dsl.fetchValue("SELECT sqlite_source_id()"));
                var flags=new ArrayList<String>();for(var r:dsl.fetch("PRAGMA compile_options"))flags.add(r.get(0,String.class));flags.sort(String::compareTo);identity.put("SqliteCompileOptions",flags);
                identity.put("Pragmas",Json.map("journal_mode",dsl.fetchValue("PRAGMA journal_mode"),"synchronous",dsl.fetchValue("PRAGMA synchronous"),"foreign_keys",dsl.fetchValue("PRAGMA foreign_keys"),"busy_timeout",dsl.fetchValue("PRAGMA busy_timeout")));
                var mapped=new LinkedHashMap<String,Object>();
                for(String line:Files.readAllLines(Path.of("/proc/self/maps"))){
                    String[] parts=line.split("\\s+",6);
                    if(parts.length==6&&(parts[5].contains("sqlitejdbc")||parts[5].contains("libsqlite3"))){
                        String path=parts[5].replace(" (deleted)","");if(!mapped.containsKey(path))mapped.put(path,Files.exists(Path.of(path))?sha256(Path.of(path)):"deleted-mapping-unavailable");
                    }
                }
                identity.put("LoadedSQLiteImages",mapped);
                var enginePaths=mapped.keySet().stream().filter(path->Path.of(path).getFileName().toString().startsWith("libsqlite3.so")).toList();
                if(enginePaths.size()!=1||!Path.of(enginePaths.get(0)).toRealPath().equals(options.sqliteNativeLibrary.toRealPath()))
                    throw Oracle.fail("The sole mapped SQLite engine is not the explicitly selected baseline library","dataset");
                if(!"3.51.3".equals(identity.get("SQLiteVersion")))throw Oracle.fail("The fixed SQLite version differs from 3.51.3","dataset");
            }else backendPids.add(((Number)dsl.fetchValue("SELECT pg_backend_pid()")).longValue());
            return new Workload(options,c,dsl);
        }catch(Exception e){c.close();throw e;}
    }
    static String sha256(Path path)throws Exception{
        var digest=MessageDigest.getInstance("SHA-256");byte[] block=new byte[65536];
        try(var in=Files.newInputStream(path)){int n;while((n=in.read(block))>=0)if(n>0)digest.update(block,0,n);}
        return HexFormat.of().formatHex(digest.digest());
    }
}
