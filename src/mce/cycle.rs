//! Cycle IN → traitement → OUT du MCE.
//!
//! Le MCE lit sa BAL_IN, traite, dépose dans BAL_OUT.
//! Jamais de contact direct avec l'extérieur.

use crate::mce::bal::{BAL, PaquetBAL, TypePayload};
use crate::mce::crypto::{CleEphem, nonce_ephemere, sceller, FragmentScelle};
use crate::mce::entropie::GraineEntropie;
use crate::mce::fragment::{fragmenter, ParamsFragment};
use crate::mce::types::EtatMCE;

// =============================================================================
// Paquet OUT — résultat du traitement MCE
// =============================================================================

#[derive(Debug, Clone)]
pub struct PaquetOUT {
    /// ID original du paquet IN — pour traçabilité interne uniquement.
    pub id_origine: [u8; 32],
    /// Fragments scellés, prêts pour le Transporter.
    pub fragments: Vec<FragmentScelle>,
    /// Nombre de fragments.
    pub n_fragments: u32,
}

// =============================================================================
// MCE
// =============================================================================

pub struct MCE {
    pub bal_in: BAL,
    pub bal_out: BAL_OUT,
    pub etat: EtatMCE,
    graine: GraineEntropie,
    cle_maitre: [u8; 32],
    compteur_nonce: u64,
}

/// BAL_OUT — contient des PaquetOUT (pas des PaquetBAL).
pub struct BAL_OUT {
    file: std::sync::Mutex<std::collections::VecDeque<PaquetOUT>>,
}

impl BAL_OUT {
    pub fn nouvelle() -> Self {
        Self { file: std::sync::Mutex::new(std::collections::VecDeque::new()) }
    }

    pub fn deposer(&self, paquet: PaquetOUT) {
        self.file.lock().unwrap().push_back(paquet);
    }

    pub fn lire(&self) -> Option<PaquetOUT> {
        self.file.lock().unwrap().pop_front()
    }

    pub fn est_vide(&self) -> bool {
        self.file.lock().unwrap().is_empty()
    }
}

impl MCE {
    pub fn nouveau(cle_maitre: [u8; 32], seed_entropie: [u8; 32]) -> Self {
        Self {
            bal_in: BAL::nouvelle(),
            bal_out: BAL_OUT::nouvelle(),
            etat: EtatMCE::nouveau(16), // seuil saturation = 16 paquets
            graine: GraineEntropie::nouvelle(seed_entropie),
            cle_maitre,
            compteur_nonce: 0,
        }
    }

    /// Traite un cycle : lit un paquet de BAL_IN, produit des fragments dans BAL_OUT.
    /// Retourne true si un paquet a été traité.
    pub fn cycle(&mut self) -> bool {
        // Mettre à jour le mode selon la charge
        self.etat.mettre_a_jour_mode(self.bal_in.taille());

        let paquet = match self.bal_in.lire() {
            Some(p) => p,
            None => return false,
        };

        let id_origine = paquet.id;

        // Extraire le payload bytes
        let payload_bytes = match &paquet.payload {
            TypePayload::Texte(s) => s.as_bytes().to_vec(),
            TypePayload::Fichier { contenu, .. } => contenu.clone(),
        };

        // Fragmentation entropique
        let seed_frag = self.graine.suivant();
        let params = ParamsFragment::default();
        let fragments = fragmenter(&payload_bytes, &params, &seed_frag);

        // Scellage de chaque fragment
        let fragments_scelles: Vec<FragmentScelle> = fragments
            .iter()
            .map(|f| {
                let nonce = nonce_ephemere(&self.cle_maitre, self.compteur_nonce);
                self.compteur_nonce += 1;

                let contexte = f.index.to_le_bytes();
                let cle = CleEphem::deriver(&self.cle_maitre, &contexte, &nonce);
                sceller(f.index, &f.contenu, &cle, &nonce)
            })
            .collect();

        let n = fragments_scelles.len() as u32;

        // Déposer dans BAL_OUT
        self.bal_out.deposer(PaquetOUT {
            id_origine,
            fragments: fragments_scelles,
            n_fragments: n,
        });

        // Mettre à jour les indicateurs
        self.etat.indicateurs.paquets_traites += 1;
        self.etat.indicateurs.fragments_produits += n as u64;

        true
    }

