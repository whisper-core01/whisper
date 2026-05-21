use crate::moteur::loader::CandleModel;
use crate::moteur::types::*;
use serde::de::DeserializeOwned;

pub fn generer_structure<T: DeserializeOwned>(
    modele: &CandleModel,
    prompt: &PromptFroid,
) -> Result<T> {
    // 1. Encoder le prompt froid en tokens
    let tokens = prompt.encoder()?;

    // 2. Appeler Candle pour générer une sortie brute
    let sortie = modele.modele.forward(&tokens)?;

    // 3. Décoder la sortie en JSON interne
    let json = prompt.decoder(&sortie)?;

    // 4. Convertir en structure typée
    let structure: T = serde_json::from_str(&json)?;

    Ok(structure)
}

