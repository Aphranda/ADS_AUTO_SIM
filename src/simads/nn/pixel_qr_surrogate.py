"""Small CNN surrogate for 16x16 pixel QR BPF S-parameter prediction.

S21 remains the primary optimization signal, but the model can also learn
S11/S22 as auxiliary curve targets so the surrogate carries reflection context.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

try:  # pragma: no cover - exercised when the optional nn dependency exists.
    import torch
    from torch import Tensor, nn
except ImportError:  # pragma: no cover - keeps non-NN project tools importable.
    torch = None
    Tensor = Any  # type: ignore[assignment]
    nn = None  # type: ignore[assignment]


TORCH_AVAILABLE = torch is not None


def require_torch() -> Any:
    if torch is None:
        raise RuntimeError(
            "PyTorch is required for simads.nn. Install the optional dependency, "
            "for example: python -m pip install -e .[nn]"
        )
    return torch


@dataclass(frozen=True)
class S21BandpassFeatures:
    passband_min_db: float
    passband_avg_db: float
    passband_ripple_db: float
    s21_5g_db: float
    low_stop_max_db: float
    high_stop_max_db: float
    bandpass_score: float


def _finite_values(freq_ghz: list[float], s21_db: list[float], start: float, stop: float) -> list[float]:
    return [
        float(value)
        for freq, value in zip(freq_ghz, s21_db, strict=False)
        if start <= float(freq) <= stop and math.isfinite(float(value))
    ]


def _value_at_freq(freq_ghz: list[float], s21_db: list[float], target: float, *, tol: float = 1e-6) -> float:
    pairs = [
        (float(freq), float(value))
        for freq, value in zip(freq_ghz, s21_db, strict=False)
        if math.isfinite(float(freq)) and math.isfinite(float(value))
    ]
    if not pairs:
        return float("nan")
    for freq, value in pairs:
        if abs(freq - target) <= tol:
            return value
    pairs.sort(key=lambda item: item[0])
    if target < pairs[0][0] or target > pairs[-1][0]:
        return float("nan")
    for (left_f, left_v), (right_f, right_v) in zip(pairs, pairs[1:], strict=False):
        if left_f <= target <= right_f and right_f > left_f:
            alpha = (target - left_f) / (right_f - left_f)
            return left_v + alpha * (right_v - left_v)
    return float("nan")


def s21_bandpass_features(
    freq_ghz: list[float],
    s21_db: list[float],
    *,
    passband: tuple[float, float] = (6.0, 8.0),
    low_stop: tuple[float, float] = (1.0, 5.5),
    high_stop: tuple[float, float] = (8.5, 10.0),
    low_notch_freq_ghz: float = 5.0,
    pass_min_target_db: float = -5.0,
    ripple_target_db: float = 3.5,
    stop_max_target_db: float = -20.0,
) -> S21BandpassFeatures:
    """Compute S21-only features and a scalar 6-8 GHz BPF feedback score."""

    pass_values = _finite_values(freq_ghz, s21_db, *passband)
    low_values = _finite_values(freq_ghz, s21_db, *low_stop)
    high_values = _finite_values(freq_ghz, s21_db, *high_stop)

    pass_min = min(pass_values) if pass_values else float("nan")
    pass_max = max(pass_values) if pass_values else float("nan")
    pass_avg = sum(pass_values) / len(pass_values) if pass_values else float("nan")
    ripple = pass_max - pass_min if pass_values else float("nan")
    s21_5g = _value_at_freq(freq_ghz, s21_db, low_notch_freq_ghz)
    low_stop_max = max(low_values) if low_values else float("nan")
    high_stop_max = max(high_values) if high_values else float("nan")

    score = 100.0
    if math.isfinite(pass_min):
        score -= 14.0 * max(0.0, pass_min_target_db - pass_min) ** 2
        score += 1.8 * pass_avg
    else:
        score -= 80.0
    if math.isfinite(ripple):
        score -= 4.0 * max(0.0, ripple - ripple_target_db) ** 2
        score -= 1.0 * ripple
    else:
        score -= 40.0
    if math.isfinite(low_stop_max):
        score -= 2.0 * max(0.0, low_stop_max - stop_max_target_db) ** 2
    else:
        score -= 20.0
    if math.isfinite(s21_5g):
        score -= 4.0 * max(0.0, s21_5g - stop_max_target_db) ** 2
    else:
        score -= 20.0
    if math.isfinite(high_stop_max):
        score -= 2.0 * max(0.0, high_stop_max - stop_max_target_db) ** 2
    else:
        score -= 20.0

    return S21BandpassFeatures(
        passband_min_db=pass_min,
        passband_avg_db=pass_avg,
        passband_ripple_db=ripple,
        s21_5g_db=s21_5g,
        low_stop_max_db=low_stop_max,
        high_stop_max_db=high_stop_max,
        bandpass_score=score,
    )


def bandpass_frequency_weights(
    freq_ghz: list[float],
    *,
    passband: tuple[float, float] = (6.0, 8.0),
    low_stop: tuple[float, float] = (1.0, 5.5),
    high_stop: tuple[float, float] = (8.5, 10.0),
) -> list[float]:
    """Higher weights where the S21 curve controls the 6-8 GHz BPF decision."""

    weights: list[float] = []
    for freq in freq_ghz:
        value = 1.0
        if low_stop[0] <= freq <= low_stop[1]:
            value = 2.0
        if passband[0] <= freq <= passband[1]:
            value = 4.0
        if high_stop[0] <= freq <= high_stop[1]:
            value = 2.8
        if abs(freq - 5.0) < 1e-9:
            value += 4.0
        if abs(freq - passband[0]) < 1e-9 or abs(freq - passband[1]) < 1e-9:
            value += 1.5
        weights.append(value)
    return weights


if nn is not None:

    class ResidualSeparableConvBlock(nn.Module):
        """Depthwise 3x3 + pointwise 1x1 block for local pixel connectivity."""

        def __init__(self, channels: int, *, dilation: int = 1) -> None:
            super().__init__()
            padding = dilation
            self.depthwise = nn.Conv2d(
                channels,
                channels,
                kernel_size=3,
                padding=padding,
                dilation=dilation,
                groups=channels,
                bias=False,
            )
            self.pointwise = nn.Conv2d(channels, channels, kernel_size=1, bias=False)
            self.norm = nn.GroupNorm(num_groups=min(8, channels), num_channels=channels)
            self.act = nn.SiLU()

        def forward(self, x: Tensor) -> Tensor:
            residual = x
            x = self.depthwise(x)
            x = self.pointwise(x)
            x = self.norm(x)
            x = self.act(x)
            return x + residual


    class PixelQrS21Surrogate(nn.Module):
        """Locality-aware CNN that maps a pixel mask to sampled S21(dB)."""

        def __init__(
            self,
            *,
            matrix_n: int = 16,
            num_freqs: int = 19,
            num_sparams: int = 1,
            channels: int = 32,
            coord_channels: bool = True,
            mask_channels: int = 1,
            geom_features: int = 0,
            hidden: int = 96,
            aux_features: int = 7,
        ) -> None:
            super().__init__()
            self.matrix_n = matrix_n
            self.num_freqs = num_freqs
            self.num_sparams = num_sparams
            self.coord_channels = coord_channels
            self.mask_channels = mask_channels
            self.geom_features = geom_features
            self.aux_features = aux_features
            in_channels = mask_channels + 2 if coord_channels else mask_channels
            self.stem = nn.Sequential(
                nn.Conv2d(in_channels, channels, kernel_size=3, padding=1, bias=False),
                nn.GroupNorm(num_groups=min(8, channels), num_channels=channels),
                nn.SiLU(),
            )
            self.blocks = nn.Sequential(
                ResidualSeparableConvBlock(channels, dilation=1),
                ResidualSeparableConvBlock(channels, dilation=1),
                ResidualSeparableConvBlock(channels, dilation=2),
                ResidualSeparableConvBlock(channels, dilation=1),
            )
            self.avg_pool = nn.AdaptiveAvgPool2d(1)
            self.max_pool = nn.AdaptiveMaxPool2d(1)
            self.embedding = nn.Sequential(
                nn.Flatten(),
                nn.Linear(channels * 2 + geom_features, hidden),
                nn.SiLU(),
                nn.Dropout(p=0.05),
            )
            self.curve_head = nn.Linear(hidden, num_sparams * num_freqs)
            self.aux_head = nn.Linear(hidden, aux_features)

            # A global-pooling CNN can miss a single destructive local edit.
            # The auxiliary head gives small datasets direct supervision on
            # decision features such as 6G/8G guard points and 5G leakage.

        def _append_coord_channels(self, x: Tensor) -> Tensor:
            if not self.coord_channels:
                return x
            if x.shape[1] != self.mask_channels:
                raise ValueError(f"expected {self.mask_channels} input mask channels, got {x.shape[1]}")
            batch, _, height, width = x.shape
            device = x.device
            dtype = x.dtype
            yy = torch.linspace(-1.0, 1.0, height, device=device, dtype=dtype).view(1, 1, height, 1)
            xx = torch.linspace(-1.0, 1.0, width, device=device, dtype=dtype).view(1, 1, 1, width)
            xx = xx.expand(batch, 1, height, width)
            yy = yy.expand(batch, 1, height, width)
            return torch.cat([x, xx, yy], dim=1)

        def _embed(self, x: Tensor, geom: Tensor | None = None) -> Tensor:
            x = self._append_coord_channels(x)
            x = self.stem(x)
            x = self.blocks(x)
            x = torch.cat([self.avg_pool(x), self.max_pool(x)], dim=1)
            if self.geom_features:
                if geom is None:
                    geom = torch.zeros(
                        x.shape[0],
                        self.geom_features,
                        device=x.device,
                        dtype=x.dtype,
                    )
                if geom.shape != (x.shape[0], self.geom_features):
                    raise ValueError(f"expected geom shape {(x.shape[0], self.geom_features)}, got {tuple(geom.shape)}")
                while geom.ndim < x.ndim:
                    geom = geom.unsqueeze(-1)
                x = torch.cat([x, geom], dim=1)
            x = self.embedding(x)
            return x

        def forward(self, x: Tensor, geom: Tensor | None = None) -> Tensor:
            x = self._embed(x, geom)
            curves = self.curve_head(x)
            if self.num_sparams == 1:
                return curves
            return curves.view(curves.shape[0], self.num_sparams, self.num_freqs)

        def forward_with_aux(self, x: Tensor, geom: Tensor | None = None) -> tuple[Tensor, Tensor]:
            x = self._embed(x, geom)
            curves = self.curve_head(x)
            if self.num_sparams != 1:
                curves = curves.view(curves.shape[0], self.num_sparams, self.num_freqs)
            return curves, self.aux_head(x)


    def masked_weighted_mse(pred: Tensor, target: Tensor, valid_mask: Tensor, freq_weights: Tensor) -> Tensor:
        weights = freq_weights.to(device=pred.device, dtype=pred.dtype)
        while weights.ndim < pred.ndim:
            weights = weights.unsqueeze(0)
        mask = valid_mask.to(device=pred.device, dtype=pred.dtype)
        error = (pred - target.to(device=pred.device, dtype=pred.dtype)) ** 2
        weighted = error * mask * weights
        denom = torch.clamp((mask * weights).sum(), min=1.0)
        return weighted.sum() / denom


    def s21_aux_feature_tensor(curves: Tensor, valid_mask: Tensor, freq_ghz: Tensor) -> tuple[Tensor, Tensor]:
        """Return compact S21 features used to teach the ranker's guard logic."""

        freq = freq_ghz.to(device=curves.device, dtype=curves.dtype).view(1, -1)
        valid = valid_mask.to(device=curves.device, dtype=torch.bool)
        neg_large = torch.full_like(curves, -1.0e6)
        pos_large = torch.full_like(curves, 1.0e6)

        pass_mask = valid & (freq >= 6.0) & (freq <= 8.0)
        low_mask = valid & (freq >= 1.0) & (freq <= 5.5)
        high_mask = valid & (freq >= 8.5) & (freq <= 10.0)
        f5_mask = valid & torch.isclose(freq, torch.tensor(5.0, device=curves.device, dtype=curves.dtype))
        f6_mask = valid & torch.isclose(freq, torch.tensor(6.0, device=curves.device, dtype=curves.dtype))
        f8_mask = valid & torch.isclose(freq, torch.tensor(8.0, device=curves.device, dtype=curves.dtype))
        f9_mask = valid & torch.isclose(freq, torch.tensor(9.0, device=curves.device, dtype=curves.dtype))

        def masked_min(mask: Tensor) -> tuple[Tensor, Tensor]:
            has = mask.any(dim=1)
            values = torch.where(mask, curves, pos_large).min(dim=1).values
            return values, has

        def masked_max(mask: Tensor) -> tuple[Tensor, Tensor]:
            has = mask.any(dim=1)
            values = torch.where(mask, curves, neg_large).max(dim=1).values
            return values, has

        pass_min, has_pass = masked_min(pass_mask)
        pass_max, _ = masked_max(pass_mask)
        low_max, has_low = masked_max(low_mask)
        high_max, has_high = masked_max(high_mask)
        s21_5g, has_5g = masked_max(f5_mask)
        s21_6g, has_6g = masked_max(f6_mask)
        s21_8g, has_8g = masked_max(f8_mask)
        s21_9g, has_9g = masked_max(f9_mask)
        ripple = pass_max - pass_min

        features = torch.stack([pass_min, ripple, s21_5g, s21_6g, s21_8g, s21_9g, high_max], dim=1)
        feature_mask = torch.stack([has_pass, has_pass, has_5g, has_6g, has_8g, has_9g, has_high], dim=1)
        return features, feature_mask


    def masked_aux_mse(pred: Tensor, target: Tensor, valid_mask: Tensor) -> Tensor:
        mask = valid_mask.to(device=pred.device, dtype=pred.dtype)
        error = (pred - target.to(device=pred.device, dtype=pred.dtype)) ** 2
        weighted = error * mask
        denom = torch.clamp(mask.sum(), min=1.0)
        return weighted.sum() / denom

else:

    class PixelQrS21Surrogate:  # type: ignore[no-redef]
        def __init__(self, *args: object, **kwargs: object) -> None:
            require_torch()


    def masked_weighted_mse(*args: object, **kwargs: object) -> object:
        require_torch()


    def s21_aux_feature_tensor(*args: object, **kwargs: object) -> object:
        require_torch()


    def masked_aux_mse(*args: object, **kwargs: object) -> object:
        require_torch()
