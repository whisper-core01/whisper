//! Fragmentation entropique — découpage des paquets MCE.
//!
//! Le MCE décide :
//! - taille des fragments
//! - ordre (permuté entropiquement)
//! - redondance
//! - stratégie de reconstruction

use crate::utils::hashing::hash_bytes;

// =============================================================================
// Fragment
// =============================================================================

#[derive(Debug, Clone)]
pub struct Fragment {
    /// Index de position dans la séquence originale.
    pub index: u32,
    /// Nonce unique — non rejouable.
    pub nonce: [u8; 16],
    /// Payload du fragment.
    pub contenu: Vec<u8>,
    /// BLAKE3 du contenu — intégrité.
    pub checksum: [u8; 32],
}

impl Fragment {
    pub fn nouveau(index: u32, contenu: Vec<u8>, nonce: [u8; 16]) -> Self {
        let checksum = hash_bytes(&contenu);
        Self { index, nonce, contenu, checksum }
    }
}

// =============================================================================
// Paramètres de fragmentation
// =============================================================================

pub struct ParamsFragment {
    /// Taille cible d'un fragment en bytes.
    pub taille_fragment: usize,
    /// Permuter l'ordre des fragments (entropie d'émission).
    pub permuter: bool,
}

impl Default for ParamsFragment {
    fn default() -> Self {
        Self {
            taille_fragment: 512,
            permuter: true,
        }
    }
}

// =============================================================================
// Fragmentation
// =============================================================================

/// Fragmente un payload en N fragments.
/// Chaque fragment reçoit un nonce dérivé de son index + seed.
pub fn fragmenter(
    payload: &[u8],
    params: &ParamsFragment,
    seed: &[u8; 32],
) -> Vec<Fragment> {
    let chunks: Vec<&[u8]> = payload.chunks(params.taille_fragment).collect();
    let mut fragments: Vec<Fragment> = chunks
        .iter()
        .enumerate()
        .map(|(i, chunk)| {
            let nonce = derive_nonce(seed, i as u32);
            Fragment::nouveau(i as u32, chunk.to_vec(), nonce)
        })
        .collect();

    if params.permuter {
        permuter_fragments(&mut fragments, seed);
    }

    fragments
}

/// Reconstruit le payload depuis les fragments (triés par index).
pub fn reconstruire(mut fragments: Vec<Fragment>) -> Vec<u8> {
    fragments.sort_by_key(|f| f.index);
    fragments.into_iter().flat_map(|f| f.contenu).collect()
}

/// Dérive un nonce 16 bytes depuis un seed + index.
fn derive_nonce(seed: &[u8; 32], index: u32) -> [u8; 16] {
    let mut data = seed.to_vec();
    data.extend_from_slice(&index.to_le_bytes());
    let hash = hash_bytes(&data);
    hash[..16].try_into().unwrap()
}

/// Permutation déterministe Fisher-Yates sur les fragments.
fn permuter_fragments(fragments: &mut Vec<Fragment>, seed: &[u8; 32]) {
    let n = fragments.len();
    for i in (1..n).rev() {
        let mut data = seed.to_vec();
        data.extend_from_slice(&(i as u32).to_le_bytes());
        let hash = hash_bytes(&data);
        let j = u32::from_le_bytes(hash[..4].try_into().unwrap()) as usize % (i + 1);
        fragments.swap(i, j);
    }
}

// =============================================================================
// Tests
// =============================================================================

#[cfg(test)]
mod tests {
    use super::*;

    fn seed_test() -> [u8; 32] { [0x42u8; 32] }

    #[test]
    fn fragmentation_aller_retour() {
        let payload = b"hello whisper".repeat(100);
        let params = ParamsFragment::default();
        let fragments = fragmenter(&payload, &params, &seed_test());
        let reconstruit = reconstruire(fragments);
        assert_eq!(payload.as_slice(), reconstruit.as_slice());
    }

    #[test]
    fn fragmentation_sans_permutation() {
        let payload = b"abcdefgh".repeat(10);
        let params = ParamsFragment { taille_fragment: 4, permuter: false };
        let fragments = fragmenter(&payload, &params, &seed_test());
        // sans permutation, ordre = index croissant
        for (i, f) in fragments.iter().enumerate() {
            assert_eq!(f.index, i as u32);
        }
    }

    #[test]
    fn fragmentation_deterministe() {
        let payload = b"test deterministe".repeat(50);
        let params = ParamsFragment::default();
        let f1 = fragmenter(&payload, &params, &seed_test());
        let f2 = fragmenter(&payload, &params, &seed_test());
        // même seed → même ordre
        for (a, b) in f1.iter().zip(f2.iter()) {
            assert_eq!(a.index, b.index);
            assert_eq!(a.nonce, b.nonce);
        }
    }

    #[test]
    fn checksum_integrite() {
        let payload = b"integrite".repeat(20);
        let params = ParamsFragment { taille_fragment: 4, permuter: false };
        let fragments = fragmenter(&payload, &params, &seed_test());
        for f in &fragments {
            assert_eq!(f.checksum, hash_bytes(&f.contenu));
        }
    }
}
