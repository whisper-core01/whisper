//! Module central : moteur Sol / Branches / Instantanés.
//!
//! Invariants garantis :
//! - Une Branche est immuable après construction.
//! - Le Sol est vivant (mutable), toujours dérivé d'une Branche.
//! - epsilon_topo_safe est global au Sol, jamais par Branche.
//! - La greffe ne fusionne rien — elle recompose.

pub mod builder;
pub mod errors;
pub mod topo;
pub mod transitions;
pub mod types;
