//! Helpers pour les durées et timestamps.
//!
//! Note : on utilise l'horloge système (pas NTP) — décision d'architecture
//! documentée dans la spec Whisper. Le temps est local et souverain.

use std::time::Duration;
use chrono::{DateTime, Utc};

/// Timestamp actuel en UTC.
pub fn maintenant_utc() -> DateTime<Utc> {
    Utc::now()
}

/// Durée bornée pour t_idle_snapshot : [1h, 24h].
pub fn borner_idle(d: Duration) -> Duration {
    let min = Duration::from_secs(3600);
    let max = Duration::from_secs(24 * 3600);
    d.clamp(min, max)
}
