use super::sonde::MVF_JOIGNABLE;
use std::sync::atomic::Ordering;

pub struct ComputeRequest {
    // mirror du rpc::ComputeRequest côté MVF
    pub entite_a: crate::entropie_monde::EntiteDto,
    pub entite_b: crate::entropie_monde::EntiteDto,
    pub params: crate::entropie_monde::ParamsDto,
}

pub struct Hybride {
    pub vs_label: String,
    pub vecteur: Vec<f32>,
}

pub fn compute_hybride(
    mvf_url: &str,
    req: &serde_json::Value,
) -> Option<serde_json::Value> {
    if !MVF_JOIGNABLE.load(Ordering::Relaxed) {
        return None; // fallback immédiat, silencieux
    }

    reqwest::blocking::Client::new()
        .post(format!("{}/compute_hybride", mvf_url))
        .timeout(std::time::Duration::from_millis(100))
        .json(req)
        .send()
        .ok()
        .filter(|r| r.status().is_success())
        .and_then(|r| r.json::<serde_json::Value>().ok())
}