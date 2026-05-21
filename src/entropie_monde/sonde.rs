use std::sync::atomic::{AtomicBool, Ordering};
use std::time::Duration;

pub static MVF_JOIGNABLE: AtomicBool = AtomicBool::new(false);

fn intervalle_aleatoire(min_ms: u64, max_ms: u64) -> Duration {
    let range = max_ms - min_ms;
    let ms = min_ms + (rand::random::<u64>() % range);
    Duration::from_millis(ms)
}

pub fn demarrer_sonde(health_url: String, min_ms: u64, max_ms: u64) {
    std::thread::spawn(move || {
        let client = reqwest::blocking::Client::builder()
            .timeout(Duration::from_millis(500))
            .build()
            .expect("sonde: impossible de créer le client HTTP");

        loop {
            let ok = client
                .get(&health_url)
                .send()
                .map(|r| r.status().is_success())
                .unwrap_or(false);

            MVF_JOIGNABLE.store(ok, Ordering::Relaxed);

            std::thread::sleep(intervalle_aleatoire(min_ms, max_ms));
        }
    });
}