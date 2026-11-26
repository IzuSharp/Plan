#define _GNU_SOURCE
#include <dlfcn.h>
#include <poll.h>
#include <stdatomic.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include "korda_database_binding_v1.h"
#include "korda_query_command_v1.h"
#include "korda_cursor_pull_v1.h"

#define SYMBOL_COUNT 53
static _Atomic(void*) targets[SYMBOL_COUNT];
static _Atomic uint64_t calls[SYMBOL_COUNT], pending[SYMBOL_COUNT], waits[4];

static nw_status NW_CDECL probe_nw_db_operation_start_v1(nw_db_ref op, const nw_operation_callbacks_v1* callbacks, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[0], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref op, const nw_operation_callbacks_v1* callbacks, nw_error_info_v1* error))atomic_load(&targets[0]))(op, callbacks, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[0], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_operation_request_cancel_v1(nw_db_ref op)
{
    atomic_fetch_add(&calls[1], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref op))atomic_load(&targets[1]))(op);
    if (result == NW_PENDING) atomic_fetch_add(&pending[1], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_operation_take_owner_v1(nw_db_ref op, uint32_t expected_kind, nw_db_ref* owner, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[2], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref op, uint32_t expected_kind, nw_db_ref* owner, nw_error_info_v1* error))atomic_load(&targets[2]))(op, expected_kind, owner, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[2], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_operation_take_buffer_v1(nw_db_ref op, nw_db_buffer** buffer, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[3], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref op, nw_db_buffer** buffer, nw_error_info_v1* error))atomic_load(&targets[3]))(op, buffer, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[3], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_operation_take_count_v1(nw_db_ref op, int64_t* count, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[4], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref op, int64_t* count, nw_error_info_v1* error))atomic_load(&targets[4]))(op, count, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[4], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_operation_take_error_v1(nw_db_ref op, nw_db_buffer** error_payload, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[5], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref op, nw_db_buffer** error_payload, nw_error_info_v1* error))atomic_load(&targets[5]))(op, error_payload, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[5], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_operation_try_retire_v1(nw_db_ref op)
{
    atomic_fetch_add(&calls[6], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref op))atomic_load(&targets[6]))(op);
    if (result == NW_PENDING) atomic_fetch_add(&pending[6], 1); return result;
}
static void NW_CDECL probe_nw_db_operation_release_v1(nw_db_ref op)
{
    atomic_fetch_add(&calls[7], 1);
    ((void (NW_CDECL*)(nw_db_ref op))atomic_load(&targets[7]))(op);
    
}
static nw_status NW_CDECL probe_nw_db_source_create_v1(nw_bytes_view_v1 config, nw_db_ref* source, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[8], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_bytes_view_v1 config, nw_db_ref* source, nw_error_info_v1* error))atomic_load(&targets[8]))(config, source, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[8], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_session_open_create_v1(nw_db_ref source, nw_db_ref* op, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[9], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref source, nw_db_ref* op, nw_error_info_v1* error))atomic_load(&targets[9]))(source, op, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[9], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_codec_register_v1(nw_db_ref source, uint32_t logical_codec, nw_bytes_view_v1 configuration, uint32_t* bound_codec_id, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[10], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref source, uint32_t logical_codec, nw_bytes_view_v1 configuration, uint32_t* bound_codec_id, nw_error_info_v1* error))atomic_load(&targets[10]))(source, logical_codec, configuration, bound_codec_id, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[10], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_metadata_register_v1(nw_db_ref source, nw_bytes_view_v1 metadata, nw_db_ref* model, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[11], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref source, nw_bytes_view_v1 metadata, nw_db_ref* model, nw_error_info_v1* error))atomic_load(&targets[11]))(source, metadata, model, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[11], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_projection_register_v1(nw_db_ref source, nw_bytes_view_v1 projection, uint32_t* projection_id, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[12], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref source, nw_bytes_view_v1 projection, uint32_t* projection_id, nw_error_info_v1* error))atomic_load(&targets[12]))(source, projection, projection_id, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[12], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_relation_register_v1(nw_db_ref source, nw_db_ref parent_model, nw_db_ref child_model, nw_bytes_view_v1 definition, nw_db_ref* relation, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[13], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref source, nw_db_ref parent_model, nw_db_ref child_model, nw_bytes_view_v1 definition, nw_db_ref* relation, nw_error_info_v1* error))atomic_load(&targets[13]))(source, parent_model, child_model, definition, relation, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[13], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_relation_load_create_v1(nw_db_ref session, nw_db_ref relation, nw_bytes_view_v1 parent_key, uint32_t child_projection_id, nw_db_ref* op, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[14], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref session, nw_db_ref relation, nw_bytes_view_v1 parent_key, uint32_t child_projection_id, nw_db_ref* op, nw_error_info_v1* error))atomic_load(&targets[14]))(session, relation, parent_key, child_projection_id, op, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[14], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_query_create_v1(nw_db_ref session, nw_db_ref model, uint32_t table_id, nw_db_ref* query, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[15], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref session, nw_db_ref model, uint32_t table_id, nw_db_ref* query, nw_error_info_v1* error))atomic_load(&targets[15]))(session, model, table_id, query, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[15], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_expr_column_v1(nw_db_ref query, nw_db_token alias, uint32_t column_id, nw_db_token* expr, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[16], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref query, nw_db_token alias, uint32_t column_id, nw_db_token* expr, nw_error_info_v1* error))atomic_load(&targets[16]))(query, alias, column_id, expr, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[16], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_expr_value_v1(nw_db_ref query, nw_bytes_view_v1 one_cell, nw_db_token* expr, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[17], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref query, nw_bytes_view_v1 one_cell, nw_db_token* expr, nw_error_info_v1* error))atomic_load(&targets[17]))(query, one_cell, expr, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[17], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_expr_parameter_v1(nw_db_ref query, uint32_t parameter_id, nw_bytes_view_v1 name, uint32_t codec_id, uint32_t nullable, nw_db_token* expr, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[18], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref query, uint32_t parameter_id, nw_bytes_view_v1 name, uint32_t codec_id, uint32_t nullable, nw_db_token* expr, nw_error_info_v1* error))atomic_load(&targets[18]))(query, parameter_id, name, codec_id, nullable, expr, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[18], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_expr_binary_v1(nw_db_ref query, uint32_t op_code, nw_db_token left, nw_db_token right, nw_db_token* expr, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[19], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref query, uint32_t op_code, nw_db_token left, nw_db_token right, nw_db_token* expr, nw_error_info_v1* error))atomic_load(&targets[19]))(query, op_code, left, right, expr, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[19], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_expr_unary_v1(nw_db_ref query, uint32_t op_code, nw_db_token input, nw_db_token* expr, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[20], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref query, uint32_t op_code, nw_db_token input, nw_db_token* expr, nw_error_info_v1* error))atomic_load(&targets[20]))(query, op_code, input, expr, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[20], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_expr_list_v1(nw_db_ref query, uint32_t op_code, nw_db_token input, nw_bytes_view_v1 cells, nw_db_token* expr, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[21], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref query, uint32_t op_code, nw_db_token input, nw_bytes_view_v1 cells, nw_db_token* expr, nw_error_info_v1* error))atomic_load(&targets[21]))(query, op_code, input, cells, expr, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[21], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_query_import_v1(nw_db_ref query, nw_db_ref dependency, uint32_t kind, nw_db_token* token, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[22], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref query, nw_db_ref dependency, uint32_t kind, nw_db_token* token, nw_error_info_v1* error))atomic_load(&targets[22]))(query, dependency, kind, token, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[22], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_query_clause_v1(nw_db_ref query, uint32_t clause, nw_bytes_view_v1 operands, nw_db_token* out_token, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[23], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref query, uint32_t clause, nw_bytes_view_v1 operands, nw_db_token* out_token, nw_error_info_v1* error))atomic_load(&targets[23]))(query, clause, operands, out_token, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[23], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_query_seal_v1(nw_db_ref query, uint32_t terminal, nw_db_ref* plan, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[24], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref query, uint32_t terminal, nw_db_ref* plan, nw_error_info_v1* error))atomic_load(&targets[24]))(query, terminal, plan, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[24], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_query_clone_v1(nw_db_ref query, nw_db_ref* clone, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[25], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref query, nw_db_ref* clone, nw_error_info_v1* error))atomic_load(&targets[25]))(query, clone, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[25], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_query_render_v1(nw_db_ref query, nw_db_buffer** sql, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[26], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref query, nw_db_buffer** sql, nw_error_info_v1* error))atomic_load(&targets[26]))(query, sql, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[26], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_cte_create_v1(nw_db_ref declared_model, uint32_t table_id, nw_db_ref body_query, uint32_t recursive, nw_db_ref* cte, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[27], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref declared_model, uint32_t table_id, nw_db_ref body_query, uint32_t recursive, nw_db_ref* cte, nw_error_info_v1* error))atomic_load(&targets[27]))(declared_model, table_id, body_query, recursive, cte, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[27], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_execute_create_v1(nw_db_ref session, nw_db_ref plan, nw_bytes_view_v1 parameters, nw_db_ref* op, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[28], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref session, nw_db_ref plan, nw_bytes_view_v1 parameters, nw_db_ref* op, nw_error_info_v1* error))atomic_load(&targets[28]))(session, plan, parameters, op, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[28], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_sql_create_v1(nw_db_ref session, nw_bytes_view_v1 template, nw_bytes_view_v1 parameters, nw_bytes_view_v1 command_options, nw_db_ref* plan, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[29], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref session, nw_bytes_view_v1 template, nw_bytes_view_v1 parameters, nw_bytes_view_v1 command_options, nw_db_ref* plan, nw_error_info_v1* error))atomic_load(&targets[29]))(session, template, parameters, command_options, plan, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[29], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_cursor_fetch_create_v1(nw_db_ref cursor, uint32_t max_rows, uint64_t max_bytes, nw_db_ref* op, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[30], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref cursor, uint32_t max_rows, uint64_t max_bytes, nw_db_ref* op, nw_error_info_v1* error))atomic_load(&targets[30]))(cursor, max_rows, max_bytes, op, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[30], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_tx_begin_create_v1(nw_db_ref session, nw_bytes_view_v1 options, nw_db_ref* op, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[31], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref session, nw_bytes_view_v1 options, nw_db_ref* op, nw_error_info_v1* error))atomic_load(&targets[31]))(session, options, op, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[31], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_tx_finish_create_v1(nw_db_ref tx, uint32_t action, nw_db_ref* op, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[32], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref tx, uint32_t action, nw_db_ref* op, nw_error_info_v1* error))atomic_load(&targets[32]))(tx, action, op, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[32], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_savepoint_create_v1(nw_db_ref tx, nw_db_ref* op, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[33], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref tx, nw_db_ref* op, nw_error_info_v1* error))atomic_load(&targets[33]))(tx, op, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[33], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_savepoint_action_create_v1(nw_db_ref savepoint, uint32_t action, nw_db_ref* op, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[34], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref savepoint, uint32_t action, nw_db_ref* op, nw_error_info_v1* error))atomic_load(&targets[34]))(savepoint, action, op, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[34], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_mutation_create_v1(nw_db_ref session, nw_db_ref model, uint32_t mutation, nw_bytes_view_v1 values_keys_checks, nw_db_ref* op, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[35], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref session, nw_db_ref model, uint32_t mutation, nw_bytes_view_v1 values_keys_checks, nw_db_ref* op, nw_error_info_v1* error))atomic_load(&targets[35]))(session, model, mutation, values_keys_checks, op, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[35], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_admin_create_v1(nw_db_ref source, uint32_t action, nw_bytes_view_v1 payload, nw_db_ref* op, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[36], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref source, uint32_t action, nw_bytes_view_v1 payload, nw_db_ref* op, nw_error_info_v1* error))atomic_load(&targets[36]))(source, action, payload, op, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[36], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_close_create_v1(nw_db_ref owner, nw_db_ref* op, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[37], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref owner, nw_db_ref* op, nw_error_info_v1* error))atomic_load(&targets[37]))(owner, op, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[37], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_snapshot_v1(nw_db_ref owner, nw_bytes_view_v1 query, nw_db_buffer** snapshot, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[38], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref owner, nw_bytes_view_v1 query, nw_db_buffer** snapshot, nw_error_info_v1* error))atomic_load(&targets[38]))(owner, query, snapshot, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[38], 1); return result;
}
static void NW_CDECL probe_nw_db_owner_release_v1(nw_db_ref owner)
{
    atomic_fetch_add(&calls[39], 1);
    ((void (NW_CDECL*)(nw_db_ref owner))atomic_load(&targets[39]))(owner);
    
}
static nw_status NW_CDECL probe_nw_db_buffer_view_v1(nw_db_buffer* buffer, nw_bytes_view_v1* view, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[40], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_buffer* buffer, nw_bytes_view_v1* view, nw_error_info_v1* error))atomic_load(&targets[40]))(buffer, view, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[40], 1); return result;
}
static void NW_CDECL probe_nw_db_buffer_release_v1(nw_db_buffer* buffer)
{
    atomic_fetch_add(&calls[41], 1);
    ((void (NW_CDECL*)(nw_db_buffer* buffer))atomic_load(&targets[41]))(buffer);
    
}
static nw_status NW_CDECL probe_nw_db_query_command_compile_v1(nw_db_ref session, nw_bytes_view_v1 command, const nw_db_query_dependency_v1* dependencies, uint32_t dependency_count, uint32_t terminal, nw_db_ref* plan, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[42], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref session, nw_bytes_view_v1 command, const nw_db_query_dependency_v1* dependencies, uint32_t dependency_count, uint32_t terminal, nw_db_ref* plan, nw_error_info_v1* error))atomic_load(&targets[42]))(session, command, dependencies, dependency_count, terminal, plan, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[42], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_query_command_render_v1(nw_db_ref session, nw_bytes_view_v1 command, const nw_db_query_dependency_v1* dependencies, uint32_t dependency_count, nw_db_buffer** sql, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[43], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref session, nw_bytes_view_v1 command, const nw_db_query_dependency_v1* dependencies, uint32_t dependency_count, nw_db_buffer** sql, nw_error_info_v1* error))atomic_load(&targets[43]))(session, command, dependencies, dependency_count, sql, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[43], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_query_command_cte_v1(nw_db_ref session, nw_bytes_view_v1 command, const nw_db_query_dependency_v1* dependencies, uint32_t dependency_count, nw_db_ref declared_model, uint32_t table_id, uint32_t recursive, nw_db_ref* cte, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[44], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref session, nw_bytes_view_v1 command, const nw_db_query_dependency_v1* dependencies, uint32_t dependency_count, nw_db_ref declared_model, uint32_t table_id, uint32_t recursive, nw_db_ref* cte, nw_error_info_v1* error))atomic_load(&targets[44]))(session, command, dependencies, dependency_count, declared_model, table_id, recursive, cte, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[44], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_cursor_pull_create_v1(nw_db_ref session, nw_db_ref plan, nw_bytes_view_v1 arguments, nw_db_ref* channel, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[45], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref session, nw_db_ref plan, nw_bytes_view_v1 arguments, nw_db_ref* channel, nw_error_info_v1* error))atomic_load(&targets[45]))(session, plan, arguments, channel, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[45], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_cursor_pull_relation_create_v1(nw_db_ref session, nw_db_ref relation, nw_bytes_view_v1 key, uint32_t projection, nw_db_ref* channel, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[46], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref session, nw_db_ref relation, nw_bytes_view_v1 key, uint32_t projection, nw_db_ref* channel, nw_error_info_v1* error))atomic_load(&targets[46]))(session, relation, key, projection, channel, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[46], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_cursor_pull_mutation_create_v1(nw_db_ref session, nw_db_ref model, uint32_t kind, nw_bytes_view_v1 payload, nw_db_ref* channel, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[47], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref session, nw_db_ref model, uint32_t kind, nw_bytes_view_v1 payload, nw_db_ref* channel, nw_error_info_v1* error))atomic_load(&targets[47]))(session, model, kind, payload, channel, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[47], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_cursor_pull_request_v1(nw_db_ref channel, uint64_t generation, uint32_t rows, uint64_t bytes, const nw_db_cursor_callbacks_v1* callbacks, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[48], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref channel, uint64_t generation, uint32_t rows, uint64_t bytes, const nw_db_cursor_callbacks_v1* callbacks, nw_error_info_v1* error))atomic_load(&targets[48]))(channel, generation, rows, bytes, callbacks, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[48], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_cursor_pull_take_v1(nw_db_ref channel, uint64_t generation, nw_db_batch_result_v1* result, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[49], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref channel, uint64_t generation, nw_db_batch_result_v1* result, nw_error_info_v1* error))atomic_load(&targets[49]))(channel, generation, result, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[49], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_cursor_pull_take_error_v1(nw_db_ref channel, uint64_t generation, nw_db_buffer** result, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[50], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref channel, uint64_t generation, nw_db_buffer** result, nw_error_info_v1* error))atomic_load(&targets[50]))(channel, generation, result, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[50], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_cursor_pull_check_read_v1(nw_db_ref channel, nw_error_info_v1* error)
{
    atomic_fetch_add(&calls[51], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref channel, nw_error_info_v1* error))atomic_load(&targets[51]))(channel, error);
    if (result == NW_PENDING) atomic_fetch_add(&pending[51], 1); return result;
}
static nw_status NW_CDECL probe_nw_db_cursor_pull_stop_v1(nw_db_ref channel)
{
    atomic_fetch_add(&calls[52], 1);
    nw_status result = ((nw_status (NW_CDECL*)(nw_db_ref channel))atomic_load(&targets[52]))(channel);
    if (result == NW_PENDING) atomic_fetch_add(&pending[52], 1); return result;
}

