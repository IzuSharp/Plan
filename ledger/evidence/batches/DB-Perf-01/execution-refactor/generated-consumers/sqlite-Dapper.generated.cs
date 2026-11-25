#nullable enable
#pragma warning disable IDE0078 // unnecessary suppression is necessary
#pragma warning disable CS9270 // SDK-dependent change to interceptors usage
namespace Dapper.AOT // interceptors must be in a known namespace
{
    file static class DapperGeneratedInterceptors
    {
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 116, 28)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<long> QueryUnbufferedAsync0(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2
            // returns data: long
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory0.Instance0).QueryUnbufferedAsync((global::Workload.Parameters)param!, global::Dapper.RowFactory.Inbuilt.Value<long>());

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 117, 28)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<global::TextRow> QueryUnbufferedAsync1(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, BindResultsByName, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2
            // returns data: global::TextRow
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory0.Instance1).QueryUnbufferedAsync((global::Workload.Parameters)param!, RowFactory0.Instance);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 118, 28)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<global::MoneyRow> QueryUnbufferedAsync2(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, BindResultsByName, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2
            // returns data: global::MoneyRow
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory0.Instance2).QueryUnbufferedAsync((global::Workload.Parameters)param!, RowFactory1.Instance);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 119, 28)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<global::JsonRow> QueryUnbufferedAsync3(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, BindResultsByName, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2
            // returns data: global::JsonRow
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory0.Instance3).QueryUnbufferedAsync((global::Workload.Parameters)param!, RowFactory2.Instance);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 120, 28)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<global::Order> QueryUnbufferedAsync4(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, BindResultsByName, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2
            // returns data: global::Order
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory0.Instance4).QueryUnbufferedAsync((global::Workload.Parameters)param!, RowFactory3.Instance);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 121, 28)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<long> QueryUnbufferedAsync5(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2 p3
            // returns data: long
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory1.Instance0).QueryUnbufferedAsync((global::Workload.Parameters)param!, global::Dapper.RowFactory.Inbuilt.Value<long>());

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 122, 28)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<long> QueryUnbufferedAsync6(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2 p3 p4
            // returns data: long
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory2.Instance0).QueryUnbufferedAsync((global::Workload.Parameters)param!, global::Dapper.RowFactory.Inbuilt.Value<long>());

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 123, 28)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<global::JoinRow> QueryUnbufferedAsync7(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, BindResultsByName, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2
            // returns data: global::JoinRow
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory0.Instance5).QueryUnbufferedAsync((global::Workload.Parameters)param!, RowFactory4.Instance);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 124, 28)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<global::JoinRow> QueryUnbufferedAsync8(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, BindResultsByName, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2
            // returns data: global::JoinRow
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory0.Instance6).QueryUnbufferedAsync((global::Workload.Parameters)param!, RowFactory4.Instance);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 125, 28)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<long> QueryUnbufferedAsync9(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2
            // returns data: long
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory0.Instance7).QueryUnbufferedAsync((global::Workload.Parameters)param!, global::Dapper.RowFactory.Inbuilt.Value<long>());

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 126, 29)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<long> QueryUnbufferedAsync10(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p3 pattern
            // returns data: long
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory3.Instance0).QueryUnbufferedAsync((global::Workload.Parameters)param!, global::Dapper.RowFactory.Inbuilt.Value<long>());

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 127, 29)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<global::CustomerTotal> QueryUnbufferedAsync11(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, BindResultsByName, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2
            // returns data: global::CustomerTotal
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory0.Instance8).QueryUnbufferedAsync((global::Workload.Parameters)param!, RowFactory5.Instance);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 128, 29)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<global::ProductTotal> QueryUnbufferedAsync12(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, BindResultsByName, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2
            // returns data: global::ProductTotal
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory0.Instance9).QueryUnbufferedAsync((global::Workload.Parameters)param!, RowFactory6.Instance);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 129, 29)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<decimal?> QueryUnbufferedAsync13(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1
            // returns data: decimal?
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory4.Instance0).QueryUnbufferedAsync((global::Workload.Parameters)param!, global::Dapper.RowFactory.Inbuilt.NullableValue<decimal>());

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 130, 29)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<long> QueryUnbufferedAsync14(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2 p3 p4 p5 p6 p7
            // returns data: long
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory5.Instance0).QueryUnbufferedAsync((global::Workload.Parameters)param!, global::Dapper.RowFactory.Inbuilt.Value<long>());

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 131, 29)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<long> QueryUnbufferedAsync15(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2 p3
            // returns data: long
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory1.Instance1).QueryUnbufferedAsync((global::Workload.Parameters)param!, global::Dapper.RowFactory.Inbuilt.Value<long>());

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 132, 29)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<long> QueryUnbufferedAsync16(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2 p3
            // returns data: long
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory1.Instance2).QueryUnbufferedAsync((global::Workload.Parameters)param!, global::Dapper.RowFactory.Inbuilt.Value<long>());

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 133, 29)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<long> QueryUnbufferedAsync17(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2 p3
            // returns data: long
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory1.Instance3).QueryUnbufferedAsync((global::Workload.Parameters)param!, global::Dapper.RowFactory.Inbuilt.Value<long>());

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 134, 29)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<long> QueryUnbufferedAsync18(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2 p3
            // returns data: long
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory1.Instance4).QueryUnbufferedAsync((global::Workload.Parameters)param!, global::Dapper.RowFactory.Inbuilt.Value<long>());

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 135, 29)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<global::RankRow> QueryUnbufferedAsync19(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, BindResultsByName, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2
            // returns data: global::RankRow
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory0.Instance10).QueryUnbufferedAsync((global::Workload.Parameters)param!, RowFactory7.Instance);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 136, 29)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<long> QueryUnbufferedAsync20(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2 p3 p4 p5
            // returns data: long
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory6.Instance0).QueryUnbufferedAsync((global::Workload.Parameters)param!, global::Dapper.RowFactory.Inbuilt.Value<long>());

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 137, 29)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<long> QueryUnbufferedAsync21(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2 p3 p4 p5
            // returns data: long
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory6.Instance1).QueryUnbufferedAsync((global::Workload.Parameters)param!, global::Dapper.RowFactory.Inbuilt.Value<long>());

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 138, 29)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<long> QueryUnbufferedAsync22(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2 p3 p4 p5
            // returns data: long
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory6.Instance2).QueryUnbufferedAsync((global::Workload.Parameters)param!, global::Dapper.RowFactory.Inbuilt.Value<long>());

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 139, 29)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<long> QueryUnbufferedAsync23(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2 p3 p4 p5
            // returns data: long
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory6.Instance3).QueryUnbufferedAsync((global::Workload.Parameters)param!, global::Dapper.RowFactory.Inbuilt.Value<long>());

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 140, 29)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<global::RunningRow> QueryUnbufferedAsync24(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, BindResultsByName, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2
            // returns data: global::RunningRow
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory0.Instance11).QueryUnbufferedAsync((global::Workload.Parameters)param!, RowFactory8.Instance);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 141, 29)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<global::DetailRow> QueryUnbufferedAsync25(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, BindResultsByName, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2
            // returns data: global::DetailRow
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory0.Instance12).QueryUnbufferedAsync((global::Workload.Parameters)param!, RowFactory9.Instance);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 142, 29)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<long> QueryUnbufferedAsync26(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2 p3 p4
            // returns data: long
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory2.Instance1).QueryUnbufferedAsync((global::Workload.Parameters)param!, global::Dapper.RowFactory.Inbuilt.Value<long>());

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 143, 29)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<long> QueryUnbufferedAsync27(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2
            // returns data: long
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory0.Instance13).QueryUnbufferedAsync((global::Workload.Parameters)param!, global::Dapper.RowFactory.Inbuilt.Value<long>());

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 144, 29)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<global::TextRow> QueryUnbufferedAsync28(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, BindResultsByName, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2
            // returns data: global::TextRow
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory0.Instance14).QueryUnbufferedAsync((global::Workload.Parameters)param!, RowFactory0.Instance);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 155, 32)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 160, 32)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 161, 32)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 164, 32)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 165, 33)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 169, 33)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 170, 33)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 171, 33)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 172, 33)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 173, 33)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 175, 33)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 176, 33)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 177, 33)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 178, 33)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 181, 33)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 182, 33)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<long> QueryUnbufferedAsync29(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: (deferred)
            // returns data: long
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, default, commandTimeout.GetValueOrDefault(), CommandFactory7.Instance).QueryUnbufferedAsync((global::Workload.Parameters)param!, global::Dapper.RowFactory.Inbuilt.Value<long>());

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 156, 32)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 183, 33)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<global::TextRow> QueryUnbufferedAsync30(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, BindResultsByName, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: (deferred)
            // returns data: global::TextRow
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, default, commandTimeout.GetValueOrDefault(), CommandFactory7.Instance).QueryUnbufferedAsync((global::Workload.Parameters)param!, RowFactory0.Instance);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 157, 32)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<global::MoneyRow> QueryUnbufferedAsync31(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, BindResultsByName, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: (deferred)
            // returns data: global::MoneyRow
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, default, commandTimeout.GetValueOrDefault(), CommandFactory7.Instance).QueryUnbufferedAsync((global::Workload.Parameters)param!, RowFactory1.Instance);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 158, 32)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<global::JsonRow> QueryUnbufferedAsync32(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, BindResultsByName, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: (deferred)
            // returns data: global::JsonRow
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, default, commandTimeout.GetValueOrDefault(), CommandFactory7.Instance).QueryUnbufferedAsync((global::Workload.Parameters)param!, RowFactory2.Instance);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 159, 32)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/LifecycleCases.cs", 41, 27)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<global::Order> QueryUnbufferedAsync33(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, BindResultsByName, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: (deferred)
            // returns data: global::Order
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, default, commandTimeout.GetValueOrDefault(), CommandFactory7.Instance).QueryUnbufferedAsync((global::Workload.Parameters)param!, RowFactory3.Instance);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 162, 32)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 163, 32)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<global::JoinRow> QueryUnbufferedAsync34(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, BindResultsByName, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: (deferred)
            // returns data: global::JoinRow
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, default, commandTimeout.GetValueOrDefault(), CommandFactory7.Instance).QueryUnbufferedAsync((global::Workload.Parameters)param!, RowFactory4.Instance);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 166, 33)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<global::CustomerTotal> QueryUnbufferedAsync35(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, BindResultsByName, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: (deferred)
            // returns data: global::CustomerTotal
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, default, commandTimeout.GetValueOrDefault(), CommandFactory7.Instance).QueryUnbufferedAsync((global::Workload.Parameters)param!, RowFactory5.Instance);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 167, 33)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<global::ProductTotal> QueryUnbufferedAsync36(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, BindResultsByName, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: (deferred)
            // returns data: global::ProductTotal
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, default, commandTimeout.GetValueOrDefault(), CommandFactory7.Instance).QueryUnbufferedAsync((global::Workload.Parameters)param!, RowFactory6.Instance);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 168, 33)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<decimal?> QueryUnbufferedAsync37(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: (deferred)
            // returns data: decimal?
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, default, commandTimeout.GetValueOrDefault(), CommandFactory7.Instance).QueryUnbufferedAsync((global::Workload.Parameters)param!, global::Dapper.RowFactory.Inbuilt.NullableValue<decimal>());

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 174, 33)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<global::RankRow> QueryUnbufferedAsync38(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, BindResultsByName, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: (deferred)
            // returns data: global::RankRow
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, default, commandTimeout.GetValueOrDefault(), CommandFactory7.Instance).QueryUnbufferedAsync((global::Workload.Parameters)param!, RowFactory7.Instance);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 179, 33)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<global::RunningRow> QueryUnbufferedAsync39(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, BindResultsByName, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: (deferred)
            // returns data: global::RunningRow
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, default, commandTimeout.GetValueOrDefault(), CommandFactory7.Instance).QueryUnbufferedAsync((global::Workload.Parameters)param!, RowFactory8.Instance);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 180, 33)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<global::DetailRow> QueryUnbufferedAsync40(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, BindResultsByName, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: (deferred)
            // returns data: global::DetailRow
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, default, commandTimeout.GetValueOrDefault(), CommandFactory7.Instance).QueryUnbufferedAsync((global::Workload.Parameters)param!, RowFactory9.Instance);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 289, 97)]
        internal static global::System.Threading.Tasks.Task<global::System.Collections.Generic.IEnumerable<global::IndexedLine>> QueryAsync41(this global::System.Data.IDbConnection cnn, string sql, object? param, global::System.Data.IDbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Buffered, Text, BindResultsByName, CacheCommand, KnownParameters
            // takes parameter: global::Workload.RelatedParameters
            // parameter map: parent_id_0 parent_id_1 parent_id_10 parent_id_11 parent_id_12 parent_id_13 parent_id_14 parent_id_15 parent_id_16 parent_id_17 parent_id_18 parent_id_19 parent_id_2 parent_id_20 parent_id_21 parent_id_22 parent_id_23 parent_id_24 parent_id_25 parent_id_26 parent_id_27 parent_id_28 parent_id_29 parent_id_3 parent_id_30 parent_id_31 parent_id_4 parent_id_5 parent_id_6 parent_id_7 parent_id_8 parent_id_9 parent_index_0 parent_index_1 parent_index_10 parent_index_11 parent_index_12 parent_index_13 parent_index_14 parent_index_15 parent_index_16 parent_index_17 parent_index_18 parent_index_19 parent_index_2 parent_index_20 parent_index_21 parent_index_22 parent_index_23 parent_index_24 parent_index_25 parent_index_26 parent_index_27 parent_index_28 parent_index_29 parent_index_3 parent_index_30 parent_index_31 parent_index_4 parent_index_5 parent_index_6 parent_index_7 parent_index_8 parent_index_9 tenant_0 tenant_1 tenant_10 tenant_11 tenant_12 tenant_13 tenant_14 tenant_15 tenant_16 tenant_17 tenant_18 tenant_19 tenant_2 tenant_20 tenant_21 tenant_22 tenant_23 tenant_24 tenant_25 tenant_26 tenant_27 tenant_28 tenant_29 tenant_3 tenant_30 tenant_31 tenant_4 tenant_5 tenant_6 tenant_7 tenant_8 tenant_9
            // returns data: global::IndexedLine
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.AsEnumerableAsync(
                global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory8.Instance0).QueryBufferedAsync((global::Workload.RelatedParameters)param!, RowFactory10.Instance));

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Contracts.generated.cs", 291, 98)]
        internal static global::System.Threading.Tasks.Task<global::System.Collections.Generic.IEnumerable<global::IndexedLine>> QueryAsync42(this global::System.Data.IDbConnection cnn, string sql, object? param, global::System.Data.IDbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Buffered, BindResultsByName, KnownParameters
            // takes parameter: global::Workload.RelatedParameters
            // parameter map: (deferred)
            // returns data: global::IndexedLine
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.AsEnumerableAsync(
                global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, default, commandTimeout.GetValueOrDefault(), CommandFactory9.Instance).QueryBufferedAsync((global::Workload.RelatedParameters)param!, RowFactory10.Instance));

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Driver.cs", 57, 30)]
        internal static global::System.Threading.Tasks.Task<int> ExecuteAsync43(this global::System.Data.IDbConnection cnn, string sql, object? param, global::System.Data.IDbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Execute, Async, Text
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), DefaultCommandFactory).ExecuteAsync(param);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Driver.cs", 75, 33)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Driver.cs", 76, 36)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/LifecycleVerification.cs", 24, 33)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/LifecycleVerification.cs", 46, 37)]
        internal static global::System.Threading.Tasks.Task<long> ExecuteScalarAsync44(this global::System.Data.IDbConnection cnn, string sql, object? param, global::System.Data.IDbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Execute, Async, TypedResult, Text, Scalar
            // returns data: long
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), DefaultCommandFactory).ExecuteScalarAsync<long>(param);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/Driver.cs", 79, 39)]
        internal static global::System.Collections.Generic.IEnumerable<string> Query45(this global::System.Data.IDbConnection cnn, string sql, object? param, global::System.Data.IDbTransaction? transaction, bool buffered, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, TypedResult, Buffered, Text
            // returns data: string
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(buffered is true);
            global::System.Diagnostics.Debug.Assert(param is null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), DefaultCommandFactory).QueryBuffered(param, global::Dapper.RowFactory.Inbuilt.Value<string>());

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/LifecycleCases.cs", 38, 27)]
        internal static global::System.Collections.Generic.IAsyncEnumerable<global::Order> QueryUnbufferedAsync46(this global::System.Data.Common.DbConnection cnn, string sql, object? param, global::System.Data.Common.DbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, Unbuffered, Text, BindResultsByName, CacheCommand, KnownParameters
            // takes parameter: global::Workload.Parameters
            // parameter map: p1 p2
            // returns data: global::Order
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory0.Instance15).QueryUnbufferedAsync((global::Workload.Parameters)param!, RowFactory3.Instance);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/LifecycleCases.cs", 61, 29)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/LifecycleCases.cs", 87, 34)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/LifecycleCases.cs", 120, 30)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/LifecycleVerification.cs", 59, 94)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/LifecycleVerification.cs", 60, 36)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/LifecycleVerification.cs", 83, 32)]
        internal static global::System.Threading.Tasks.Task<global::Order> QuerySingleAsync47(this global::System.Data.IDbConnection cnn, string sql, object? param, global::System.Data.IDbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Query, Async, TypedResult, HasParameters, SingleRow, Text, AtLeastOne, AtMostOne, BindResultsByName, KnownParameters
            // takes parameter: <anonymous type: long tenant, long id>
            // parameter map: id tenant
            // returns data: global::Order
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory10.Instance).QuerySingleAsync(param, RowFactory3.Instance);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/LifecycleCases.cs", 68, 54)]
        internal static global::System.Threading.Tasks.Task<int> ExecuteAsync48(this global::System.Data.IDbConnection cnn, string sql, object? param, global::System.Data.IDbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Execute, Async, HasParameters, Text, KnownParameters
            // takes parameter: <anonymous type: long tenant, long id, string? note, long version, long expected>
            // parameter map: expected id note tenant version
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory11.Instance).ExecuteAsync(param);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/LifecycleCases.cs", 69, 48)]
        internal static global::System.Threading.Tasks.Task<int> ExecuteAsync49(this global::System.Data.IDbConnection cnn, string sql, object? param, global::System.Data.IDbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Execute, Async, HasParameters, Text, KnownParameters
            // takes parameter: <anonymous type: long tenant, long id, string? note, long version, long expected>
            // parameter map: id note tenant
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory12.Instance).ExecuteAsync(param);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/LifecycleCases.cs", 69, 104)]
        internal static global::System.Threading.Tasks.Task<int> ExecuteAsync50(this global::System.Data.IDbConnection cnn, string sql, object? param, global::System.Data.IDbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Execute, Async, HasParameters, Text, KnownParameters
            // takes parameter: <anonymous type: long tenant, long id, string? note, long version, long expected>
            // parameter map: id note tenant version
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory13.Instance).ExecuteAsync(param);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/LifecycleCases.cs", 77, 38)]
        internal static global::System.Threading.Tasks.Task<int> ExecuteAsync51(this global::System.Data.IDbConnection cnn, string sql, object? param, global::System.Data.IDbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Execute, Async, HasParameters, Text, KnownParameters
            // takes parameter: <anonymous type: long tenant, long id, string note, long expected>
            // parameter map: expected id note tenant
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory14.Instance).ExecuteAsync(param);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/LifecycleCases.cs", 101, 65)]
        internal static global::System.Threading.Tasks.Task<int> ExecuteAsync52(this global::System.Data.IDbConnection cnn, string sql, object? param, global::System.Data.IDbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Execute, Async, HasParameters, Text, KnownParameters
            // takes parameter: <anonymous type: long tenant, long id, string? note, long version>
            // parameter map: id note tenant
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory15.Instance).ExecuteAsync(param);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/LifecycleCases.cs", 101, 121)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/LifecycleVerification.cs", 81, 29)]
        internal static global::System.Threading.Tasks.Task<int> ExecuteAsync53(this global::System.Data.IDbConnection cnn, string sql, object? param, global::System.Data.IDbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Execute, Async, HasParameters, Text, KnownParameters
            // takes parameter: <anonymous type: long tenant, long id, string? note, long version>
            // parameter map: id note tenant version
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory16.Instance).ExecuteAsync(param);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/LifecycleVerification.cs", 28, 37)]
        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/LifecycleVerification.cs", 43, 37)]
        internal static global::System.Threading.Tasks.Task<long> ExecuteScalarAsync54(this global::System.Data.IDbConnection cnn, string sql, object? param, global::System.Data.IDbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Execute, Async, TypedResult, HasParameters, Text, Scalar, KnownParameters
            // takes parameter: <anonymous type: long value, CancellationToken cancellation>
            // parameter map: value
            // returns data: long
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory17.Instance).ExecuteScalarAsync<long>(param);

        }

        [global::System.Runtime.CompilerServices.InterceptsLocationAttribute("/workspace/scratch/17ac3f8f2fbf/consumers/dapper-sqlite/LifecycleVerification.cs", 66, 37)]
        internal static global::System.Threading.Tasks.Task<int> ExecuteAsync55(this global::System.Data.IDbConnection cnn, string sql, object? param, global::System.Data.IDbTransaction? transaction, int? commandTimeout, global::System.Data.CommandType? commandType)
        {
            // Execute, Async, HasParameters, Text, KnownParameters
            // takes parameter: <anonymous type: long tenant, long id, long version, long expected>
            // parameter map: expected id tenant version
            global::System.Diagnostics.Debug.Assert(!string.IsNullOrWhiteSpace(sql));
            global::System.Diagnostics.Debug.Assert((commandType ?? global::Dapper.DapperAotExtensions.GetCommandType(sql)) == global::System.Data.CommandType.Text);
            global::System.Diagnostics.Debug.Assert(param is not null);

            return global::Dapper.DapperAotExtensions.Command(cnn, transaction, sql, global::System.Data.CommandType.Text, commandTimeout.GetValueOrDefault(), CommandFactory18.Instance).ExecuteAsync(param);

        }


        private static global::Dapper.CommandFactory<object?> DefaultCommandFactory => global::Dapper.CommandFactory.Simple;

        private sealed class RowFactory0 : global::Dapper.RowFactory<global::TextRow>
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
            public override global::TextRow Read(global::System.Data.Common.DbDataReader reader, global::System.ReadOnlySpan<int> tokens, int columnOffset, object? state)
            {
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
                return new global::TextRow(value0, value1);
            }
        }

        private sealed class RowFactory1 : global::Dapper.RowFactory<global::MoneyRow>
        {
            internal static readonly RowFactory1 Instance = new();
            private RowFactory1() {}
            public override object? Tokenize(global::System.Data.Common.DbDataReader reader, global::System.Span<int> tokens, int columnOffset)
            {
                var handlerTokens = new int[tokens.Length];
                var handlerOffset = columnOffset; // the loop below advances columnOffset
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
                        case 80777981U when NormalizedEquals(name, "total"):
                            token = 3; // type-handler: the handler decides
                            break;

                    }
                    tokens[i] = token;
                    columnOffset++;

                }
                for (int i = 0; i < tokens.Length; i++)
                {
                    switch (tokens[i])
                    {
                        case 1: case 3:
                            handlerTokens[i] = TypeHandler0.Tokenize(reader, handlerOffset + i);
                            break;

                    }

                }
                return handlerTokens;
            }
            public override global::MoneyRow Read(global::System.Data.Common.DbDataReader reader, global::System.ReadOnlySpan<int> tokens, int columnOffset, object? state)
            {
                long value0 = default;
                decimal value1 = default;
                var handlerTokens = (int[])state!;
                for (int i = 0; i < tokens.Length; i++)
                {
                    switch (tokens[i])
                    {
                        case 0:
                            value0 = reader.GetInt64(columnOffset);
                            break;
                        case 2:
                            value0 = GetValue<long>(reader, columnOffset);
                            break;
                        case 1:
                            value1 = TypeHandler0.Parse(reader, columnOffset, handlerTokens[i]);
                            break;
                        case 3:
                            value1 = TypeHandler0.Parse(reader, columnOffset, handlerTokens[i]);
                            break;

                    }
                    columnOffset++;

                }
                return new global::MoneyRow(value0, value1);
            }
        }

        private sealed class RowFactory2 : global::Dapper.RowFactory<global::JsonRow>
        {
            internal static readonly RowFactory2 Instance = new();
            private RowFactory2() {}
            public override object? Tokenize(global::System.Data.Common.DbDataReader reader, global::System.Span<int> tokens, int columnOffset)
            {
                var handlerTokens = new int[tokens.Length];
                var handlerOffset = columnOffset; // the loop below advances columnOffset
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
                        case 1745255176U when NormalizedEquals(name, "settings"):
                            token = 3; // type-handler: the handler decides
                            break;

                    }
                    tokens[i] = token;
                    columnOffset++;

                }
                for (int i = 0; i < tokens.Length; i++)
                {
                    switch (tokens[i])
                    {
                        case 1: case 3:
                            handlerTokens[i] = TypeHandler2.Tokenize(reader, handlerOffset + i);
                            break;

                    }

                }
                return handlerTokens;
            }
            public override global::JsonRow Read(global::System.Data.Common.DbDataReader reader, global::System.ReadOnlySpan<int> tokens, int columnOffset, object? state)
            {
                long value0 = default;
                global::OrderSettings value1 = default!;
                var handlerTokens = (int[])state!;
                for (int i = 0; i < tokens.Length; i++)
                {
                    switch (tokens[i])
                    {
                        case 0:
                            value0 = reader.GetInt64(columnOffset);
                            break;
                        case 2:
                            value0 = GetValue<long>(reader, columnOffset);
                            break;
                        case 1:
                            value1 = TypeHandler2.Parse(reader, columnOffset, handlerTokens[i]);
                            break;
                        case 3:
                            value1 = TypeHandler2.Parse(reader, columnOffset, handlerTokens[i]);
                            break;

                    }
                    columnOffset++;

                }
                return new global::JsonRow(value0, value1);
            }
        }

        private sealed class RowFactory3 : global::Dapper.RowFactory<global::Order>
        {
            internal static readonly RowFactory3 Instance = new();
            private RowFactory3() {}
            public override object? Tokenize(global::System.Data.Common.DbDataReader reader, global::System.Span<int> tokens, int columnOffset)
            {
                var handlerTokens = new int[tokens.Length];
                var handlerOffset = columnOffset; // the loop below advances columnOffset
                for (int i = 0; i < tokens.Length; i++)
                {
                    int token = -1;
                    var name = reader.GetName(columnOffset);
                    var type = reader.GetFieldType(columnOffset);
                    switch (NormalizedHash(name))
                    {
                        case 1725646016U when NormalizedEquals(name, "tenantid"):
                            token = type == typeof(long) ? 0 : 9; // two tokens for right-typed and type-flexible
                            break;
                        case 926444256U when NormalizedEquals(name, "id"):
                            token = type == typeof(long) ? 1 : 10;
                            break;
                        case 365500078U when NormalizedEquals(name, "createdat"):
                            token = type == typeof(long) ? 2 : 11;
                            break;
                        case 3454278620U when NormalizedEquals(name, "customerid"):
                            token = type == typeof(long) ? 3 : 12;
                            break;
                        case 80777981U when NormalizedEquals(name, "total"):
                            token = 13; // type-handler: the handler decides
                            break;
                        case 2442791997U when NormalizedEquals(name, "note"):
                            token = type == typeof(string) ? 5 : 14;
                            break;
                        case 1181855383U when NormalizedEquals(name, "version"):
                            token = type == typeof(long) ? 6 : 15;
                            break;
                        case 1745255176U when NormalizedEquals(name, "settings"):
                            token = 16; // type-handler: the handler decides
                            break;
                        case 1222310698U when NormalizedEquals(name, "internalmemo"):
                            token = type == typeof(string) ? 8 : 17;
                            break;

                    }
                    tokens[i] = token;
                    columnOffset++;

                }
                for (int i = 0; i < tokens.Length; i++)
                {
                    switch (tokens[i])
                    {
                        case 4: case 13:
                            handlerTokens[i] = TypeHandler0.Tokenize(reader, handlerOffset + i);
                            break;
                        case 7: case 16:
                            handlerTokens[i] = TypeHandler2.Tokenize(reader, handlerOffset + i);
                            break;

                    }

                }
                return handlerTokens;
            }
            public override global::Order Read(global::System.Data.Common.DbDataReader reader, global::System.ReadOnlySpan<int> tokens, int columnOffset, object? state)
            {
                long value0 = default;
                long value1 = default;
                long value2 = default;
                long? value3 = default;
                decimal value4 = default;
                string? value5 = default;
                long value6 = default;
                global::OrderSettings value7 = default!;
                string value8 = default!;
                var handlerTokens = (int[])state!;
                for (int i = 0; i < tokens.Length; i++)
                {
                    switch (tokens[i])
                    {
                        case 0:
                            value0 = reader.GetInt64(columnOffset);
                            break;
                        case 9:
                            value0 = GetValue<long>(reader, columnOffset);
                            break;
                        case 1:
                            value1 = reader.GetInt64(columnOffset);
                            break;
                        case 10:
                            value1 = GetValue<long>(reader, columnOffset);
                            break;
                        case 2:
                            value2 = reader.GetInt64(columnOffset);
                            break;
                        case 11:
                            value2 = GetValue<long>(reader, columnOffset);
                            break;
                        case 3:
                            value3 = reader.IsDBNull(columnOffset) ? (long?)null : reader.GetInt64(columnOffset);
                            break;
                        case 12:
                            value3 = reader.IsDBNull(columnOffset) ? (long?)null : GetValue<long>(reader, columnOffset);
                            break;
                        case 4:
                            value4 = TypeHandler0.Parse(reader, columnOffset, handlerTokens[i]);
                            break;
                        case 13:
                            value4 = TypeHandler0.Parse(reader, columnOffset, handlerTokens[i]);
                            break;
                        case 5:
                            value5 = reader.IsDBNull(columnOffset) ? (string?)null : reader.GetString(columnOffset);
                            break;
                        case 14:
                            value5 = reader.IsDBNull(columnOffset) ? (string?)null : GetValue<string>(reader, columnOffset);
                            break;
                        case 6:
                            value6 = reader.GetInt64(columnOffset);
                            break;
                        case 15:
                            value6 = GetValue<long>(reader, columnOffset);
                            break;
                        case 7:
                            value7 = TypeHandler2.Parse(reader, columnOffset, handlerTokens[i]);
                            break;
                        case 16:
                            value7 = TypeHandler2.Parse(reader, columnOffset, handlerTokens[i]);
                            break;
                        case 8:
                            value8 = reader.GetString(columnOffset);
                            break;
                        case 17:
                            value8 = GetValue<string>(reader, columnOffset);
                            break;

                    }
                    columnOffset++;

                }
                return new global::Order(value0, value1, value2, value3, value4, value5, value6, value7, value8);
            }
        }

        private sealed class RowFactory4 : global::Dapper.RowFactory<global::JoinRow>
        {
            internal static readonly RowFactory4 Instance = new();
            private RowFactory4() {}
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
                        case 2369371622U when NormalizedEquals(name, "name"):
                            token = type == typeof(string) ? 1 : 3;
                            break;

                    }
                    tokens[i] = token;
                    columnOffset++;

                }
                return null;
            }
            public override global::JoinRow Read(global::System.Data.Common.DbDataReader reader, global::System.ReadOnlySpan<int> tokens, int columnOffset, object? state)
            {
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
                return new global::JoinRow(value0, value1);
            }
        }

        private sealed class RowFactory5 : global::Dapper.RowFactory<global::CustomerTotal>
        {
            internal static readonly RowFactory5 Instance = new();
            private RowFactory5() {}
            public override object? Tokenize(global::System.Data.Common.DbDataReader reader, global::System.Span<int> tokens, int columnOffset)
            {
                var handlerTokens = new int[tokens.Length];
                var handlerOffset = columnOffset; // the loop below advances columnOffset
                for (int i = 0; i < tokens.Length; i++)
                {
                    int token = -1;
                    var name = reader.GetName(columnOffset);
                    var type = reader.GetFieldType(columnOffset);
                    switch (NormalizedHash(name))
                    {
                        case 3454278620U when NormalizedEquals(name, "customerid"):
                            token = type == typeof(long) ? 0 : 3; // two tokens for right-typed and type-flexible
                            break;
                        case 967958004U when NormalizedEquals(name, "count"):
                            token = type == typeof(long) ? 1 : 4;
                            break;
                        case 80777981U when NormalizedEquals(name, "total"):
                            token = 5; // type-handler: the handler decides
                            break;

                    }
                    tokens[i] = token;
                    columnOffset++;

                }
                for (int i = 0; i < tokens.Length; i++)
                {
                    switch (tokens[i])
                    {
                        case 2: case 5:
                            handlerTokens[i] = TypeHandler0.Tokenize(reader, handlerOffset + i);
                            break;

                    }

                }
                return handlerTokens;
            }
            public override global::CustomerTotal Read(global::System.Data.Common.DbDataReader reader, global::System.ReadOnlySpan<int> tokens, int columnOffset, object? state)
            {
                long? value0 = default;
                long value1 = default;
                decimal? value2 = default;
                var handlerTokens = (int[])state!;
                for (int i = 0; i < tokens.Length; i++)
                {
                    switch (tokens[i])
                    {
                        case 0:
                            value0 = reader.IsDBNull(columnOffset) ? (long?)null : reader.GetInt64(columnOffset);
                            break;
                        case 3:
                            value0 = reader.IsDBNull(columnOffset) ? (long?)null : GetValue<long>(reader, columnOffset);
                            break;
                        case 1:
                            value1 = reader.GetInt64(columnOffset);
                            break;
                        case 4:
                            value1 = GetValue<long>(reader, columnOffset);
                            break;
                        case 2:
                            value2 = reader.IsDBNull(columnOffset) ? (decimal?)null : TypeHandler0.Parse(reader, columnOffset, handlerTokens[i]);
                            break;
                        case 5:
                            value2 = reader.IsDBNull(columnOffset) ? (decimal?)null : TypeHandler0.Parse(reader, columnOffset, handlerTokens[i]);
                            break;

                    }
                    columnOffset++;

                }
                return new global::CustomerTotal(value0, value1, value2);
            }
        }

        private sealed class RowFactory6 : global::Dapper.RowFactory<global::ProductTotal>
        {
            internal static readonly RowFactory6 Instance = new();
            private RowFactory6() {}
            public override object? Tokenize(global::System.Data.Common.DbDataReader reader, global::System.Span<int> tokens, int columnOffset)
            {
                for (int i = 0; i < tokens.Length; i++)
                {
                    int token = -1;
                    var name = reader.GetName(columnOffset);
                    var type = reader.GetFieldType(columnOffset);
                    switch (NormalizedHash(name))
                    {
                        case 3846717740U when NormalizedEquals(name, "product"):
                            token = type == typeof(string) ? 0 : 2; // two tokens for right-typed and type-flexible
                            break;
                        case 1265799128U when NormalizedEquals(name, "quantity"):
                            token = type == typeof(long) ? 1 : 3;
                            break;

                    }
                    tokens[i] = token;
                    columnOffset++;

                }
                return null;
            }
            public override global::ProductTotal Read(global::System.Data.Common.DbDataReader reader, global::System.ReadOnlySpan<int> tokens, int columnOffset, object? state)
            {
                string value0 = default!;
                long? value1 = default;
                foreach (var token in tokens)
                {
                    switch (token)
                    {
                        case 0:
                            value0 = reader.GetString(columnOffset);
                            break;
                        case 2:
                            value0 = GetValue<string>(reader, columnOffset);
                            break;
                        case 1:
                            value1 = reader.IsDBNull(columnOffset) ? (long?)null : reader.GetInt64(columnOffset);
                            break;
                        case 3:
                            value1 = reader.IsDBNull(columnOffset) ? (long?)null : GetValue<long>(reader, columnOffset);
                            break;

                    }
                    columnOffset++;

                }
                return new global::ProductTotal(value0, value1);
            }
        }

        private sealed class RowFactory7 : global::Dapper.RowFactory<global::RankRow>
        {
            internal static readonly RowFactory7 Instance = new();
            private RowFactory7() {}
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
                        case 2895879719U when NormalizedEquals(name, "rank"):
                            token = type == typeof(long) ? 1 : 3;
                            break;

                    }
                    tokens[i] = token;
                    columnOffset++;

                }
                return null;
            }
            public override global::RankRow Read(global::System.Data.Common.DbDataReader reader, global::System.ReadOnlySpan<int> tokens, int columnOffset, object? state)
            {
                long value0 = default;
                long value1 = default;
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
                            value1 = reader.GetInt64(columnOffset);
                            break;
                        case 3:
                            value1 = GetValue<long>(reader, columnOffset);
                            break;

                    }
                    columnOffset++;

                }
                return new global::RankRow(value0, value1);
            }
        }

        private sealed class RowFactory8 : global::Dapper.RowFactory<global::RunningRow>
        {
            internal static readonly RowFactory8 Instance = new();
            private RowFactory8() {}
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
                        case 1265799128U when NormalizedEquals(name, "quantity"):
                            token = type == typeof(long) ? 1 : 3;
                            break;

                    }
                    tokens[i] = token;
                    columnOffset++;

                }
                return null;
            }
            public override global::RunningRow Read(global::System.Data.Common.DbDataReader reader, global::System.ReadOnlySpan<int> tokens, int columnOffset, object? state)
            {
                long value0 = default;
                long? value1 = default;
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
                            value1 = reader.IsDBNull(columnOffset) ? (long?)null : reader.GetInt64(columnOffset);
                            break;
                        case 3:
                            value1 = reader.IsDBNull(columnOffset) ? (long?)null : GetValue<long>(reader, columnOffset);
                            break;

                    }
                    columnOffset++;

                }
                return new global::RunningRow(value0, value1);
            }
        }

        private sealed class RowFactory9 : global::Dapper.RowFactory<global::DetailRow>
        {
            internal static readonly RowFactory9 Instance = new();
            private RowFactory9() {}
            public override object? Tokenize(global::System.Data.Common.DbDataReader reader, global::System.Span<int> tokens, int columnOffset)
            {
                for (int i = 0; i < tokens.Length; i++)
                {
                    int token = -1;
                    var name = reader.GetName(columnOffset);
                    var type = reader.GetFieldType(columnOffset);
                    switch (NormalizedHash(name))
                    {
                        case 4146583578U when NormalizedEquals(name, "orderid"):
                            token = type == typeof(long) ? 0 : 4; // two tokens for right-typed and type-flexible
                            break;
                        case 2369371622U when NormalizedEquals(name, "name"):
                            token = type == typeof(string) ? 1 : 5;
                            break;
                        case 3846717740U when NormalizedEquals(name, "product"):
                            token = type == typeof(string) ? 2 : 6;
                            break;
                        case 1265799128U when NormalizedEquals(name, "quantity"):
                            token = type == typeof(long) ? 3 : 7;
                            break;

                    }
                    tokens[i] = token;
                    columnOffset++;

                }
                return null;
            }
            public override global::DetailRow Read(global::System.Data.Common.DbDataReader reader, global::System.ReadOnlySpan<int> tokens, int columnOffset, object? state)
            {
                long value0 = default;
                string value1 = default!;
                string value2 = default!;
                long value3 = default;
                foreach (var token in tokens)
                {
                    switch (token)
                    {
                        case 0:
                            value0 = reader.GetInt64(columnOffset);
                            break;
                        case 4:
                            value0 = GetValue<long>(reader, columnOffset);
                            break;
                        case 1:
                            value1 = reader.GetString(columnOffset);
                            break;
                        case 5:
                            value1 = GetValue<string>(reader, columnOffset);
                            break;
                        case 2:
                            value2 = reader.GetString(columnOffset);
                            break;
                        case 6:
                            value2 = GetValue<string>(reader, columnOffset);
                            break;
                        case 3:
                            value3 = reader.GetInt64(columnOffset);
                            break;
                        case 7:
                            value3 = GetValue<long>(reader, columnOffset);
                            break;

                    }
                    columnOffset++;

                }
                return new global::DetailRow(value0, value1, value2, value3);
            }
        }

        private sealed class RowFactory10 : global::Dapper.RowFactory<global::IndexedLine>
        {
            internal static readonly RowFactory10 Instance = new();
            private RowFactory10() {}
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
                            token = type == typeof(long) ? 0 : 6; // two tokens for right-typed and type-flexible
                            break;
                        case 1725646016U when NormalizedEquals(name, "tenantid"):
                            token = type == typeof(long) ? 1 : 7;
                            break;
                        case 4146583578U when NormalizedEquals(name, "orderid"):
                            token = type == typeof(long) ? 2 : 8;
                            break;
                        case 3846717740U when NormalizedEquals(name, "product"):
                            token = type == typeof(string) ? 3 : 9;
                            break;
                        case 1265799128U when NormalizedEquals(name, "quantity"):
                            token = type == typeof(long) ? 4 : 10;
                            break;
                        case 408316356U when NormalizedEquals(name, "kordaparentindex"):
                            token = type == typeof(int) ? 5 : 11;
                            break;

                    }
                    tokens[i] = token;
                    columnOffset++;

                }
                return null;
            }
            public override global::IndexedLine Read(global::System.Data.Common.DbDataReader reader, global::System.ReadOnlySpan<int> tokens, int columnOffset, object? state)
            {
                long value0 = default;
                long value1 = default;
                long value2 = default;
                string value3 = default!;
                long value4 = default;
                int value5 = default;
                foreach (var token in tokens)
                {
                    switch (token)
                    {
                        case 0:
                            value0 = reader.GetInt64(columnOffset);
                            break;
                        case 6:
                            value0 = GetValue<long>(reader, columnOffset);
                            break;
                        case 1:
                            value1 = reader.GetInt64(columnOffset);
                            break;
                        case 7:
                            value1 = GetValue<long>(reader, columnOffset);
                            break;
                        case 2:
                            value2 = reader.GetInt64(columnOffset);
                            break;
                        case 8:
                            value2 = GetValue<long>(reader, columnOffset);
                            break;
                        case 3:
                            value3 = reader.GetString(columnOffset);
                            break;
                        case 9:
                            value3 = GetValue<string>(reader, columnOffset);
                            break;
                        case 4:
                            value4 = reader.GetInt64(columnOffset);
                            break;
                        case 10:
                            value4 = GetValue<long>(reader, columnOffset);
                            break;
                        case 5:
                            value5 = reader.GetInt32(columnOffset);
                            break;
                        case 11:
                            value5 = GetValue<int>(reader, columnOffset);
                            break;

                    }
                    columnOffset++;

                }
                return new global::IndexedLine(value0, value1, value2, value3, value4, value5);
            }
        }

        private abstract class CommandFactory0 : global::Dapper.CommandFactory<global::Workload.Parameters>
        {
            // these represent different call-sites (and most likely all have different SQL etc)
            internal static readonly CommandFactory0.Cached0 Instance0 = new();
            internal static readonly CommandFactory0.Cached1 Instance1 = new();
            internal static readonly CommandFactory0.Cached2 Instance2 = new();
            internal static readonly CommandFactory0.Cached3 Instance3 = new();
            internal static readonly CommandFactory0.Cached4 Instance4 = new();
            internal static readonly CommandFactory0.Cached5 Instance5 = new();
            internal static readonly CommandFactory0.Cached6 Instance6 = new();
            internal static readonly CommandFactory0.Cached7 Instance7 = new();
            internal static readonly CommandFactory0.Cached8 Instance8 = new();
            internal static readonly CommandFactory0.Cached9 Instance9 = new();
            internal static readonly CommandFactory0.Cached10 Instance10 = new();
            internal static readonly CommandFactory0.Cached11 Instance11 = new();
            internal static readonly CommandFactory0.Cached12 Instance12 = new();
            internal static readonly CommandFactory0.Cached13 Instance13 = new();
            internal static readonly CommandFactory0.Cached14 Instance14 = new();
            internal static readonly CommandFactory0.Cached15 Instance15 = new();

            public override void AddParameters(in global::Dapper.UnifiedCommand cmd, global::Workload.Parameters args)
            {
                var ps = cmd.Parameters;
                global::System.Data.Common.DbParameter p;
                p = cmd.CreateParameter();
                p.ParameterName = "p1";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.p1);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "p2";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.p2);
                ps.Add(p);

            }
            public override void UpdateParameters(in global::Dapper.UnifiedCommand cmd, global::Workload.Parameters args)
            {
                var ps = cmd.Parameters;
                ps[0].Value = AsValue(args.p1);
                ps[1].Value = AsValue(args.p2);

            }
            public override bool CanPrepare => true;

            public override global::System.Data.Common.DbCommand GetCommand(global::System.Data.Common.DbConnection connection,
                string sql, global::System.Data.CommandType commandType, global::Workload.Parameters args)
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
            internal sealed class Cached2 : CommandFactory0
            {
                protected override ref global::System.Data.Common.DbCommand? Storage => ref s_Storage;
                [global::System.ThreadStatic] // note this works correctly with ref-return
                private static global::System.Data.Common.DbCommand? s_Storage;

            }
            internal sealed class Cached3 : CommandFactory0
            {
                protected override ref global::System.Data.Common.DbCommand? Storage => ref s_Storage;
                [global::System.ThreadStatic] // note this works correctly with ref-return
                private static global::System.Data.Common.DbCommand? s_Storage;

            }
            internal sealed class Cached4 : CommandFactory0
            {
                protected override ref global::System.Data.Common.DbCommand? Storage => ref s_Storage;
                [global::System.ThreadStatic] // note this works correctly with ref-return
                private static global::System.Data.Common.DbCommand? s_Storage;

            }
            internal sealed class Cached5 : CommandFactory0
            {
                protected override ref global::System.Data.Common.DbCommand? Storage => ref s_Storage;
                [global::System.ThreadStatic] // note this works correctly with ref-return
                private static global::System.Data.Common.DbCommand? s_Storage;

            }
            internal sealed class Cached6 : CommandFactory0
            {
                protected override ref global::System.Data.Common.DbCommand? Storage => ref s_Storage;
                [global::System.ThreadStatic] // note this works correctly with ref-return
                private static global::System.Data.Common.DbCommand? s_Storage;

            }
            internal sealed class Cached7 : CommandFactory0
            {
                protected override ref global::System.Data.Common.DbCommand? Storage => ref s_Storage;
                [global::System.ThreadStatic] // note this works correctly with ref-return
                private static global::System.Data.Common.DbCommand? s_Storage;

            }
            internal sealed class Cached8 : CommandFactory0
            {
                protected override ref global::System.Data.Common.DbCommand? Storage => ref s_Storage;
                [global::System.ThreadStatic] // note this works correctly with ref-return
                private static global::System.Data.Common.DbCommand? s_Storage;

            }
            internal sealed class Cached9 : CommandFactory0
            {
                protected override ref global::System.Data.Common.DbCommand? Storage => ref s_Storage;
                [global::System.ThreadStatic] // note this works correctly with ref-return
                private static global::System.Data.Common.DbCommand? s_Storage;

            }
            internal sealed class Cached10 : CommandFactory0
            {
                protected override ref global::System.Data.Common.DbCommand? Storage => ref s_Storage;
                [global::System.ThreadStatic] // note this works correctly with ref-return
                private static global::System.Data.Common.DbCommand? s_Storage;

            }
            internal sealed class Cached11 : CommandFactory0
            {
                protected override ref global::System.Data.Common.DbCommand? Storage => ref s_Storage;
                [global::System.ThreadStatic] // note this works correctly with ref-return
                private static global::System.Data.Common.DbCommand? s_Storage;

            }
            internal sealed class Cached12 : CommandFactory0
            {
                protected override ref global::System.Data.Common.DbCommand? Storage => ref s_Storage;
                [global::System.ThreadStatic] // note this works correctly with ref-return
                private static global::System.Data.Common.DbCommand? s_Storage;

            }
            internal sealed class Cached13 : CommandFactory0
            {
                protected override ref global::System.Data.Common.DbCommand? Storage => ref s_Storage;
                [global::System.ThreadStatic] // note this works correctly with ref-return
                private static global::System.Data.Common.DbCommand? s_Storage;

            }
            internal sealed class Cached14 : CommandFactory0
            {
                protected override ref global::System.Data.Common.DbCommand? Storage => ref s_Storage;
                [global::System.ThreadStatic] // note this works correctly with ref-return
                private static global::System.Data.Common.DbCommand? s_Storage;

            }
            internal sealed class Cached15 : CommandFactory0
            {
                protected override ref global::System.Data.Common.DbCommand? Storage => ref s_Storage;
                [global::System.ThreadStatic] // note this works correctly with ref-return
                private static global::System.Data.Common.DbCommand? s_Storage;

            }

        }

        private abstract class CommandFactory1 : global::Dapper.CommandFactory<global::Workload.Parameters>
        {
            // these represent different call-sites (and most likely all have different SQL etc)
            internal static readonly CommandFactory1.Cached0 Instance0 = new();
            internal static readonly CommandFactory1.Cached1 Instance1 = new();
            internal static readonly CommandFactory1.Cached2 Instance2 = new();
            internal static readonly CommandFactory1.Cached3 Instance3 = new();
            internal static readonly CommandFactory1.Cached4 Instance4 = new();

            public override void AddParameters(in global::Dapper.UnifiedCommand cmd, global::Workload.Parameters args)
            {
                var ps = cmd.Parameters;
                global::System.Data.Common.DbParameter p;
                p = cmd.CreateParameter();
                p.ParameterName = "p1";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.p1);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "p2";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.p2);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "p3";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.p3);
                ps.Add(p);

            }
            public override void UpdateParameters(in global::Dapper.UnifiedCommand cmd, global::Workload.Parameters args)
            {
                var ps = cmd.Parameters;
                ps[0].Value = AsValue(args.p1);
                ps[1].Value = AsValue(args.p2);
                ps[2].Value = AsValue(args.p3);

            }
            public override bool CanPrepare => true;

            public override global::System.Data.Common.DbCommand GetCommand(global::System.Data.Common.DbConnection connection,
                string sql, global::System.Data.CommandType commandType, global::Workload.Parameters args)
                 => TryReuseThreadStatic(ref Storage, sql, commandType, args, _cmdPool) ?? base.GetCommand(connection, sql, commandType, args);

            public override bool TryRecycle(global::System.Data.Common.DbCommand command) => TryRecycleThreadStatic(ref Storage, command, _cmdPool);
            private readonly DbCommandCache _cmdPool = new(); // note: per cache instance
            protected abstract ref global::System.Data.Common.DbCommand? Storage {get;}

            internal sealed class Cached0 : CommandFactory1
            {
                protected override ref global::System.Data.Common.DbCommand? Storage => ref s_Storage;
                [global::System.ThreadStatic] // note this works correctly with ref-return
                private static global::System.Data.Common.DbCommand? s_Storage;

            }
            internal sealed class Cached1 : CommandFactory1
            {
                protected override ref global::System.Data.Common.DbCommand? Storage => ref s_Storage;
                [global::System.ThreadStatic] // note this works correctly with ref-return
                private static global::System.Data.Common.DbCommand? s_Storage;

            }
            internal sealed class Cached2 : CommandFactory1
            {
                protected override ref global::System.Data.Common.DbCommand? Storage => ref s_Storage;
                [global::System.ThreadStatic] // note this works correctly with ref-return
                private static global::System.Data.Common.DbCommand? s_Storage;

            }
            internal sealed class Cached3 : CommandFactory1
            {
                protected override ref global::System.Data.Common.DbCommand? Storage => ref s_Storage;
                [global::System.ThreadStatic] // note this works correctly with ref-return
                private static global::System.Data.Common.DbCommand? s_Storage;

            }
            internal sealed class Cached4 : CommandFactory1
            {
                protected override ref global::System.Data.Common.DbCommand? Storage => ref s_Storage;
                [global::System.ThreadStatic] // note this works correctly with ref-return
                private static global::System.Data.Common.DbCommand? s_Storage;

            }

        }

        private abstract class CommandFactory2 : global::Dapper.CommandFactory<global::Workload.Parameters>
        {
            // these represent different call-sites (and most likely all have different SQL etc)
            internal static readonly CommandFactory2.Cached0 Instance0 = new();
            internal static readonly CommandFactory2.Cached1 Instance1 = new();

            public override void AddParameters(in global::Dapper.UnifiedCommand cmd, global::Workload.Parameters args)
            {
                var ps = cmd.Parameters;
                global::System.Data.Common.DbParameter p;
                p = cmd.CreateParameter();
                p.ParameterName = "p1";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.p1);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "p2";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.p2);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "p3";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.p3);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "p4";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.p4);
                ps.Add(p);

            }
            public override void UpdateParameters(in global::Dapper.UnifiedCommand cmd, global::Workload.Parameters args)
            {
                var ps = cmd.Parameters;
                ps[0].Value = AsValue(args.p1);
                ps[1].Value = AsValue(args.p2);
                ps[2].Value = AsValue(args.p3);
                ps[3].Value = AsValue(args.p4);

            }
            public override bool CanPrepare => true;

            public override global::System.Data.Common.DbCommand GetCommand(global::System.Data.Common.DbConnection connection,
                string sql, global::System.Data.CommandType commandType, global::Workload.Parameters args)
                 => TryReuseThreadStatic(ref Storage, sql, commandType, args, _cmdPool) ?? base.GetCommand(connection, sql, commandType, args);

            public override bool TryRecycle(global::System.Data.Common.DbCommand command) => TryRecycleThreadStatic(ref Storage, command, _cmdPool);
            private readonly DbCommandCache _cmdPool = new(); // note: per cache instance
            protected abstract ref global::System.Data.Common.DbCommand? Storage {get;}

            internal sealed class Cached0 : CommandFactory2
            {
                protected override ref global::System.Data.Common.DbCommand? Storage => ref s_Storage;
                [global::System.ThreadStatic] // note this works correctly with ref-return
                private static global::System.Data.Common.DbCommand? s_Storage;

            }
            internal sealed class Cached1 : CommandFactory2
            {
                protected override ref global::System.Data.Common.DbCommand? Storage => ref s_Storage;
                [global::System.ThreadStatic] // note this works correctly with ref-return
                private static global::System.Data.Common.DbCommand? s_Storage;

            }

        }

        private sealed class CommandFactory3 : global::Dapper.CommandFactory<global::Workload.Parameters>
        {
            internal static readonly CommandFactory3 Instance0 = new();
            public override void AddParameters(in global::Dapper.UnifiedCommand cmd, global::Workload.Parameters args)
            {
                var ps = cmd.Parameters;
                global::System.Data.Common.DbParameter p;
                p = cmd.CreateParameter();
                p.ParameterName = "p1";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.p1);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "p3";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.p3);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "pattern";
                p.DbType = global::System.Data.DbType.String;
                p.Direction = global::System.Data.ParameterDirection.Input;
                SetValueWithDefaultSize(p, args.pattern);
                ps.Add(p);

            }
            public override void UpdateParameters(in global::Dapper.UnifiedCommand cmd, global::Workload.Parameters args)
            {
                var ps = cmd.Parameters;
                ps[0].Value = AsValue(args.p1);
                ps[1].Value = AsValue(args.p3);
                ps[2].Value = AsValue(args.pattern);

            }
            public override bool CanPrepare => true;

            public override global::System.Data.Common.DbCommand GetCommand(global::System.Data.Common.DbConnection connection,
                string sql, global::System.Data.CommandType commandType, global::Workload.Parameters args)
                 => TryReuseThreadStatic(ref Storage, sql, commandType, args, _cmdPool) ?? base.GetCommand(connection, sql, commandType, args);

            public override bool TryRecycle(global::System.Data.Common.DbCommand command) => TryRecycleThreadStatic(ref Storage, command, _cmdPool);
            private static readonly DbCommandCache _cmdPool = new();
            [global::System.ThreadStatic] // note this works correctly with ref
            private static global::System.Data.Common.DbCommand? Storage;

        }

        private sealed class CommandFactory4 : global::Dapper.CommandFactory<global::Workload.Parameters>
        {
            internal static readonly CommandFactory4 Instance0 = new();
            public override void AddParameters(in global::Dapper.UnifiedCommand cmd, global::Workload.Parameters args)
            {
                var ps = cmd.Parameters;
                global::System.Data.Common.DbParameter p;
                p = cmd.CreateParameter();
                p.ParameterName = "p1";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.p1);
                ps.Add(p);

            }
            public override void UpdateParameters(in global::Dapper.UnifiedCommand cmd, global::Workload.Parameters args)
            {
                var ps = cmd.Parameters;
                ps[0].Value = AsValue(args.p1);

            }
            public override bool CanPrepare => true;

            public override global::System.Data.Common.DbCommand GetCommand(global::System.Data.Common.DbConnection connection,
                string sql, global::System.Data.CommandType commandType, global::Workload.Parameters args)
                 => TryReuseThreadStatic(ref Storage, sql, commandType, args, _cmdPool) ?? base.GetCommand(connection, sql, commandType, args);

            public override bool TryRecycle(global::System.Data.Common.DbCommand command) => TryRecycleThreadStatic(ref Storage, command, _cmdPool);
            private static readonly DbCommandCache _cmdPool = new();
            [global::System.ThreadStatic] // note this works correctly with ref
            private static global::System.Data.Common.DbCommand? Storage;

        }

        private sealed class CommandFactory5 : global::Dapper.CommandFactory<global::Workload.Parameters>
        {
            internal static readonly CommandFactory5 Instance0 = new();
            public override void AddParameters(in global::Dapper.UnifiedCommand cmd, global::Workload.Parameters args)
            {
                var ps = cmd.Parameters;
                global::System.Data.Common.DbParameter p;
                p = cmd.CreateParameter();
                p.ParameterName = "p1";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.p1);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "p2";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.p2);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "p3";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.p3);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "p4";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.p4);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "p5";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.p5);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "p6";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.p6);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "p7";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.p7);
                ps.Add(p);

            }
            public override void UpdateParameters(in global::Dapper.UnifiedCommand cmd, global::Workload.Parameters args)
            {
                var ps = cmd.Parameters;
                ps[0].Value = AsValue(args.p1);
                ps[1].Value = AsValue(args.p2);
                ps[2].Value = AsValue(args.p3);
                ps[3].Value = AsValue(args.p4);
                ps[4].Value = AsValue(args.p5);
                ps[5].Value = AsValue(args.p6);
                ps[6].Value = AsValue(args.p7);

            }
            public override bool CanPrepare => true;

            public override global::System.Data.Common.DbCommand GetCommand(global::System.Data.Common.DbConnection connection,
                string sql, global::System.Data.CommandType commandType, global::Workload.Parameters args)
                 => TryReuseThreadStatic(ref Storage, sql, commandType, args, _cmdPool) ?? base.GetCommand(connection, sql, commandType, args);

            public override bool TryRecycle(global::System.Data.Common.DbCommand command) => TryRecycleThreadStatic(ref Storage, command, _cmdPool);
            private static readonly DbCommandCache _cmdPool = new();
            [global::System.ThreadStatic] // note this works correctly with ref
            private static global::System.Data.Common.DbCommand? Storage;

        }

        private abstract class CommandFactory6 : global::Dapper.CommandFactory<global::Workload.Parameters>
        {
            // these represent different call-sites (and most likely all have different SQL etc)
            internal static readonly CommandFactory6.Cached0 Instance0 = new();
            internal static readonly CommandFactory6.Cached1 Instance1 = new();
            internal static readonly CommandFactory6.Cached2 Instance2 = new();
            internal static readonly CommandFactory6.Cached3 Instance3 = new();

            public override void AddParameters(in global::Dapper.UnifiedCommand cmd, global::Workload.Parameters args)
            {
                var ps = cmd.Parameters;
                global::System.Data.Common.DbParameter p;
                p = cmd.CreateParameter();
                p.ParameterName = "p1";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.p1);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "p2";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.p2);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "p3";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.p3);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "p4";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.p4);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "p5";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.p5);
                ps.Add(p);

            }
            public override void UpdateParameters(in global::Dapper.UnifiedCommand cmd, global::Workload.Parameters args)
            {
                var ps = cmd.Parameters;
                ps[0].Value = AsValue(args.p1);
                ps[1].Value = AsValue(args.p2);
                ps[2].Value = AsValue(args.p3);
                ps[3].Value = AsValue(args.p4);
                ps[4].Value = AsValue(args.p5);

            }
            public override bool CanPrepare => true;

            public override global::System.Data.Common.DbCommand GetCommand(global::System.Data.Common.DbConnection connection,
                string sql, global::System.Data.CommandType commandType, global::Workload.Parameters args)
                 => TryReuseThreadStatic(ref Storage, sql, commandType, args, _cmdPool) ?? base.GetCommand(connection, sql, commandType, args);

            public override bool TryRecycle(global::System.Data.Common.DbCommand command) => TryRecycleThreadStatic(ref Storage, command, _cmdPool);
            private readonly DbCommandCache _cmdPool = new(); // note: per cache instance
            protected abstract ref global::System.Data.Common.DbCommand? Storage {get;}

            internal sealed class Cached0 : CommandFactory6
            {
                protected override ref global::System.Data.Common.DbCommand? Storage => ref s_Storage;
                [global::System.ThreadStatic] // note this works correctly with ref-return
                private static global::System.Data.Common.DbCommand? s_Storage;

            }
            internal sealed class Cached1 : CommandFactory6
            {
                protected override ref global::System.Data.Common.DbCommand? Storage => ref s_Storage;
                [global::System.ThreadStatic] // note this works correctly with ref-return
                private static global::System.Data.Common.DbCommand? s_Storage;

            }
            internal sealed class Cached2 : CommandFactory6
            {
                protected override ref global::System.Data.Common.DbCommand? Storage => ref s_Storage;
                [global::System.ThreadStatic] // note this works correctly with ref-return
                private static global::System.Data.Common.DbCommand? s_Storage;

            }
            internal sealed class Cached3 : CommandFactory6
            {
                protected override ref global::System.Data.Common.DbCommand? Storage => ref s_Storage;
                [global::System.ThreadStatic] // note this works correctly with ref-return
                private static global::System.Data.Common.DbCommand? s_Storage;

            }

        }

        private sealed class CommandFactory7 : global::Dapper.CommandFactory<global::Workload.Parameters>
        {
            internal static readonly CommandFactory7 Instance = new();
            public override void AddParameters(in global::Dapper.UnifiedCommand cmd, global::Workload.Parameters args)
            {
                var ps = cmd.Parameters;
                global::System.Data.Common.DbParameter p;
                var sql = cmd.CommandText;
                var commandType = cmd.CommandType;
                if (Include(sql, commandType, "p1"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "p1";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.p1);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "p2"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "p2";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.p2);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "p3"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "p3";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.p3);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "p4"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "p4";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.p4);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "p5"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "p5";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.p5);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "p6"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "p6";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.p6);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "p7"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "p7";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.p7);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "pattern"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "pattern";
                    p.DbType = global::System.Data.DbType.String;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    SetValueWithDefaultSize(p, args.pattern);
                    ps.Add(p);

                }

            }
            public override void UpdateParameters(in global::Dapper.UnifiedCommand cmd, global::Workload.Parameters args)
            {
                var ps = cmd.Parameters;
                var sql = cmd.CommandText;
                var commandType = cmd.CommandType;
                if (Include(sql, commandType, "p1"))
                {
                    ps["p1"].Value = AsValue(args.p1);

                }
                if (Include(sql, commandType, "p2"))
                {
                    ps["p2"].Value = AsValue(args.p2);

                }
                if (Include(sql, commandType, "p3"))
                {
                    ps["p3"].Value = AsValue(args.p3);

                }
                if (Include(sql, commandType, "p4"))
                {
                    ps["p4"].Value = AsValue(args.p4);

                }
                if (Include(sql, commandType, "p5"))
                {
                    ps["p5"].Value = AsValue(args.p5);

                }
                if (Include(sql, commandType, "p6"))
                {
                    ps["p6"].Value = AsValue(args.p6);

                }
                if (Include(sql, commandType, "p7"))
                {
                    ps["p7"].Value = AsValue(args.p7);

                }
                if (Include(sql, commandType, "pattern"))
                {
                    ps["pattern"].Value = AsValue(args.pattern);

                }

            }
            public override bool CanPrepare => true;

        }

        private sealed class CommandFactory8 : global::Dapper.CommandFactory<global::Workload.RelatedParameters>
        {
            internal static readonly CommandFactory8 Instance0 = new();
            public override void AddParameters(in global::Dapper.UnifiedCommand cmd, global::Workload.RelatedParameters args)
            {
                var ps = cmd.Parameters;
                global::System.Data.Common.DbParameter p;
                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_0";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_0);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_0";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_0);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_0";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_0);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_1";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_1);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_1";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_1);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_1";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_1);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_2";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_2);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_2";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_2);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_2";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_2);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_3";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_3);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_3";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_3);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_3";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_3);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_4";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_4);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_4";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_4);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_4";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_4);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_5";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_5);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_5";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_5);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_5";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_5);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_6";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_6);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_6";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_6);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_6";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_6);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_7";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_7);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_7";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_7);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_7";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_7);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_8";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_8);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_8";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_8);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_8";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_8);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_9";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_9);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_9";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_9);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_9";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_9);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_10";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_10);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_10";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_10);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_10";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_10);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_11";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_11);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_11";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_11);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_11";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_11);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_12";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_12);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_12";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_12);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_12";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_12);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_13";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_13);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_13";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_13);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_13";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_13);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_14";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_14);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_14";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_14);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_14";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_14);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_15";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_15);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_15";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_15);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_15";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_15);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_16";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_16);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_16";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_16);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_16";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_16);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_17";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_17);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_17";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_17);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_17";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_17);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_18";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_18);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_18";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_18);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_18";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_18);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_19";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_19);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_19";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_19);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_19";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_19);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_20";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_20);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_20";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_20);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_20";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_20);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_21";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_21);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_21";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_21);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_21";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_21);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_22";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_22);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_22";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_22);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_22";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_22);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_23";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_23);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_23";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_23);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_23";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_23);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_24";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_24);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_24";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_24);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_24";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_24);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_25";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_25);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_25";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_25);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_25";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_25);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_26";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_26);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_26";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_26);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_26";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_26);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_27";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_27);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_27";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_27);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_27";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_27);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_28";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_28);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_28";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_28);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_28";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_28);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_29";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_29);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_29";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_29);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_29";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_29);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_30";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_30);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_30";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_30);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_30";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_30);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_index_31";
                p.DbType = global::System.Data.DbType.Int32;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_index_31);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "tenant_31";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.tenant_31);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "parent_id_31";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(args.parent_id_31);
                ps.Add(p);

            }
            public override void UpdateParameters(in global::Dapper.UnifiedCommand cmd, global::Workload.RelatedParameters args)
            {
                var ps = cmd.Parameters;
                ps[0].Value = AsValue(args.parent_index_0);
                ps[1].Value = AsValue(args.tenant_0);
                ps[2].Value = AsValue(args.parent_id_0);
                ps[3].Value = AsValue(args.parent_index_1);
                ps[4].Value = AsValue(args.tenant_1);
                ps[5].Value = AsValue(args.parent_id_1);
                ps[6].Value = AsValue(args.parent_index_2);
                ps[7].Value = AsValue(args.tenant_2);
                ps[8].Value = AsValue(args.parent_id_2);
                ps[9].Value = AsValue(args.parent_index_3);
                ps[10].Value = AsValue(args.tenant_3);
                ps[11].Value = AsValue(args.parent_id_3);
                ps[12].Value = AsValue(args.parent_index_4);
                ps[13].Value = AsValue(args.tenant_4);
                ps[14].Value = AsValue(args.parent_id_4);
                ps[15].Value = AsValue(args.parent_index_5);
                ps[16].Value = AsValue(args.tenant_5);
                ps[17].Value = AsValue(args.parent_id_5);
                ps[18].Value = AsValue(args.parent_index_6);
                ps[19].Value = AsValue(args.tenant_6);
                ps[20].Value = AsValue(args.parent_id_6);
                ps[21].Value = AsValue(args.parent_index_7);
                ps[22].Value = AsValue(args.tenant_7);
                ps[23].Value = AsValue(args.parent_id_7);
                ps[24].Value = AsValue(args.parent_index_8);
                ps[25].Value = AsValue(args.tenant_8);
                ps[26].Value = AsValue(args.parent_id_8);
                ps[27].Value = AsValue(args.parent_index_9);
                ps[28].Value = AsValue(args.tenant_9);
                ps[29].Value = AsValue(args.parent_id_9);
                ps[30].Value = AsValue(args.parent_index_10);
                ps[31].Value = AsValue(args.tenant_10);
                ps[32].Value = AsValue(args.parent_id_10);
                ps[33].Value = AsValue(args.parent_index_11);
                ps[34].Value = AsValue(args.tenant_11);
                ps[35].Value = AsValue(args.parent_id_11);
                ps[36].Value = AsValue(args.parent_index_12);
                ps[37].Value = AsValue(args.tenant_12);
                ps[38].Value = AsValue(args.parent_id_12);
                ps[39].Value = AsValue(args.parent_index_13);
                ps[40].Value = AsValue(args.tenant_13);
                ps[41].Value = AsValue(args.parent_id_13);
                ps[42].Value = AsValue(args.parent_index_14);
                ps[43].Value = AsValue(args.tenant_14);
                ps[44].Value = AsValue(args.parent_id_14);
                ps[45].Value = AsValue(args.parent_index_15);
                ps[46].Value = AsValue(args.tenant_15);
                ps[47].Value = AsValue(args.parent_id_15);
                ps[48].Value = AsValue(args.parent_index_16);
                ps[49].Value = AsValue(args.tenant_16);
                ps[50].Value = AsValue(args.parent_id_16);
                ps[51].Value = AsValue(args.parent_index_17);
                ps[52].Value = AsValue(args.tenant_17);
                ps[53].Value = AsValue(args.parent_id_17);
                ps[54].Value = AsValue(args.parent_index_18);
                ps[55].Value = AsValue(args.tenant_18);
                ps[56].Value = AsValue(args.parent_id_18);
                ps[57].Value = AsValue(args.parent_index_19);
                ps[58].Value = AsValue(args.tenant_19);
                ps[59].Value = AsValue(args.parent_id_19);
                ps[60].Value = AsValue(args.parent_index_20);
                ps[61].Value = AsValue(args.tenant_20);
                ps[62].Value = AsValue(args.parent_id_20);
                ps[63].Value = AsValue(args.parent_index_21);
                ps[64].Value = AsValue(args.tenant_21);
                ps[65].Value = AsValue(args.parent_id_21);
                ps[66].Value = AsValue(args.parent_index_22);
                ps[67].Value = AsValue(args.tenant_22);
                ps[68].Value = AsValue(args.parent_id_22);
                ps[69].Value = AsValue(args.parent_index_23);
                ps[70].Value = AsValue(args.tenant_23);
                ps[71].Value = AsValue(args.parent_id_23);
                ps[72].Value = AsValue(args.parent_index_24);
                ps[73].Value = AsValue(args.tenant_24);
                ps[74].Value = AsValue(args.parent_id_24);
                ps[75].Value = AsValue(args.parent_index_25);
                ps[76].Value = AsValue(args.tenant_25);
                ps[77].Value = AsValue(args.parent_id_25);
                ps[78].Value = AsValue(args.parent_index_26);
                ps[79].Value = AsValue(args.tenant_26);
                ps[80].Value = AsValue(args.parent_id_26);
                ps[81].Value = AsValue(args.parent_index_27);
                ps[82].Value = AsValue(args.tenant_27);
                ps[83].Value = AsValue(args.parent_id_27);
                ps[84].Value = AsValue(args.parent_index_28);
                ps[85].Value = AsValue(args.tenant_28);
                ps[86].Value = AsValue(args.parent_id_28);
                ps[87].Value = AsValue(args.parent_index_29);
                ps[88].Value = AsValue(args.tenant_29);
                ps[89].Value = AsValue(args.parent_id_29);
                ps[90].Value = AsValue(args.parent_index_30);
                ps[91].Value = AsValue(args.tenant_30);
                ps[92].Value = AsValue(args.parent_id_30);
                ps[93].Value = AsValue(args.parent_index_31);
                ps[94].Value = AsValue(args.tenant_31);
                ps[95].Value = AsValue(args.parent_id_31);

            }
            public override bool CanPrepare => true;

            public override global::System.Data.Common.DbCommand GetCommand(global::System.Data.Common.DbConnection connection,
                string sql, global::System.Data.CommandType commandType, global::Workload.RelatedParameters args)
                 => TryReuseThreadStatic(ref Storage, sql, commandType, args, _cmdPool) ?? base.GetCommand(connection, sql, commandType, args);

            public override bool TryRecycle(global::System.Data.Common.DbCommand command) => TryRecycleThreadStatic(ref Storage, command, _cmdPool);
            private static readonly DbCommandCache _cmdPool = new();
            [global::System.ThreadStatic] // note this works correctly with ref
            private static global::System.Data.Common.DbCommand? Storage;

        }

        private sealed class CommandFactory9 : global::Dapper.CommandFactory<global::Workload.RelatedParameters>
        {
            internal static readonly CommandFactory9 Instance = new();
            public override void AddParameters(in global::Dapper.UnifiedCommand cmd, global::Workload.RelatedParameters args)
            {
                var ps = cmd.Parameters;
                global::System.Data.Common.DbParameter p;
                var sql = cmd.CommandText;
                var commandType = cmd.CommandType;
                if (Include(sql, commandType, "parent_index_0"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_0";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_0);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_0"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_0";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_0);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_0"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_0";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_0);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_1"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_1";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_1);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_1"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_1";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_1);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_1"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_1";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_1);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_2"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_2";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_2);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_2"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_2";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_2);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_2"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_2";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_2);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_3"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_3";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_3);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_3"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_3";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_3);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_3"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_3";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_3);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_4"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_4";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_4);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_4"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_4";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_4);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_4"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_4";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_4);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_5"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_5";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_5);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_5"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_5";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_5);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_5"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_5";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_5);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_6"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_6";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_6);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_6"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_6";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_6);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_6"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_6";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_6);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_7"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_7";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_7);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_7"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_7";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_7);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_7"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_7";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_7);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_8"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_8";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_8);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_8"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_8";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_8);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_8"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_8";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_8);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_9"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_9";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_9);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_9"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_9";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_9);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_9"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_9";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_9);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_10"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_10";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_10);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_10"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_10";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_10);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_10"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_10";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_10);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_11"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_11";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_11);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_11"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_11";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_11);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_11"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_11";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_11);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_12"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_12";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_12);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_12"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_12";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_12);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_12"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_12";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_12);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_13"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_13";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_13);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_13"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_13";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_13);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_13"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_13";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_13);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_14"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_14";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_14);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_14"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_14";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_14);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_14"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_14";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_14);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_15"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_15";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_15);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_15"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_15";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_15);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_15"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_15";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_15);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_16"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_16";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_16);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_16"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_16";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_16);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_16"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_16";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_16);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_17"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_17";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_17);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_17"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_17";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_17);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_17"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_17";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_17);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_18"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_18";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_18);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_18"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_18";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_18);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_18"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_18";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_18);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_19"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_19";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_19);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_19"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_19";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_19);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_19"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_19";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_19);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_20"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_20";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_20);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_20"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_20";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_20);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_20"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_20";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_20);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_21"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_21";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_21);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_21"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_21";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_21);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_21"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_21";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_21);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_22"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_22";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_22);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_22"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_22";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_22);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_22"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_22";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_22);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_23"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_23";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_23);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_23"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_23";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_23);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_23"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_23";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_23);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_24"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_24";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_24);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_24"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_24";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_24);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_24"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_24";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_24);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_25"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_25";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_25);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_25"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_25";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_25);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_25"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_25";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_25);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_26"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_26";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_26);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_26"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_26";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_26);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_26"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_26";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_26);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_27"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_27";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_27);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_27"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_27";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_27);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_27"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_27";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_27);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_28"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_28";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_28);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_28"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_28";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_28);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_28"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_28";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_28);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_29"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_29";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_29);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_29"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_29";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_29);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_29"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_29";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_29);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_30"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_30";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_30);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_30"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_30";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_30);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_30"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_30";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_30);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_index_31"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_index_31";
                    p.DbType = global::System.Data.DbType.Int32;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_index_31);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "tenant_31"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "tenant_31";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.tenant_31);
                    ps.Add(p);

                }

                if (Include(sql, commandType, "parent_id_31"))
                {
                    p = cmd.CreateParameter();
                    p.ParameterName = "parent_id_31";
                    p.DbType = global::System.Data.DbType.Int64;
                    p.Direction = global::System.Data.ParameterDirection.Input;
                    p.Value = AsValue(args.parent_id_31);
                    ps.Add(p);

                }

            }
            public override void UpdateParameters(in global::Dapper.UnifiedCommand cmd, global::Workload.RelatedParameters args)
            {
                var ps = cmd.Parameters;
                var sql = cmd.CommandText;
                var commandType = cmd.CommandType;
                if (Include(sql, commandType, "parent_index_0"))
                {
                    ps["parent_index_0"].Value = AsValue(args.parent_index_0);

                }
                if (Include(sql, commandType, "tenant_0"))
                {
                    ps["tenant_0"].Value = AsValue(args.tenant_0);

                }
                if (Include(sql, commandType, "parent_id_0"))
                {
                    ps["parent_id_0"].Value = AsValue(args.parent_id_0);

                }
                if (Include(sql, commandType, "parent_index_1"))
                {
                    ps["parent_index_1"].Value = AsValue(args.parent_index_1);

                }
                if (Include(sql, commandType, "tenant_1"))
                {
                    ps["tenant_1"].Value = AsValue(args.tenant_1);

                }
                if (Include(sql, commandType, "parent_id_1"))
                {
                    ps["parent_id_1"].Value = AsValue(args.parent_id_1);

                }
                if (Include(sql, commandType, "parent_index_2"))
                {
                    ps["parent_index_2"].Value = AsValue(args.parent_index_2);

                }
                if (Include(sql, commandType, "tenant_2"))
                {
                    ps["tenant_2"].Value = AsValue(args.tenant_2);

                }
                if (Include(sql, commandType, "parent_id_2"))
                {
                    ps["parent_id_2"].Value = AsValue(args.parent_id_2);

                }
                if (Include(sql, commandType, "parent_index_3"))
                {
                    ps["parent_index_3"].Value = AsValue(args.parent_index_3);

                }
                if (Include(sql, commandType, "tenant_3"))
                {
                    ps["tenant_3"].Value = AsValue(args.tenant_3);

                }
                if (Include(sql, commandType, "parent_id_3"))
                {
                    ps["parent_id_3"].Value = AsValue(args.parent_id_3);

                }
                if (Include(sql, commandType, "parent_index_4"))
                {
                    ps["parent_index_4"].Value = AsValue(args.parent_index_4);

                }
                if (Include(sql, commandType, "tenant_4"))
                {
                    ps["tenant_4"].Value = AsValue(args.tenant_4);

                }
                if (Include(sql, commandType, "parent_id_4"))
                {
                    ps["parent_id_4"].Value = AsValue(args.parent_id_4);

                }
                if (Include(sql, commandType, "parent_index_5"))
                {
                    ps["parent_index_5"].Value = AsValue(args.parent_index_5);

                }
                if (Include(sql, commandType, "tenant_5"))
                {
                    ps["tenant_5"].Value = AsValue(args.tenant_5);

                }
                if (Include(sql, commandType, "parent_id_5"))
                {
                    ps["parent_id_5"].Value = AsValue(args.parent_id_5);

                }
                if (Include(sql, commandType, "parent_index_6"))
                {
                    ps["parent_index_6"].Value = AsValue(args.parent_index_6);

                }
                if (Include(sql, commandType, "tenant_6"))
                {
                    ps["tenant_6"].Value = AsValue(args.tenant_6);

                }
                if (Include(sql, commandType, "parent_id_6"))
                {
                    ps["parent_id_6"].Value = AsValue(args.parent_id_6);

                }
                if (Include(sql, commandType, "parent_index_7"))
                {
                    ps["parent_index_7"].Value = AsValue(args.parent_index_7);

                }
                if (Include(sql, commandType, "tenant_7"))
                {
                    ps["tenant_7"].Value = AsValue(args.tenant_7);

                }
                if (Include(sql, commandType, "parent_id_7"))
                {
                    ps["parent_id_7"].Value = AsValue(args.parent_id_7);

                }
                if (Include(sql, commandType, "parent_index_8"))
                {
                    ps["parent_index_8"].Value = AsValue(args.parent_index_8);

                }
                if (Include(sql, commandType, "tenant_8"))
                {
                    ps["tenant_8"].Value = AsValue(args.tenant_8);

                }
                if (Include(sql, commandType, "parent_id_8"))
                {
                    ps["parent_id_8"].Value = AsValue(args.parent_id_8);

                }
                if (Include(sql, commandType, "parent_index_9"))
                {
                    ps["parent_index_9"].Value = AsValue(args.parent_index_9);

                }
                if (Include(sql, commandType, "tenant_9"))
                {
                    ps["tenant_9"].Value = AsValue(args.tenant_9);

                }
                if (Include(sql, commandType, "parent_id_9"))
                {
                    ps["parent_id_9"].Value = AsValue(args.parent_id_9);

                }
                if (Include(sql, commandType, "parent_index_10"))
                {
                    ps["parent_index_10"].Value = AsValue(args.parent_index_10);

                }
                if (Include(sql, commandType, "tenant_10"))
                {
                    ps["tenant_10"].Value = AsValue(args.tenant_10);

                }
                if (Include(sql, commandType, "parent_id_10"))
                {
                    ps["parent_id_10"].Value = AsValue(args.parent_id_10);

                }
                if (Include(sql, commandType, "parent_index_11"))
                {
                    ps["parent_index_11"].Value = AsValue(args.parent_index_11);

                }
                if (Include(sql, commandType, "tenant_11"))
                {
                    ps["tenant_11"].Value = AsValue(args.tenant_11);

                }
                if (Include(sql, commandType, "parent_id_11"))
                {
                    ps["parent_id_11"].Value = AsValue(args.parent_id_11);

                }
                if (Include(sql, commandType, "parent_index_12"))
                {
                    ps["parent_index_12"].Value = AsValue(args.parent_index_12);

                }
                if (Include(sql, commandType, "tenant_12"))
                {
                    ps["tenant_12"].Value = AsValue(args.tenant_12);

                }
                if (Include(sql, commandType, "parent_id_12"))
                {
                    ps["parent_id_12"].Value = AsValue(args.parent_id_12);

                }
                if (Include(sql, commandType, "parent_index_13"))
                {
                    ps["parent_index_13"].Value = AsValue(args.parent_index_13);

                }
                if (Include(sql, commandType, "tenant_13"))
                {
                    ps["tenant_13"].Value = AsValue(args.tenant_13);

                }
                if (Include(sql, commandType, "parent_id_13"))
                {
                    ps["parent_id_13"].Value = AsValue(args.parent_id_13);

                }
                if (Include(sql, commandType, "parent_index_14"))
                {
                    ps["parent_index_14"].Value = AsValue(args.parent_index_14);

                }
                if (Include(sql, commandType, "tenant_14"))
                {
                    ps["tenant_14"].Value = AsValue(args.tenant_14);

                }
                if (Include(sql, commandType, "parent_id_14"))
                {
                    ps["parent_id_14"].Value = AsValue(args.parent_id_14);

                }
                if (Include(sql, commandType, "parent_index_15"))
                {
                    ps["parent_index_15"].Value = AsValue(args.parent_index_15);

                }
                if (Include(sql, commandType, "tenant_15"))
                {
                    ps["tenant_15"].Value = AsValue(args.tenant_15);

                }
                if (Include(sql, commandType, "parent_id_15"))
                {
                    ps["parent_id_15"].Value = AsValue(args.parent_id_15);

                }
                if (Include(sql, commandType, "parent_index_16"))
                {
                    ps["parent_index_16"].Value = AsValue(args.parent_index_16);

                }
                if (Include(sql, commandType, "tenant_16"))
                {
                    ps["tenant_16"].Value = AsValue(args.tenant_16);

                }
                if (Include(sql, commandType, "parent_id_16"))
                {
                    ps["parent_id_16"].Value = AsValue(args.parent_id_16);

                }
                if (Include(sql, commandType, "parent_index_17"))
                {
                    ps["parent_index_17"].Value = AsValue(args.parent_index_17);

                }
                if (Include(sql, commandType, "tenant_17"))
                {
                    ps["tenant_17"].Value = AsValue(args.tenant_17);

                }
                if (Include(sql, commandType, "parent_id_17"))
                {
                    ps["parent_id_17"].Value = AsValue(args.parent_id_17);

                }
                if (Include(sql, commandType, "parent_index_18"))
                {
                    ps["parent_index_18"].Value = AsValue(args.parent_index_18);

                }
                if (Include(sql, commandType, "tenant_18"))
                {
                    ps["tenant_18"].Value = AsValue(args.tenant_18);

                }
                if (Include(sql, commandType, "parent_id_18"))
                {
                    ps["parent_id_18"].Value = AsValue(args.parent_id_18);

                }
                if (Include(sql, commandType, "parent_index_19"))
                {
                    ps["parent_index_19"].Value = AsValue(args.parent_index_19);

                }
                if (Include(sql, commandType, "tenant_19"))
                {
                    ps["tenant_19"].Value = AsValue(args.tenant_19);

                }
                if (Include(sql, commandType, "parent_id_19"))
                {
                    ps["parent_id_19"].Value = AsValue(args.parent_id_19);

                }
                if (Include(sql, commandType, "parent_index_20"))
                {
                    ps["parent_index_20"].Value = AsValue(args.parent_index_20);

                }
                if (Include(sql, commandType, "tenant_20"))
                {
                    ps["tenant_20"].Value = AsValue(args.tenant_20);

                }
                if (Include(sql, commandType, "parent_id_20"))
                {
                    ps["parent_id_20"].Value = AsValue(args.parent_id_20);

                }
                if (Include(sql, commandType, "parent_index_21"))
                {
                    ps["parent_index_21"].Value = AsValue(args.parent_index_21);

                }
                if (Include(sql, commandType, "tenant_21"))
                {
                    ps["tenant_21"].Value = AsValue(args.tenant_21);

                }
                if (Include(sql, commandType, "parent_id_21"))
                {
                    ps["parent_id_21"].Value = AsValue(args.parent_id_21);

                }
                if (Include(sql, commandType, "parent_index_22"))
                {
                    ps["parent_index_22"].Value = AsValue(args.parent_index_22);

                }
                if (Include(sql, commandType, "tenant_22"))
                {
                    ps["tenant_22"].Value = AsValue(args.tenant_22);

                }
                if (Include(sql, commandType, "parent_id_22"))
                {
                    ps["parent_id_22"].Value = AsValue(args.parent_id_22);

                }
                if (Include(sql, commandType, "parent_index_23"))
                {
                    ps["parent_index_23"].Value = AsValue(args.parent_index_23);

                }
                if (Include(sql, commandType, "tenant_23"))
                {
                    ps["tenant_23"].Value = AsValue(args.tenant_23);

                }
                if (Include(sql, commandType, "parent_id_23"))
                {
                    ps["parent_id_23"].Value = AsValue(args.parent_id_23);

                }
                if (Include(sql, commandType, "parent_index_24"))
                {
                    ps["parent_index_24"].Value = AsValue(args.parent_index_24);

                }
                if (Include(sql, commandType, "tenant_24"))
                {
                    ps["tenant_24"].Value = AsValue(args.tenant_24);

                }
                if (Include(sql, commandType, "parent_id_24"))
                {
                    ps["parent_id_24"].Value = AsValue(args.parent_id_24);

                }
                if (Include(sql, commandType, "parent_index_25"))
                {
                    ps["parent_index_25"].Value = AsValue(args.parent_index_25);

                }
                if (Include(sql, commandType, "tenant_25"))
                {
                    ps["tenant_25"].Value = AsValue(args.tenant_25);

                }
                if (Include(sql, commandType, "parent_id_25"))
                {
                    ps["parent_id_25"].Value = AsValue(args.parent_id_25);

                }
                if (Include(sql, commandType, "parent_index_26"))
                {
                    ps["parent_index_26"].Value = AsValue(args.parent_index_26);

                }
                if (Include(sql, commandType, "tenant_26"))
                {
                    ps["tenant_26"].Value = AsValue(args.tenant_26);

                }
                if (Include(sql, commandType, "parent_id_26"))
                {
                    ps["parent_id_26"].Value = AsValue(args.parent_id_26);

                }
                if (Include(sql, commandType, "parent_index_27"))
                {
                    ps["parent_index_27"].Value = AsValue(args.parent_index_27);

                }
                if (Include(sql, commandType, "tenant_27"))
                {
                    ps["tenant_27"].Value = AsValue(args.tenant_27);

                }
                if (Include(sql, commandType, "parent_id_27"))
                {
                    ps["parent_id_27"].Value = AsValue(args.parent_id_27);

                }
                if (Include(sql, commandType, "parent_index_28"))
                {
                    ps["parent_index_28"].Value = AsValue(args.parent_index_28);

                }
                if (Include(sql, commandType, "tenant_28"))
                {
                    ps["tenant_28"].Value = AsValue(args.tenant_28);

                }
                if (Include(sql, commandType, "parent_id_28"))
                {
                    ps["parent_id_28"].Value = AsValue(args.parent_id_28);

                }
                if (Include(sql, commandType, "parent_index_29"))
                {
                    ps["parent_index_29"].Value = AsValue(args.parent_index_29);

                }
                if (Include(sql, commandType, "tenant_29"))
                {
                    ps["tenant_29"].Value = AsValue(args.tenant_29);

                }
                if (Include(sql, commandType, "parent_id_29"))
                {
                    ps["parent_id_29"].Value = AsValue(args.parent_id_29);

                }
                if (Include(sql, commandType, "parent_index_30"))
                {
                    ps["parent_index_30"].Value = AsValue(args.parent_index_30);

                }
                if (Include(sql, commandType, "tenant_30"))
                {
                    ps["tenant_30"].Value = AsValue(args.tenant_30);

                }
                if (Include(sql, commandType, "parent_id_30"))
                {
                    ps["parent_id_30"].Value = AsValue(args.parent_id_30);

                }
                if (Include(sql, commandType, "parent_index_31"))
                {
                    ps["parent_index_31"].Value = AsValue(args.parent_index_31);

                }
                if (Include(sql, commandType, "tenant_31"))
                {
                    ps["tenant_31"].Value = AsValue(args.tenant_31);

                }
                if (Include(sql, commandType, "parent_id_31"))
                {
                    ps["parent_id_31"].Value = AsValue(args.parent_id_31);

                }

            }
            public override bool CanPrepare => true;

        }

        private sealed class CommandFactory10 : global::Dapper.CommandFactory<object?> // <anonymous type: long tenant, long id>
        {
            internal static readonly CommandFactory10 Instance = new();
            public override void AddParameters(in global::Dapper.UnifiedCommand cmd, object? args)
            {
                var typed = Cast(args, static () => new { tenant = default(long), id = default(long) }); // expected shape
                var ps = cmd.Parameters;
                global::System.Data.Common.DbParameter p;
                p = cmd.CreateParameter();
                p.ParameterName = "tenant";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.tenant);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "id";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.id);
                ps.Add(p);

            }
            public override void UpdateParameters(in global::Dapper.UnifiedCommand cmd, object? args)
            {
                var typed = Cast(args, static () => new { tenant = default(long), id = default(long) }); // expected shape
                var ps = cmd.Parameters;
                ps[0].Value = AsValue(typed.tenant);
                ps[1].Value = AsValue(typed.id);

            }
            public override bool CanPrepare => true;

        }

        private sealed class CommandFactory11 : global::Dapper.CommandFactory<object?> // <anonymous type: long tenant, long id, string? note, long version, long expected>
        {
            internal static readonly CommandFactory11 Instance = new();
            public override void AddParameters(in global::Dapper.UnifiedCommand cmd, object? args)
            {
                var typed = Cast(args, static () => new { tenant = default(long), id = default(long), note = default(string?), version = default(long), expected = default(long) }); // expected shape
                var ps = cmd.Parameters;
                global::System.Data.Common.DbParameter p;
                p = cmd.CreateParameter();
                p.ParameterName = "tenant";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.tenant);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "id";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.id);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "note";
                p.DbType = global::System.Data.DbType.String;
                p.Direction = global::System.Data.ParameterDirection.Input;
                SetValueWithDefaultSize(p, typed.note);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "version";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.version);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "expected";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.expected);
                ps.Add(p);

            }
            public override void UpdateParameters(in global::Dapper.UnifiedCommand cmd, object? args)
            {
                var typed = Cast(args, static () => new { tenant = default(long), id = default(long), note = default(string?), version = default(long), expected = default(long) }); // expected shape
                var ps = cmd.Parameters;
                ps[0].Value = AsValue(typed.tenant);
                ps[1].Value = AsValue(typed.id);
                ps[2].Value = AsValue(typed.note);
                ps[3].Value = AsValue(typed.version);
                ps[4].Value = AsValue(typed.expected);

            }
            public override bool CanPrepare => true;

        }

        private sealed class CommandFactory12 : global::Dapper.CommandFactory<object?> // <anonymous type: long tenant, long id, string? note, long version, long expected>
        {
            internal static readonly CommandFactory12 Instance = new();
            public override void AddParameters(in global::Dapper.UnifiedCommand cmd, object? args)
            {
                var typed = Cast(args, static () => new { tenant = default(long), id = default(long), note = default(string?), version = default(long), expected = default(long) }); // expected shape
                var ps = cmd.Parameters;
                global::System.Data.Common.DbParameter p;
                p = cmd.CreateParameter();
                p.ParameterName = "tenant";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.tenant);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "id";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.id);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "note";
                p.DbType = global::System.Data.DbType.String;
                p.Direction = global::System.Data.ParameterDirection.Input;
                SetValueWithDefaultSize(p, typed.note);
                ps.Add(p);

            }
            public override void UpdateParameters(in global::Dapper.UnifiedCommand cmd, object? args)
            {
                var typed = Cast(args, static () => new { tenant = default(long), id = default(long), note = default(string?), version = default(long), expected = default(long) }); // expected shape
                var ps = cmd.Parameters;
                ps[0].Value = AsValue(typed.tenant);
                ps[1].Value = AsValue(typed.id);
                ps[2].Value = AsValue(typed.note);

            }
            public override bool CanPrepare => true;

        }

        private sealed class CommandFactory13 : global::Dapper.CommandFactory<object?> // <anonymous type: long tenant, long id, string? note, long version, long expected>
        {
            internal static readonly CommandFactory13 Instance = new();
            public override void AddParameters(in global::Dapper.UnifiedCommand cmd, object? args)
            {
                var typed = Cast(args, static () => new { tenant = default(long), id = default(long), note = default(string?), version = default(long), expected = default(long) }); // expected shape
                var ps = cmd.Parameters;
                global::System.Data.Common.DbParameter p;
                p = cmd.CreateParameter();
                p.ParameterName = "tenant";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.tenant);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "id";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.id);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "note";
                p.DbType = global::System.Data.DbType.String;
                p.Direction = global::System.Data.ParameterDirection.Input;
                SetValueWithDefaultSize(p, typed.note);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "version";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.version);
                ps.Add(p);

            }
            public override void UpdateParameters(in global::Dapper.UnifiedCommand cmd, object? args)
            {
                var typed = Cast(args, static () => new { tenant = default(long), id = default(long), note = default(string?), version = default(long), expected = default(long) }); // expected shape
                var ps = cmd.Parameters;
                ps[0].Value = AsValue(typed.tenant);
                ps[1].Value = AsValue(typed.id);
                ps[2].Value = AsValue(typed.note);
                ps[3].Value = AsValue(typed.version);

            }
            public override bool CanPrepare => true;

        }

        private sealed class CommandFactory14 : global::Dapper.CommandFactory<object?> // <anonymous type: long tenant, long id, string note, long expected>
        {
            internal static readonly CommandFactory14 Instance = new();
            public override void AddParameters(in global::Dapper.UnifiedCommand cmd, object? args)
            {
                var typed = Cast(args, static () => new { tenant = default(long), id = default(long), note = default(string), expected = default(long) }); // expected shape
                var ps = cmd.Parameters;
                global::System.Data.Common.DbParameter p;
                p = cmd.CreateParameter();
                p.ParameterName = "tenant";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.tenant);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "id";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.id);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "note";
                p.DbType = global::System.Data.DbType.String;
                p.Direction = global::System.Data.ParameterDirection.Input;
                SetValueWithDefaultSize(p, typed.note);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "expected";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.expected);
                ps.Add(p);

            }
            public override void UpdateParameters(in global::Dapper.UnifiedCommand cmd, object? args)
            {
                var typed = Cast(args, static () => new { tenant = default(long), id = default(long), note = default(string), expected = default(long) }); // expected shape
                var ps = cmd.Parameters;
                ps[0].Value = AsValue(typed.tenant);
                ps[1].Value = AsValue(typed.id);
                ps[2].Value = AsValue(typed.note);
                ps[3].Value = AsValue(typed.expected);

            }
            public override bool CanPrepare => true;

        }

        private sealed class CommandFactory15 : global::Dapper.CommandFactory<object?> // <anonymous type: long tenant, long id, string? note, long version>
        {
            internal static readonly CommandFactory15 Instance = new();
            public override void AddParameters(in global::Dapper.UnifiedCommand cmd, object? args)
            {
                var typed = Cast(args, static () => new { tenant = default(long), id = default(long), note = default(string?), version = default(long) }); // expected shape
                var ps = cmd.Parameters;
                global::System.Data.Common.DbParameter p;
                p = cmd.CreateParameter();
                p.ParameterName = "tenant";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.tenant);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "id";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.id);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "note";
                p.DbType = global::System.Data.DbType.String;
                p.Direction = global::System.Data.ParameterDirection.Input;
                SetValueWithDefaultSize(p, typed.note);
                ps.Add(p);

            }
            public override void UpdateParameters(in global::Dapper.UnifiedCommand cmd, object? args)
            {
                var typed = Cast(args, static () => new { tenant = default(long), id = default(long), note = default(string?), version = default(long) }); // expected shape
                var ps = cmd.Parameters;
                ps[0].Value = AsValue(typed.tenant);
                ps[1].Value = AsValue(typed.id);
                ps[2].Value = AsValue(typed.note);

            }
            public override bool CanPrepare => true;

        }

        private sealed class CommandFactory16 : global::Dapper.CommandFactory<object?> // <anonymous type: long tenant, long id, string? note, long version>
        {
            internal static readonly CommandFactory16 Instance = new();
            public override void AddParameters(in global::Dapper.UnifiedCommand cmd, object? args)
            {
                var typed = Cast(args, static () => new { tenant = default(long), id = default(long), note = default(string?), version = default(long) }); // expected shape
                var ps = cmd.Parameters;
                global::System.Data.Common.DbParameter p;
                p = cmd.CreateParameter();
                p.ParameterName = "tenant";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.tenant);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "id";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.id);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "note";
                p.DbType = global::System.Data.DbType.String;
                p.Direction = global::System.Data.ParameterDirection.Input;
                SetValueWithDefaultSize(p, typed.note);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "version";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.version);
                ps.Add(p);

            }
            public override void UpdateParameters(in global::Dapper.UnifiedCommand cmd, object? args)
            {
                var typed = Cast(args, static () => new { tenant = default(long), id = default(long), note = default(string?), version = default(long) }); // expected shape
                var ps = cmd.Parameters;
                ps[0].Value = AsValue(typed.tenant);
                ps[1].Value = AsValue(typed.id);
                ps[2].Value = AsValue(typed.note);
                ps[3].Value = AsValue(typed.version);

            }
            public override bool CanPrepare => true;

        }

        private sealed class CommandFactory17 : global::Dapper.CommandFactory<object?> // <anonymous type: long value, CancellationToken cancellation>
        {
            internal static readonly CommandFactory17 Instance = new();
            public override void AddParameters(in global::Dapper.UnifiedCommand cmd, object? args)
            {
                var typed = Cast(args, static () => new { value = default(long), cancellation = default(global::System.Threading.CancellationToken) }); // expected shape
                var ps = cmd.Parameters;
                global::System.Data.Common.DbParameter p;
                p = cmd.CreateParameter();
                p.ParameterName = "value";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.value);
                ps.Add(p);

            }
            public override void UpdateParameters(in global::Dapper.UnifiedCommand cmd, object? args)
            {
                var typed = Cast(args, static () => new { value = default(long), cancellation = default(global::System.Threading.CancellationToken) }); // expected shape
                var ps = cmd.Parameters;
                ps[0].Value = AsValue(typed.value);

            }
            public override global::System.Threading.CancellationToken GetCancellationToken(object? args)
            {
                var typed = Cast(args, static () => new { value = default(long), cancellation = default(global::System.Threading.CancellationToken) }); // expected shape
                return typed.cancellation;
            }
            public override bool CanPrepare => true;

        }

        private sealed class CommandFactory18 : global::Dapper.CommandFactory<object?> // <anonymous type: long tenant, long id, long version, long expected>
        {
            internal static readonly CommandFactory18 Instance = new();
            public override void AddParameters(in global::Dapper.UnifiedCommand cmd, object? args)
            {
                var typed = Cast(args, static () => new { tenant = default(long), id = default(long), version = default(long), expected = default(long) }); // expected shape
                var ps = cmd.Parameters;
                global::System.Data.Common.DbParameter p;
                p = cmd.CreateParameter();
                p.ParameterName = "tenant";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.tenant);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "id";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.id);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "version";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.version);
                ps.Add(p);

                p = cmd.CreateParameter();
                p.ParameterName = "expected";
                p.DbType = global::System.Data.DbType.Int64;
                p.Direction = global::System.Data.ParameterDirection.Input;
                p.Value = AsValue(typed.expected);
                ps.Add(p);

            }
            public override void UpdateParameters(in global::Dapper.UnifiedCommand cmd, object? args)
            {
                var typed = Cast(args, static () => new { tenant = default(long), id = default(long), version = default(long), expected = default(long) }); // expected shape
                var ps = cmd.Parameters;
                ps[0].Value = AsValue(typed.tenant);
                ps[1].Value = AsValue(typed.id);
                ps[2].Value = AsValue(typed.version);
                ps[3].Value = AsValue(typed.expected);

            }
            public override bool CanPrepare => true;

        }


        private static readonly global::Dapper.IDbValueHandler<decimal> TypeHandler0 = new global::MoneyHandler();
        private static readonly global::Dapper.IDbValueHandler<global::OrderSettings> TypeHandler2 = new global::SettingsHandler();

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