use std::sync::Arc;
use whisper::sol::builder::BrancheBuilder;
use whisper::sol::types::{InstantaneOrigine, SolParams, Sol};

fn sol_vierge() -> Sol {
    let branche = Arc::new(BrancheBuilder::new().build());
    Sol::nouveau(branche, SolParams::default())
}

#[test]
fn snapshot_produit_une_branche() {
    let mut sol = sol_vierge();
    let branche = sol.snapshot(InstantaneOrigine::Manuel).unwrap();
    assert_eq!(branche.id.0.len(), 32);
}

#[test]
fn snapshot_vide_le_drift() {
    let mut sol = sol_vierge();
    sol.snapshot(InstantaneOrigine::Manuel).unwrap();
    assert!(sol.drift.est_vide());
}

#[test]
fn snapshot_enregistre_instantane() {
    let mut sol = sol_vierge();
    assert_eq!(sol.instantanes.len(), 0);
    sol.snapshot(InstantaneOrigine::Manuel).unwrap();
    assert_eq!(sol.instantanes.len(), 1);
}

#[test]
fn deux_snapshots_deux_instantanes() {
    let mut sol = sol_vierge();
    sol.snapshot(InstantaneOrigine::Manuel).unwrap();
    sol.snapshot(InstantaneOrigine::Manuel).unwrap();
    assert_eq!(sol.instantanes.len(), 2);
}