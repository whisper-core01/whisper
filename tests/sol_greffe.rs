use std::sync::Arc;
use whisper::sol::builder::BrancheBuilder;
use whisper::sol::types::{Sol, SolParams};
use whisper::sol::errors::SolError;

fn branche_vide() -> Arc<whisper::sol::types::Branche> {
    Arc::new(BrancheBuilder::new().build())
}

#[test]
fn test_greffe_vide_retourne_erreur() {
    let result = Sol::greffer(&[], SolParams::default());
    assert!(matches!(result, Err(SolError::GreffeSansSource)));
}

#[test]
fn test_greffe_une_branche() {
    let b = branche_vide();
    let sol = Sol::greffer(&[b], SolParams::default()).unwrap();
    assert!(sol.drift.est_vide());
    assert!(sol.instantanes.is_empty());
}

#[test]
fn test_greffe_deux_branches_deux_alice() {
    let b1 = branche_vide();
    let b2 = branche_vide();
    let sol = Sol::greffer(&[b1, b2], SolParams::default()).unwrap();
    // Sol recomposé existe, drift vide, pas d'instantané initial
    assert!(sol.drift.est_vide());
    assert!(sol.instantanes.is_empty());
}