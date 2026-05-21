//! Construction des Branches immuables.
//!
//! INVARIANT : BrancheBuilder::build() est le seul point d'entrée
//!             pour créer une Branche. Après build(), la Branche
//!             est définitivement immuable.

use crate::sol::types::{
    Artefacts, Branche, BrancheId, Contact, Drift, Message, MetaStruct, Topologie,
};

pub struct BrancheBuilder {
    pub topo: Topologie,
    pub meta: MetaStruct,
    pub artefacts: Artefacts,
    pub contacts: Vec<Contact>,
    pub messages: Vec<Message>,
}

impl BrancheBuilder {
    pub fn new() -> Self {
        Self {
            topo: Topologie,
            meta: MetaStruct,
            artefacts: Artefacts,
            contacts: Vec::new(),
            messages: Vec::new(),
        }
    }

    /// Construit un builder en partant d'une Branche existante
    /// et en y appliquant le contenu du Drift par-dessus.
    /// C'est le constructeur utilisé par snapshot().
    pub fn depuis_sol(base: &Branche, drift: &Drift) -> Self {
        let mut contacts = base.contacts.clone();
        contacts.extend(drift.nouveaux_contacts.clone());

        let mut messages = base.messages.clone();
        messages.extend(drift.messages_non_snapshot.clone());

        // TODO: appliquer drift.modifs_topo à base.topo
        // TODO: fusionner drift.artefacts_temp dans base.artefacts

        Self {
            topo: base.topo.clone(),
            meta: base.meta.clone(),
            artefacts: base.artefacts.clone(),
            contacts,
            messages,
        }
    }

    /// Point d'entrée unique pour construire une Branche immuable.
    /// L'identifiant est calculé par BLAKE3 sur le contenu sérialisé.
    pub fn build(self) -> Branche {
        let serialized = self.serialize_for_hash();
        let id = BrancheId(*blake3::hash(&serialized).as_bytes());

        Branche {
            id,
            topo: self.topo,
            meta: self.meta,
            artefacts: self.artefacts,
            contacts: self.contacts,
            messages: self.messages,
        }
    }

    /// Sérialisation minimale pour le calcul du BrancheId.
    /// TODO: implémenter la sérialisation réelle des champs.
    fn serialize_for_hash(&self) -> Vec<u8> {
        // TODO: sérialiser topo, meta, artefacts, contacts, messages
        Vec::new()
    }
}

impl Default for BrancheBuilder {
    fn default() -> Self {
        Self::new()
    }
}
