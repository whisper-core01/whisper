use std::sync::Arc;
use whisper::sol::builder::BrancheBuilder;
use whisper::sol::types::{InstantaneOrigine, SolParams};

fn sol_vierge() -> whisper::sol::types::Sol {
    let branche = Arc::new(BrancheBuilder::new().build());
    whisper::sol::types::Sol::nouveau(branche, SolParams::default())
}

#[test]
fn naviguer_cree_un_snapshot_avant_de_basculer() {
    let mut sol = sol_vierge();
    sol.snapshot(InstantaneOrigine::Manuel).unwrap();
    let n_avant = sol.instantanes.len();

    let inst = sol.instantanes.last().unwrap();
    // on clone l'Arc pour éviter le borrow conflict
    let inst_branche = Arc::clone(&inst.branche);

    let inst_clone = whisper::sol::types::Instantane {
        branche: inst_branche,
        timestamp: sol.instantanes.last().unwrap().timestamp,
        origine: InstantaneOrigine::Manuel,
    };

    sol.naviguer(&inst_clone).unwrap();
    assert!(sol.instantanes.len() > n_avant);
}

#[test]
fn ouvrir_instantane_ne_modifie_pas_le_sol() {
    let mut sol = sol_vierge();
    sol.snapshot(InstantaneOrigine::Manuel).unwrap();
    let n_avant = sol.instantanes.len();

    let inst = sol.instantanes.last().unwrap();
    let inst_clone = whisper::sol::types::Instantane {
        branche: Arc::clone(&inst.branche),
        timestamp: inst.timestamp,
        origine: InstantaneOrigine::Manuel,
    };

    let _exploration = sol.ouvrir_instantane(&inst_clone).unwrap();
    assert_eq!(sol.instantanes.len(), n_avant);
}