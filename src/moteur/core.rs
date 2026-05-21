use crate::moteur::{
    loader::CandleModel,
    infer::generer_structure,
    profiles::*,
    types::*,
};

pub struct Moteur {
    modele: CandleModel,
}

impl Moteur {
    pub fn nouveau(cfg: ConfigMoteur) -> Result<Self> {
        let modele = CandleModel::charger(cfg)?;
        Ok(Self { modele })
    }

    pub fn mvf(&self, ctx: &ContexteMVF) -> Result<SuggestionsMVF> {
        let prompt = ProfilMVF::construire_prompt(ctx);
        generer_structure::<SuggestionsMVF>(&self.modele, &prompt)
    }

    pub fn mce(&self, ctx: &ContexteMCE) -> Result<SuggestionsMCE> {
        let prompt = ProfilMCE::construire_prompt(ctx);
        generer_structure::<SuggestionsMCE>(&self.modele, &prompt)
    }

    pub fn defense(&self, etat: &EtatSysteme) -> Result<Vec<StrategieDefense>> {
        let prompt = ProfilDefense::construire_prompt(etat);
        generer_structure::<Vec<StrategieDefense>>(&self.modele, &prompt)
    }

    pub fn bio(&self, sol: &Sol) -> Result<AjoutsBiologiques> {
        let prompt = ProfilBio::construire_prompt(sol);
        generer_structure::<AjoutsBiologiques>(&self.modele, &prompt)
    }
}

