//! Test MCE end-to-end: fragmenter → sceller → desceller → reconstruire

use whisper::mce::fragment::{fragmenter, ParamsFragment};
use whisper::mce::crypto::{CleEphem, sceller, desceller, nonce_ephemere};

fn main() {
    println!("=== MCE End-to-End Test ===\n");

    // Message plaintext
    let message = b"WHISPER: sovereign encrypted mesh communication".repeat(10);
    println!("Message original ({} bytes)", message.len());

    // Clé maître (simulée)
    let maitre = [0xABu8; 32];
    let cle = CleEphem::deriver(&maitre, b"test", b"nonce");

    // Seed pour nonce non-rejouable
    let seed = [0x42u8; 32];
    let nonce = nonce_ephemere(&seed, 0);
    println!("Nonce: {:?}\n", nonce);

    // 1. Fragmenter
    let params = ParamsFragment::default();
    let fragments = fragmenter(&message, &params, &seed);
    println!("✓ Fragmenté en {} fragments", fragments.len());

    // 2. Sceller chaque fragment
    let mut fragments_scelles = Vec::new();
    for (i, frag) in fragments.iter().enumerate() {
        let scelle = sceller(frag.index, &frag.contenu, &cle, &nonce);
        let ciphertext_len = scelle.ciphertext.len();
        fragments_scelles.push((frag.index, scelle));
        println!("  Fragment {}: {} → {} bytes (chiffré)", i, frag.contenu.len(), ciphertext_len);
    }

    // 3. Desceller chaque fragment
    let mut fragments_descelles = Vec::new();
    for (idx, scelle) in &fragments_scelles {
        match desceller(scelle, &cle) {
            Some(plaintext) => {
                let len = plaintext.len();
                fragments_descelles.push((*idx, plaintext));
                println!("✓ Fragment {} descellé ({} bytes)", idx, len);
            }
            None => panic!("Fragment {} failed authentication!", idx),
        }
    }

    // 4. Reconstruire
    fragments_descelles.sort_by_key(|(idx, _)| *idx);
    let reconstructed: Vec<u8> = fragments_descelles
        .into_iter()
        .flat_map(|(_, data)| data)
        .collect();

    println!("\n✓ Reconstructed: {} bytes", reconstructed.len());

    // Vérifier
    if reconstructed == message {
        println!("✅ SUCCESS: Message matches original!");
    } else {
        panic!("❌ FAIL: Message mismatch!");
    }
}
