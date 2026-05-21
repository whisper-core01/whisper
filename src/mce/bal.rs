//! BAL — Boîte Aux Lettres
//!
//! Unique point de contact entre le MCE et l'extérieur.
//! Le Coursier dépose dans BAL_IN.
//! Le MCE dépose dans BAL_OUT.
//! Personne d'autre ne touche à ces files.

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::VecDeque;
use std::sync::Mutex;

// =============================================================================
// Types
// =============================================================================

#[derive(Debug, Serialize, Deserialize, Clone)]
pub enum TypePayload {
    /// Fragment de texte normalisé par le Dôme.
    Texte(String),
    /// Fragment de fichier normalisé par le Dôme.
    Fichier { nom: String, contenu: Vec<u8> },
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct PaquetBAL {
    /// BLAKE3 du contenu — identité unique, non rejouable.
    pub id: [u8; 32],
    pub payload: TypePayload,
    pub timestamp: DateTime<Utc>,
}

impl PaquetBAL {
    pub fn nouveau(payload: TypePayload) -> Self {
        let id = crate::utils::hashing::hash_bytes(&match &payload {
            TypePayload::Texte(s) => s.as_bytes().to_vec(),
            TypePayload::Fichier { contenu, .. } => contenu.clone(),
        });
        Self {
            id,
            payload,
            timestamp: chrono::Utc::now(),
        }
    }
}

// =============================================================================
// BAL — file FIFO thread-safe
// =============================================================================

pub struct BAL {
    file: Mutex<VecDeque<PaquetBAL>>,
}

impl BAL {
    pub fn nouvelle() -> Self {
        Self {
            file: Mutex::new(VecDeque::new()),
        }
    }

    /// Dépose un paquet dans la BAL.
    pub fn deposer(&self, paquet: PaquetBAL) {
        self.file.lock().unwrap().push_back(paquet);
    }

    /// Lit et retire le prochain paquet. None si vide.
    pub fn lire(&self) -> Option<PaquetBAL> {
        self.file.lock().unwrap().pop_front()
    }

    /// Nombre de paquets en attente.
    pub fn taille(&self) -> usize {
        self.file.lock().unwrap().len()
    }

    pub fn est_vide(&self) -> bool {
        self.file.lock().unwrap().is_empty()
    }
}

// =============================================================================
// Tests
// =============================================================================

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn bal_depose_et_lit() {
        let bal = BAL::nouvelle();
        let p = PaquetBAL::nouveau(TypePayload::Texte("hello".into()));
        bal.deposer(p);
        assert_eq!(bal.taille(), 1);
        let lu = bal.lire().unwrap();
        assert!(matches!(lu.payload, TypePayload::Texte(_)));
        assert!(bal.est_vide());
    }

    #[test]
    fn bal_fifo_ordre() {
        let bal = BAL::nouvelle();
        bal.deposer(PaquetBAL::nouveau(TypePayload::Texte("premier".into())));
        bal.deposer(PaquetBAL::nouveau(TypePayload::Texte("deuxieme".into())));
        let p1 = bal.lire().unwrap();
        let p2 = bal.lire().unwrap();
        assert!(matches!(&p1.payload, TypePayload::Texte(s) if s == "premier"));
        assert!(matches!(&p2.payload, TypePayload::Texte(s) if s == "deuxieme"));
    }

    #[test]
    fn bal_vide_retourne_none() {
        let bal = BAL::nouvelle();
        assert!(bal.lire().is_none());
    }

    #[test]
    fn paquet_id_est_deterministe() {
        let p1 = PaquetBAL::nouveau(TypePayload::Texte("test".into()));
        let p2 = PaquetBAL::nouveau(TypePayload::Texte("test".into()));
        assert_eq!(p1.id, p2.id);
    }
}
