pub struct Moteur {
    modele: CandleModel,
}

impl Moteur {
    pub fn nouveau(cfg: ConfigMoteur) -> Result<Self>;

    pub fn mvf(&self, ctx: &ContexteMVF) -> Result<SuggestionsMVF>;
    pub fn mce(&self, ctx: &ContexteMCE) -> Result<SuggestionsMCE>;
    pub fn defense(&self, etat: &EtatSysteme) -> Result<Vec<StrategieDefense>>;
    pub fn bio(&self, sol: &Sol) -> Result<AjoutsBiologiques>;
}

