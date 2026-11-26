#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <linux/perf_event.h>
#include <sched.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <sys/syscall.h>
#include <sys/time.h>
#include <time.h>
#include <ucontext.h>
#include <unistd.h>

/* Capability probe only. This is not a database/product benchmark. */
static uintptr_t signal_ips[4096];
static volatile sig_atomic_t signal_count;
static volatile uint64_t sink;

static uint64_t clock_ns(clockid_t id) {
    struct timespec value;
    if (clock_gettime(id, &value)) return 0;
    return (uint64_t)value.tv_sec * UINT64_C(1000000000) + value.tv_nsec;
}

static void sample_signal(int signo, siginfo_t *info, void *context) {
    (void)signo; (void)info;
    sig_atomic_t i = signal_count;
    if (i < (sig_atomic_t)(sizeof(signal_ips) / sizeof(signal_ips[0]))) {
        signal_ips[i] = (uintptr_t)((ucontext_t *)context)->uc_mcontext.gregs[REG_RIP];
        signal_count = i + 1;
    }
}

static inline uint64_t mix_value(uint64_t value) {
    value ^= value >> 12;
    value ^= value << 25;
    value ^= value >> 27;
    return value * UINT64_C(2685821657736338717);
}

__attribute__((noinline)) static void measured_busy_work(void) {
    const uint64_t end = clock_ns(CLOCK_MONOTONIC_RAW) + UINT64_C(300000000);
    uint64_t value = 12345;
    do {
        for (int i = 0; i < 20000; ++i) value = mix_value(value);
        sink = value;
    } while (clock_ns(CLOCK_MONOTONIC_RAW) < end);
}

static void boundary(const char *name) {
    struct rusage usage = {0};
    errno = 0;
    int rc = getrusage(RUSAGE_THREAD, &usage);
    int saved_errno = errno;
    printf("{\"kind\":\"boundary\",\"name\":\"%s\",\"pid\":%ld,\"tid\":%ld,"
           "\"monotonic_raw_ns\":%" PRIu64 ",\"thread_cpu_ns\":%" PRIu64 ","
           "\"cpu\":%d,\"rusage_rc\":%d,\"rusage_errno\":%d,"
           "\"voluntary_switches\":%ld,\"involuntary_switches\":%ld}\n",
           name, (long)getpid(), (long)syscall(SYS_gettid),
           clock_ns(CLOCK_MONOTONIC_RAW), clock_ns(CLOCK_THREAD_CPUTIME_ID),
           sched_getcpu(), rc, saved_errno, usage.ru_nvcsw, usage.ru_nivcsw);
}

static void read_schedstat(const char *phase) {
    char buffer[256] = {0};
    errno = 0;
    int fd = open("/proc/self/schedstat", O_RDONLY);
    int open_errno = errno;
    ssize_t n = -1;
    if (fd >= 0) { n = read(fd, buffer, sizeof(buffer)-1); close(fd); }
    uint64_t on_cpu = 0, run_queue = 0, slices = 0;
    int parsed = n > 0 ? sscanf(buffer, "%" SCNu64 " %" SCNu64 " %" SCNu64,
                              &on_cpu, &run_queue, &slices) : 0;
    printf("{\"kind\":\"schedstat\",\"phase\":\"%s\",\"open_errno\":%d,"
           "\"read_bytes\":%ld,\"parsed\":%d,\"on_cpu_ns\":%" PRIu64 ","
           "\"run_queue_ns\":%" PRIu64 ",\"timeslices\":%" PRIu64 "}\n",
           phase, open_errno, (long)n, parsed, on_cpu, run_queue, slices);
}

static int open_perf(uint64_t event, const char *name, int sampling) {
    struct perf_event_attr attr = {0};
    attr.type = PERF_TYPE_SOFTWARE;
    attr.size = sizeof(attr);
    attr.config = event;
    attr.disabled = 1;
    attr.exclude_kernel = sampling ? 1 : 0;
    attr.exclude_hv = 1;
    if (sampling) {
        attr.sample_period = 1000000;
        attr.sample_type = PERF_SAMPLE_IP | PERF_SAMPLE_TID | PERF_SAMPLE_TIME;
        attr.wakeup_events = 1;
        attr.context_switch = 1;
        attr.sample_id_all = 1;
        attr.use_clockid = 1;
        attr.clockid = CLOCK_MONOTONIC_RAW;
    }
    errno = 0;
    int fd = (int)syscall(SYS_perf_event_open, &attr, 0, -1, -1, 0);
    int saved_errno = errno;
    printf("{\"kind\":\"perf_event_open\",\"event\":\"%s\",\"self\":true,"
           "\"sampling\":%s,\"fd\":%d,\"errno\":%d,\"error\":\"%s\"}\n",
           name, sampling ? "true" : "false", fd, saved_errno, strerror(saved_errno));
    return fd;
}

static void ring_copy(void *out, const char *ring, size_t ring_size,
                      uint64_t offset, size_t bytes) {
    size_t pos = (size_t)(offset % ring_size);
    size_t first = ring_size - pos;
    if (first > bytes) first = bytes;
    memcpy(out, ring + pos, first);
    if (bytes > first) memcpy((char *)out + first, ring, bytes - first);
}

