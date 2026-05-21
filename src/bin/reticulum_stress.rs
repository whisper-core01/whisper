use std::net::UdpSocket;
use std::thread;
use std::time::{Duration, Instant};
use whisper::mce::fragment::fragmenter;
use whisper::mce::crypto::{CleEphem, sceller, desceller, nonce_ephemere, FragmentScelle};

fn main() {
    println!("=== Reticulum Stress Test ===\n");

    let msg = b"WHISPER stress test - ".repeat(500000);
    println!("Message: {} MB\n", msg.len() / 1_000_000);

    let msg = std::sync::Arc::new(msg);

    // Receiver
    let msg_r = msg.clone();
    let receiver = thread::spawn(move || {
        println!("[RX] Starting receiver...");
        let sock = UdpSocket::bind("127.0.0.1:7003").unwrap();
        sock.set_read_timeout(Some(Duration::from_secs(2))).ok();

        let cle = CleEphem::deriver(&[0xABu8; 32], b"stress", b"test");
        let mut frags = Vec::new();
        let mut received = 0;
        let mut empty_count = 0;

        // Reçoit jusqu'à 5 timeouts consécutifs (indique fin)
        loop {
            let mut buf = [0u8; 65536];
            match sock.recv_from(&mut buf) {
                Ok((n, _)) => {
                    empty_count = 0;
                    if let Ok(scelle) = bincode::deserialize::<FragmentScelle>(&buf[..n]) {
                        if let Some(plain) = desceller(&scelle, &cle) {
                            frags.push((scelle.index, plain));
                            received += 1;
                            if received % 1000 == 0 {
                                println!("[RX] {} fragments", received);
                            }
                        }
                    }
                }
                Err(_) => {
                    empty_count += 1;
                    if empty_count > 5 {
                        break;
                    }
                }
            }
        }

        println!("[RX] Total: {}", received);
        frags.sort_by_key(|(idx, _)| *idx);
        frags.into_iter().flat_map(|(_, f)| f).collect::<Vec<_>>()
    });

    thread::sleep(Duration::from_millis(500));

    // Sender
    let msg_s = msg.clone();
    let sender = thread::spawn(move || {
        println!("[TX] Starting sender...");
        let sock = UdpSocket::bind("127.0.0.1:7004").unwrap();

        let cle = CleEphem::deriver(&[0xABu8; 32], b"stress", b"test");
        let nonce = nonce_ephemere(&[0x42u8; 32], 0);
        
        let start = Instant::now();
        let frags = fragmenter(&msg_s, &Default::default(), &[0x42u8; 32]);
        println!("[TX] {} fragments", frags.len());

        let mut sent = 0;
        for f in frags.iter() {
            let scelle = sceller(f.index, &f.contenu, &cle, &nonce);
            if let Ok(data) = bincode::serialize(&scelle) {
                sock.send_to(&data, "127.0.0.1:7003").ok();
                sent += 1;
                if sent % 1000 == 0 {
                    println!("[TX] {} sent", sent);
                }
            }
        }
        println!("[TX] Done in {:?}\n", start.elapsed());
    });

    let start = Instant::now();
    sender.join().unwrap();
    let recon = receiver.join().unwrap();
    let elapsed = start.elapsed();

    println!("\n=== Results ===");
    println!("Recon: {:.2} MB", recon.len() as f64 / 1_000_000.0);
    println!("Orig:  {:.2} MB", msg.len() as f64 / 1_000_000.0);
    println!("Time:  {:.2}s", elapsed.as_secs_f64());
    println!("Speed: {:.2} MB/s", (msg.len() as f64 / 1_000_000.0) / elapsed.as_secs_f64());
    
    if recon == msg.as_slice() {
        println!("✅ SUCCESS!");
    } else {
        println!("❌ FAIL: Lost {} bytes", msg.len() - recon.len());
    }
}
