#nullable enable
#pragma warning disable IDE0078 // unnecessary suppression is necessary
#pragma warning disable CS9270 // SDK-dependent change to interceptors usage
namespace Dapper.AOT // interceptors must be in a known namespace
{
    file static class DapperGeneratedInterceptors
    {
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/754bc732518e/orm-probe/Program.cs", 28, 26)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/754bc732518e/orm-probe/Program.cs", 68, 26)]
        internal static global::System.Threading.Tasks.Task<int> ExecuteAsync0(this global::System.Data.IDbConnection cnn, string sql, object? param, global::System.Data.IDbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Execute, Async, Text
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), DefaultCommandFactory).ExecuteAsync(param);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/754bc732518e/orm-probe/Program.cs", 31, 41)]
        internal static global::System.Threading.Tasks.Task<int> ExecuteAsync1(this global::System.Data.IDbConnection cnn, string sql, object? param, global::System.Data.IDbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Execute, Async, HasParameters, Text, KnownParameters
            // takes parameter: <anonymous type: long Id, string Customer, string? Note, decimal Total>
            // parameter map: Customer Id Note Total
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory0.Instance).ExecuteAsync(param);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/754bc732518e/orm-probe/Program.cs", 37, 39)]
        internal static global::System.Threading.Tasks.Task<global::ProbeRow> QuerySingleAsync2(this global::System.Data.IDbConnection cnn, string sql, object? param, global::System.Data.IDbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, SingleRow, Text, AtLeastOne, AtMostOne, BindResultsByName, KnownParameters
            // takes parameter: <anonymous type: long Id>
            // parameter map: Id
            // returns data: global::ProbeRow
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory1.Instance).QuerySingleAsync(param, RowFactory0.Instance);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/754bc732518e/orm-probe/Program.cs", 42, 46)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<global::ProbeRow> QueryUnbufferedAsync3(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, BindResultsByName, KnownParameters
            // takes parameter: <anonymous type: long Id>
            // parameter map: Id
            // returns data: global::ProbeRow
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory1.Instance).QueryUnbufferedAsync(param, RowFactory0.Instance);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/754bc732518e/orm-probe/Program.cs", 52, 30)]
        internal static global::System.Threading.Tasks.Task<int> ExecuteAsync4(this global::System.Data.IDbConnection cnn, string sql, object? param, global::System.Data.IDbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Execute, Async, HasParameters, Text, KnownParameters
            // takes parameter: <anonymous type: string Customer, long Id>
            // parameter map: Customer Id
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory2.Instance).ExecuteAsync(param);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/754bc732518e/orm-probe/Program.cs", 56, 36)]
        internal static global::ProbeRow QuerySingle5(this global::System.Data.IDbConnection cnn, string sql, object? param, global::System.Data.IDbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, TypedResult, HasParameters, SingleRow, Text, AtLeastOne, AtMostOne, BindResultsByName, KnownParameters
            // takes parameter: <anonymous type: long Id>
            // parameter map: Id
            // returns data: global::ProbeRow
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory1.Instance).QuerySingle(param, RowFactory0.Instance);

        }


        private static global::Dapper.CommandFactory<object?> DefaultCommandFactory => global::Dapper.CommandFactory.Simple;

        private sealed class RowFactory0 : global::Dapper.RowFactory<global::ProbeRow>
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
                            token = type == typeof(long) ? 0 : 4; // two tokens for right-typed and type-flexible
                            break;
                        case 2763893273U when NormalizedEquals(name, "customer"):
                            token = type == typeof(string) ? 1 : 5;
                            break;
                        case 2442791997U when NormalizedEquals(name, "note"):
                            token = type == typeof(string) ? 2 : 6;
                            break;
                        case 80777981U when NormalizedEquals(name, "total"):
                            token = type == typeof(decimal) ? 3 : 7;
                            break;

                    }
                    tokens[i] = token;
                    columnOffset++;

                }
                return null;
            }
            public override global::ProbeRow Read(global::System.Data.Common.DbDataReader reader, global::System.ReadOnlySpan<int> tokens, int columnOffset, object? state)
            {
                global::ProbeRow result = new();
                foreach (var token in tokens)
                {
                    switch (token)
                    {
                        case 0:
                            result.Id = reader.GetInt64(columnOffset);
                            break;
                        case 4:
                            result.Id = GetValue<long>(reader, columnOffset);
                            break;
                        case 1:
                            result.Customer = reader.GetString(columnOffset);
                            break;
                        case 5:
                            result.Customer = GetValue<string>(reader, columnOffset);
                            break;
                        case 2:
                            result.Note = reader.IsDBNull(columnOffset) ? (string?)null : reader.GetString(columnOffset);
                            break;
                        case 6:
                            result.Note = reader.IsDBNull(columnOffset) ? (string?)null : GetValue<string>(reader, columnOffset);
                            break;
                        case 3:
                            result.Total = reader.GetDecimal(columnOffset);
                            break;
                        case 7:
                            result.Total = GetValue<decimal>(reader, columnOffset);
                            break;

                    }
                    columnOffset++;

                }
                return result;

            }

        }

        private sealed class CommandFactory0 : global::Dapper.CommandFactory<object?> // <anonymous type: long Id, string Customer, string? Note, decimal Total>
        {
            internal static readonly CommandFactory0 Instance = new();
            public override void AddParameters(in global::Dapper.UnifiedCommand cmd, object? args)
            {
                var typed = Cast(args, static () => new { Id = default(long), Customer = default(string), Note = default(string?), Total = default(decimal) }); // expected shape
                var ps = cmd.Parameters;
                global::System.Data.Common.DbParameter p;
                p = cmd.CreateParameter();
                p.ParameterName = "Id";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.Id);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "Customer";
                p.DbType = global::System.Data.DbType.String;
                p.Direction = global::System.Data.ParameterDirection.Input;
                SetValueWithDefaultSize(p, typed.Customer);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "Note";
                p.DbType = global::System.Data.DbType.String;
                p.Direction = global::System.Data.ParameterDirection.Input;
                SetValueWithDefaultSize(p, typed.Note);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "Total";
                p.DbType = global::System.Data.DbType.Decimal;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.Total);
                ps.Add(p);

            }
            public override void UpdateParameters(in global::Dapper.UnifiedCommand cmd, object? args)
            {
                var typed = Cast(args, static () => new { Id = default(long), Customer = default(string), Note = default(string?), Total = default(decimal) }); // expected shape
                var ps = cmd.Parameters;
                ps[0].Value = AsValue(typed.Id);
                ps[1].Value = AsValue(typed.Customer);
                ps[2].Value = AsValue(typed.Note);
                ps[3].Value = AsValue(typed.Total);

            }
            public override bool CanPrepare => true;

        }

        private sealed class CommandFactory1 : global::Dapper.CommandFactory<object?> // <anonymous type: long Id>
        {
            internal static readonly CommandFactory1 Instance = new();
            public override void AddParameters(in global::Dapper.UnifiedCommand cmd, object? args)
            {
                var typed = Cast(args, static () => new { Id = default(long) }); // expected shape
                var ps = cmd.Parameters;
                global::System.Data.Common.DbParameter p;
                p = cmd.CreateParameter();
                p.ParameterName = "Id";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.Id);
                ps.Add(p);

            }
            public override void UpdateParameters(in global::Dapper.UnifiedCommand cmd, object? args)
            {
                var typed = Cast(args, static () => new { Id = default(long) }); // expected shape
                var ps = cmd.Parameters;
                ps[0].Value = AsValue(typed.Id);

            }
            public override bool CanPrepare => true;

        }

        private sealed class CommandFactory2 : global::Dapper.CommandFactory<object?> // <anonymous type: string Customer, long Id>
        {
            internal static readonly CommandFactory2 Instance = new();
            public override void AddParameters(in global::Dapper.UnifiedCommand cmd, object? args)
            {
                var typed = Cast(args, static () => new { Customer = default(string), Id = default(long) }); // expected shape
                var ps = cmd.Parameters;
                global::System.Data.Common.DbParameter p;
                p = cmd.CreateParameter();
                p.ParameterName = "Customer";
                p.DbType = global::System.Data.DbType.String;
                p.Direction = global::System.Data.ParameterDirection.Input;
                SetValueWithDefaultSize(p, typed.Customer);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "Id";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.Id);
                ps.Add(p);

            }
            public override void UpdateParameters(in global::Dapper.UnifiedCommand cmd, object? args)
            {
                var typed = Cast(args, static () => new { Customer = default(string), Id = default(long) }); // expected shape
                var ps = cmd.Parameters;
                ps[0].Value = AsValue(typed.Customer);
                ps[1].Value = AsValue(typed.Id);

            }
            public override bool CanPrepare => true;

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