void* dlsym(void* handle, const char* name)
{
    void* (*original)(void*, const char*) = dlvsym(RTLD_NEXT, "dlsym", "GLIBC_2.2.5");
    void* address = original(handle, name);
    if (!address) return address;
    if (!strcmp(name, "nw_db_operation_start_v1")) { atomic_store(&targets[0], address); return (void*)&probe_nw_db_operation_start_v1; }
    if (!strcmp(name, "nw_db_operation_request_cancel_v1")) { atomic_store(&targets[1], address); return (void*)&probe_nw_db_operation_request_cancel_v1; }
    if (!strcmp(name, "nw_db_operation_take_owner_v1")) { atomic_store(&targets[2], address); return (void*)&probe_nw_db_operation_take_owner_v1; }
    if (!strcmp(name, "nw_db_operation_take_buffer_v1")) { atomic_store(&targets[3], address); return (void*)&probe_nw_db_operation_take_buffer_v1; }
    if (!strcmp(name, "nw_db_operation_take_count_v1")) { atomic_store(&targets[4], address); return (void*)&probe_nw_db_operation_take_count_v1; }
    if (!strcmp(name, "nw_db_operation_take_error_v1")) { atomic_store(&targets[5], address); return (void*)&probe_nw_db_operation_take_error_v1; }
    if (!strcmp(name, "nw_db_operation_try_retire_v1")) { atomic_store(&targets[6], address); return (void*)&probe_nw_db_operation_try_retire_v1; }
    if (!strcmp(name, "nw_db_operation_release_v1")) { atomic_store(&targets[7], address); return (void*)&probe_nw_db_operation_release_v1; }
    if (!strcmp(name, "nw_db_source_create_v1")) { atomic_store(&targets[8], address); return (void*)&probe_nw_db_source_create_v1; }
    if (!strcmp(name, "nw_db_session_open_create_v1")) { atomic_store(&targets[9], address); return (void*)&probe_nw_db_session_open_create_v1; }
    if (!strcmp(name, "nw_db_codec_register_v1")) { atomic_store(&targets[10], address); return (void*)&probe_nw_db_codec_register_v1; }
    if (!strcmp(name, "nw_db_metadata_register_v1")) { atomic_store(&targets[11], address); return (void*)&probe_nw_db_metadata_register_v1; }
    if (!strcmp(name, "nw_db_projection_register_v1")) { atomic_store(&targets[12], address); return (void*)&probe_nw_db_projection_register_v1; }
    if (!strcmp(name, "nw_db_relation_register_v1")) { atomic_store(&targets[13], address); return (void*)&probe_nw_db_relation_register_v1; }
    if (!strcmp(name, "nw_db_relation_load_create_v1")) { atomic_store(&targets[14], address); return (void*)&probe_nw_db_relation_load_create_v1; }
    if (!strcmp(name, "nw_db_query_create_v1")) { atomic_store(&targets[15], address); return (void*)&probe_nw_db_query_create_v1; }
    if (!strcmp(name, "nw_db_expr_column_v1")) { atomic_store(&targets[16], address); return (void*)&probe_nw_db_expr_column_v1; }
    if (!strcmp(name, "nw_db_expr_value_v1")) { atomic_store(&targets[17], address); return (void*)&probe_nw_db_expr_value_v1; }
    if (!strcmp(name, "nw_db_expr_parameter_v1")) { atomic_store(&targets[18], address); return (void*)&probe_nw_db_expr_parameter_v1; }
    if (!strcmp(name, "nw_db_expr_binary_v1")) { atomic_store(&targets[19], address); return (void*)&probe_nw_db_expr_binary_v1; }
    if (!strcmp(name, "nw_db_expr_unary_v1")) { atomic_store(&targets[20], address); return (void*)&probe_nw_db_expr_unary_v1; }
    if (!strcmp(name, "nw_db_expr_list_v1")) { atomic_store(&targets[21], address); return (void*)&probe_nw_db_expr_list_v1; }
    if (!strcmp(name, "nw_db_query_import_v1")) { atomic_store(&targets[22], address); return (void*)&probe_nw_db_query_import_v1; }
    if (!strcmp(name, "nw_db_query_clause_v1")) { atomic_store(&targets[23], address); return (void*)&probe_nw_db_query_clause_v1; }
    if (!strcmp(name, "nw_db_query_seal_v1")) { atomic_store(&targets[24], address); return (void*)&probe_nw_db_query_seal_v1; }
    if (!strcmp(name, "nw_db_query_clone_v1")) { atomic_store(&targets[25], address); return (void*)&probe_nw_db_query_clone_v1; }
    if (!strcmp(name, "nw_db_query_render_v1")) { atomic_store(&targets[26], address); return (void*)&probe_nw_db_query_render_v1; }
    if (!strcmp(name, "nw_db_cte_create_v1")) { atomic_store(&targets[27], address); return (void*)&probe_nw_db_cte_create_v1; }
    if (!strcmp(name, "nw_db_execute_create_v1")) { atomic_store(&targets[28], address); return (void*)&probe_nw_db_execute_create_v1; }
    if (!strcmp(name, "nw_db_sql_create_v1")) { atomic_store(&targets[29], address); return (void*)&probe_nw_db_sql_create_v1; }
    if (!strcmp(name, "nw_db_cursor_fetch_create_v1")) { atomic_store(&targets[30], address); return (void*)&probe_nw_db_cursor_fetch_create_v1; }
    if (!strcmp(name, "nw_db_tx_begin_create_v1")) { atomic_store(&targets[31], address); return (void*)&probe_nw_db_tx_begin_create_v1; }
    if (!strcmp(name, "nw_db_tx_finish_create_v1")) { atomic_store(&targets[32], address); return (void*)&probe_nw_db_tx_finish_create_v1; }
    if (!strcmp(name, "nw_db_savepoint_create_v1")) { atomic_store(&targets[33], address); return (void*)&probe_nw_db_savepoint_create_v1; }
    if (!strcmp(name, "nw_db_savepoint_action_create_v1")) { atomic_store(&targets[34], address); return (void*)&probe_nw_db_savepoint_action_create_v1; }
    if (!strcmp(name, "nw_db_mutation_create_v1")) { atomic_store(&targets[35], address); return (void*)&probe_nw_db_mutation_create_v1; }
    if (!strcmp(name, "nw_db_admin_create_v1")) { atomic_store(&targets[36], address); return (void*)&probe_nw_db_admin_create_v1; }
    if (!strcmp(name, "nw_db_close_create_v1")) { atomic_store(&targets[37], address); return (void*)&probe_nw_db_close_create_v1; }
    if (!strcmp(name, "nw_db_snapshot_v1")) { atomic_store(&targets[38], address); return (void*)&probe_nw_db_snapshot_v1; }
    if (!strcmp(name, "nw_db_owner_release_v1")) { atomic_store(&targets[39], address); return (void*)&probe_nw_db_owner_release_v1; }
    if (!strcmp(name, "nw_db_buffer_view_v1")) { atomic_store(&targets[40], address); return (void*)&probe_nw_db_buffer_view_v1; }
    if (!strcmp(name, "nw_db_buffer_release_v1")) { atomic_store(&targets[41], address); return (void*)&probe_nw_db_buffer_release_v1; }
    if (!strcmp(name, "nw_db_query_command_compile_v1")) { atomic_store(&targets[42], address); return (void*)&probe_nw_db_query_command_compile_v1; }
    if (!strcmp(name, "nw_db_query_command_render_v1")) { atomic_store(&targets[43], address); return (void*)&probe_nw_db_query_command_render_v1; }
    if (!strcmp(name, "nw_db_query_command_cte_v1")) { atomic_store(&targets[44], address); return (void*)&probe_nw_db_query_command_cte_v1; }
    if (!strcmp(name, "nw_db_cursor_pull_create_v1")) { atomic_store(&targets[45], address); return (void*)&probe_nw_db_cursor_pull_create_v1; }
    if (!strcmp(name, "nw_db_cursor_pull_relation_create_v1")) { atomic_store(&targets[46], address); return (void*)&probe_nw_db_cursor_pull_relation_create_v1; }
    if (!strcmp(name, "nw_db_cursor_pull_mutation_create_v1")) { atomic_store(&targets[47], address); return (void*)&probe_nw_db_cursor_pull_mutation_create_v1; }
    if (!strcmp(name, "nw_db_cursor_pull_request_v1")) { atomic_store(&targets[48], address); return (void*)&probe_nw_db_cursor_pull_request_v1; }
    if (!strcmp(name, "nw_db_cursor_pull_take_v1")) { atomic_store(&targets[49], address); return (void*)&probe_nw_db_cursor_pull_take_v1; }
    if (!strcmp(name, "nw_db_cursor_pull_take_error_v1")) { atomic_store(&targets[50], address); return (void*)&probe_nw_db_cursor_pull_take_error_v1; }
    if (!strcmp(name, "nw_db_cursor_pull_check_read_v1")) { atomic_store(&targets[51], address); return (void*)&probe_nw_db_cursor_pull_check_read_v1; }
    if (!strcmp(name, "nw_db_cursor_pull_stop_v1")) { atomic_store(&targets[52], address); return (void*)&probe_nw_db_cursor_pull_stop_v1; }
    return address;
}

