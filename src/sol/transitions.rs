//! Transitions du moteur Sol.
//!
//! Toutes les opérations qui font évoluer un Sol sont ici.
//! Aucune logique métier ne doit fuir dans types.rs ou builder.rs.

use std::sync::Arc;
use chrono::Utc;
use crate::sol::builder::BrancheBuilder;
use crate::sol::errors::SolError;
use crate::sol::types::{
    Branche, Contact, Drift, EvenementDeclencheur, Exploration, Instantane,
    InstantaneOrigine, Message, Sol, SolParams,
};

impl Sol {
    /// Crée une Branche immuable à partir de l'état actuel (branche_active + drift).
    /// - Fusionne branche_active et drift dans une nouvelle Branche.
    /// - Ajoute un Instantane à l'historique.
    /// - Vide le drift.
    /// - Met à jour branche_active.

    pub fn nouveau(branche: Arc<Branche>, params: SolParams) -> Self {
    Self {
        branche_active: branche,
        drift: Drift::default(),
        instantanes: Vec::new(),
        params,
    }
}
    
    pub fn snapshot(&mut self, origine: InstantaneOrigine) -> Result<Arc<Branche>, SolError> {
        // Construire la nouvelle branche = base + drift
        let nouvelle_branche = Arc::new(
            BrancheBuilder::depuis_sol(&self.branche_active, &self.drift).build()
        );

        // Enregistrer l'instantané
        let inst = Instantane {
            branche: Arc::clone(&nouvelle_branche),
            timestamp: Utc::now(),
            origine,
        };
        self.instantanes.push(inst);

        // Avancer la branche active
        self.branche_active = Arc::clone(&nouvelle_branche);

        // Vider le drift
        self.drift = Drift::default();

        Ok(nouvelle_branche)
    }

    /// Ouvre un instantané passé dans une Exploration temporaire.
    /// Ne modifie pas le Sol courant — &self, pas &mut self.
    /// Le Sol temporaire hérite des params du Sol parent.
    pub fn ouvrir_instantane(&self, inst: &Instantane) -> Result<Exploration, SolError> {
        let sol_temp = Sol {
            branche_active: Arc::clone(&inst.branche),
            drift: Drift::default(),
            instantanes: Vec::new(),
            params: self.params.clone(),
        };

        Ok(Exploration {
            base: Arc::clone(&inst.branche),
            sol_temp,
        })
    }

    /// Recompose un nouveau Sol à partir de plusieurs branches.
    /// Re-quantifie toutes les branches au même epsilon_topo_safe.
    /// Retourne une erreur si la liste est vide.
   pub fn greffer(branches: &[Arc<Branche>], params: SolParams) -> Result<Sol, SolError> {
    if branches.is_empty() {
        return Err(SolError::GreffeSansSource);
    }

    // Recomposition : contacts + messages de toutes les branches
    // INVARIANT : pas de merge, pas de fusion — entités distinctes conservées
    let mut contacts: Vec<Contact> = Vec::new();
    let mut messages: Vec<Message> = Vec::new();

    for branche in branches {
        // Chaque entité garde son origine — deux "Alice" = deux entités locales
        contacts.extend(branche.contacts.clone());
        messages.extend(branche.messages.clone());
    }

    // Base structurelle : première branche comme référence topo/meta/artefacts
    // TODO: re-quantifier toutes les topos à epsilon_topo_safe une fois Topologie définie
    let base = &branches[0];

    let nouvelle_branche = Arc::new(
        BrancheBuilder {
            topo: base.topo.clone(),
            meta: base.meta.clone(),
            artefacts: base.artefacts.clone(),
            contacts,
            messages,
        }.build()
    );

    Ok(Sol {
        branche_active: nouvelle_branche,
        drift: Drift::default(),
        instantanes: Vec::new(),
        params,
    })
}

    /// Bascule le Sol actif vers un instantané.
    /// - Snapshot du présent avant de basculer (rien n'est perdu).
    /// - Remplace branche_active par la branche de l'instantané cible.
    /// - Drift vidé par snapshot, repart à zéro pour la nouvelle base.
    pub fn naviguer(&mut self, inst: &Instantane) -> Result<(), SolError> {
        // Sauvegarder le présent avant de partir
        self.snapshot(InstantaneOrigine::Auto(EvenementDeclencheur::ChangementStructurel))?;

        // Basculer vers la branche cible
        self.branche_active = Arc::clone(&inst.branche);

        Ok(())
    }

    /// Vérifie si un événement mérite un instantané automatique.
    /// Retourne Some(branche) si un instantané a été créé, None sinon.
    pub fn detecter_evenement(
        &mut self,
        _evt: EvenementDeclencheur,
    ) -> Result<Option<Arc<Branche>>, SolError> {
        todo!()
    }
}