int main(void) {
    int perf_cpu = open_perf(PERF_COUNT_SW_CPU_CLOCK, "cpu-clock", 1);
    int perf_sched = open_perf(PERF_COUNT_SW_CONTEXT_SWITCHES, "context-switches", 0);
    size_t page = (size_t)sysconf(_SC_PAGESIZE), ring_size = page * 8;
    void *mapping = MAP_FAILED;
    if (perf_cpu >= 0) {
        mapping = mmap(NULL, page + ring_size, PROT_READ | PROT_WRITE, MAP_SHARED, perf_cpu, 0);
        printf("{\"kind\":\"perf_mmap\",\"ok\":%s,\"errno\":%d}\n",
               mapping != MAP_FAILED ? "true" : "false", mapping == MAP_FAILED ? errno : 0);
        ioctl(perf_cpu, PERF_EVENT_IOC_RESET, 0);
        ioctl(perf_cpu, PERF_EVENT_IOC_ENABLE, 0);
    }
    if (perf_sched >= 0) ioctl(perf_sched, PERF_EVENT_IOC_ENABLE, 0);

    errno = 0;
    int tracefd = open("/sys/kernel/tracing/events/sched/sched_switch/id", O_RDONLY);
    int trace_errno = errno;
    printf("{\"kind\":\"sched_tracepoint\",\"fd\":%d,\"errno\":%d,\"error\":\"%s\"}\n",
           tracefd, trace_errno, strerror(trace_errno));
    if (tracefd >= 0) close(tracefd);

    struct sigaction action = {0};
    action.sa_sigaction = sample_signal;
    action.sa_flags = SA_SIGINFO;
    sigemptyset(&action.sa_mask);
    if (sigaction(SIGPROF, &action, NULL)) { perror("sigaction"); return 2; }
    struct itimerval timer = {{0, 1000}, {0, 1000}};
    errno = 0;
    int timer_rc = setitimer(ITIMER_PROF, &timer, NULL);
    printf("{\"kind\":\"signal_sampling\",\"timer_rc\":%d,\"errno\":%d,\"requested_interval_us\":1000}\n",
           timer_rc, errno);
    read_schedstat("before");
    boundary("work_start");
    measured_busy_work();
    boundary("work_end");
    timer = (struct itimerval){{0,0},{0,0}};
    setitimer(ITIMER_PROF, &timer, NULL);
    boundary("wait_start");
    struct timespec remaining = {0, 20000000};
    while (nanosleep(&remaining, &remaining) && errno == EINTR) {}
    boundary("wait_end");
    read_schedstat("after");

    if (perf_cpu >= 0) ioctl(perf_cpu, PERF_EVENT_IOC_DISABLE, 0);
    if (mapping != MAP_FAILED) {
        struct perf_event_mmap_page *meta = mapping;
        uint64_t head = __atomic_load_n(&meta->data_head, __ATOMIC_ACQUIRE);
        uint64_t tail = meta->data_tail;
        const char *ring = (const char *)mapping + page;
        unsigned samples = 0, lost = 0, switches = 0;
        while (tail < head) {
            struct perf_event_header header;
            ring_copy(&header, ring, ring_size, tail, sizeof(header));
            if (header.size < sizeof(header) || header.size > ring_size) break;
            if (header.type == PERF_RECORD_SAMPLE) {
                struct { uint64_t ip; uint32_t pid, tid; uint64_t time; } sample;
                ring_copy(&sample, ring, ring_size, tail + sizeof(header), sizeof(sample));
                printf("{\"kind\":\"perf_sample\",\"ip\":\"0x%" PRIx64 "\",\"pid\":%u,\"tid\":%u,\"monotonic_raw_ns\":%" PRIu64 "}\n",
                       sample.ip,sample.pid,sample.tid,sample.time);
                ++samples;
            } else if (header.type == PERF_RECORD_SWITCH) {
                struct { uint32_t pid, tid; uint64_t time; } sample_id;
                ring_copy(&sample_id, ring, ring_size, tail + sizeof(header), sizeof(sample_id));
                printf("{\"kind\":\"perf_switch\",\"switch_out\":%s,\"pid\":%u,\"tid\":%u,\"monotonic_raw_ns\":%" PRIu64 "}\n",
                       header.misc & PERF_RECORD_MISC_SWITCH_OUT ? "true" : "false",
                       sample_id.pid,sample_id.tid,sample_id.time);
                ++switches;
            } else if (header.type == PERF_RECORD_LOST) ++lost;
            tail += header.size;
        }
        printf("{\"kind\":\"perf_ring_summary\",\"samples\":%u,\"lost_records\":%u,\"context_switch_records\":%u}\n",samples,lost,switches);
        munmap(mapping, page + ring_size);
    }
    if (perf_sched >= 0) {
        ioctl(perf_sched, PERF_EVENT_IOC_DISABLE, 0);
        uint64_t count = 0;
        ssize_t n = read(perf_sched, &count, sizeof(count));
        printf("{\"kind\":\"perf_context_switch_count\",\"read_bytes\":%ld,\"count\":%" PRIu64 "}\n",(long)n,count);
        close(perf_sched);
    }
    if (perf_cpu >= 0) close(perf_cpu);
    printf("{\"kind\":\"signal_sample_summary\",\"count\":%d,\"scope\":\"self-native-capability-probe-only\"}\n",signal_count);
    for (sig_atomic_t i=0;i<signal_count;i++)
        printf("{\"kind\":\"signal_sample\",\"ip\":\"0x%" PRIxPTR "\"}\n", signal_ips[i]);
    return 0;
}
