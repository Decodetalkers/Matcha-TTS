from typing import Optional, Protocol, List

from dataclasses import dataclass


@dataclass
class EncoderConfig:
    encoder_type: str
    encoder_params: EncoderParams
    duration_predictor_params: DurationPredictorParams


@dataclass
class EncoderParams:
    n_feats: int
    n_channels: int
    filter_channels: int
    filter_channels_dp: int
    n_head: int
    n_layers: int
    kernel_size: int
    p_dropout: float
    spk_emb_dim: int
    n_spks: int
    prenet: float


@dataclass
class DurationPredictorParams:
    filter_channels_dp: float
    kernel_size: int
    p_dropout: float


@dataclass
class CFMParam:
    solver: str

    sigma_min: Optional[float]


@dataclass
class DataStatisTics:
    mel_mean: float
    mel_std: float
