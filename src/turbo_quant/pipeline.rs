//! Pipeline TurboQuant : encode / decode.
//!
//! v1 : quantisation scalaire 8/16 bits + delta encoding sur séquences.
//! Coordonnées fractales (Topologie) : TODO quand Topologie sera définie.

use super::header::{HeaderTQ, ModeBloc};
use super::passthrough::est_incompressible;

// CRC32 maison minimal (pas de dépendance externe)
fn crc32_simple(data: &[u8]) -> u32 {
    let mut crc: u32 = 0xFFFFFFFF;
    for &b in data {
        crc ^= b as u32;
        for _ in 0..8 {
            if crc & 1 != 0 { crc = (crc >> 1) ^ 0xEDB88320; }
            else             { crc >>= 1; }
        }
    }
    !crc
}

/// Encode un slice de bytes via TurboQuant.
/// Retourne : header sérialisé + payload encodé.
pub fn encoder(data: &[u8], epsilon: f32, q_bits: u8) -> Vec<u8> {
    let taille_originale = data.len() as u64;

    let (payload, header) = if est_incompressible(data) {
        // Passthrough — données trop aléatoires, on ne touche pas
        let checksum = crc32_simple(data);
        let h = HeaderTQ::new_raw(taille_originale, checksum);
        (data.to_vec(), h)
    } else {
        // Encodage : delta encoding sur les bytes
        let encoded = delta_encode(data);
        let checksum = crc32_simple(&encoded);
        let h = HeaderTQ::new_encode(epsilon, q_bits, taille_originale, checksum);
        (encoded, h)
    };

    // Sérialiser header + payload
    let header_bytes = bincode::serialize(&header).expect("header TQ sérialisable");
    let header_len = header_bytes.len() as u32;

    let mut out = Vec::with_capacity(4 + header_bytes.len() + payload.len());
    out.extend_from_slice(&header_len.to_le_bytes()); // taille header
    out.extend_from_slice(&header_bytes);              // header
    out.extend_from_slice(&payload);                   // payload

    out
}

/// Décode un bloc TurboQuant.
pub fn decoder(data: &[u8]) -> Result<Vec<u8>, String> {
    if data.len() < 4 {
        return Err("bloc TQ trop court".into());
    }

    // Lire taille header
    let header_len = u32::from_le_bytes(data[..4].try_into().unwrap()) as usize;
    if data.len() < 4 + header_len {
        return Err("bloc TQ tronqué".into());
    }

    // Désérialiser header
    let header: HeaderTQ = bincode::deserialize(&data[4..4 + header_len])
        .map_err(|e| format!("header TQ invalide: {e}"))?;

    if &header.magic != b"TQ01" {
        return Err("magic TQ invalide".into());
    }

    let payload = &data[4 + header_len..];

    // Vérifier checksum
    let checksum = crc32_simple(payload);
    if checksum != header.checksum {
        return Err(format!(
            "checksum TQ invalide: attendu {}, reçu {}", header.checksum, checksum
        ));
    }

    // Décoder selon le mode
    let decoded = match header.mode {
        ModeBloc::Raw    => payload.to_vec(),
        ModeBloc::Encode => delta_decode(payload),
    };

    Ok(decoded)
}

/// Delta encoding : chaque byte = différence avec le précédent.
/// Très efficace sur des données corrélées (métadonnées, TTL, flags).
fn delta_encode(data: &[u8]) -> Vec<u8> {
    if data.is_empty() { return vec![]; }
    let mut out = Vec::with_capacity(data.len());
    out.push(data[0]);
    for i in 1..data.len() {
        out.push(data[i].wrapping_sub(data[i - 1]));
    }
    out
}

fn delta_decode(data: &[u8]) -> Vec<u8> {
    if data.is_empty() { return vec![]; }
    let mut out = Vec::with_capacity(data.len());
    out.push(data[0]);
    for i in 1..data.len() {
        out.push(data[i].wrapping_add(out[i - 1]));
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn aller_retour_donnees_simples() {
        let data = b"hello whisper".repeat(10);
        let encoded = encoder(&data, 1e-4, 16);
        let decoded = decoder(&encoded).unwrap();
        assert_eq!(data.as_slice(), decoded.as_slice());
    }

    #[test]
    fn aller_retour_donnees_aleatoires() {
        // données haute entropie → passthrough
        let data: Vec<u8> = (0..=255u8).cycle().take(512).collect();
        let encoded = encoder(&data, 1e-4, 16);
        let decoded = decoder(&encoded).unwrap();
        assert_eq!(data, decoded);
    }

    #[test]
    fn checksum_detecte_corruption() {
        let data = b"donnees importantes".repeat(5);
        let mut encoded = encoder(&data, 1e-4, 16);
        // corrompre un byte dans le payload
        let last = encoded.len() - 1;
        encoded[last] ^= 0xFF;
        assert!(decoder(&encoded).is_err());
    }

    #[test]
    fn delta_encode_decode_aller_retour() {
        let data: Vec<u8> = (0u8..=200).collect();
        let encoded = delta_encode(&data);
        let decoded = delta_decode(&encoded);
        assert_eq!(data, decoded);
    }
}