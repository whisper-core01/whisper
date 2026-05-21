//! Transport Reticulum — UDP loopback
//! Nœud → fragmenter → sceller → UDP → receiver → desceller → reconstruct

use std::net::UdpSocket;
use serde::{Serialize, Deserialize};
use crate::mce::crypto::FragmentScelle;

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Packet {
    pub node_id: u32,
    pub index: u32,
    pub fragment: FragmentScelle,
}

pub struct Node {
    pub id: u32,
    pub socket: UdpSocket,
    pub local_addr: String,
    pub remote_addr: String,
}

impl Node {
    pub fn new(id: u32, local_addr: &str, remote_addr: &str) -> Self {
        let socket = UdpSocket::bind(local_addr).expect("Failed to bind");
        socket.set_read_timeout(Some(std::time::Duration::from_secs(5))).ok();
        Node {
            id,
            socket,
            local_addr: local_addr.to_string(),
            remote_addr: remote_addr.to_string(),
        }
    }

    pub fn send_packet(&self, pkt: &Packet) -> std::io::Result<()> {
        let data = bincode::serialize(pkt).expect("Serialize failed");
        self.socket.send_to(&data, &self.remote_addr)?;
        Ok(())
    }

    pub fn recv_packet(&self) -> std::io::Result<Packet> {
        let mut buf = [0u8; 4096];
        let (n, _) = self.socket.recv_from(&mut buf)?;
        let pkt = bincode::deserialize(&buf[..n]).expect("Deserialize failed");
        Ok(pkt)
    }
}
