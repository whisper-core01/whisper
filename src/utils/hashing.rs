//! Helpers pour BLAKE3 et conversions cryptographiques.

/// Hash BLAKE3 d'un slice de bytes. Retourne 32 bytes.
pub fn hash_bytes(data: &[u8]) -> [u8; 32] {
    *blake3::hash(data).as_bytes()
}

/// Hash BLAKE3 incrémental sur plusieurs sources.
pub fn hash_multiple(parts: &[&[u8]]) -> [u8; 32] {
    let mut hasher = blake3::Hasher::new();
    for part in parts {
        hasher.update(part);
    }
    *hasher.finalize().as_bytes()
}
