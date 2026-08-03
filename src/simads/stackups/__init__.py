"""Independent stackup domain helpers.

This package is intentionally separate from ADS/HFSS workflow modules. It owns
the stackup configuration model and simulator-specific mappings; tool modules
consume these helpers when they need to materialize a stackup in a workspace.
"""

from simads.config.stackups import (
    StackupConfig,
    StackupGeometryConfig,
    StackupLayerConfig,
    StackupMaterialConfig,
    default_stackup_config_path,
    default_stackups_dir,
    load_stackup_config,
    stackup_from_mapping,
)

__all__ = [
    "StackupConfig",
    "StackupGeometryConfig",
    "StackupLayerConfig",
    "StackupMaterialConfig",
    "default_stackup_config_path",
    "default_stackups_dir",
    "load_stackup_config",
    "stackup_from_mapping",
]
