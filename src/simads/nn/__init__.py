"""Neural-network helpers for pixelated filter surrogate models."""

from .pixel_qr_surrogate import (
    TORCH_AVAILABLE,
    PixelQrS21Surrogate,
    bandpass_frequency_weights,
    masked_aux_mse,
    masked_weighted_mse,
    require_torch,
    s21_aux_feature_tensor,
    s21_bandpass_features,
)
from .interdigital_surrogate import InterdigitalSParamSurrogate

__all__ = [
    "TORCH_AVAILABLE",
    "PixelQrS21Surrogate",
    "InterdigitalSParamSurrogate",
    "bandpass_frequency_weights",
    "masked_aux_mse",
    "masked_weighted_mse",
    "require_torch",
    "s21_aux_feature_tensor",
    "s21_bandpass_features",
]
