//! Sérialisation / désérialisation bincode des types Sol.
//!
//! Pipeline : Sol → bincode → TurboQuant → LZH → LUKS

use crate::sol::types::{Branche, Sol};
use crate::turbo_quant::{encoder, decoder};
use crate::turbo_quant::lzh;
use std::sync::Arc;
use std::path::Path;
use std::fs;

// =============================================================================
// Sérialisation brute bincode
// =============================================================================

pub fn serialiser_sol(sol: &Sol) -> Result<Vec<u8>, bincode::Error> {
    bincode::serialize(sol)
}

pub fn deserialiser_sol(bytes: &[u8]) -> Result<Sol, bincode::Error> {
    bincode::deserialize(bytes)
}

pub fn serialiser_branche(branche: &Branche) -> Result<Vec<u8>, bincode::Error> {
    bincode::serialize(branche)
}

pub fn deserialiser_branche(bytes: &[u8]) -> Result<Arc<Branche>, bincode::Error> {
    let branche: Branche = bincode::deserialize(bytes)?;
    Ok(Arc::new(branche))
}

// =============================================================================
// Pipeline complet : bincode → TurboQuant → LZH → disque
// =============================================================================

/// Sol → bincode → TurboQuant → LZH → fichier
pub fn sauvegarder_sol(sol: &Sol, chemin: &Path) -> Result<(), Box<dyn std::error::Error>> {
    let bytes = serialiser_sol(sol)?;
    let tq = encoder(&bytes, sol.params.epsilon_topo_safe, sol.params.q_bits);
    let compressed = lzh::comprimer(&tq)?;
    fs::write(chemin, compressed)?;
    Ok(())
}

/// fichier → LZH → TurboQuant → bincode → Sol
pub fn charger_sol(chemin: &Path) -> Result<Sol, Box<dyn std::error::Error>> {
    let compressed = fs::read(chemin)?;
    let tq = lzh::decompresser(&compressed)?;
    let bytes = decoder(&tq)?;
    Ok(deserialiser_sol(&bytes)?)
}

/// Branche → bincode → TurboQuant → LZH → fichier
pub fn sauvegarder_branche(branche: &Branche, chemin: &Path) -> Result<(), Box<dyn std::error::Error>> {
    let bytes = serialiser_branche(branche)?;
    let tq = encoder(&bytes, 1e-4, 16);
    let compressed = lzh::comprimer(&tq)?;
    fs::write(chemin, compressed)?;
    Ok(())
}

/// fichier → LZH → TurboQuant → bincode → Branche
pub fn charger_branche(chemin: &Path) -> Result<Arc<Branche>, Box<dyn std::error::Error>> {
    let compressed = fs::read(chemin)?;
    let tq = lzh::decompresser(&compressed)?;
    let bytes = decoder(&tq)?;
    Ok(deserialiser_branche(&bytes)?)
}

// =============================================================================
// Tests
// =============================================================================

#[cfg(test)]
mod tests {
    use super::*;
    use crate::sol::builder::BrancheBuilder;
    use crate::sol::types::SolParams;

    #[test]
    fn branche_aller_retour_bincode() {
        let branche = BrancheBuilder::new().build();
        let bytes = serialiser_branche(&branche).unwrap();
        let branche2 = deserialiser_branche(&bytes).unwrap();
        assert_eq!(branche.id.0, branche2.id.0);
    }

    #[test]
    fn sol_aller_retour_bincode() {
        let branche = Arc::new(BrancheBuilder::new().build());
        let sol = Sol::nouveau(branche, SolParams::default());
        let bytes = serialiser_sol(&sol).unwrap();
        let sol2 = deserialiser_sol(&bytes).unwrap();
        assert_eq!(sol.branche_active.id.0, sol2.branche_active.id.0);
    }

    #[test]
    fn taille_branche_vide() {
        let branche = BrancheBuilder::new().build();
        let bytes = serialiser_branche(&branche).unwrap();
        assert!(bytes.len() < 256);
    }

    #[test]
    fn sol_persist_sur_disque() {
        let branche = Arc::new(BrancheBuilder::new().build());
        let sol = Sol::nouveau(branche, SolParams::default());
        let chemin = Path::new("/tmp/whisper_test_sol.bin");
        sauvegarder_sol(&sol, chemin).unwrap();
        let sol2 = charger_sol(chemin).unwrap();
        assert_eq!(sol.branche_active.id.0, sol2.branche_active.id.0);
        fs::remove_file(chemin).ok();
    }

    #[test]
    fn branche_persist_sur_disque() {
        let branche = BrancheBuilder::new().build();
        let chemin = Path::new("/tmp/whisper_test_branche.bin");
        sauvegarder_branche(&branche, chemin).unwrap();
        let branche2 = charger_branche(chemin).unwrap();
        assert_eq!(branche.id.0, branche2.id.0);
        fs::remove_file(chemin).ok();
    }

    #[test]
    fn taille_fichier_sol_vide() {
        let branche = Arc::new(BrancheBuilder::new().build());
        let sol = Sol::nouveau(branche, SolParams::default());
        let chemin = Path::new("/tmp/whisper_test_taille.bin");
        sauvegarder_sol(&sol, chemin).unwrap();
        let metadata = fs::metadata(chemin).unwrap();
        println!("taille Sol vide sur disque : {} bytes", metadata.len());
        assert!(metadata.len() < 1024);
        fs::remove_file(chemin).ok();
    }
}