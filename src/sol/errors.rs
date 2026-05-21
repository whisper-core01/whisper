//! Erreurs du moteur Sol.

#[derive(Debug)]
pub enum SolError {
    /// Snapshot impossible : le drift contient des données non cohérentes.
    DriftNonVide,
    /// L'instantané demandé n'existe pas dans ce Sol.
    InstantaneIntrouvable,
    /// Branche incompatible à la greffe (epsilon ou version incohérents).
    BrancheIncompatible,
    /// greffer() appelé avec une liste vide — interdit.
    GreffeSansSource,
}

impl std::fmt::Display for SolError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            SolError::DriftNonVide => write!(f, "snapshot impossible : drift non vide"),
            SolError::InstantaneIntrouvable => write!(f, "instantané introuvable"),
            SolError::BrancheIncompatible => write!(f, "branche incompatible à la greffe"),
            SolError::GreffeSansSource => write!(f, "greffe impossible : aucune branche source"),
        }
    }
}

impl std::error::Error for SolError {}
