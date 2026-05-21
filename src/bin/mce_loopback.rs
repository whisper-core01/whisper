use std::sync::mpsc;
use std::sync::Arc;
use std::thread;
use whisper::mce::fragment::{fragmenter, ParamsFragment};
use whisper::mce::crypto::{CleEphem, sceller, desceller, nonce_ephemere, FragmentScelle};

fn main() {
    println!("=== MCE Loopback Test (2 threads) ===\n");

    let message = b"WHISPER mesh loopback test".repeat(100).to_vec();
    println!("Message: {} bytes\n", message.len());

    let (tx, rx) = mpsc::channel::<(u32, FragmentScelle)>();

    // Partager la clé maître via Arc
    let maitre = Arc::new([0xABu8; 32]);
    let maitre_sender = Arc::clone(&maitre);
    let maitre_receiver = Arc::clone(&maitre);

    // Thread A: Sender
    let message_clone = message.clone();
    let sender = thread::spawn(move || {
        println!("[Sender] Starting...");
        let cle = CleEphem::deriver(&maitre_sender, b"loopback", b"test");
        let seed = [0x42u8; 32];
        let nonce = nonce_ephemere(&seed, 0);
        
        let params = ParamsFragment::default();
        let fragments = fragmenter(&message_clone, &params, &seed);
        
        println!("[Sender] Fragmenté en {} fragments", fragments.len());
        
        for (i, frag) in fragments.iter().enumerate() {
            let scelle = sceller(frag.index, &frag.contenu, &cle, &nonce);
            tx.send((frag.index, scelle)).unwrap();
            println!("[Sender] Fragment {} envoyé", i);
        }
        println!("[Sender] Tous les fragments envoyés\n");
    });

    // Thread B: Receiver
    let receiver = thread::spawn(move || {
        println!("[Receiver] En attente de fragments...\n");
        let cle = CleEphem::deriver(&maitre_receiver, b"loopback", b"test");
        let mut fragments_recus = Vec::new();
        
        while let Ok((idx, scelle)) = rx.recv() {
            match desceller(&scelle, &cle) {
                Some(plaintext) => {
                    fragments_recus.push((idx, plaintext));
                    println!("[Receiver] Fragment {} reçu et descellé", idx);
                }
                None => panic!("[Receiver] Fragment {} authentication failed!", idx),
            }
        }
        
        println!("\n[Receiver] {} fragments reçus", fragments_recus.len());
        
        fragments_recus.sort_by_key(|(idx, _)| *idx);
        let reconstructed: Vec<u8> = fragments_recus
            .into_iter()
            .flat_map(|(_, data)| data)
            .collect();
        
        reconstructed
    });

    sender.join().unwrap();
    let reconstructed = receiver.join().unwrap();
    
    println!("[Main] Message reconstructed: {} bytes", reconstructed.len());
    
    if reconstructed == message {
        println!("✅ SUCCESS: Loopback complete!");
    } else {
        panic!("❌ FAIL: Mismatch!");
    }
}
