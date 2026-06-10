use whisper::mce::fragment::{fragmenter, ParamsFragment};
use whisper::mce::crypto::{CleEphem, sceller, desceller, nonce_ephemere};

fn main() {
    // Gros message pour tester fragmentation
    let message = b"WHISPER".repeat(10000); // ~70KB
    let maitre = [0xABu8; 32];
    let cle = CleEphem::deriver(&maitre, b"test", b"nonce");
    let seed = [0x42u8; 32];

    let params = ParamsFragment::default();
    let fragments = fragmenter(&message, &params, &seed);
    println!("Message: {} bytes → {} fragments", message.len(), fragments.len());

    let mut descelles = 0;
        for (i, frag) in fragments.iter().enumerate() {
        let nonce = nonce_ephemere(&seed, i as u64);
        let scelle = sceller(i as u32, &frag.contenu, &cle, &nonce);

        if desceller(&scelle, &cle).is_some() {
            descelles += 1;
         }
       }	

    println!("✅ {} fragments descellés avec succès", descelles);
}
