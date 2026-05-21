//! LZH — compression LZ77 + Huffman après TurboQuant.
//! Utilise flate2 (deflate) qui est LZ77 + Huffman = LZH.

use flate2::Compression;
use flate2::write::DeflateEncoder;
use flate2::read::DeflateDecoder;
use std::io::{Read, Write};

/// Compresse un slice de bytes via LZH (deflate).
pub fn comprimer(data: &[u8]) -> Result<Vec<u8>, std::io::Error> {
    let mut encoder = DeflateEncoder::new(Vec::new(), Compression::best());
    encoder.write_all(data)?;
    encoder.finish()
}

/// Décompresse un slice de bytes LZH.
pub fn decompresser(data: &[u8]) -> Result<Vec<u8>, std::io::Error> {
    let mut decoder = DeflateDecoder::new(data);
    let mut out = Vec::new();
    decoder.read_to_end(&mut out)?;
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;

   #[test]
fn aller_retour_lzh() {
    let data = b"hello whisper".repeat(100);
    let compressed = comprimer(&data).unwrap();
    let decompressed = decompresser(&compressed).unwrap();
    assert_eq!(data.as_slice(), decompressed.as_slice());
}

    #[test]
fn lzh_reduit_la_taille() {
    let data = b"aaaaaaaaabbbbbbbbcccccccc".repeat(100);
    let compressed = comprimer(&data).unwrap();
    assert!(compressed.len() < data.len());
    }
}
