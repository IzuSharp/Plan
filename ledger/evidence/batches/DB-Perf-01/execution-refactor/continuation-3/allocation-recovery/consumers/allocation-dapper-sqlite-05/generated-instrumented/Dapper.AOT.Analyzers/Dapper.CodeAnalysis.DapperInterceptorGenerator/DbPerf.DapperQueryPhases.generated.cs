#nullable enable
#pragma warning disable IDE0078 // unnecessary suppression is necessary
#pragma warning disable CS9270 // SDK-dependent change to interceptors usage
namespace Dapper.AOT // interceptors must be in a known namespace
{
    file static class DapperGeneratedInterceptors
    {
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/4a65d70f0fe1/consumers/allocation-dapper-sqlite-05/Driver.cs", 74, 26)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/4a65d70f0fe1/consumers/allocation-dapper-sqlite-05/Driver.cs", 82, 26)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/4a65d70f0fe1/consumers/allocation-dapper-sqlite-05/Driver.cs", 99, 26)]
        internal static global::System.Threading.Tasks.Task<int> ExecuteAsync0(this global::System.Data.IDbConnection cnn, string sql, object? param, global::System.Data.IDbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Execute, Async, Text
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), DefaultCommandFactory).ExecuteAsync(param);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/4a65d70f0fe1/consumers/allocation-dapper-sqlite-05/Driver.cs", 75, 44)]
        internal static global::System.Threading.Tasks.Task<string> QuerySingleAsync1(this global::System.Data.IDbConnection cnn, string sql, object? param, global::System.Data.IDbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, SingleRow, Text, AtLeastOne, AtMostOne
            // returns data: string
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), DefaultCommandFactory).QuerySingleAsync(param, global::Dapper.RowFactory.Inbuilt.Value<string>());

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/4a65d70f0fe1/consumers/allocation-dapper-sqlite-05/Driver.cs", 76, 37)]
        internal static global::System.Collections.Generic.IEnumerable<string> Query2(this global::System.Data.IDbConnection cnn, string sql, object? param, global::System.Data.IDbTransaction? transaction, bool buffered, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, TypedResult, Buffered, Text
            // returns data: string
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(buffered is true);
            global::System.Diagnostics.Debug.Assert(param is null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), DefaultCommandFactory).QueryBuffered(param, global::Dapper.RowFactory.Inbuilt.Value<string>());

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/4a65d70f0fe1/consumers/allocation-dapper-sqlite-05/Driver.cs", 95, 30)]
        internal static global::System.Threading.Tasks.Task<int> ExecuteAsync3(this global::System.Data.IDbConnection cnn, string sql, object? param, global::System.Data.IDbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Execute, Async
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert(param is null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, default, commandTimeout.GetValueOrDefault(), DefaultCommandFactory).ExecuteAsync(param);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/4a65d70f0fe1/consumers/allocation-dapper-sqlite-05/PhaseProbe.cs", 27, 26)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<global::PhaseRow> QueryUnbufferedAsync4(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, BindResultsByName, CacheCommand, KnownParameters
            // takes parameter: global::PhaseProbe.Arguments
            // parameter map: id tenant
            // returns data: global::PhaseRow
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory0.Instance0).QueryUnbufferedAsync((global::PhaseProbe.Arguments)param!, RowFactory0.Instance);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/4a65d70f0fe1/consumers/allocation-dapper-sqlite-05/PhaseProbe.cs", 28, 26)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<global::PhaseRow> QueryUnbufferedAsync5(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, BindResultsByName, CacheCommand, KnownParameters
            // takes parameter: global::PhaseProbe.Arguments
            // parameter map: id tenant
            // returns data: global::PhaseRow
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory0.Instance1).QueryUnbufferedAsync((global::PhaseProbe.Arguments)param!, RowFactory0.Instance);

        }


        private static global::Dapper.CommandFactory<object?> DefaultCommandFactory => global::Dapper.CommandFactory.Simple;

        private sealed class RowFactory0 : global::Dapper.RowFactory<global::PhaseRow>
        {
            internal static readonly RowFactory0 Instance = new();
            private RowFactory0() {}
            public override object? Tokenize(global::System.Data.Common.DbDataReader reader, global::System.Span<int> tokens, int columnOffset)
            {
                for (int i = 0; i < tokens.Length; i++)
                {
                    int token = -1;
                    var name = reader.GetName(columnOffset);
                    var type = reader.GetFieldType(columnOffset);
                    switch (NormalizedHash(name))
                    {
                        case 926444256U when NormalizedEquals(name, "id"):
                            token = type == typeof(long) ? 0 : 2; // two tokens for right-typed and type-flexible
                            break;
                        case 2442791997U when NormalizedEquals(name, "note"):
                            token = type == typeof(string) ? 1 : 3;
                            break;

                    }
                    tokens[i] = token;
                    columnOffset++;

                }
                return null;
            }
            public override global::PhaseRow Read(global::System.Data.Common.DbDataReader reader, global::System.ReadOnlySpan<int> tokens, int columnOffset, object? state)
            {
                using var __allocationScope = global::BusinessAllocation.Mapper();
                long value0 = default;
                string? value1 = default;
                foreach (var token in tokens)
                {
                    switch (token)
                    {
                        case 0:
                            value0 = reader.GetInt64(columnOffset);
                            break;
                        case 2:
                            value0 = GetValue<long>(reader, columnOffset);
                            break;
                        case 1:
                            value1 = reader.IsDBNull(columnOffset) ? (string?)null : reader.GetString(columnOffset);
                            break;
                        case 3:
                            value1 = reader.IsDBNull(columnOffset) ? (string?)null : GetValue<string>(reader, columnOffset);
                            break;

                    }
                    columnOffset++;

                }
                return new global::PhaseRow(value0, value1);
            }
        }

        private abstract class CommandFactory0 : global::Dapper.CommandFactory<global::PhaseProbe.Arguments>
        {
            // these represent different call-sites (and most likely all have different SQL etc)
            internal static readonly CommandFactory0.Cached0 Instance0 = new();
            internal static readonly CommandFactory0.Cached1 Instance1 = new();

            public override void AddParameters(in global::Dapper.UnifiedCommand cmd, global::PhaseProbe.Arguments args)
            {
                var ps = cmd.Parameters;
                global::System.Data.Common.DbParameter p;
                p = cmd.CreateParameter();
                p.ParameterName = "tenant";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "id";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.id);
                ps.Add(p);

            }
            public override void UpdateParameters(in global::Dapper.UnifiedCommand cmd, global::PhaseProbe.Arguments args)
            {
                var ps = cmd.Parameters;
                ps[0].Value = AsValue(args.tenant);
                ps[1].Value = AsValue(args.id);

            }
            public override bool CanPrepare => true;

            public override global::System.Data.Common.DbCommand GetCommand(global::System.Data.Common.DbConnection connection,
                string sql, global::System.Data.CommandType commandType, global::PhaseProbe.Arguments args)
                 => TryReuseThreadStatic(ref Storage, sql, commandType, args, _cmdPool) ?? base.GetCommand(connection, sql, commandType, args);

            public override bool TryRecycle(global::System.Data.Common.DbCommand command) => TryRecycleThreadStatic(ref Storage, command, _cmdPool);
            private readonly DbCommandCache _cmdPool = new(); // note: per cache instance
            protected abstract ref global::System.Data.Common.DbCommand? Storage {get;}

            internal sealed class Cached0 : CommandFactory0
            {
                protected override ref global::System.Data.Common.DbCommand? Storage => ref s_Storage;
                [global::System.ThreadStatic] // note this works correctly with ref-return
                private static global::System.Data.Common.DbCommand? s_Storage;

            }
            internal sealed class Cached1 : CommandFactory0
            {
                protected override ref global::System.Data.Common.DbCommand? Storage => ref s_Storage;
                [global::System.ThreadStatic] // note this works correctly with ref-return
                private static global::System.Data.Common.DbCommand? s_Storage;

            }

        }


    }
}
namespace System.Runtime.CompilerServices
{
    // this type is needed by the compiler to implement interceptors - it doesn't need to
    // come from the runtime itself, though

    [global::System.Diagnostics.Conditional("DEBUG")] // not needed post-build, so: evaporate
    [global::System.AttributeUsage(global::System.AttributeTargets.Method, AllowMultiple = true)]
    sealed file class InterceptsLocationAttribute : global::System.Attribute
    {
        public InterceptsLocationAttribute(string path, int lineNumber, int columnNumber)
        {
            _ = path;
            _ = lineNumber;
            _ = columnNumber;
        }
    }
}