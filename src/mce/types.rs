//! Types internes du MCE — état, modes, indicateurs.

use serde::{Deserialize, Serialize};

// =============================================================================
// Modes du MCE
// =============================================================================

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum ModeMCE {
    /// MCE en attente — BAL_IN vide.
    Idle,
    /// MCE en traitement — paquets en cours.
    Actif,
    /// BAL_IN saturée — MCE sous pression.
    Sature,
}

// =============================================================================
// Indicateurs internes
// =============================================================================

#[derive(Debug, Clone)]
pub struct IndicateursMCE {
    /// Entropie moyenne des derniers paquets traités (bits/byte).
    pub entropie_moyenne: f32,
    /// Nombre de paquets traités depuis le dernier reset.
    pub paquets_traites: u64,
    /// Nombre de fragments produits.
    pub fragments_produits: u64,
    /// Charge actuelle : taille BAL_IN.
    pub charge: usize,
}

impl Default for IndicateursMCE {
    fn default() -> Self {
        Self {
            entropie_moyenne: 0.0,
            paquets_traites: 0,
            fragments_produits: 0,
            charge: 0,
        }
    }
}

// =============================================================================
// État interne du MCE
// =============================================================================

pub struct EtatMCE {
    pub mode: ModeMCE,
    pub indicateurs: IndicateursMCE,
    /// Seuil de saturation : si BAL_IN > seuil → mode Sature.
    pub seuil_saturation: usize,
}

impl EtatMCE {
    pub fn nouveau(seuil_saturation: usize) -> Self {
        Self {
            mode: ModeMCE::Idle,
            indicateurs: IndicateursMCE::default(),
            seuil_saturation,
        }
    }

    pub fn mettre_a_jour_mode(&mut self, charge: usize) {
        self.indicateurs.charge = charge;
        self.mode = match charge {
            0 => ModeMCE::Idle,
            n if n >= self.seuil_saturation => ModeMCE::Sature,
            _ => ModeMCE::Actif,
        };
    }
}
