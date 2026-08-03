"""Surrogates for parameterized interdigital BPF S-parameter curves."""

from __future__ import annotations

from typing import Any

try:  # pragma: no cover - exercised when the optional nn dependency exists.
    import torch
    from torch import Tensor, nn
except ImportError:  # pragma: no cover - keeps non-NN project tools importable.
    torch = None
    Tensor = Any  # type: ignore[assignment]
    nn = None  # type: ignore[assignment]


def require_torch() -> Any:
    if torch is None:
        raise RuntimeError("PyTorch is required for simads.nn interdigital surrogate tools.")
    return torch


if nn is not None:

    class ResidualMlpBlock(nn.Module):
        """Small residual fully connected block for smooth geometry responses."""

        def __init__(self, hidden: int, dropout: float = 0.03) -> None:
            super().__init__()
            self.net = nn.Sequential(
                nn.LayerNorm(hidden),
                nn.Linear(hidden, hidden * 2),
                nn.SiLU(),
                nn.Dropout(dropout),
                nn.Linear(hidden * 2, hidden),
            )

        def forward(self, x: Tensor) -> Tensor:
            return x + self.net(x)


    class InterdigitalSParamSurrogate(nn.Module):
        """Map normalized interdigital geometry vectors to S-parameter curves.

        The original version accepted one flat geometry vector.  The refined
        version also accepts four physically grouped inputs: resonator/base
        geometry, coupling gaps, feed/external coupling, and derived physics
        proxy features.
        """

        def __init__(
            self,
            *,
            input_features: int,
            num_freqs: int,
            num_sparams: int = 3,
            hidden: int = 128,
            blocks: int = 4,
            aux_features: int = 7,
            resonator_features: int | None = None,
            gap_features: int | None = None,
            feed_features: int | None = None,
            derived_features: int | None = None,
        ) -> None:
            super().__init__()
            self.input_features = input_features
            self.num_freqs = num_freqs
            self.num_sparams = num_sparams
            self.aux_features = aux_features
            self.resonator_features = resonator_features
            self.gap_features = gap_features
            self.feed_features = feed_features
            self.derived_features = derived_features
            self.refined = all(
                value is not None
                for value in (resonator_features, gap_features, feed_features, derived_features)
            )
            if self.refined:
                branch_hidden = max(16, hidden // 4)
                self.resonator_encoder = self._branch(int(resonator_features), branch_hidden)
                self.gap_encoder = self._branch(int(gap_features), branch_hidden)
                self.feed_encoder = self._branch(int(feed_features), branch_hidden)
                self.derived_encoder = self._branch(int(derived_features), branch_hidden)
                trunk_in = branch_hidden * 4
            else:
                self.encoder = nn.Sequential(
                    nn.Linear(input_features, hidden),
                    nn.SiLU(),
                    *[ResidualMlpBlock(hidden) for _ in range(blocks)],
                    nn.LayerNorm(hidden),
                    nn.SiLU(),
                )
                trunk_in = hidden
            trunk_layers: list[nn.Module] = [nn.Linear(trunk_in, hidden), nn.SiLU()]
            if self.refined:
                trunk_layers.extend(ResidualMlpBlock(hidden) for _ in range(blocks))
                trunk_layers.extend([nn.LayerNorm(hidden), nn.SiLU()])
            self.trunk = nn.Sequential(*trunk_layers)
            self.curve_head = nn.Linear(hidden, num_sparams * num_freqs)
            self.aux_head = nn.Linear(hidden, aux_features)

        @staticmethod
        def _branch(features: int, hidden: int) -> nn.Sequential:
            return nn.Sequential(
                nn.Linear(features, hidden),
                nn.SiLU(),
                nn.LayerNorm(hidden),
                nn.Linear(hidden, hidden),
                nn.SiLU(),
            )

        def embed(
            self,
            x: Tensor | None = None,
            *,
            x_resonator: Tensor | None = None,
            x_gap: Tensor | None = None,
            x_feed: Tensor | None = None,
            x_derived: Tensor | None = None,
        ) -> Tensor:
            if self.refined:
                missing = [
                    name
                    for name, value in {
                        "x_resonator": x_resonator,
                        "x_gap": x_gap,
                        "x_feed": x_feed,
                        "x_derived": x_derived,
                    }.items()
                    if value is None
                ]
                if missing:
                    raise ValueError(f"refined surrogate missing inputs: {', '.join(missing)}")
                z = torch.cat(
                    [
                        self.resonator_encoder(x_resonator),
                        self.gap_encoder(x_gap),
                        self.feed_encoder(x_feed),
                        self.derived_encoder(x_derived),
                    ],
                    dim=1,
                )
                return self.trunk(z)
            if x is None:
                raise ValueError("flat surrogate requires x")
            if x.ndim != 2 or x.shape[1] != self.input_features:
                raise ValueError(f"expected input shape [B,{self.input_features}], got {tuple(x.shape)}")
            return self.trunk(self.encoder(x))

        def forward(
            self,
            x: Tensor | None = None,
            *,
            x_resonator: Tensor | None = None,
            x_gap: Tensor | None = None,
            x_feed: Tensor | None = None,
            x_derived: Tensor | None = None,
        ) -> Tensor:
            z = self.embed(
                x,
                x_resonator=x_resonator,
                x_gap=x_gap,
                x_feed=x_feed,
                x_derived=x_derived,
            )
            curves = self.curve_head(z)
            return curves.view(curves.shape[0], self.num_sparams, self.num_freqs)

        def forward_with_aux(
            self,
            x: Tensor | None = None,
            *,
            x_resonator: Tensor | None = None,
            x_gap: Tensor | None = None,
            x_feed: Tensor | None = None,
            x_derived: Tensor | None = None,
        ) -> tuple[Tensor, Tensor]:
            z = self.embed(
                x,
                x_resonator=x_resonator,
                x_gap=x_gap,
                x_feed=x_feed,
                x_derived=x_derived,
            )
            curves = self.curve_head(z).view(z.shape[0], self.num_sparams, self.num_freqs)
            return curves, self.aux_head(z)


    class FlatInterdigitalSParamSurrogate(nn.Module):
        """Backward-compatible flat-vector surrogate."""

        def __init__(
            self,
            *,
            input_features: int,
            num_freqs: int,
            num_sparams: int = 3,
            hidden: int = 128,
            blocks: int = 4,
            aux_features: int = 7,
        ) -> None:
            super().__init__()
            self.input_features = input_features
            self.num_freqs = num_freqs
            self.num_sparams = num_sparams
            self.aux_features = aux_features
            self.encoder = nn.Sequential(
                nn.Linear(input_features, hidden),
                nn.SiLU(),
                *[ResidualMlpBlock(hidden) for _ in range(blocks)],
                nn.LayerNorm(hidden),
                nn.SiLU(),
            )
            self.curve_head = nn.Linear(hidden, num_sparams * num_freqs)
            self.aux_head = nn.Linear(hidden, aux_features)

        def embed(self, x: Tensor) -> Tensor:
            if x.ndim != 2 or x.shape[1] != self.input_features:
                raise ValueError(f"expected input shape [B,{self.input_features}], got {tuple(x.shape)}")
            return self.encoder(x)

        def forward(self, x: Tensor) -> Tensor:
            z = self.embed(x)
            curves = self.curve_head(z)
            return curves.view(curves.shape[0], self.num_sparams, self.num_freqs)

        def forward_with_aux(self, x: Tensor) -> tuple[Tensor, Tensor]:
            z = self.embed(x)
            curves = self.curve_head(z).view(z.shape[0], self.num_sparams, self.num_freqs)
            return curves, self.aux_head(z)

else:

    class InterdigitalSParamSurrogate:  # type: ignore[no-redef]
        def __init__(self, *args: object, **kwargs: object) -> None:
            require_torch()
