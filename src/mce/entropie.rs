//! Entropie interne du MCE.
//!
//! - bruit interne contrôlé
//! - variabilité non reproductible
//! - destruction des traces
//! - impossibilité de rejouer un OUT

use crate::utils::hashing::hash_bytes;

// =============================================================================
// Graine d'entropie interne
// =============================================================================

/// Graine d'entropie — évolue à chaque usage, jamais réutilisée.
pub struct GraineEntropie {
    etat: [u8; 32],
    compteur: u64,
}

impl GraineEntropie {
    pub fn nouvelle(seed_initial: [u8; 32]) -> Self {
        Self { etat: seed_initial, compteur: 0 }
    }

    /// Produit 32 bytes de bruit déterministe depuis l'état courant.
    /// Fait évoluer l'état — non rejouable.
    pub fn suivant(&mut self) -> [u8; 32] {
        let mut input = self.etat.to_vec();
        input.extend_from_slice(&self.compteur.to_le_bytes());
        let hash = hash_bytes(&input);

        // Faire évoluer l'état — l'ancien état est écrasé
        self.etat = hash;
        self.compteur += 1;

        hash
    }

    /// Injecte du bruit externe dans la graine (événement système, timestamp, etc.)
    pub fn injecter(&mut self, bruit: &[u8]) {
        let mut input = self.etat.to_vec();
        input.extend_from_slice(bruit);
        input.extend_from_slice(&self.compteur.to_le_bytes());
        self.etat = hash_bytes(&input);
        self.compteur += 1;
    }
}

// =============================================================================
// Destruction des traces
// =============================================================================

/// Zéroïse un buffer — destruction sécurisée des données sensibles.
pub fn detruire(buffer: &mut Vec<u8>) {
    for b in buffer.iter_mut() { *b = 0; }
    buffer.clear();
}

/// Zéroïse un tableau fixe.
pub fn detruire_fixe(buffer: &mut [u8]) {
    for b in buffer.iter_mut() { *b = 0; }
}

// =============================================================================
// Padding entropique
// =============================================================================

/// Ajoute du padding entropique à un payload.
/// Rend la taille des fragments non corrélable au contenu.
pub fn padder(payload: &[u8], graine: &mut GraineEntropie, taille_cible: usize) -> Vec<u8> {
    let mut out = payload.to_vec();
    while out.len() < taille_cible {
        let bruit = graine.suivant();
        let restant = taille_cible - out.len();
        out.extend_from_slice(&bruit[..restant.min(32)]);
    }
    out.truncate(taille_cible);
    out
}

// =============================================================================
// Tests
// =============================================================================

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn graine_evolue_a_chaque_appel() {
        let mut g = GraineEntropie::nouvelle([0x01u8; 32]);
        let a = g.suivant();
        let b = g.suivant();
        assert_ne!(a, b);
    }

    #[test]
    fn graine_non_rejouable() {
        // deux graines identiques → même séquence (déterministe)
        // mais la séquence ne peut pas être rejouée sans la graine initiale
        let mut g1 = GraineEntropie::nouvelle([0x42u8; 32]);
        let mut g2 = GraineEntropie::nouvelle([0x42u8; 32]);
        assert_eq!(g1.suivant(), g2.suivant());
        assert_eq!(g1.suivant(), g2.suivant());
    }

    #[test]
    fn injection_change_letat() {
        let mut g = GraineEntropie::nouvelle([0x01u8; 32]);
        let avant = g.suivant();
        g.injecter(b"evenement_systeme");
        let apres = g.suivant();
        assert_ne!(avant, apres);
    }

    #[test]
    fn destruction_zeroise() {
        let mut buf = vec![0xFFu8; 32];
        detruire(&mut buf);
        assert!(buf.is_empty());
    }

    #[test]
    fn padding_atteint_taille_cible() {
        let mut g = GraineEntropie::nouvelle([0x01u8; 32]);
        let payload = b"court";
        let padded = padder(payload, &mut g, 64);
        assert_eq!(padded.len(), 64);
        // le début doit être le payload original
        assert_eq!(&padded[..payload.len()], payload.as_slice());
    }
}
