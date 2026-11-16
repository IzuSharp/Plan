use nativeweave_interop_abi::*;
use nativeweave_interop_errors::*;
use std::ffi::c_void;
use std::sync::{Arc, Barrier};
unsafe extern "C" {
    fn mmap(address: *mut c_void, length: usize, protection: i32, flags: i32, fd: i32, offset: i64) -> *mut c_void;
    fn mprotect(address: *mut c_void, length: usize, protection: i32) -> i32;
    fn munmap(address: *mut c_void, length: usize) -> i32;
    fn getpagesize() -> i32;
}
fn main() {
    let mut cases = 0;
    // Independent real guard page: an accidentally created 24-byte reference or
    // oversized write crosses into PROT_NONE. The truthful capacity is only 8.
    unsafe {
        let page = getpagesize() as usize;
        let memory = mmap(std::ptr::null_mut(), page * 2, 3, 0x22, -1, 0);
        assert_ne!(memory as usize, usize::MAX);
        assert_eq!(mprotect(memory.cast::<u8>().add(page).cast(), page, 0), 0);
        for capacity in [0_u32, 3, 4, 7, 8] {
            let slot = memory.cast::<u8>().add(page - 8);
            std::ptr::write_bytes(slot, 0xa5, 8);
            slot.cast::<u32>().write(capacity);
            let before = std::slice::from_raw_parts(slot, 8).to_vec();
            assert_eq!(write_error(13, slot.cast(), ErrorFields::default()), 13);
            assert_eq!(std::slice::from_raw_parts(slot, 8), before);
            cases += 1;
        }
        assert_eq!(munmap(memory, page * 2), 0);
    }
    for status in (0..=14).chain([u32::MAX]) {
        let boundary = EngineBoundary::new();
        let failure = boundary.business(|| Err::<(), _>(Failure { status, fields: ErrorFields { domain: 99, code: -7, correlation_id: 55 } })).unwrap_err();
        assert_eq!(failure.status, if status < 2 { NW_CONTRACT_VIOLATION } else { status });
        assert_eq!(failure.fields.code, -7);
        assert_eq!(boundary.is_poisoned(), status < 2 || [9,10,11].contains(&status));
        assert_eq!(boundary.active_calls(), 0);
        assert_eq!(boundary.cleanup(|| Ok(5)), Ok(5));
        cases += 1;
    }
    let mut source = "prefix 水🦀".to_owned();
    let detail = BoundedDetail::from_redacted(&source, 4096);
    source.clear();
    assert_eq!(std::str::from_utf8(detail.bytes()).unwrap(), "prefix 水🦀");
    cases += 1;
    let boundary = Arc::new(EngineBoundary::new());
    boundary.poison();
    let started = Arc::new(Barrier::new(2)); let release = Arc::new(Barrier::new(2));
    let clone = boundary.clone(); let a = started.clone(); let b = release.clone();
    let worker = std::thread::spawn(move || clone.cleanup(|| { a.wait(); b.wait(); Ok(()) }));
    started.wait();
    assert_eq!(boundary.active_calls(), 1);
    assert_eq!(boundary.business(|| Ok(())).unwrap_err().status, NW_ENGINE_POISONED);
    release.wait(); assert_eq!(worker.join().unwrap(), Ok(())); assert_eq!(boundary.active_calls(), 0);
    cases += 1;
    println!("{{\"passed\":true,\"independent_cases\":{cases},\"guard_page_short_header\":true,\"trusted_cleanup_counted\":true}}");
}
