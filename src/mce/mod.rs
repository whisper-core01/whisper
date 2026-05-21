//! MCE — Moteur de Cohérence Externe
//!
//! Chaîne : UI → Dôme → Coursier → BAL_IN → MCE → BAL_OUT → Transporter → Daemon → réseau
//!
//! Invariants :
//! - Le MCE ne voit jamais l'UI, le Dôme, le Daemon, le réseau.
//! - Le MCE ne lit que sa BAL_IN.
//! - Le MCE ne sort que via sa BAL_OUT.
//! - Isolation parfaite. Organe froid, déterministe, aveugle.

pub mod bal;
pub mod types;
pub mod cycle;
pub mod fragment;
pub mod crypto;
pub mod entropie;