uint64_t db_perf_ffi_count(uint32_t group, uint32_t index)
{
    if (group == 0 && index < SYMBOL_COUNT) return atomic_load(&calls[index]);
    if (group == 1 && index < SYMBOL_COUNT) return atomic_load(&pending[index]);
    if (group == 2 && index < 4) return atomic_load(&waits[index]);
    return 0;
}

int poll(struct pollfd* fds, nfds_t count, int timeout)
{
    int (*original)(struct pollfd*, nfds_t, int) = dlvsym(RTLD_NEXT, "poll", "GLIBC_2.2.5");
    Dl_info caller;
    int tracked = dladdr(__builtin_return_address(0), &caller) && caller.dli_fname
        && strstr(caller.dli_fname, "libnw_database_") != NULL;
    struct timespec before, after;
    if (tracked) clock_gettime(CLOCK_MONOTONIC, &before);
    int result = original(fds, count, timeout);
    if (tracked)
    {
        clock_gettime(CLOCK_MONOTONIC, &after);
        uint64_t elapsed = (uint64_t)(after.tv_sec - before.tv_sec) * 1000000000
            + after.tv_nsec - before.tv_nsec;
        atomic_fetch_add(&waits[0], 1);
        if (!result) atomic_fetch_add(&waits[1], 1);
        if (result < 0) atomic_fetch_add(&waits[2], 1);
        atomic_fetch_add(&waits[3], elapsed);
    }
    return result;
}