    /// Vide la BAL_IN en traitant tous les paquets en attente.
    pub fn traiter_tout(&mut self) {
        while self.cycle() {}
    }
}

// =============================================================================
// Tests
// =============================================================================

#[cfg(test)]
mod tests {
    use super::*;
    use crate::mce::bal::TypePayload;

    fn mce_test() -> MCE {
        MCE::nouveau([0x42u8; 32], [0x01u8; 32])
    }

    #[test]
    fn cycle_traite_un_paquet() {
        let mut mce = mce_test();
        let p = PaquetBAL::nouveau(TypePayload::Texte("hello whisper".into()));
        mce.bal_in.deposer(p);
        assert!(mce.cycle());
        assert!(!mce.bal_out.est_vide());
    }

    #[test]
    fn cycle_vide_produit_false() {
        let mut mce = mce_test();
        assert!(!mce.cycle());
    }

    #[test]
    fn traiter_tout_vide_bal_in() {
        let mut mce = mce_test();
        for i in 0..5 {
            mce.bal_in.deposer(PaquetBAL::nouveau(
                TypePayload::Texte(format!("message {}", i))
            ));
        }
        mce.traiter_tout();
        assert!(mce.bal_in.est_vide());
        assert_eq!(mce.etat.indicateurs.paquets_traites, 5);
    }

    #[test]
    fn mode_sature_si_charge_elevee() {
        let mut mce = mce_test();
        for i in 0..20 {
            mce.bal_in.deposer(PaquetBAL::nouveau(
                TypePayload::Texte(format!("msg {}", i))
            ));
        }
        mce.etat.mettre_a_jour_mode(mce.bal_in.taille());
        assert_eq!(mce.etat.mode, crate::mce::types::ModeMCE::Sature);
    }
    
    #[test]
fn sup_inv_03_mce_output_fragments_do_not_expose_forbidden_material() {
    use bincode;
    use crate::mce::bal::{PaquetBAL, TypePayload};

    let cle_maitre = [0x42u8; 32];
    let seed_entropie = [0x01u8; 32];

    let secret_message = b"SUP_INV_03_SECRET_MESSAGE_MUST_NOT_LEAK".repeat(32);
    let forbidden_file_name = "forbidden_secret_filename.txt";

    let mut mce = MCE::nouveau(cle_maitre, seed_entropie);

    let paquet = PaquetBAL::nouveau(TypePayload::Fichier {
        nom: forbidden_file_name.to_string(),
        contenu: secret_message.clone(),
    });

    mce.bal_in.deposer(paquet);

    assert!(mce.cycle());

    let out = mce.bal_out.lire().expect("BAL_OUT must contain one PaquetOUT");

    assert!(out.n_fragments > 0);
    assert_eq!(out.fragments.len(), out.n_fragments as usize);

    let mut serialized_output = Vec::new();

    for fragment_scelle in &out.fragments {
        let bytes = bincode::serialize(fragment_scelle)
            .expect("FragmentScelle must serialize");
        serialized_output.extend_from_slice(&bytes);
    }

    // 1. Le message complet ne doit pas apparaître dans la sortie scellée.
    assert!(
        !serialized_output
            .windows(secret_message.len())
            .any(|w| w == secret_message.as_slice()),
        "sealed MCE output must not expose full plaintext message"
    );

    // 2. Une signature claire évidente du message ne doit pas apparaître.
    let marker = b"SUP_INV_03_SECRET_MESSAGE_MUST_NOT_LEAK";
    assert!(
        !serialized_output
            .windows(marker.len())
            .any(|w| w == marker),
        "sealed MCE output must not expose plaintext marker"
    );

    // 3. Le nom de fichier ne doit pas sortir.
    assert!(
        !serialized_output
            .windows(forbidden_file_name.as_bytes().len())
            .any(|w| w == forbidden_file_name.as_bytes()),
        "sealed MCE output must not expose original filename"
    );

    // 4. La clé maître ne doit pas sortir.
    assert!(
        !serialized_output
            .windows(cle_maitre.len())
            .any(|w| w == cle_maitre),
        "sealed MCE output must not expose master key material"
    );

    // 5. Le seed entropique ne doit pas sortir.
    assert!(
        !serialized_output
            .windows(seed_entropie.len())
            .any(|w| w == seed_entropie),
        "sealed MCE output must not expose entropy seed material"
    );
}
}
