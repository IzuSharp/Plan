use nativeweave_data_sqlite::Limits;
use std::time::Duration;
fn main() {
    let limits = Limits { acquire_timeout: Duration::MAX, ..Limits::default() };
    let accepted = limits.validate().is_ok();
    println!("provider_validate_accepted={accepted}");
    let options = limits.pool_options().expect("pre-fix accepts Duration::MAX");
    let runtime = tokio::runtime::Builder::new_current_thread().enable_all().build().unwrap();
    let attempted = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| runtime.block_on(options.connect_with(sqlx::sqlite::SqliteConnectOptions::new().in_memory(true)))));
    println!("actual_sqlx_connect_panicked={}", attempted.is_err());
    assert!(attempted.is_err(), "review probe expects current overflow defect");
}
