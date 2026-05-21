//! TurboQuant — pré-encodeur avant LZH + LUKS
//!
//! Pipeline : Sol → bincode → TurboQuant → LZH → LUKS
//!
//! Invariants :
//! - lossy by design, lossless in intent
//! - passthrough-safe : flux incompressible → marqué "raw", jamais corrompu
//! - paramètres explicites, versionnés dans le header de bloc

pub mod header;
pub mod pipeline;
pub mod passthrough;
pub mod lzh;

pub use pipeline::encoder;
pub use pipeline::decoder;
