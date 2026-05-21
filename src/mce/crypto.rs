//! Dérivation cryptographique interne du MCE.

use crate::utils::hashing::hash_bytes;
use chacha20poly1305::{ChaCha20Poly1305, Key, Nonce as C20Nonce, aead::Aead, KeyInit};
use serde::{Serialize, Deserialize};

pub struct CleEphem {
    data: [u8; 32],
}

impl CleEphem {
    pub fn deriver(maitre: &[u8; 32], contexte: &[u8], nonce: &[u8]) -> Self {
        let mut input = maitre.to_vec();
        input.extend_from_slice(contexte);
        input.extend_from_slice(nonce);
        let hash = hash_bytes(&input);
        Self { data: hash }
    }

    pub fn as_bytes(&self) -> &[u8; 32] {
        &self.data
    }
}

impl Drop for CleEphem {
    fn drop(&mut self) {
        self.data = [0u8; 32];
    }
}

pub fn nonce_ephemere(seed: &[u8; 32], compteur: u64) -> [u8; 12] {
    let mut input = seed.to_vec();
    input.extend_from_slice(&compteur.to_le_bytes());
    let hash = hash_bytes(&input);
    hash[..12].try_into().unwrap()
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FragmentScelle {
    pub index: u32,          // ← AJOUTÉ: index non-chiffré
    pub nonce: [u8; 12],
    pub ciphertext: Vec<u8>,
}

pub fn sceller(index: u32, plaintext: &[u8], cle: &CleEphem, nonce: &[u8; 12]) -> FragmentScelle {
    let key = Key::from(*cle.as_bytes());
    let c20_nonce = C20Nonce::from_slice(nonce);
    let cipher = ChaCha20Poly1305::new(&key);
    
    let ciphertext = cipher.encrypt(c20_nonce, plaintext)
        .expect("Encryption failed");
    
    FragmentScelle {
        index,
        nonce: *nonce,
        ciphertext,
    }
}

pub fn desceller(scelle: &FragmentScelle, cle: &CleEphem) -> Option<Vec<u8>> {
    let key = Key::from(*cle.as_bytes());
    let c20_nonce = C20Nonce::from_slice(&scelle.nonce);
    let cipher = ChaCha20Poly1305::new(&key);
    
    match cipher.decrypt(c20_nonce, scelle.ciphertext.as_ref()) {
        Ok(plaintext) => Some(plaintext),
        Err(_) => None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn cle_test() -> CleEphem {
        CleEphem { data: [0x42u8; 32] }
    }

    fn nonce_test() -> [u8; 12] { [0x01u8; 12] }

    #[test]
    fn sceller_desceller_aller_retour() {
        let plaintext = b"message secret whisper";
        let cle = cle_test();
        let nonce = nonce_test();
        let scelle = sceller(0, plaintext, &cle, &nonce);

        let cle2 = CleEphem { data: [0x42u8; 32] };
        let decrypte = desceller(&scelle, &cle2).unwrap();
        assert_eq!(plaintext.as_slice(), decrypte.as_slice());
    }

    #[test]
    fn tag_invalide_retourne_none() {
        let plaintext = b"message secret";
        let cle = cle_test();
        let nonce = nonce_test();
        let mut scelle = sceller(0, plaintext, &cle, &nonce);

        if !scelle.ciphertext.is_empty() {
            scelle.ciphertext[0] ^= 0xFF;
        }

        let cle2 = CleEphem { data: [0x42u8; 32] };
        assert!(desceller(&scelle, &cle2).is_none());
    }

    #[test]
    fn cle_ephemere_derivation_deterministe() {
        let maitre = [0xABu8; 32];
        let c1 = CleEphem::deriver(&maitre, b"contexte", b"nonce");
        let c2 = CleEphem::deriver(&maitre, b"contexte", b"nonce");
        assert_eq!(c1.as_bytes(), c2.as_bytes());
    }

    #[test]
    fn nonce_ephemere_non_rejouable() {
        let seed = [0x01u8; 32];
        let n1 = nonce_ephemere(&seed, 0);
        let n2 = nonce_ephemere(&seed, 1);
        assert_ne!(n1, n2);
    }

    #[test]
    fn mauvaise_cle_retourne_none() {
        let plaintext = b"secret";
        let cle = cle_test();
        let nonce = nonce_test();
        let scelle = sceller(0, plaintext, &cle, &nonce);

        let mauvaise_cle = CleEphem { data: [0xFFu8; 32] };
        assert!(desceller(&scelle, &mauvaise_cle).is_none());
    }
}
