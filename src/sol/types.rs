use std::sync::Arc;
use std::time::Duration;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub struct Sol {
    pub branche_active: Arc<Branche>,
    pub drift: Drift,
    pub instantanes: Vec<Instantane>,
    pub params: SolParams,
}

#[derive(Serialize, Deserialize)]
pub struct Exploration {
    pub base: Arc<Branche>,
    pub sol_temp: Sol,
}

#[derive(Serialize, Deserialize)]
pub struct Branche {
    pub id: BrancheId,
    pub topo: Topologie,
    pub meta: MetaStruct,
    pub artefacts: Artefacts,
    pub contacts: Vec<Contact>,
    pub messages: Vec<Message>,
}

#[derive(Serialize, Deserialize)]
pub struct BrancheId(pub [u8; 32]);

#[derive(Serialize, Deserialize)]
pub struct Instantane {
    pub branche: Arc<Branche>,
    pub timestamp: DateTime<Utc>,
    pub origine: InstantaneOrigine,
}

#[derive(Serialize, Deserialize)]
pub enum InstantaneOrigine {
    Manuel,
    Auto(EvenementDeclencheur),
    Inactivite(Duration),
}

#[derive(Serialize, Deserialize)]
pub enum EvenementDeclencheur {
    ChangementStructurel,
    BlocConversation,
    AjoutArtefact,
}

#[derive(Serialize, Deserialize)]
pub struct Drift {
    pub messages_non_snapshot: Vec<Message>,
    pub nouveaux_contacts: Vec<Contact>,
    pub modifs_topo: Vec<TopoDelta>,
    pub artefacts_temp: Vec<Artefact>,
}

impl Default for Drift {
    fn default() -> Self {
        Self {
            messages_non_snapshot: Vec::new(),
            nouveaux_contacts: Vec::new(),
            modifs_topo: Vec::new(),
            artefacts_temp: Vec::new(),
        }
    }
}

// impl Default for Drift { ... }  // inchangé
// impl Drift { ... }              // inchangé

impl Drift {
    pub fn est_vide(&self) -> bool {
        self.messages_non_snapshot.is_empty()
            && self.nouveaux_contacts.is_empty()
            && self.modifs_topo.is_empty()
            && self.artefacts_temp.is_empty()
    }
}

#[derive(Clone, Serialize, Deserialize)]
pub struct SolParams {
    pub epsilon_topo_safe: f32,
    pub t_idle_snapshot: Duration,
    pub max_scalar_error: f32,
    pub q_bits: u8,
    pub bloc_conversation_seuil: usize,
}

// impl Default for SolParams { ... } // inchangé
impl Default for SolParams {
    fn default() -> Self {
        Self {
            epsilon_topo_safe: 1e-4,
            t_idle_snapshot: Duration::from_secs(4 * 3600),
            max_scalar_error: 1e-3,
            q_bits: 16,
            bloc_conversation_seuil: 10,
        }
    }
}


#[derive(Clone, Default, Serialize, Deserialize)]
pub struct Topologie;

#[derive(Clone, Default, Serialize, Deserialize)]
pub struct MetaStruct;

#[derive(Clone, Default, Serialize, Deserialize)]
pub struct Artefacts;

#[derive(Clone, Serialize, Deserialize)]
pub struct Contact;

#[derive(Clone, Serialize, Deserialize)]
pub struct Message;

#[derive(Clone, Serialize, Deserialize)]
pub struct TopoDelta;

#[derive(Clone, Serialize, Deserialize)]
pub struct Artefact;
