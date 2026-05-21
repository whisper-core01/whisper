//! Header de bloc TurboQuant — stocké en tête de chaque bloc encodé.

use serde::{Deserialize, Serialize};

pub const MAGIC: &[u8; 4] = b"TQ01";
pub const ENTROPIE_SEUIL: f32 = 7.8; // bits/byte — seuil passthrough

#[derive(Debug, Serialize, Deserialize, PartialEq)]
pub enum ModeBloc {
    /// Bloc quantifié par TurboQuant.
    Encode,
    /// Bloc passthrough — entropie trop haute, données non quantifiables.
    Raw,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct HeaderTQ {
    pub magic: [u8; 4],          // "TQ01"
    pub mode: ModeBloc,          // Encode ou Raw
    pub epsilon_effective: f32,  // epsilon utilisé pour ce bloc
    pub q_bits: u8,              // profondeur de quantisation scalaire
    pub taille_originale: u64,   // taille avant encodage (pour décodage)
    pub checksum: u32,           // CRC32 du payload encodé
}

impl HeaderTQ {
    pub fn new_encode(epsilon: f32, q_bits: u8, taille_originale: u64, checksum: u32) -> Self {
        Self {
            magic: *MAGIC,
            mode: ModeBloc::Encode,
            epsilon_effective: epsilon,
            q_bits,
            taille_originale,
            checksum,
        }
    }

    pub fn new_raw(taille_originale: u64, checksum: u32) -> Self {
        Self {
            magic: *MAGIC,
            mode: ModeBloc::Raw,
            epsilon_effective: 0.0,
            q_bits: 0,
            taille_originale,
            checksum,
        }
    }
}