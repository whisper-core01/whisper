use candle_core::{Device};
use candle_transformers::models::llama::{Model as LlamaModel, Config as LlamaConfig};
use candle_transformers::quantized::gguf::GgufModel;

pub struct CandleModel {
    pub modele: LlamaModel,
    pub device: Device,
}

impl CandleModel {
    pub fn charger(cfg: ConfigMoteur) -> Result<Self> {
        let device = if cfg.use_gpu {
            Device::new_cuda(0)?
        } else {
            Device::Cpu
        };

        // Charge le fichier GGUF
        let gguf = GgufModel::from_path(&cfg.chemin_modele)?;

        // Construit la config Candle
        let config = LlamaConfig::from_gguf(&gguf)?;

        // Instancie le modèle
        let modele = LlamaModel::load(gguf, &config, &device)?;

        Ok(Self { modele, device })
    }
}

