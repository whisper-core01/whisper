use std::net::UdpSocket;
use std::thread;
use std::time::Duration;
use whisper::mce::fragment::fragmenter;
use whisper::mce::crypto::{CleEphem, sceller, desceller, nonce_ephemere, FragmentScelle};

fn main() {
    println!("=== Reticulum UDP Test ===\n");

    let msg = b"WHISPER network test".repeat(30).to_vec();
    println!("Message: {} bytes\n", msg.len());

    let msg = std::sync::Arc::new(msg);

    // Receiver
    let msg_r = msg.clone();
    let receiver = thread::spawn(move || {
        println!("[RX] Bind 127.0.0.1:7002");
        let sock = UdpSocket::bind("127.0.0.1:7002").unwrap();
        sock.set_read_timeout(Some(Duration::from_secs(5))).ok();

        let cle = CleEphem::deriver(&[0xABu8; 32], b"net", b"test");
        let mut frags = Vec::new();

        for _ in 0..10 {
            let mut buf = [0u8; 2048];
            match sock.recv_from(&mut buf) {
                Ok((n, _)) => {
                    if let Ok(scelle) = bincode::deserialize::<FragmentScelle>(&buf[..n]) {
                        if let Some(plain) = desceller(&scelle, &cle) {
                            println!("[RX] Fragment {} OK ({} bytes)", scelle.index, plain.len());
                            frags.push((scelle.index, plain));
                        }
                    }
                }
                Err(_) => break,
            }
        }

        frags.sort_by_key(|(idx, _)| *idx);
        frags.into_iter().flat_map(|(_, f)| f).collect::<Vec<_>>()
    });

    thread::sleep(Duration::from_millis(200));

    // Sender
    let msg_s = msg.clone();
    let sender = thread::spawn(move || {
        println!("[TX] Bind 127.0.0.1:7001");
        let sock = UdpSocket::bind("127.0.0.1:7001").unwrap();

        let cle = CleEphem::deriver(&[0xABu8; 32], b"net", b"test");
        let nonce = nonce_ephemere(&[0x42u8; 32], 0);
        
        let frags = fragmenter(&msg_s, &Default::default(), &[0x42u8; 32]);
        println!("[TX] {} fragments\n", frags.len());

        for (i, f) in frags.iter().enumerate() {
            let scelle = sceller(f.index, &f.contenu, &cle, &nonce);
            if let Ok(data) = bincode::serialize(&scelle) {
                sock.send_to(&data, "127.0.0.1:7002").ok();
                println!("[TX] Fragment {} sent", i);
            }
            thread::sleep(Duration::from_millis(50));
        }
        println!("[TX] Done\n");
    });

    sender.join().unwrap();
    let recon = receiver.join().unwrap();

    println!("Reconstructed: {} bytes", recon.len());
    println!("Original:      {} bytes", msg.len());
    if recon == msg.as_slice() {
        println!("✅ SUCCESS!");
    } else {
        println!("❌ FAIL!");
        println!("First 50 recon: {:?}", &recon[..recon.len().min(50)]);
        println!("First 50 orig:  {:?}", &msg[..msg.len().min(50)]);
    }
}
