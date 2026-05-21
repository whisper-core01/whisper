//! Détection de flux à haute entropie → passthrough.

use super::header::ENTROPIE_SEUIL;

/// Mesure l'entropie de Shannon d'un slice de bytes (bits/byte).
/// Si > ENTROPIE_SEUIL → passthrough, TurboQuant ne touche pas au flux.
pub fn entropie_shannon(data: &[u8]) -> f32 {
    if data.is_empty() { return 0.0; }

    let mut freq = [0u32; 256];
    for &b in data { freq[b as usize] += 1; }

    let n = data.len() as f32;
    freq.iter()
        .filter(|&&c| c > 0)
        .map(|&c| {
            let p = c as f32 / n;
            -p * p.log2()
        })
        .sum()
}

pub fn est_incompressible(data: &[u8]) -> bool {
    entropie_shannon(data) > ENTROPIE_SEUIL
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn entropie_zeros_est_nulle() {
        let data = vec![0u8; 1024];
        assert!(entropie_shannon(&data) < 0.01);
    }

    #[test]
    fn entropie_aleatoire_est_haute() {
        // bytes pseudo-aléatoires via pattern 0..255 répété
        let data: Vec<u8> = (0..=255u8).cycle().take(1024).collect();
        assert!(entropie_shannon(&data) > 7.9);
    }

    #[test]
    fn donnees_structurees_sont_compressibles() {
        let data: Vec<u8> = b"aaaaaaaaabbbbbbbbcccccccc".repeat(100);
        assert!(!est_incompressible(&data));
    }
}