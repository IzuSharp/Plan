// SPDX-License-Identifier: MIT
#include "nw/host.hpp"
#include "nw_database_fingerprint.hpp"

#include <algorithm>
#include <cstdlib>
#include <filesystem>
#include <limits>

namespace nw
{
std::atomic<std::uint64_t> source_count{0}, session_count{0}, operation_count{0}, cursor_count{0}, buffer_count{0},
    pull_count{0};
namespace
{
std::atomic<std::uint64_t> next_source{1};
constexpr std::uint64_t hour_ns = 3'600'000'000'000;
[[maybe_unused]] constexpr std::uint64_t second_ns = 1'000'000'000;
const std::shared_ptr<Error>& cursor_cleanup_failure()
{
    // Initialized before the first channel can accept a request. Publishing
    // an accepted request's cleanup failure must not allocate another error.
    static const auto failure = std::make_shared<Error>(NW_NATIVE_PANIC, 8, "cleanup failed");
    return failure;
}
std::uint64_t checked_timeout(std::uint64_t value)
{
    if (!value || value > hour_ns)
        throw Error::invalid("database finite timeout");
    return value;
}
void throw_configuration()
{
    throw Error(NW_DOMAIN_ERROR, 8, "invalid provider configuration");
}
void rethrow_transaction_error(const Error& source)
{
    Error error(NW_DOMAIN_ERROR, 1, "transaction operation failed");
    error.provider = source.provider;
    error.correlation = source.correlation;
    throw error;
}
std::size_t sqlite_input_remaining(const Session& session, const SqlPlan& plan)
{
    const auto maximum = session.source->config.limits.parameter_bytes;
    if (plan.sql.empty() || plan.sql.size() > std::min(maximum, std::size_t{1024 * 1024}) ||
        plan.sql.find('\0') != std::string::npos)
        throw Error(NW_DOMAIN_ERROR, 8, "invalid SQLite SQL byte length");
    return maximum - plan.sql.size();
}
const std::vector<Scalar>& command_parameters(const Session& session, const SqlPlan& plan)
{
    const auto& limits = session.source->config.limits;
    if (session.source->config.provider.profile != Profile::Sqlite)
    {
        try
        {
            validate_parameters(plan.arguments, plan.expectation, plan.parameter_wire_bytes, limits.parameters,
                                limits.parameter_bytes, std::min(limits.field_bytes, limits.parameter_bytes));
            return plan.arguments;
        }
        catch (const Error&)
        {
            throw Error(NW_DOMAIN_ERROR, 3, "database scalar conversion failed");
        }
    }

    // Preserve B03's published admission boundary: SQL plus two complete
    // logical wire lengths per physical session. Typed arguments no longer
    // allocate those two frames. The existing CommandGate still owns this
    // conservative grant until command/cursor retirement.
    const auto remaining = sqlite_input_remaining(session, plan);
    if (plan.parameter_wire_bytes > remaining / 2)
        throw Error::capacity();
    const auto available = std::min(remaining, std::max(plan.parameter_wire_bytes, std::size_t{1}));
    try
    {
        validate_parameters(plan.arguments, plan.expectation, plan.parameter_wire_bytes, MAX_NODES, available,
                            available);
        return plan.arguments;
    }
    catch (const Error&)
    {
        // B03 maps B07 decode failures to its provider codec category. Physical
        // grant refusal above remains the distinct ResourceLimit category.
        throw Error(NW_DOMAIN_ERROR, 3, "SQLite parameter conversion failed");
    }
}
} // namespace

Bytes u32_bytes(std::uint32_t value)
{
    Bytes bytes(4);
    put_u32(bytes, 0, value);
    return bytes;
}
Bytes u64_bytes(std::uint64_t value)
{
    Bytes bytes(8);
    put_u64(bytes, 0, value);
    return bytes;
}
ByteView text_view(std::string_view value)
{
    return {reinterpret_cast<const std::uint8_t*>(value.data()), value.size()};
}
Bytes snapshot_record(std::uint32_t state, std::uint32_t outcome, bool attempted, std::uint32_t cleanup,
                      std::uint32_t disposition, bool released, bool deadline, std::uint64_t correlation,
                      const std::optional<std::string>& provider)
{
    std::vector<ControlField> fields{{1, 1, u32_bytes(state)},       {2, 1, u32_bytes(outcome)},
                                     {3, 1, u32_bytes(attempted)},   {4, 1, u32_bytes(cleanup)},
                                     {5, 1, u32_bytes(disposition)}, {6, 1, u32_bytes(released)},
                                     {7, 1, u32_bytes(deadline)},    {8, 2, u64_bytes(correlation)}};
    if (provider)
        fields.push_back({9, 4, Bytes(provider->begin(), provider->end())});
    return encode_control(7, fields);
}
std::uint64_t capability_mask()
{
    std::uint64_t result = (1ULL << 28) - 1;
#if !NW_ENABLE_POSTGRES
    result &= ~((1ULL << 11) | (1ULL << 14));
#endif
#if !NW_ENABLE_SQLITE
    result &= ~(1ULL << 15);
#endif
    return result;
}
HostLimits HostLimits::parse(ByteView bytes)
{
    std::vector<FieldSpec> spec;
    for (std::uint16_t id = 1; id <= 15; ++id)
        spec.push_back({id, static_cast<std::uint16_t>((id == 3 || id == 15) ? 3 : 2), true});
    const auto fields = Fields::parse(bytes, 10, spec);
    const auto value = [&](std::uint16_t id, std::uint64_t maximum, bool zero = false) -> std::size_t
    {
        const auto count = fields.u64(id);
        if (count > maximum || (!zero && !count))
            throw Error::invalid("database limit outside native profile");
        return static_cast<std::size_t>(count);
    };
    return {value(1, 1024),
            value(2, 4096),
            value(4, 1'000'000, true),
            value(5, 1ULL << 30, true),
            value(6, MAX_NODES),
            value(7, MAX_BYTES),
            value(8, 64ULL << 20),
            value(9, MAX_NODES),
            value(11, MAX_NODES),
            value(12, MAX_BYTES),
            value(13, MAX_NODES),
            value(14, 1ULL << 30),
            static_cast<std::uint32_t>(value(10, 256)),
            checked_timeout(fields.u64(3)),
            checked_timeout(fields.u64(15))};
}
QueryLimits HostLimits::binding() const
{
    return {nodes, depth, parameter_bytes, parameters};
}
AdministrationLimits HostLimits::administration() const
{
    return {buffered_rows, buffered_bytes, field_bytes, parameter_bytes, nodes, command_ns};
}
HostConfig HostConfig::parse(ByteView bytes)
{
    const auto fields =
        Fields::parse(bytes, 1, {{1, 1, true}, {2, 4, true}, {3, 5, true}, {4, 5, true}, {5, 4, false}});
    HostConfig config;
    config.limits = HostLimits::parse(fields.bytes(3));
    config.provider.connection = fields.text(2);
    config.name = fields.get(5) ? std::string(fields.text(5)) : "default";
    if (config.provider.connection.empty() || config.provider.connection.size() > 8192 ||
        config.provider.connection.find('\0') != std::string::npos)
        throw Error::invalid("connection identity");
    if (config.name.empty() || config.name.size() > 256 || config.name.find('\0') != std::string::npos)
        throw Error::invalid("source name");
    auto& provider = config.provider;
    provider.statement_timeout_ns = config.limits.command_ns;
    if (fields.u32(1) == 0)
    {
#if NW_ENABLE_POSTGRES
        provider.profile = Profile::PostgreSql;
        const auto options =
            Fields::parse(fields.bytes(4), 8, {{1, 1, true}, {2, 4, false}, {3, 4, true}, {4, 3, true}});
        if (options.u32(1) > 1)
            throw Error::invalid("TLS profile");
        provider.verify_tls = options.u32(1) == 0;
        provider.application_name = options.text(3);
        provider.connect_timeout_ns = options.u64(4);
        if (options.get(2))
            provider.root_certificate = std::string(options.text(2));
        const auto& uri = provider.connection;
        const auto scheme = uri.find("://");
        const auto at = uri.find('@', scheme == std::string::npos ? 0 : scheme + 3);
        const auto slash = at == std::string::npos ? std::string::npos : uri.find('/', at);
        if ((!uri.starts_with("postgres://") && !uri.starts_with("postgresql://")) ||
            uri.find_first_of("?#") != std::string::npos || at == std::string::npos || at <= scheme + 3 ||
            slash == std::string::npos || slash == at + 1 || slash + 1 >= uri.size() ||
            provider.application_name.empty() || provider.application_name.size() > 256 ||
            provider.application_name.find('\0') != std::string::npos || provider.connect_timeout_ns == 0 ||
            provider.connect_timeout_ns / second_ns > 3600)
            throw_configuration();
        for (const char* key : {"PGHOSTADDR", "PGHOST", "PGPORT", "PGUSER", "PGDATABASE", "PGPASSWORD", "PGPASSFILE",
                                "PGSSLMODE", "PGSSLROOTCERT", "PGSSLCERT", "PGSSLKEY", "PGAPPNAME", "PGOPTIONS"})
            // Concurrent reads preserve the original environment-refusal policy.
            // Product code never mutates the process environment.
            // NOLINTNEXTLINE(concurrency-mt-unsafe)
            if (std::getenv(key))
                throw_configuration();
        if (provider.root_certificate && (!std::filesystem::path(*provider.root_certificate).is_absolute() ||
                                          !std::filesystem::is_regular_file(*provider.root_certificate)))
            throw_configuration();
#else
        throw Error::unsupported();
#endif
    }
    else if (fields.u32(1) == 1)
    {
#if NW_ENABLE_SQLITE
        provider.profile = Profile::Sqlite;
        const auto options = Fields::parse(
            fields.bytes(4), 9, {{1, 1, true}, {2, 1, true}, {3, 1, true}, {4, 1, true}, {5, 2, true}, {6, 1, true}});
        provider.sqlite_mode = options.u32(1);
        provider.sqlite_journal = options.u32(2);
        provider.sqlite_synchronous = options.u32(3);
        provider.sqlite_begin = options.u32(4);
        provider.sqlite_busy_timeout_ns = options.u64(5);
        provider.sqlite_foreign_keys = options.boolean(6);
        if (provider.sqlite_mode > 3 || provider.sqlite_journal > 2 || provider.sqlite_synchronous > 1 ||
            provider.sqlite_begin > 1 || provider.sqlite_busy_timeout_ns % 1'000'000 ||
            provider.sqlite_busy_timeout_ns / 1'000'000 > INT32_MAX || provider.connection.size() > 4096 ||
            provider.connection.starts_with("file:"))
            throw_configuration();
        if ((provider.sqlite_mode == 3 || provider.connection == ":memory:") &&
            (provider.sqlite_mode != 3 || provider.sqlite_journal != 2 || config.limits.connections != 1))
            throw_configuration();
#else
        throw Error::unsupported();
#endif
    }
    else
        throw Error::unsupported();
    return config;
}

struct WorkerPool::State
{
    std::mutex mutex;
    std::condition_variable changed;
    std::deque<std::function<void()>> work;
    bool stop = false;
};
WorkerPool::WorkerPool(std::size_t workers) : state_(std::make_shared<State>())
{
    try
    {
        for (std::size_t i = 0; i < workers; ++i)
            threads_.emplace_back(
                [state = state_]
                {
                    for (;;)
                    {
                        std::function<void()> work;
                        {
                            std::unique_lock lock(state->mutex);
                            state->changed.wait(lock, [&] { return state->stop || !state->work.empty(); });
                            if (state->work.empty())
                                return;
                            work = std::move(state->work.front());
                            state->work.pop_front();
                        }
                        work();
                    }
                });
    }
    catch (...)
    {
        stop();
        throw;
    }
}
WorkerPool::~WorkerPool()
{
    stop();
}
void WorkerPool::post(std::function<void()> work)
{
#ifdef NW_HOST_TEST_HOOKS
    if (test_before_post)
        test_before_post();
#endif
    {
        std::lock_guard lock(state_->mutex);
        if (state_->stop)
            throw Error::closed();
        state_->work.push_back(std::move(work));
    }
    state_->changed.notify_one();
}
void WorkerPool::stop()
{
    std::lock_guard control(stop_mutex_);
    {
        std::lock_guard lock(state_->mutex);
        state_->stop = true;
    }
    state_->changed.notify_all();
    for (auto& thread : threads_)
        if (thread.joinable())
        {
            if (thread.get_id() == std::this_thread::get_id())
                thread.detach();
            else
                thread.join();
        }
}

void RetirementFence::add()
{
    std::lock_guard lock(mutex_);
    ++pending_;
}
void RetirementFence::complete()
{
    {
        std::lock_guard lock(mutex_);
        if (!pending_)
            std::terminate();
        --pending_;
    }
    changed_.notify_all();
}
void RetirementFence::wait()
{
    std::unique_lock lock(mutex_);
    changed_.wait(lock, [&] { return pending_ == 0; });
}
void RetirementFence::wait_until(Clock::time_point deadline)
{
    std::unique_lock lock(mutex_);
    changed_.wait_until(lock, deadline, [&] { return pending_ == 0; });
}
bool RetirementFence::done() const
{
    std::lock_guard lock(mutex_);
    return pending_ == 0;
}

Source::Source(HostConfig value)
    : config(std::move(value)), identity{module_identity(), next_source.fetch_add(1), 1, config.provider.profile},
      parameters(std::make_shared<ParameterRegistry>(identity, config.limits.nodes)),
      workers(std::min<std::size_t>(config.limits.connections, 16) + 2),
      shapes(config.limits.prepared_plans, config.limits.prepared_bytes, database_abi_fingerprint)
{
    stream_max_bytes = config.limits.batch_bytes * 8 * config.limits.connections;
    ++source_count;
}
std::shared_ptr<Source> Source::create(HostConfig config)
{
    auto source = std::shared_ptr<Source>(new Source(std::move(config)));
    source->admission_thread = std::thread([source] { source->admission_loop(); });
    return source;
}
Source::~Source()
{
    // A detached transaction's last reference may destroy this Source before
    // its independent ticket completes. Only explicit join waits that fence;
    // waiting here would make the worker wait for its own final release.
    {
        std::lock_guard lock(mutex);
        admission_stop = true;
    }
    changed.notify_all();
    if (admission_thread.joinable())
    {
        if (admission_thread.get_id() == std::this_thread::get_id())
            admission_thread.detach();
        else
            admission_thread.join();
    }
    workers.stop();
    controls.stop();
    for (auto& connection : idle)
        connection->close();
    --source_count;
}
void Source::admit() const
{
    if (poisoned.load())
        throw Error(NW_ENGINE_POISONED, 8, "database source poisoned");
    if (closing.load())
        throw Error::closed();
}
bool Source::reserve_operation(bool control)
{
    if (!control)
        admit();
    std::lock_guard lock(mutex);
    if (retired.load() || admission_stop)
    {
        if (control)
            return false;
        throw Error::closed();
    }
    const auto maximum = config.limits.nodes + config.limits.connections + config.limits.waiters;
    if (pending.load() >= maximum)
        throw Error::capacity();
    ++pending;
    return true;
}
void Source::release_operation()
{
    {
        // Join checks the last operation owner under this same mutex. An
        // atomic counter alone would still allow its notification to be lost
        // between that predicate check and the condition-variable wait.
        std::lock_guard lock(mutex);
        --pending;
    }
    changed.notify_all();
}
void Source::queue_admission(std::shared_ptr<DbOperation> operation)
{
    {
        std::lock_guard lock(mutex);
        admit();
        if (admissions.size() >= config.limits.waiters)
            throw Error::capacity();
        admissions.push_back(std::move(operation));
    }
    changed.notify_all();
}
void Source::queue_administration(std::shared_ptr<DbOperation> operation)
{
    {
        std::lock_guard lock(mutex);
        admit();
        const bool waiting = administration_active || !administration_admissions.empty();
        const auto maximum = config.limits.waiters + (administration_active ? 0 : 1);
        if (administration_admissions.size() >= maximum)
            throw Error::capacity();
        // The head may claim the otherwise free permit immediately. Every
        // waiter is charged and timed here, before any worker can be occupied.
        operation->admission_deadline =
            waiting ? Clock::now() + std::chrono::nanoseconds(config.limits.admission_ns) : Clock::time_point::max();
        administration_admissions.push_back(std::move(operation));
    }
    changed.notify_all();
}
void Source::finish_administration()
{
    {
        std::lock_guard lock(mutex);
        administration_cancel.reset();
        administration_active = false;
    }
    changed.notify_all();
}
void Source::admission_loop()
{
    bool retry = false;
    for (;;)
    {
        std::array<std::shared_ptr<DbOperation>, 2> operations;
        std::array<std::optional<Error>, 2> failures;
        {
            std::unique_lock lock(mutex);
            if (!retry)
                changed.wait_for(lock, std::chrono::milliseconds(5),
                                 [&]
                                 {
                                     return admission_stop ||
                                            (closing.load() &&
                                             (!admissions.empty() || !administration_admissions.empty())) ||
                                            (!admissions.empty() && leased < config.limits.connections) ||
                                            (!administration_admissions.empty() && !administration_active);
                                 });
            retry = false;
            if (admission_stop || (closing.load() && admissions.empty() && administration_admissions.empty()))
                return;
            for (std::size_t index = 0; index < operations.size(); ++index)
            {
                const bool administrative = index == 1;
                auto& queue = administrative ? administration_admissions : admissions;
                auto& operation = operations[index];
                auto& failure = failures[index];
                for (auto iterator = queue.begin(); iterator != queue.end(); ++iterator)
                {
                    const auto& current = *iterator;
                    if (current->cancel->requested())
                        failure = Error::canceled();
                    else if (closing.load())
                        failure = Error::closed();
                    else if (Clock::now() >= current->admission_deadline)
                        failure = administrative ? Error(NW_TIMEOUT, 1, "administrative admission timed out")
                                                 : Error::capacity();
                    else if (administrative ? administration_active : leased >= config.limits.connections)
                        continue;
                    operation = current;
                    queue.erase(iterator);
                    if (!failure)
                    {
                        if (administrative)
                        {
                            administration_active = true;
                            administration_cancel = operation->cancel;
                            operation->administration_reserved.store(true);
                        }
                        else
                            ++leased;
                    }
                    retry = true;
                    break;
                }
            }
        }
        for (std::size_t index = 0; index < operations.size(); ++index)
        {
            auto& operation = operations[index];
            auto& failure = failures[index];
            if (!operation)
                continue;
            if (failure)
                operation->fail(std::move(*failure));
            else
            {
                try
                {
                    workers.post([operation] { operation->run(); });
                }
                catch (const Error& error)
                {
                    if (index == 1)
                        operation->release_administration();
                    else
                        return_connection({}, true);
                    operation->fail(error);
                }
                catch (...)
                {
                    if (index == 1)
                        operation->release_administration();
                    else
                        return_connection({}, true);
                    operation->fail(Error::capacity());
                }
            }
        }
    }
}
void Source::return_connection(std::shared_ptr<ProviderConnection> connection, bool discard)
{
    {
        std::lock_guard lock(mutex);
        if (connection && !discard && connection->healthy() && !closing.load())
        {
            idle.push_back(std::move(connection));
            if (leased)
                --leased;
            changed.notify_all();
            return;
        }
    }
    // A discarded physical connection remains charged while close is running.
    // A waiter cannot open a replacement before the last native accessor retires.
    if (connection)
        connection->close();
    {
        std::lock_guard lock(mutex);
        if (leased)
            --leased;
    }
    changed.notify_all();
}
void Source::request_close()
{
    if (closing.exchange(true))
        return;
    std::shared_ptr<Cancel> administrative_work;
    {
        std::lock_guard lock(mutex);
        administrative_work = administration_cancel.lock();
    }
    if (administrative_work)
        administrative_work->request();
    changed.notify_all();
    std::vector<std::shared_ptr<Session>> sessions;
    std::vector<std::shared_ptr<ProviderConnection>> connections;
    {
        std::lock_guard lock(mutex);
        for (const auto& child : children)
            if (auto session = child.lock())
                sessions.push_back(std::move(session));
        connections.swap(idle);
    }
    shapes.clear();
    {
        std::lock_guard lock(registry_mutex);
        models.clear();
        projections.clear();
        configured.clear();
        relations.clear();
        registry_bytes = 0;
    }
    for (auto& session : sessions)
        session->request_close();
    for (auto& connection : connections)
        connection->close();
    changed.notify_all();
}
void Source::join()
{
    request_close();
    std::lock_guard control(join_mutex);
    if (retired.load())
        return;
    {
        std::unique_lock lock(mutex);
        while (leased != 0 || pending.load() != 0)
        {
#ifdef NW_HOST_TEST_HOOKS
            if (test_before_join_wait)
                test_before_join_wait();
#endif
            changed.wait(lock);
        }
        admission_stop = true;
    }
    changed.notify_all();
    if (admission_thread.joinable())
        admission_thread.join();
    // The join caller retains this Source. Wait without its state mutex and
    // before stopping the pools which descendant cleanup can still use.
#ifdef NW_HOST_TEST_HOOKS
    if (!transaction_workers->done() && test_before_transaction_wait)
        test_before_transaction_wait();
#endif
    transaction_workers->wait();
    pull_workers->wait();
    workers.stop();
    controls.stop();
    retired.store(true);
}
Bytes Source::snapshot() const
{
    const bool done = retired.load();
    return snapshot_record(0, 0, false, done ? 2 : closing.load() ? 1 : 0, done ? 3 : 0, done, false, 0);
}

void Source::registry_capacity(std::size_t bytes) const
{
    if (configured.size() + models.size() + projections.size() + relations.size() >= config.limits.nodes ||
        bytes > config.limits.parameter_bytes - std::min(config.limits.parameter_bytes, registry_bytes))
        throw Error::capacity();
}
std::shared_ptr<const CodecBindings> Source::codecs()
{
    std::lock_guard lock(registry_mutex);
    return std::make_shared<CodecBindings>(config.provider.profile, configured);
}
std::uint32_t Source::register_codec(std::uint32_t logical, std::optional<std::string> configuration)
{
    admit();
    Codec codec{logical, std::move(configuration), false};
    codec.validate(config.provider.profile);
    if (!codec.configuration)
    {
        (void)CodecBindings(config.provider.profile).get(logical, false);
        return logical;
    }
    std::lock_guard lock(registry_mutex);
    admit();
    for (const auto& [id, previous] : configured)
        if (previous.same_scalar(codec))
            return id;
    registry_capacity(codec.configuration->size());
    const auto id = static_cast<std::uint32_t>(1024 + configured.size());
    registry_bytes += codec.configuration->size();
    configured.emplace_back(id, std::move(codec));
    return id;
}
ModelBinding Source::register_model(ByteView bytes)
{
    admit();
    const auto fields = Fields::parse(bytes, 2, {{1, 5, true}, {2, 5, true}});
    const auto canonical = fields.bytes(1);
    const auto hash = sha256(canonical);
    if (fields.bytes(2).size() != hash.size() || !std::equal(hash.begin(), hash.end(), fields.bytes(2).begin()))
        throw Error::invalid("metadata content hash");
    auto model = std::make_shared<Model>(Model::parse(canonical, config.provider.profile));
    auto bindings = codecs();
    std::lock_guard lock(registry_mutex);
    admit();
    if (auto found = models.find(hash); found != models.end())
    {
        if (found->second->bytes() != model->bytes())
            throw Error::invalid("metadata hash collision");
        return {identity, found->second, bindings};
    }
    for (const auto& [key, previous] : models)
        if (previous->table_id() == model->table_id())
            throw Error::invalid("table ID collision");
    registry_capacity(canonical.size());
    ModelBinding binding(identity, model, bindings);
    registry_bytes += canonical.size();
    models.emplace(hash, std::move(model));
    return binding;
}
ProjectionBinding Source::register_projection(ByteView bytes)
{
    admit();
    auto bindings = codecs();
    std::lock_guard lock(registry_mutex);
    admit();
    auto binding = projection_record(bytes, identity, next_projection, std::move(bindings));
    const auto hash = binding.projection->hash();
    if (auto found = projections.find(hash); found != projections.end())
    {
        if (found->second.projection->bytes() != binding.projection->bytes())
            throw Error::invalid("projection hash collision");
        return found->second;
    }
    registry_capacity(bytes.size());
    ++next_projection;
    registry_bytes += bytes.size();
    projections.emplace(hash, binding);
    return binding;
}
ProjectionBinding Source::resolve_projection(ProjectionBinding binding)
{
    admit();
    if (binding.source != identity)
        throw Error::state("mixed projection source");
    std::lock_guard lock(registry_mutex);
    admit();
    const auto hash = binding.projection->hash();
    if (auto found = projections.find(hash); found != projections.end())
    {
        if (found->second.projection->bytes() != binding.projection->bytes())
            throw Error::invalid("projection hash collision");
        return found->second;
    }
    registry_capacity(binding.projection->bytes().size());
    binding.id = next_projection++;
    registry_bytes += binding.projection->bytes().size();
    projections.emplace(hash, binding);
    return binding;
}
ProjectionBinding Source::projection(std::uint32_t id)
{
    std::lock_guard lock(registry_mutex);
    for (const auto& [hash, binding] : projections)
        if (binding.id == id)
            return binding;
    throw Error::invalid("unregistered projection");
}
std::shared_ptr<RelationBinding> Source::register_relation(ModelBinding parent, ModelBinding child, ByteView bytes)
{
    admit();
    auto binding =
        RelationBinding::create(identity, std::move(parent), std::move(child), bytes, {true, true, true, true, true});
    std::lock_guard lock(registry_mutex);
    admit();
    const auto hash = binding->relation->hash();
    if (auto found = relations.find(hash); found != relations.end())
    {
        if (found->second->relation->bytes() != binding->relation->bytes())
            throw Error::invalid("relation hash collision");
        return found->second;
    }
    registry_capacity(bytes.size());
    registry_bytes += bytes.size();
    relations.emplace(hash, binding);
    return binding;
}

Owner::Owner(std::shared_ptr<Source> parent, OwnerData value) : source(std::move(parent)), data(std::move(value)) {}
Owner::~Owner()
{
    try
    {
        if (std::holds_alternative<std::monostate>(data))
            source->request_close();
        else if (auto session = std::get_if<std::shared_ptr<Session>>(&data))
            (*session)->request_close();
        else if (auto cursor = std::get_if<std::shared_ptr<Cursor>>(&data))
            (*cursor)->request_close();
        else if (auto pull = std::get_if<std::shared_ptr<CursorPull>>(&data))
            (*pull)->request_close();
        else if (auto transaction = std::get_if<std::shared_ptr<Transaction>>(&data))
            (*transaction)->request_close();
        else if (auto savepoint = std::get_if<std::shared_ptr<Savepoint>>(&data))
            (*savepoint)->request_close();
    }
    catch (...)
    {
        source->poisoned.store(true);
    }
}
std::uint32_t Owner::kind() const
{
    return data.index() >= 1 && data.index() <= 4 ? static_cast<std::uint32_t>(data.index()) : 0;
}
std::shared_ptr<StreamReservation> Source::reserve_stream(std::size_t bytes)
{
    auto reservation = std::make_shared<StreamReservation>();
    reservation->bytes = bytes;
    {
        std::lock_guard lock(stream_mutex);
        if (stream_stats[0] >= config.limits.connections || bytes > stream_max_bytes - stream_stats[1])
            throw Error::capacity();
        ++stream_stats[0];
        stream_stats[1] += bytes;
        stream_stats[2] = std::max(stream_stats[2], stream_stats[1]);
        reservation->source = shared_from_this();
    }
    return reservation;
}
StreamReservation::~StreamReservation()
{
    if (source)
    {
        std::lock_guard lock(source->stream_mutex);
        --source->stream_stats[0];
        source->stream_stats[1] -= bytes;
    }
}
Buffer::Buffer(std::shared_ptr<Source> parent, Bytes value, std::shared_ptr<Cursor> cursor_owner, bool end_known)
    : source(std::move(parent)), bytes(std::move(value)), cursor(std::move(cursor_owner)), known_end(end_known)
{
    if (cursor)
    {
        std::lock_guard lock(source->stream_mutex);
        ++source->stream_stats[3];
        source->stream_stats[4] += bytes.size();
        source->stream_stats[5] = std::max(source->stream_stats[5], source->stream_stats[4]);
    }
    ++buffer_count;
}
void Buffer::mark_taken()
{
    if (cursor && !taken.exchange(true))
    {
        std::lock_guard lock(source->stream_mutex);
        ++source->stream_stats[6];
    }
}
Buffer::~Buffer()
{
    if (cursor)
    {
        {
            std::lock_guard lock(source->stream_mutex);
            --source->stream_stats[3];
            source->stream_stats[4] -= bytes.size();
        }
        cursor->batch_live.store(false);
    }
    --buffer_count;
}

DbOperation::DbOperation(std::shared_ptr<Source> parent, std::uint32_t kind, bool reserved,
                         std::function<Value(std::shared_ptr<Cancel>)> action, Dispatch mode)
    : source(std::move(parent)), work(std::move(action)), result_kind(kind), dispatch(mode), counted(reserved),
      admission_deadline(Clock::now() + std::chrono::nanoseconds(source->config.limits.admission_ns))
{
    ++operation_count;
}
std::shared_ptr<DbOperation> DbOperation::create(std::shared_ptr<Source> source, std::uint32_t kind, bool control,
                                                 std::function<Value(std::shared_ptr<Cancel>)> work, Dispatch dispatch)
{
    bool counted = false;
    if (dispatch == Dispatch::SourceClose)
    {
        const auto previous = source->close_waiters.fetch_add(1);
        if (previous >= source->config.limits.connections + 1)
        {
            --source->close_waiters;
            throw Error::capacity();
        }
    }
    else
        counted = source->reserve_operation(control);
    try
    {
        return std::shared_ptr<DbOperation>(new DbOperation(source, kind, counted, std::move(work), dispatch));
    }
    catch (...)
    {
        if (counted)
            source->release_operation();
        if (dispatch == Dispatch::SourceClose)
            --source->close_waiters;
        throw;
    }
}
DbOperation::~DbOperation()
{
    if (counted)
        source->release_operation();
    if (dispatch == Dispatch::SourceClose)
        --source->close_waiters;
    --operation_count;
}
nw_status DbOperation::start(nw_operation_callbacks_v1 callbacks)
{
    const auto status = core->start(callbacks);
    if (status != NW_OK)
        return status;
    auto [reserved, worker] = core->reserve_source();
    if (reserved != NW_OK)
        return reserved;
    lease = std::make_shared<WorkLease<Value>>(std::move(worker));
    auto self = shared_from_this();
    try
    {
        if (dispatch == Dispatch::Admission)
            source->queue_admission(self);
        else if (dispatch == Dispatch::Administration)
            source->queue_administration(self);
        else if (dispatch == Dispatch::SourceClose)
            std::thread([self] { self->run(); }).detach();
        else if (dispatch == Dispatch::Control && counted)
            source->controls.post([self] { self->run(); });
        else if (!counted)
            run();
        else
            source->workers.post([self] { self->run(); });
    }
    catch (const Error& error)
    {
        fail(error);
    }
    catch (...)
    {
        fail(Error::capacity());
    }
    return NW_OK;
}
void DbOperation::run()
{
    try
    {
        if (dispatch == Dispatch::Administration)
        {
            source->admit();
            if (cancel->requested())
                throw Error::canceled();
        }
        auto action = std::move(work);
        auto value = action(cancel);
        // The administrative action owns its dedicated physical connection
        // until it closes. Retained result/callback handles do not own its permit.
        release_administration();
        complete(std::move(value));
    }
    catch (const Error& error)
    {
        release_administration();
        fail(error);
    }
    catch (const std::bad_alloc&)
    {
        release_administration();
        fail(Error(NW_OUT_OF_MEMORY, 8, "native database allocation failed"));
    }
    catch (...)
    {
        release_administration();
        source->poisoned.store(true);
        fail(Error(NW_NATIVE_PANIC, 8, "native database exception contained"));
    }
}
void DbOperation::release_administration()
{
    if (administration_reserved.exchange(false))
        source->finish_administration();
}
void DbOperation::complete(Value value)
{
    cancel->detach();
    (void)core->complete(NW_OK, std::move(value));
    if (core->snapshot().delivery_failed)
        source->poisoned.store(true);
    lease.reset();
}
void DbOperation::fail(Error failure)
{
    cancel->detach();
    const auto status = failure.status;
    const auto fields = failure.fields();
    {
        std::lock_guard lock(mutex);
        error = std::move(failure);
    }
    (void)core->complete(status, {}, fields);
    if (core->snapshot().delivery_failed)
        source->poisoned.store(true);
    work = {};
    lease.reset();
}

std::shared_ptr<SqlPlan> SqlPlan::parse(std::shared_ptr<Source> source, ByteView sql_bytes, ByteView values,
                                        ByteView options)
{
    source->admit();
    const auto& limits = source->config.limits;
    if (sql_bytes.size() > limits.parameter_bytes || values.size() > limits.parameter_bytes)
        throw Error::capacity();
    const auto fields = Fields::parse(
        options, 20, {{1, 1, true}, {2, 1, true}, {3, 3, true}, {4, 1, true}, {5, 5, true}, {6, 1, true}});
    auto plan = std::make_shared<SqlPlan>();
    plan->source = source;
    plan->kind = fields.u32(1);
    plan->result_kind = fields.u32(2);
    plan->timeout_ns = fields.u64(3);
    const auto projection_id = fields.u32(4);
    if (plan->kind > 2 || plan->result_kind > 3 || (plan->result_kind == 0 && plan->kind == 0) ||
        (plan->result_kind != 0 && plan->kind != 0) || (plan->result_kind == 0 && projection_id != 0) ||
        (plan->result_kind != 0 && projection_id == 0))
        throw Error::invalid("command/result kind mismatch");
    if (plan->timeout_ns > hour_ns)
        throw Error::invalid("command deadline");
    auto definitions = sequence(fields.bytes(5));
    if (definitions.size() > limits.parameters)
        throw Error::capacity();
    auto codecs = source->codecs();
    std::map<std::string, std::uint32_t> names;
    std::string schema = "{\"version\":1,\"parameters\":[";
    Expectation expected{1, source->config.provider.profile, {}, 0, 0, {}, 1};
    for (std::size_t index = 0; index < definitions.size(); ++index)
    {
        const auto definition =
            Fields::parse(definitions[index], 21, {{1, 1, true}, {2, 4, true}, {3, 1, true}, {4, 1, true}});
        const auto id = definition.u32(1);
        std::string name(definition.text(2));
        if (id != index + 1 || name.empty() || name.size() > 128 ||
            !std::all_of(name.begin(), name.end(),
                         [n = std::size_t{0}](unsigned char c) mutable
                         {
                             const auto index = n++;
                             return c == '_' || (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') ||
                                    (index > 0 && c >= '0' && c <= '9');
                         }) ||
            !names.emplace(name, id).second)
            throw Error::invalid("parameter identity");
        const auto bound = definition.u32(3);
        const auto codec = codecs->get(bound, definition.boolean(4));
        if (index)
            schema += ',';
        schema += "{\"id\":" + std::to_string(id) + ",\"name\":" + json_quote(name) +
                  ",\"codec\":" + std::to_string(codec.id) +
                  ",\"codec_config\":" + codec.configuration.value_or("null") +
                  ",\"nullable\":" + (codec.nullable ? "true" : "false") + "}";
        expected.descriptors.push_back({id, codec, bound});
    }
    schema += "]}";
    expected.hash = sha256(text_view(schema));
    plan->expectation = std::move(expected);
    plan->capture_parameters(values);
    std::string sql;
    if (fields.u32(6) == 0)
    {
        if (!valid_utf8(sql_bytes) || std::find(sql_bytes.begin(), sql_bytes.end(), 1) != sql_bytes.end() ||
            std::find(sql_bytes.begin(), sql_bytes.end(), 2) != sql_bytes.end())
            throw Error::invalid("reserved SQL template marker");
        sql.assign(reinterpret_cast<const char*>(sql_bytes.data()), sql_bytes.size());
    }
    else if (fields.u32(6) == 1)
        sql = decode_interpolated_sql(sql_bytes);
    else
        throw Error::invalid("SQL template kind");
    plan->sql = render_sql_template(sql, names, source->config.provider.profile, plan->kind).sql;
    if (plan->result_kind != 0)
        plan->projection = source->projection(projection_id);
    return plan;
}
std::shared_ptr<SqlPlan> SqlPlan::rendered(std::shared_ptr<Source> source, RenderedQuery rendered)
{
    auto plan = std::make_shared<SqlPlan>();
    plan->source = source;
    plan->sql = std::move(rendered.sql);
    plan->arguments = std::move(rendered.arguments);
    plan->parameter_wire_bytes = rendered.parameter_wire_bytes;
    plan->expectation = std::move(rendered.parameter_expectation);
    plan->timeout_ns = rendered.timeout_ns;
    plan->submitted.store(true);
    plan->scalar_count = rendered.terminal == 4 || rendered.terminal == 5;
    plan->result_kind = (rendered.terminal == 6 || rendered.terminal == 7) ? 0 : plan->scalar_count ? 1 : 3;
    plan->kind = plan->result_kind == 0 ? 1 : 0;
    if (plan->scalar_count)
    {
        const auto scalar =
            Projection::parse_scalar(text_view("{\"version\":1,\"fields\":[{\"ordinal\":0,\"name\":\"\",\"codec\":3,"
                                               "\"codec_config\":null,\"nullable\":false}]}"),
                                     source->config.provider.profile);
        plan->projection =
            source->resolve_projection({source->identity, 1, std::make_shared<Projection>(scalar), source->codecs()});
    }
    else if (rendered.projection)
        plan->projection = source->resolve_projection(std::move(*rendered.projection));
    return plan;
}
void SqlPlan::capture_parameters(ByteView values)
{
    const auto batch = BatchView::parse(values, expectation);
    std::vector<Scalar> accepted;
    accepted.reserve(expectation.descriptors.size());
    for (std::size_t i = 0; i < expectation.descriptors.size(); ++i)
    {
        const auto value = batch.cell(0, i);
        accepted.push_back({expectation.descriptors[i].codec,
                            value ? std::optional<Bytes>(Bytes(value->begin(), value->end())) : std::nullopt});
    }
    parameters.assign(values.begin(), values.end());
    arguments = std::move(accepted);
    parameter_wire_bytes = values.size();
}

void SqlPlan::submit(const Source& owner)
{
    if (source->identity != owner.identity)
        throw Error::state("plan belongs to another source");
    if (submitted.exchange(true))
        throw Error::state("raw plan already submitted");
}

CommandGate::CommandGate(std::shared_ptr<Session> parent) : session(std::move(parent)) {}
CommandGate::~CommandGate()
{
    try
    {
        finish(dispatched && !completed);
    }
    catch (...)
    {
        // Finishing a gate may schedule parent cleanup. A launch failure is
        // not permitted to escape a destructor during error unwinding.
        session->discard.store(true);
        session->source->poisoned.store(true);
    }
}
void CommandGate::finish(bool failed)
{
    if (completed)
        return;
    completed = true;
    if (dispatched && failed)
    {
        std::shared_ptr<Transaction> tx;
        {
            std::lock_guard lock(session->mutex);
            tx = session->transaction.lock();
        }
        if (tx)
            tx->command_failed();
    }
    session->active.store(false);
    session->changed.notify_all();
    std::shared_ptr<Transaction> tx;
    {
        std::lock_guard lock(session->mutex);
        tx = session->transaction.lock();
    }
    if (tx)
        tx->schedule_cleanup();
    if (session->closing.load())
        session->schedule_cleanup();
}
std::shared_ptr<Session> Session::open_reserved(std::shared_ptr<Source> source, std::shared_ptr<Cancel> cancel)
{
    std::shared_ptr<ProviderConnection> connection;
    bool transferred = false;
    try
    {
        source->admit();
        if (cancel->requested())
            throw Error::canceled();
        const bool postgres = source->config.provider.profile == Profile::PostgreSql;
        // Host admission already owns its separate slot. The lower PostgreSQL
        // pool acquire has one further budget for idle testing and replacement.
        const auto acquire_ns =
            postgres ? std::min(source->config.limits.admission_ns, source->config.provider.connect_timeout_ns)
                     : source->config.limits.admission_ns;
        const CallContext acquisition{cancel, Clock::now() + std::chrono::nanoseconds(acquire_ns)};
        const auto check_acquisition = [&]
        {
            if (cancel->requested())
                throw Error::canceled();
            if (Clock::now() >= acquisition.deadline)
                throw Error(NW_DOMAIN_ERROR, 1, "PostgreSQL pool acquisition timed out");
        };
        {
            std::lock_guard lock(source->mutex);
            if (!source->idle.empty())
            {
                connection = std::move(source->idle.back());
                source->idle.pop_back();
            }
        }
        if (connection && postgres)
        {
            try
            {
                connection->verify_idle(acquisition);
            }
            catch (...)
            {
                connection->close();
                connection.reset();
                check_acquisition();
            }
        }
        if (!connection)
        {
            try
            {
                connection = ProviderConnection::open(source->config.provider, acquisition, postgres);
            }
            catch (const Error& error)
            {
                if (postgres)
                {
                    check_acquisition();
                    if (error.status == NW_TIMEOUT)
                        throw Error(NW_DOMAIN_ERROR, 1, "PostgreSQL pool acquisition timed out");
                }
                throw;
            }
        }
        if (postgres)
        {
            check_acquisition();
            connection->initialize_session();
        }
        auto session = std::make_shared<Session>();
        session->source = source;
        session->connection = connection;
        ++session_count;
        {
            std::lock_guard lock(source->mutex);
            source->children.erase(std::remove_if(source->children.begin(), source->children.end(),
                                                  [](const auto& child) { return child.expired(); }),
                                   source->children.end());
            source->children.push_back(session);
        }
        transferred = true;
        if (cancel->requested() || source->closing.load())
        {
            session->request_close();
            session->join();
            throw Error::canceled();
        }
        return session;
    }
    catch (...)
    {
        if (!transferred)
            source->return_connection(std::move(connection), true);
        throw;
    }
}
Session::~Session()
{
    --session_count;
}
std::shared_ptr<CommandGate> Session::admit(bool transaction_control)
{
    source->admit();
    if (closing.load())
        throw Error::closed();
    if (active.exchange(true))
        throw Error(NW_DOMAIN_ERROR, 7, "concurrent session operation");
    auto gate = std::make_shared<CommandGate>(shared_from_this());
    if (closing.load() || source->closing.load())
        throw Error::closed();
    if (!transaction_control)
    {
        std::shared_ptr<Transaction> tx;
        {
            std::lock_guard lock(mutex);
            tx = transaction.lock();
        }
        if (tx)
        {
            std::lock_guard lock(tx->mutex);
            if (!tx->retired && (tx->closing || tx->state != 0))
                throw Error::state("transaction admission rejected");
        }
    }
    return gate;
}
std::shared_ptr<Cursor> Session::open_cursor(std::shared_ptr<SqlPlan> plan, std::shared_ptr<Cancel> cancel,
                                             std::shared_ptr<CommandGate> gate)
{
    if (cancel->requested())
        throw Error::canceled();
    if (plan->timeout_ns == 0)
        throw Error(NW_TIMEOUT, 8, "command total deadline expired");
    const auto deadline = Clock::now() + std::chrono::nanoseconds(plan->timeout_ns);
    {
        std::lock_guard lock(mutex);
        current_cancel = cancel;
    }
    gate->dispatched = true;
    try
    {
        auto cursor = Cursor::open(shared_from_this(), plan, cancel, gate, deadline);
        {
            std::lock_guard lock(mutex);
            cursors.erase(
                std::remove_if(cursors.begin(), cursors.end(), [](const auto& child) { return child.expired(); }),
                cursors.end());
            cursors.push_back(cursor);
        }
        if (closing.load() || source->closing.load())
        {
            cursor->close_now();
            throw Error::closed();
        }
        return cursor;
    }
    catch (...)
    {
        gate->finish(true);
        throw;
    }
}
Value Session::execute(std::shared_ptr<SqlPlan> plan, std::shared_ptr<Cancel> cancel, std::shared_ptr<CommandGate> gate)
{
    if (plan->result_kind != 0)
    {
        auto cursor = open_cursor(plan, cancel, gate);
        try
        {
            const auto& limits = source->config.limits;
            if (plan->scalar_count)
            {
                auto buffer = cursor->fetch(cancel, 2, limits.batch_bytes);
                auto batch = Batch::parse(buffer->bytes, cursor->expectation);
                if (batch.rows() != 1)
                {
                    cursor->close_now();
                    throw Error(NW_DOMAIN_ERROR, 4, "count cardinality");
                }
                auto cell = batch.cell(0, 0);
                if (!cell || cell->size() != 8)
                {
                    cursor->close_now();
                    throw Error::state("count scalar width");
                }
                auto count = static_cast<std::int64_t>(read_u64(*cell, 0));
                cursor->close_now();
                return count;
            }
            return std::make_shared<Owner>(source, cursor);
        }
        catch (...)
        {
            gate->finish(true);
            throw;
        }
    }
    if (cancel->requested())
        throw Error::canceled();
    if (plan->timeout_ns == 0)
        throw Error(NW_TIMEOUT, 8, "command total deadline expired");
    const auto deadline = Clock::now() + std::chrono::nanoseconds(plan->timeout_ns);
    {
        std::lock_guard lock(mutex);
        current_cancel = cancel;
    }
    gate->dispatched = true;
    if (plan->kind == 2)
        discard.store(true);
    try
    {
        if (plan->result_kind == 0)
        {
            const auto& parameters = command_parameters(*this, *plan);
            const bool observe = source->config.provider.profile == Profile::Sqlite;
            std::int64_t count;
            try
            {
                count = connection->execute(plan->sql, parameters, {cancel, deadline, observe});
            }
            catch (...)
            {
                // The original PostgreSQL worker always drains after execution,
                // while result.and_then keeps an existing business error first.
                try
                {
                    connection->synchronize_protocol();
                }
                catch (...)
                {
                }
                retire_failed_provider();
                throw;
            }
            try
            {
                connection->synchronize_protocol();
            }
            catch (...)
            {
                retire_failed_provider();
                throw;
            }
            gate->finish();
            if (plan->kind == 2)
            {
                discard.store(true);
                request_close();
                join();
            }
            return count;
        }
        throw Error::state("nonquery result kind changed");
    }
    catch (...)
    {
        gate->finish(true);
        if (plan->kind == 2)
        {
            request_close();
            join();
        }
        throw;
    }
}
void Session::request_close()
{
    if (closing.exchange(true))
    {
        schedule_cleanup();
        return;
    }
    std::vector<std::shared_ptr<Cursor>> live;
    std::vector<std::shared_ptr<CursorPull>> live_pulls;
    std::shared_ptr<Transaction> tx;
    {
        std::lock_guard lock(mutex);
        for (const auto& child : cursors)
            if (auto cursor = child.lock())
                live.push_back(cursor);
        for (const auto& child : pulls)
            if (auto pull = child.lock())
                live_pulls.push_back(std::move(pull));
        tx = transaction.lock();
        if (auto cancel = current_cancel.lock())
            cancel->request();
    }
    for (auto& cursor : live)
        cursor->request_close();
    for (auto& pull : live_pulls)
        pull->request_close();
    if (tx)
        tx->request_close();
    schedule_cleanup();
}
void Session::schedule_cleanup()
{
    if (!closing.load() || active.load() || retired.load())
        return;
    std::shared_ptr<Transaction> tx;
    {
        std::lock_guard lock(mutex);
        tx = transaction.lock();
    }
    if (tx)
    {
        std::lock_guard lock(tx->mutex);
        if (!tx->retired)
            return;
    }
    if (cleanup_scheduled.exchange(true))
        return;
    try
    {
        auto self = shared_from_this();
        source->workers.post([self] { self->retire_now(); });
    }
    catch (...)
    {
        // No worker owns this retirement yet. Keep a later close retryable,
        // including a failed post reached through CommandGate::finish.
        cleanup_scheduled.store(false);
        throw;
    }
}
void Session::retire_now()
{
    const bool postgres = source->config.provider.profile == Profile::PostgreSql;
    bool invalid = discard.load() || !connection->healthy() || physical_retired.load();
    std::optional<std::string> code;
    if (!invalid && connection->in_transaction())
    {
        if (postgres)
        {
            // PostgreSQL Session::request_close never returns an active explicit
            // transaction to the pool, even if a later rollback could succeed.
            invalid = true;
        }
        else
        {
            try
            {
                (void)connection->execute("ROLLBACK", {}, {{}, Clock::now() + std::chrono::seconds(5), false});
            }
            catch (const Error& error)
            {
                invalid = true;
                code = error.provider;
            }
        }
    }
    if (!invalid && postgres)
    {
        try
        {
            connection->synchronize_protocol();
        }
        catch (...)
        {
            invalid = true;
        }
    }
    // The old PostgreSQL Session records returned_to_pool once it invokes and
    // awaits that pool operation. The pool can then close on shutdown or after
    // its own failed ping; that hidden discard does not change this receipt.
    const bool returned_to_pool = !invalid && (postgres || !source->closing.load());
    bool reusable = !invalid && !source->closing.load();
    if (reusable && postgres)
        reusable = connection->confirm_pool_return();
    if (!physical_retired.load())
    {
        source->return_connection(std::move(connection), !reusable);
        physical_retired.store(true);
    }
    else
    {
        // The provider already destroyed its physical transport, but the Host
        // Session admission permit remains owned until this logical close.
        source->return_connection({}, true);
        connection.reset();
    }
    {
        std::lock_guard lock(mutex);
        cleanup = provider_cleanup_failed.load() ? 4 : 2;
        disposition = returned_to_pool ? 0 : 3;
        cleanup_provider = code;
        retired.store(true);
    }
    changed.notify_all();
}
void Session::retire_failed_provider()
{
    if (source->config.provider.profile != Profile::PostgreSql || connection->healthy())
        return;
    discard.store(true);
    // The lower PostgreSQL Session retires its physical lease independently of
    // the public Host owner. Its separate Host MaxConnections permit remains
    // charged until retire_now. Keep the inert provider for the closed error.
    // This path still owns the Session gate; publish after actual destruction.
    if (!physical_retired.load())
    {
        connection->close();
        physical_retired.store(true);
    }
}
void Session::join()
{
    std::unique_lock lock(mutex);
    changed.wait(lock, [&] { return retired.load(); });
}
Bytes Session::snapshot() const
{
    std::lock_guard lock(mutex);
    return snapshot_record(0, 0, false,
                           cleanup          ? cleanup
                           : closing.load() ? 1
                                            : 0,
                           disposition, retired.load(), false, 0, cleanup_provider);
}

std::shared_ptr<Cursor> Cursor::open(std::shared_ptr<Session> session, std::shared_ptr<SqlPlan> plan,
                                     std::shared_ptr<Cancel> cancel, std::shared_ptr<CommandGate> gate,
                                     Clock::time_point deadline)
{
    if (!plan->projection)
        throw Error::state("stream projection missing");
    auto cursor = std::make_shared<Cursor>();
    ++cursor_count;
    cursor->session = session;
    cursor->plan = plan;
    cursor->gate = std::move(gate);
    cursor->deadline = deadline;
    const auto& projection = *plan->projection;
    cursor->expectation = {
        2, session->source->config.provider.profile, projection.projection->hash(), 0, projection.id, {}, std::nullopt};
    for (std::size_t i = 0; i < projection.projection->fields().size(); ++i)
    {
        const auto& field = projection.projection->fields()[i];
        cursor->codecs.push_back(field.codec);
        cursor->expectation.descriptors.push_back(
            {static_cast<std::uint32_t>(i), field.codec, projection.codecs->bound(field.codec)});
    }
    const auto& limits = session->source->config.limits;
    if (session->source->config.provider.profile == Profile::Sqlite)
    {
        // Rust Host describes SQLite SQL with a SQL-only grant before the
        // stream's SQL + two-wire input grant. Preserve missing-table/syntax
        // failure precedence without executing or copying parameter values.
        (void)sqlite_input_remaining(*session, *plan);
        cursor->statement = session->connection->prepare_unbound(plan->sql, {cancel, deadline});
    }
    const auto& parameters = command_parameters(*session, *plan);
    try
    {
        if (cursor->statement)
            cursor->statement->bind_parameters(parameters);
        else
            cursor->statement = session->connection->query(plan->sql, parameters, {cancel, deadline});
    }
    catch (...)
    {
        if (!cursor->statement)
        {
            // Description failures still consume their independent confirmation,
            // but never replace the original SQL/shape/provider error.
            try
            {
                session->connection->synchronize_protocol();
            }
            catch (...)
            {
            }
        }
        session->retire_failed_provider();
        throw;
    }
    // The original Host prepares provider inputs before B06 admits its row
    // buffers. Keep that error precedence, while still reserving all row bytes
    // before this implementation can execute the prepared statement.
    if (!limits.batch_rows || limits.batch_rows > MAX_NODES || !limits.batch_bytes || limits.batch_bytes > MAX_BYTES)
        throw Error::capacity();
    if (96 + 16 * cursor->codecs.size() + 24 * cursor->codecs.size() > limits.batch_bytes)
        throw Error(NW_DOMAIN_ERROR, 14, "single row descriptors exceed batch capacity");
    // Preserve the previous admission grant until peak-lifetime measurements
    // justify reducing it. These are conservative bookkeeping credits; no
    // owning row or cell-vector staging remains on the result path.
    const auto reserved = 5 * limits.batch_bytes +
                          limits.batch_rows * (sizeof(std::vector<std::optional<Bytes>>) + sizeof(std::size_t)) +
                          3 * projection.projection->bytes().size() +
                          cursor->codecs.size() * (sizeof(Descriptor) + sizeof(ProviderColumn));
    cursor->reservation = session->source->reserve_stream(reserved);
    const auto& columns = cursor->statement->columns();
    if (columns.size() != cursor->codecs.size())
        throw Error(NW_DOMAIN_ERROR, 4, "complete result column count differs");
    for (std::size_t i = 0; i < columns.size(); ++i)
    {
        const auto& field = projection.projection->fields()[i];
        if ((!field.name.empty() && field.name != columns[i].name) ||
            !type_matches(session->source->config.provider.profile, field.codec.id,
                          columns[i].type_name ? std::optional<std::string_view>(*columns[i].type_name) : std::nullopt))
            throw Error(NW_DOMAIN_ERROR, 4, "result ordinal, alias or database type differs");
    }
    cancel->detach();
    return cursor;
}
Cursor::~Cursor()
{
    --cursor_count;
}
namespace
{
struct CursorReadAdmission
{
    Cursor& cursor;
    explicit CursorReadAdmission(Cursor& value) : cursor(value)
    {
        if (cursor.active.exchange(true))
            throw Error(NW_DOMAIN_ERROR, 7, "concurrent cursor fetch");
    }
    ~CursorReadAdmission()
    {
        cursor.active.store(false);
        cursor.changed.notify_all();
        if (cursor.closing.load())
            cursor.schedule_cleanup();
    }
    void check() const
    {
        if (cursor.closing.load() || cursor.retired.load())
            throw Error::closed();
        if (cursor.batch_live.load())
            throw Error::state("previous row batch remains live");
        if (cursor.end_sent)
            throw Error::state("cursor end already transferred");
    }
};
} // namespace
void Cursor::check_read_admission()
{
    session->source->admit();
    CursorReadAdmission admission(*this);
    admission.check();
}
std::shared_ptr<Buffer> Cursor::fetch(std::shared_ptr<Cancel> cancel, std::size_t rows, std::size_t bytes)
{
    CursorReadAdmission admission(*this);
    admission.check();
    if (cancel->requested())
        throw Error::canceled();
    {
        std::lock_guard lock(mutex);
        current_cancel = cancel;
    }
    const auto& limits = session->source->config.limits;
    if (!rows || rows > limits.batch_rows || !bytes || bytes > limits.batch_bytes)
        throw Error::capacity();
    const std::size_t base = 96 + 16 * codecs.size(), per_row = 24 * codecs.size();
    if (base + per_row > bytes)
        throw Error(NW_DOMAIN_ERROR, 14, "single row descriptors exceed batch capacity");
    try
    {
        BatchWriter writer(expectation, static_cast<std::uint32_t>(rows), bytes);
        while (writer.rows() < rows)
        {
            RowAppendResult result{RowAppendState::End, false};
            if (!ended)
            {
                result = statement->append_next(writer, codecs,
                                                std::min({limits.field_bytes, bytes - base - per_row, MAX_BYTES}),
                                                {cancel, deadline});
                if (result.advanced)
                {
                    ++rows_pulled;
                    provider_rows_peak = std::max<std::size_t>(provider_rows_peak, 1);
                }
            }
            if (result.state == RowAppendState::End)
            {
                ended = true;
                retire_provider();
                break;
            }
            if (result.state == RowAppendState::Full)
                break;
        }
        if (writer.rows() == 0)
            end_sent = true;
        auto encoded = writer.finish();
        batch_live.store(true);
        cancel->detach();
        return std::make_shared<Buffer>(session->source, std::move(encoded), shared_from_this(), ended);
    }
    catch (...)
    {
        stop_observed = cancel->requested();
        failed = true;
        closing.store(true);
        cancel->detach();
        throw;
    }
}
void Cursor::request_close()
{
    closing.store(true);
    {
        std::lock_guard lock(mutex);
        if (auto cancel = current_cancel.lock())
            cancel->request();
    }
    schedule_cleanup();
}
void Cursor::schedule_cleanup() noexcept
{
    if (active.load() || retired.load() || cleanup_scheduled.exchange(true))
        return;
    try
    {
        auto completion = completion_;
        auto self = shared_from_this();
        session->source->workers.post(
            [self = std::move(self), completion = std::move(completion)]() mutable
            {
                self->close_resources();
                // A successful join must not race the cleanup worker's last owner.
                // The independent ticket survives even if this destroys the cursor.
                self.reset();
                completion->publish();
            });
    }
    catch (...)
    {
        // This method also runs from CursorReadAdmission's destructor. A
        // failed cleanup queue must neither terminate that worker nor strand
        // a join forever behind a cleanup_scheduled bit without a worker.
        quarantine_cleanup();
    }
}
void Cursor::close_now()
{
    if (cleanup_scheduled.exchange(true))
        return;
    close_resources();
    completion_->publish();
}
void Cursor::close_resources()
{
    if (close_started.exchange(true))
        return;
    closing.store(true);
    try
    {
#ifdef NW_HOST_TEST_HOOKS
        if (test_retire_gate)
            test_retire_gate();
#endif
        retire_provider();
        if (gate)
        {
            gate->finish(failed);
            gate.reset();
        }
        retired.store(true);
#ifdef NW_HOST_TEST_HOOKS
        if (test_after_cleanup_gate)
            test_after_cleanup_gate();
#endif
    }
    catch (...)
    {
        quarantine_cleanup();
    }
}
void Cursor::quarantine_cleanup() noexcept
{
    // A cleanup exception is not evidence of native retirement. Retain the
    // bounded reservation and physical accessor without a fallible container
    // insertion. A failed join/snapshot must never certify these resources.
    retired.store(false);
    session->discard.store(true);
    session->source->poisoned.store(true);
    quarantine_ = weak_from_this().lock();
    cleanup_unconfirmed.store(true);
    completion_->publish();
}
void Cursor::retire_provider()
{
    if (statement)
    {
        // Natural EOF already consumed this execution's ReadyForQuery. An
        // unfinished reader still owes its bounded drain/confirmation. A
        // cleanup failure changes the receipt, not already delivered rows.
        statement->close(true);
        statement.reset();
    }
    if (session->source->config.provider.profile == Profile::PostgreSql && !session->connection->healthy())
    {
        protocol_quarantined.store(true);
        session->retire_failed_provider();
    }
}
void Cursor::Completion::publish()
{
    {
        std::lock_guard lock(mutex);
        done = true;
    }
    changed.notify_all();
}
void Cursor::join()
{
    auto completion = completion_;
    std::unique_lock lock(completion->mutex);
    while (!completion->done)
    {
#ifdef NW_HOST_TEST_HOOKS
        if (test_before_join_wait)
            test_before_join_wait();
#endif
        completion->changed.wait(lock);
    }
    if (cleanup_unconfirmed.load())
        throw Error(NW_DOMAIN_ERROR, 8, "provider retirement remains unconfirmed");
}
Bytes Cursor::snapshot() const
{
    std::lock_guard lock(completion_->mutex);
    const bool done = completion_->done && retired.load();
    return snapshot_record(0, 0, false,
                           cleanup_unconfirmed.load() ? 4
                           : done                     ? 2
                           : closing.load()           ? 1
                                                      : 0,
                           cleanup_unconfirmed.load() || protocol_quarantined.load() ? 2 : 0, done, false, 0);
}

struct CursorPull::Worker
{
    std::shared_ptr<CursorPull> pull;
    std::shared_ptr<Source> source;
    std::shared_ptr<RetirementFence> channel_done, source_done;
#ifdef NW_HOST_TEST_HOOKS
    std::function<void()> before_work, after_ready;
#endif
    explicit Worker(std::shared_ptr<CursorPull> value)
        : pull(std::move(value)), source(pull->session->source), channel_done(pull->completion_),
          source_done(source->pull_workers)
    {
        // Complete all potentially throwing setup before request acceptance.
#ifdef NW_HOST_TEST_HOOKS
        before_work = pull->test_before_work;
        after_ready = pull->test_after_ready;
#endif
        source->reserve_operation(false);
        channel_done->add();
        source_done->add();
    }
    ~Worker()
    {
        // The tickets outlive every native accessor, including the Source
        // capture used to return its reservation. A true join cannot race
        // these last references even after the public channel was abandoned.
        pull.reset();
        source->release_operation();
        source.reset();
        channel_done->complete();
        source_done->complete();
    }
    void run(std::uint64_t generation, std::size_t rows, std::size_t bytes, std::shared_ptr<Cancel> cancel)
    {
#ifdef NW_HOST_TEST_HOOKS
        if (before_work)
            before_work();
#endif
        pull->run(generation, rows, bytes, std::move(cancel));
        // No channel field or callback cookie is accessed past readiness.
#ifdef NW_HOST_TEST_HOOKS
        if (after_ready)
            after_ready();
#endif
    }
};

CursorPull::CursorPull(std::shared_ptr<Session> parent, std::shared_ptr<SqlPlan> plan,
                       std::shared_ptr<CommandGate> gate, std::optional<Clock::time_point> admitted)
    : session(std::move(parent)), plan_(std::move(plan)), gate_(std::move(gate)), admitted_(admitted)
{
    (void)cursor_cleanup_failure();
    ++pull_count;
}
std::shared_ptr<CursorPull> CursorPull::create(std::shared_ptr<Session> session, std::shared_ptr<SqlPlan> plan,
                                               std::shared_ptr<CommandGate> gate,
                                               std::optional<Clock::time_point> admitted)
{
    session->source->admit();
    if (!plan->result_kind || plan->scalar_count)
        throw Error::state("cursor result plan required");
    auto pull = std::shared_ptr<CursorPull>(new CursorPull(session, std::move(plan), std::move(gate), admitted));
    {
        std::lock_guard lock(session->mutex);
        session->pulls.erase(std::remove_if(session->pulls.begin(), session->pulls.end(),
                                            [](const auto& child) { return child.expired(); }),
                             session->pulls.end());
        session->pulls.push_back(pull);
    }
    if (session->closing.load() || session->source->closing.load())
    {
        pull->request_close();
        throw Error::closed();
    }
    return pull;
}
CursorPull::~CursorPull()
{
    try
    {
        request_close();
    }
    catch (...)
    {
        session->source->poisoned.store(true);
    }
    --pull_count;
}
void CursorPull::request(std::uint64_t generation, std::size_t rows, std::size_t bytes,
                         nw_db_cursor_callbacks_v1 callbacks)
{
    if (callbacks.struct_size != sizeof(callbacks) || callbacks.reserved || !callbacks.ready)
        throw Error::invalid("cursor ready callback record");
    const auto& limits = session->source->config.limits;
    if (!rows || rows > limits.batch_rows || !bytes || bytes > limits.batch_bytes)
        throw Error::invalid("fetch capacity");
    std::shared_ptr<Worker> worker;
    std::shared_ptr<Cancel> cancel;
    std::function<void()> action;
    {
        std::lock_guard lock(mutex_);
        session->source->admit();
        if (closing_ || session->closing.load())
            throw Error::closed();
        if (outstanding_ || running_)
            throw Error(NW_DOMAIN_ERROR, 7, "cursor request remains outstanding");
        if (!generation || generation_ == std::numeric_limits<std::uint64_t>::max() || generation != generation_ + 1)
            throw Error::state("cursor request generation differs");
        if (cursor_)
            cursor_->check_read_admission();
        cancel = std::make_shared<Cancel>();
        worker = std::make_shared<Worker>(shared_from_this());
        action = [worker, generation, rows, bytes, cancel] { worker->run(generation, rows, bytes, cancel); };
        generation_ = generation;
        outstanding_ = running_ = true;
        ready_ = false;
        error_.reset();
        buffer_.reset();
        callbacks_ = callbacks;
        cancel_ = cancel;
    }
    // Everything after this point belongs to the accepted generation. A
    // queue failure therefore delivers one error notification and returns OK.
    try
    {
        session->source->workers.post(std::move(action));
    }
    catch (Error& error)
    {
        complete(generation, {}, std::move(error));
    }
    catch (const std::bad_alloc&)
    {
        complete(generation, {}, Error(NW_OUT_OF_MEMORY, 8, "out of memory"));
    }
    catch (...)
    {
        session->source->poisoned.store(true);
        complete(generation, {}, Error(NW_NATIVE_PANIC, 8, "queue failed"));
    }
}
void CursorPull::run(std::uint64_t generation, std::size_t rows, std::size_t bytes, std::shared_ptr<Cancel> cancel)
{
    std::shared_ptr<Buffer> result;
    std::optional<Error> failure;
    try
    {
        std::shared_ptr<Cursor> cursor;
        std::shared_ptr<SqlPlan> plan;
        std::shared_ptr<CommandGate> gate;
        std::optional<Clock::time_point> admitted;
#ifdef NW_HOST_TEST_HOOKS
        std::function<void()> before_fetch;
#endif
        {
            std::lock_guard lock(mutex_);
            if (closing_)
                throw Error::closed();
            cursor = cursor_;
            if (!cursor)
            {
                plan = plan_;
                gate = gate_;
                admitted = admitted_;
#ifdef NW_HOST_TEST_HOOKS
                before_fetch = test_before_first_fetch;
#endif
            }
        }
        session->source->admit();
        if (session->closing.load())
            throw Error::closed();
        if (cancel->requested())
            throw Error::canceled();
        if (!cursor)
        {
            if (admitted)
            {
                const auto elapsed = std::chrono::duration_cast<std::chrono::nanoseconds>(Clock::now() - *admitted);
                plan->timeout_ns = elapsed >= std::chrono::nanoseconds(plan->timeout_ns)
                                       ? 0
                                       : plan->timeout_ns - static_cast<std::uint64_t>(elapsed.count());
            }
            cursor = session->open_cursor(plan, cancel, gate);
            {
                std::lock_guard lock(mutex_);
                cursor_ = cursor;
                plan_.reset();
                gate_.reset();
            }
#ifdef NW_HOST_TEST_HOOKS
            if (before_fetch)
                before_fetch();
#endif
        }
        // This is the former second managed open/fetch boundary. Do not issue
        // Bind/Execute or step after a close, cancellation or source poison
        // that arrived while the full column description was being validated.
        session->source->admit();
        if (session->closing.load())
            throw Error::closed();
        if (cancel->requested())
            throw Error::canceled();
        {
            std::lock_guard lock(mutex_);
            if (closing_)
                throw Error::closed();
        }
        result = cursor->fetch(cancel, rows, bytes);
        // CursorReadAdmission is already destroyed at this point. All local
        // Session/plan/gate/provider accessors leave scope before readiness.
    }
    catch (Error& error)
    {
        failure = std::move(error);
    }
    catch (const std::bad_alloc&)
    {
        failure.emplace(NW_OUT_OF_MEMORY, 8, "out of memory");
    }
    catch (...)
    {
        session->source->poisoned.store(true);
        failure.emplace(NW_NATIVE_PANIC, 8, "cursor failed");
    }
    cancel->detach();
    cancel.reset();
    complete(generation, std::move(result), std::move(failure));
}
void CursorPull::complete(std::uint64_t generation, std::shared_ptr<Buffer> buffer, std::optional<Error> error)
{
    nw_db_cursor_callbacks_v1 callback{};
    std::shared_ptr<Cursor> closing_cursor;
    std::shared_ptr<CommandGate> abandoned_gate;
    bool failed = false;
    {
        std::lock_guard lock(mutex_);
        if (!running_ || generation != generation_)
            std::terminate();
        buffer_ = std::move(buffer);
        error_ = std::move(error);
        cancel_.reset();
        failed = bool(error_);
        if (failed)
            closing_ = true;
        if (closing_)
        {
            closing_cursor = cursor_;
            abandoned_gate = std::move(gate_);
            plan_.reset();
        }
    }
    bool cleanup_failed = false;
    try
    {
        if (closing_cursor)
        {
            closing_cursor->request_close();
            cleanup_failed = closing_cursor->cleanup_unconfirmed.load();
        }
        if (abandoned_gate)
            abandoned_gate->finish(failed);
    }
    catch (...)
    {
        cleanup_failed = true;
    }
    closing_cursor.reset();
    abandoned_gate.reset();
    {
        std::lock_guard lock(mutex_);
        if (cleanup_failed)
        {
            session->discard.store(true);
            session->source->poisoned.store(true);
            closing_ = true;
            if (!error_)
            {
                buffer_.reset();
                error_.emplace(NW_NATIVE_PANIC, 8, "cleanup failed");
            }
            error_->cleanup = cursor_cleanup_failure();
        }
        // Only publish readiness after all fallible cleanup side effects are
        // contained. A caller cannot take the result while it is being enriched.
        callback = callbacks_;
        callbacks_ = {};
        running_ = false;
        ready_ = true;
    }
    // Exactly one detached notification; no access to channel state or the
    // callback cookie follows this call. The independent worker ticket can
    // still be live and is joined only at final close.
    callback.ready(callback.context, generation);
}
std::shared_ptr<Buffer> CursorPull::take(std::uint64_t generation)
{
    std::lock_guard lock(mutex_);
    if (generation != generation_ || !outstanding_)
        throw Error::state("cursor result generation differs or was consumed");
    if (!ready_)
        throw Error(NW_PENDING, 8, "cursor request is pending");
    if (error_)
        throw *error_;
    if (!buffer_)
        throw Error::state("cursor batch is unavailable");
    outstanding_ = false;
    return std::move(buffer_);
}
Error CursorPull::take_error(std::uint64_t generation)
{
    std::lock_guard lock(mutex_);
    if (generation != generation_ || !outstanding_)
        throw Error::state("cursor error generation differs or was consumed");
    if (!ready_)
        throw Error(NW_PENDING, 8, "cursor request is pending");
    if (!error_)
        throw Error::state("cursor has no rich error");
    auto result = std::move(*error_);
    error_.reset();
    outstanding_ = false;
    return result;
}
void CursorPull::check_read_admission()
{
    std::lock_guard lock(mutex_);
    session->source->admit();
    if (closing_ || session->closing.load())
        throw Error::closed();
    if (outstanding_ || running_ || !cursor_)
        throw Error::state("cursor read admission is unavailable");
    cursor_->check_read_admission();
}
void CursorPull::request_close()
{
    std::shared_ptr<Cancel> cancel;
    std::shared_ptr<Cursor> cursor;
    std::shared_ptr<CommandGate> gate;
    {
        std::lock_guard lock(mutex_);
        closing_ = true;
        cancel = cancel_;
        cursor = cursor_;
        if (!running_ && !cursor)
        {
            gate = std::move(gate_);
            plan_.reset();
        }
    }
    if (cancel)
        cancel->request();
    if (cursor)
        cursor->request_close();
    if (gate)
        gate->finish();
}
void CursorPull::join()
{
    request_close();
    completion_->wait();
    std::shared_ptr<Cursor> cursor;
    std::shared_ptr<Buffer> unconsumed;
    {
        std::lock_guard lock(mutex_);
        cursor = cursor_;
        unconsumed = std::move(buffer_);
    }
    unconsumed.reset();
    if (cursor)
    {
        cursor->request_close();
        cursor->join();
    }
}
Bytes CursorPull::snapshot() const
{
    std::lock_guard lock(mutex_);
    const bool quiet = closing_ && !running_ && !gate_ && completion_->done();
    if (!cursor_)
        return snapshot_record(0, 0, false, quiet ? 2 : closing_ ? 1 : 0, 0, quiet, false, 0);
    auto bytes = cursor_->snapshot();
    // A cursor receipt alone does not prove all detached channel tails left.
    if (!quiet)
        return snapshot_record(0, 0, false, 1, 0, false, false, 0);
    return bytes;
}

TransactionOptions TransactionOptions::parse(ByteView bytes)
{
    const auto fields =
        Fields::parse(bytes, 3, {{1, 1, true}, {2, 1, true}, {3, 3, true}, {4, 3, true}, {5, 4, false}});
    TransactionOptions options{fields.u32(1), fields.boolean(2), fields.u64(3), fields.u64(4), {}};
    if (options.isolation > 3)
        throw Error::unsupported();
    if (fields.get(5))
        options.recovery_key = std::string(fields.text(5));
    return options;
}
void TransactionOptions::validate(Profile profile) const
{
    const auto maximum = static_cast<std::uint64_t>(
        std::chrono::duration_cast<std::chrono::nanoseconds>(Clock::time_point::max() - Clock::now()).count());
    if (commit_timeout_ns > maximum || cleanup_timeout_ns > maximum ||
        (recovery_key && recovery_key->size() > MAX_BYTES))
        throw Error::invalid("invalid transaction options");
    if (isolation > 3 || (profile == Profile::Sqlite && isolation != 0 && isolation != 3))
        throw Error::unsupported();
}
std::shared_ptr<Transaction> Transaction::begin(std::shared_ptr<Session> session, TransactionOptions options,
                                                std::shared_ptr<Cancel> cancel, std::shared_ptr<CommandGate> gate)
{
    options.validate(session->source->config.provider.profile);
    if (cancel->requested())
        throw Error::canceled();
    {
        std::lock_guard lock(session->mutex);
        if (auto previous = session->transaction.lock())
        {
            std::lock_guard state(previous->mutex);
            if (!previous->retired)
                throw Error::state("transaction already active");
        }
    }
    auto tx = std::make_shared<Transaction>();
    tx->session = session;
    tx->options = options;
    const auto profile = session->source->config.provider.profile;
    std::string sql;
    if (profile == Profile::PostgreSql)
    {
        const char* levels[] = {"READ COMMITTED", "READ COMMITTED", "REPEATABLE READ", "SERIALIZABLE"};
        sql = "BEGIN ISOLATION LEVEL " + std::string(levels[options.isolation]) +
              (options.read_only ? " READ ONLY" : " READ WRITE");
    }
    else
    {
        sql = session->source->config.provider.sqlite_begin ? "BEGIN IMMEDIATE" : "BEGIN";
    }
    gate->dispatched = true;
    try
    {
        if (profile == Profile::Sqlite)
            (void)session->connection->execute(
                options.read_only ? "PRAGMA query_only=ON" : "PRAGMA query_only=OFF", {},
                {{}, Clock::now() + std::chrono::nanoseconds(session->source->config.limits.command_ns), false});
        (void)session->connection->execute(
            sql, {}, {{}, Clock::now() + std::chrono::nanoseconds(session->source->config.limits.command_ns), false});
    }
    catch (const Error& error)
    {
        session->discard.store(true);
        gate->finish(true);
        session->request_close();
        session->join();
        rethrow_transaction_error(error);
    }
    {
        std::lock_guard lock(session->mutex);
        session->transaction = tx;
    }
    gate->finish();
    return tx;
}
bool Transaction::active() const
{
    std::lock_guard lock(mutex);
    return !closing && !retired && state == 0;
}
void Transaction::command_failed()
{
    std::lock_guard lock(mutex);
    if (!retired && state == 0)
        state = 1;
}

struct Transaction::Worker
{
    struct Start
    {
        std::mutex mutex;
        std::condition_variable changed;
        bool decided = false, run = false, dispatched = false;
        void publish(bool value)
        {
            {
                std::lock_guard lock(mutex);
                if (decided)
                    return;
                decided = true;
                run = value;
            }
            changed.notify_all();
        }
        bool wait()
        {
            std::unique_lock lock(mutex);
            changed.wait(lock, [&] { return decided; });
            return run;
        }
        void permit_deadline()
        {
            {
                std::lock_guard lock(mutex);
                dispatched = true;
            }
            changed.notify_all();
        }
        void await_dispatch()
        {
            std::unique_lock lock(mutex);
            changed.wait(lock, [&] { return dispatched; });
        }
    };

    std::shared_ptr<Transaction> owner;
    std::shared_ptr<CommandGate> gate;
    std::shared_ptr<Start> start;
    std::shared_ptr<RetirementFence> completion, parent;
    bool finish, commit;

    Worker(std::shared_ptr<Transaction> value, std::shared_ptr<CommandGate> command, std::shared_ptr<Start> launch,
           bool finishing, bool committing)
        : owner(std::move(value)), gate(std::move(command)), start(std::move(launch)), completion(owner->completion_),
          parent(owner->session->source->transaction_workers), finish(finishing), commit(committing)
    {
        completion->add();
        parent->add();
    }
    ~Worker()
    {
        // CommandGate destruction can schedule cleanup. Release it while the
        // Transaction is still retained, then release every parent owner before
        // publishing either independent ticket. No Source is held by a ticket.
        gate.reset();
        owner.reset();
        completion->complete();
        parent->complete();
    }
    void run()
    {
        if (!start->wait())
            return;
        if (finish)
        {
#ifdef NW_HOST_TEST_HOOKS
            if (owner->test_before_finish_dispatch)
                owner->test_before_finish_dispatch();
#endif
            // Previously the deadline thread was created inside finish_worker,
            // after this dispatch marker. Preserve that order even though both
            // workers are now prepared before publishing finish admission.
            gate->dispatched = true;
            start->permit_deadline();
            owner->finish_worker(commit, gate);
#ifdef NW_HOST_TEST_HOOKS
            if (owner->test_after_finish_worker)
                owner->test_after_finish_worker();
#endif
        }
        else
        {
            start->await_dispatch();
            owner->deadline_worker();
#ifdef NW_HOST_TEST_HOOKS
            if (owner->test_after_deadline_worker)
                owner->test_after_deadline_worker();
#endif
        }
    }
};

class Transaction::WorkerLaunch
{
  public:
    WorkerLaunch(const std::shared_ptr<Transaction>& owner, bool commit, const std::shared_ptr<CommandGate>& gate)
        : completion_(owner->completion_)
    {
        try
        {
            for (std::uint32_t index = 0; index != 2; ++index)
            {
                auto worker = std::make_unique<Worker>(owner, index == 0 ? gate : nullptr, start_, index == 0, commit);
#ifdef NW_HOST_TEST_HOOKS
                if (owner->test_before_worker_start)
                    owner->test_before_worker_start(index);
#endif
                std::thread thread([worker = std::move(worker)] { worker->run(); });
                try
                {
                    thread.detach();
                }
                catch (...)
                {
                    start_->publish(false);
                    thread.join();
                    throw;
                }
            }
        }
        catch (...)
        {
            // No worker enters Transaction methods until both launches succeed.
            // The caller retains owner and gate while these canceled workers
            // release their captures, so compensation cannot reenter its lock.
            start_->publish(false);
            completion_->wait();
            throw;
        }
    }
    ~WorkerLaunch()
    {
        if (!started_)
        {
            start_->publish(false);
            completion_->wait();
        }
    }
    void start()
    {
        start_->publish(true);
        started_ = true;
    }

  private:
    std::shared_ptr<Worker::Start> start_ = std::make_shared<Worker::Start>();
    std::shared_ptr<RetirementFence> completion_;
    bool started_ = false;
};

Bytes Transaction::finish(bool commit, std::shared_ptr<Cancel> cancel, std::shared_ptr<CommandGate> gate)
{
    std::optional<WorkerLaunch> launch;
    {
        std::lock_guard lock(mutex);
        if (closing || finishing || retired || (commit ? state != 0 : (state != 0 && state != 1)))
            throw Error::state("transaction admission rejected");
        if (cancel->requested())
            throw Error::canceled();
        launch.emplace(shared_from_this(), commit, gate);
        finishing = true;
        closing = true;
        state = commit ? 2 : 3;
        attempted |= commit;
        cleanup = 1;
        driver_active = true;
        deadline_phase = commit ? 1 : 2;
        phase_deadline =
            Clock::now() + std::chrono::nanoseconds(commit ? options.commit_timeout_ns : options.cleanup_timeout_ns);
    }
    launch->start();
    {
        std::unique_lock lock(mutex);
        changed.wait(lock, [&] { return primary_ready; });
        if (primary_error)
            throw *primary_error;
    }
    return snapshot();
}
void Transaction::deadline_worker()
{
    std::unique_lock lock(mutex);
    while (!retired)
    {
        const auto deadline = phase_deadline;
        const auto phase = deadline_phase;
        if (deadline == Clock::time_point::max())
        {
            changed.wait(lock, [&] { return retired || phase_deadline != deadline; });
            continue;
        }
        if (changed.wait_until(lock, deadline,
                               [&] { return retired || phase_deadline != deadline || deadline_phase != phase; }))
            continue;
        // A deadline only publishes a bounded waiter result. It never abandons
        // the provider call, cancels COMMIT, or releases its transaction owner.
        phase_deadline = Clock::time_point::max();
        deadline_exceeded = true;
        disposition = 2;
        cleanup = 1;
        if (phase <= 2 && !primary_ready)
        {
            state = 4;
            closing = true;
            if (phase == 1)
                outcome = 3;
            primary_error = Error(NW_DOMAIN_ERROR, phase == 1 ? 9 : 1,
                                  phase == 1 ? "commit outcome is unknown" : "transaction operation failed");
            primary_ready = true;
        }
        changed.notify_all();
    }
}
void Transaction::finish_worker(bool commit, std::shared_ptr<CommandGate> gate)
{
    std::optional<Error> failure;
    bool committed = false;
    bool known_rollback = false;
    const auto deadline = Clock::now() + std::chrono::nanoseconds(std::max(session->source->config.limits.command_ns,
                                                                           options.cleanup_timeout_ns));
    try
    {
#ifdef NW_HOST_TEST_HOOKS
        if (test_finish)
        {
            committed = test_finish(commit);
            known_rollback = commit && !committed;
        }
        else
#endif
        {
            if (commit && session->source->config.provider.profile == Profile::PostgreSql)
            {
                try
                {
                    (void)session->connection->execute("SELECT 1", {}, {{}, deadline, false});
                }
                catch (const Error& error)
                {
                    if (error.provider != std::optional<std::string>("25P02"))
                        throw;
                    (void)session->connection->execute("ROLLBACK", {}, {{}, deadline, false});
                    session->connection->synchronize_protocol();
                    failure = error;
                    known_rollback = true;
                }
                if (!known_rollback && !savepoints.empty())
                    throw Error(NW_DOMAIN_ERROR, 1, "transaction depth is not one");
            }
            if (!known_rollback)
            {
                if (commit && !session->connection->in_transaction())
                    throw Error(NW_DOMAIN_ERROR, 1, "transaction no longer active");
                (void)session->connection->execute(commit ? "COMMIT" : "ROLLBACK", {}, {{}, deadline, false});
                // Driver confirmation precedes publication of Committed. Loss
                // of this first post-COMMIT Sync must still report Unknown.
                session->connection->synchronize_protocol();
                committed = commit;
            }
        }
    }
    catch (const Error& error)
    {
        failure = error;
    }
    catch (...)
    {
        failure = Error(NW_NATIVE_PANIC, 8, "transaction exception contained");
        session->source->poisoned.store(true);
    }
    {
        std::lock_guard lock(mutex);
        if (!primary_ready)
        {
            if (known_rollback)
            {
                outcome = 2;
                Error error(NW_DOMAIN_ERROR, 1, "transaction operation failed");
                if (failure)
                {
                    error.provider = failure->provider;
                    error.correlation = failure->correlation;
                }
                primary_error = error;
            }
            else if (!failure)
            {
                outcome = committed ? 1 : 2;
            }
            else
            {
                if (commit)
                    outcome = 3;
                Error error(NW_DOMAIN_ERROR, commit ? 9 : 1,
                            commit ? "commit outcome is unknown" : "transaction operation failed");
                error.provider = failure->provider;
                error.correlation = failure->correlation;
                primary_error = error;
            }
            primary_ready = true;
        }
        state = 4;
        if (failure)
        {
            provider = failure->provider;
            correlation = failure->correlation;
            if (!commit)
                cleanup_failure = 3;
        }
        deadline_phase = 3;
        phase_deadline = Clock::now() + std::chrono::nanoseconds(options.cleanup_timeout_ns);
    }
    changed.notify_all();
    bool clean = session->connection->healthy();
    if (commit && failure && !known_rollback)
    {
        try
        {
            // The old coordinator attempts cleanup_rollback after every failed
            // commit driver call, including an untrusted first Sync. A failed
            // cleanup remains Failed even if later recover says Untrusted.
            if (clean && session->connection->in_transaction())
                (void)session->connection->execute(
                    "ROLLBACK", {}, {{}, Clock::now() + std::chrono::nanoseconds(options.cleanup_timeout_ns), false});
            session->connection->synchronize_protocol();
        }
        catch (const Error& error)
        {
            clean = false;
            if (session->source->config.provider.profile == Profile::PostgreSql)
                session->provider_cleanup_failed.store(true);
            std::lock_guard lock(mutex);
            provider = error.provider;
            correlation = error.correlation;
            cleanup_failure = 4;
        }
    }
    {
        // The original coordinator gives cleanup_rollback and recover separate
        // bounded waiters. Neither deadline abandons the native accessor.
        std::lock_guard lock(mutex);
        deadline_phase = 3;
        phase_deadline = Clock::now() + std::chrono::nanoseconds(options.cleanup_timeout_ns);
    }
    changed.notify_all();
    try
    {
        // Recovery observes protocol safety only. In particular a successful
        // cleanup ROLLBACK never rewrites an already published Unknown outcome.
        if (clean && session->connection->in_transaction())
            (void)session->connection->execute(
                "ROLLBACK", {}, {{}, Clock::now() + std::chrono::nanoseconds(options.cleanup_timeout_ns), false});
        if (clean)
            session->connection->synchronize_protocol();
        if (clean && options.read_only && session->source->config.provider.profile == Profile::Sqlite)
            (void)session->connection->execute(
                "PRAGMA query_only=OFF", {},
                {{}, Clock::now() + std::chrono::nanoseconds(options.cleanup_timeout_ns), false});
    }
    catch (const Error& error)
    {
        clean = false;
        std::lock_guard lock(mutex);
        provider = error.provider;
        correlation = error.correlation;
        cleanup_failure = 4;
    }
    {
        std::lock_guard lock(mutex);
        driver_active = false;
        deadline_phase = 4;
        phase_deadline = Clock::now() + std::chrono::nanoseconds(options.cleanup_timeout_ns);
    }
    changed.notify_all();
#ifdef NW_HOST_TEST_HOOKS
    if (test_retire_gate)
        test_retire_gate();
#endif
    if (!clean)
    {
        session->discard.store(true);
        session->connection->close();
        session->retire_failed_provider();
    }
    gate->finish();
    // A closing parent still owns the physical lease. Its observed return/close
    // must precede the last transaction owner's retirement receipt.
    if (session->closing.load())
    {
        if (!session->cleanup_scheduled.exchange(true))
            session->retire_now();
        session->join();
    }
    {
        std::lock_guard lock(mutex);
        disposition = clean ? 0 : 3;
        cleanup = cleanup_failure ? cleanup_failure : 2;
        retired = true;
        finishing = false;
        savepoints.clear();
        phase_deadline = Clock::time_point::max();
    }
    changed.notify_all();
    if (session->closing.load())
        session->schedule_cleanup();
}
void Transaction::request_close()
{
    {
        std::lock_guard lock(mutex);
        if (retired)
            return;
        closing = true;
        cleanup = 1;
        if (session->active.load())
            disposition = 2;
    }
    schedule_cleanup();
}
Bytes Transaction::wait_close(std::uint64_t wait_ns)
{
    request_close();
    const auto deadline = Clock::now() + std::chrono::nanoseconds(wait_ns);
    {
        std::unique_lock lock(mutex);
        changed.wait_until(lock, deadline, [&] { return retired; });
    }
    completion_->wait_until(deadline);
    return snapshot();
}
void Transaction::schedule_cleanup()
{
    std::optional<WorkerLaunch> launch;
    std::shared_ptr<CommandGate> gate;
    {
        std::lock_guard lock(mutex);
        if (!closing || retired || finishing || session->active.load())
            return;
        if (session->active.exchange(true))
            return;
        try
        {
            gate = std::make_shared<CommandGate>(session);
            launch.emplace(shared_from_this(), false, gate);
        }
        catch (...)
        {
            // A launch failure has run no provider work and published no
            // finishing state. Leave automatic cleanup retryable, without a
            // gate destructor recursively retrying while this mutex is held.
            if (gate)
                gate->completed = true;
            session->active.store(false);
            session->changed.notify_all();
            throw;
        }
        finishing = true;
        state = 3;
        cleanup = 1;
        driver_active = true;
        deadline_phase = 2;
        phase_deadline = Clock::now() + std::chrono::nanoseconds(options.cleanup_timeout_ns);
    }
    launch->start();
}
void Transaction::join()
{
    request_close();
    {
        std::unique_lock lock(mutex);
        changed.wait(lock, [&] { return retired; });
    }
#ifdef NW_HOST_TEST_HOOKS
    if (!completion_->done() && test_before_join_wait)
        test_before_join_wait();
#endif
    completion_->wait();
}
Bytes Transaction::snapshot() const
{
    std::lock_guard lock(mutex);
    return snapshot_record(state, outcome, attempted, cleanup, disposition, retired && completion_->done(),
                           deadline_exceeded, correlation, provider);
}
std::shared_ptr<Savepoint> Transaction::create_savepoint(std::shared_ptr<Cancel> cancel,
                                                         std::shared_ptr<CommandGate> gate)
{
    std::uint64_t token;
    {
        std::lock_guard lock(mutex);
        if (closing || retired || state != 0)
            throw Error::state("transaction admission rejected");
        if (cancel->requested())
            throw Error::canceled();
        token = next_savepoint++;
    }
    gate->dispatched = true;
    try
    {
        (void)session->connection->execute(
            "SAVEPOINT _sqlx_savepoint_" + std::to_string(savepoints.size() + 1), {},
            {{}, Clock::now() + std::chrono::nanoseconds(session->source->config.limits.command_ns), false});
        session->connection->synchronize_protocol();
    }
    catch (const Error& error)
    {
        gate->finish(true);
        rethrow_transaction_error(error);
    }
    {
        std::lock_guard lock(mutex);
        savepoints.push_back(token);
    }
    gate->finish();
    auto point = std::make_shared<Savepoint>();
    point->transaction = shared_from_this();
    point->token = token;
    return point;
}
Bytes Transaction::savepoint_action(std::uint64_t token, std::uint32_t action, std::shared_ptr<Cancel> cancel,
                                    std::shared_ptr<CommandGate> gate, bool disposal)
{
    std::size_t depth;
    bool already_disposed = false;
    {
        std::lock_guard lock(mutex);
        already_disposed = disposal && (state == 4 || retired ||
                                        std::find(savepoints.begin(), savepoints.end(), token) == savepoints.end());
        if (!already_disposed &&
            (closing || retired || (state != 0 && state != 1) || (state == 1 && action == 1 && !disposal) ||
             savepoints.empty() || savepoints.back() != token))
        {
            if (disposal && !savepoints.empty() && savepoints.back() != token)
            {
                cleanup = 4;
                cleanup_failure = 4;
                provider = "savepoint-order";
                closing = true;
            }
            throw Error::state("transaction admission rejected");
        }
        if (cancel->requested())
            throw Error::canceled();
        depth = savepoints.size();
    }
    if (already_disposed)
    {
        gate->finish();
        return snapshot_record(0, 0, false, 2, 0, true, false, 0);
    }
    gate->dispatched = true;
    const auto name = "_sqlx_savepoint_" + std::to_string(depth);
    const CallContext context{
        {}, Clock::now() + std::chrono::nanoseconds(session->source->config.limits.command_ns), false};
    try
    {
        if (action == 0 || disposal)
        {
            (void)session->connection->execute("ROLLBACK TO SAVEPOINT " + name, {}, context);
            session->connection->synchronize_protocol();
        }
        if (action == 1 || disposal)
        {
            (void)session->connection->execute("RELEASE SAVEPOINT " + name, {}, context);
            session->connection->synchronize_protocol();
        }
    }
    catch (const Error& error)
    {
        gate->finish(true);
        rethrow_transaction_error(error);
    }
    {
        std::lock_guard lock(mutex);
        if (action == 0 || disposal)
            state = 0;
        if (action == 1 || disposal)
            savepoints.pop_back();
    }
    gate->finish();
    return snapshot_record(0, 0, false, 2, 0, true, false, 0);
}
Bytes Transaction::dispose_savepoint(std::uint64_t token)
{
    bool invalid_order = false;
    {
        std::lock_guard lock(mutex);
        // Match the original coordinator before touching the session gate. A
        // released token, or a logically closed transaction still retiring its
        // provider, must not compete with a later command or transaction.
        if (state == 4 || retired || std::find(savepoints.begin(), savepoints.end(), token) == savepoints.end())
            return snapshot_record(0, 0, false, 2, 0, true, false, 0);
        invalid_order = savepoints.back() != token;
        if (invalid_order)
        {
            cleanup = 4;
            cleanup_failure = 4;
            provider = "savepoint-order";
            closing = true;
        }
        else
        {
            if (closing || finishing || (state != 0 && state != 1))
                throw Error::state("transaction admission rejected");
            // This check and the token lookup share the mutex used by RELEASE
            // to remove its token. A busy gate belongs to its admitted caller.
            if (session->active.exchange(true))
                throw Error::state("transaction admission rejected");
        }
    }
    if (invalid_order)
    {
        request_close();
        throw Error::state("transaction admission rejected");
    }
    std::shared_ptr<CommandGate> gate;
    try
    {
        gate = std::make_shared<CommandGate>(session);
    }
    catch (...)
    {
        session->active.store(false);
        session->changed.notify_all();
        schedule_cleanup();
        if (session->closing.load())
            session->schedule_cleanup();
        throw;
    }
    return savepoint_action(token, 0, std::make_shared<Cancel>(), std::move(gate), true);
}
void Savepoint::request_close()
{
    if (cleanup_requested.exchange(true))
        return;
    {
        std::lock_guard lock(transaction->mutex);
        if (transaction->state == 4 || transaction->retired ||
            std::find(transaction->savepoints.begin(), transaction->savepoints.end(), token) ==
                transaction->savepoints.end())
            return;
    }
    auto self = shared_from_this();
    transaction->session->source->workers.post(
        [self]
        {
            try
            {
                (void)self->transaction->dispose_savepoint(self->token);
            }
            catch (const Error&)
            {
                // Owner Drop ignored the original coordinator's result. A
                // non-top token has already requested outer cleanup above;
                // ordinary busy admission must not close another caller's work.
            }
            catch (...)
            {
                self->transaction->request_close();
            }
        });
}
} // namespace nw
