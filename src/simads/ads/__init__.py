"""ADS automation planning helpers.

The package contains normal-Python helpers only. Modules that import Keysight
ADS APIs should remain in ADS-executed scripts or explicit adapter layers.
"""

from .dataset import (
    DatasetExportPlan,
    build_dataset_export_plan,
    build_export_command,
    dataset_path,
    db_from_mag,
    delimiter_text,
    phase_deg,
    write_ads_display_like_table,
    write_dataset_export,
    write_full_table,
)
from .emsetup import DEFAULT_SETUP_VIEW, EmSetupClonePlan, build_clone_command, build_emsetup_clone_plan
from .layout import (
    LayoutImportPlan,
    build_import_command,
    build_layout_import_plan,
    load_layout_json,
    load_p1_p2_locations,
    load_port_locations,
    parse_generated_dxf_subset,
)
from .rfpro import (
    RfproFemPlan,
    build_rfpro_command,
    build_rfpro_fem_plan,
    normalize_substrate_info,
    patch_rfpro_setup_xml,
    substrate_file_exists,
)
from .workspace import AdsCellRef, AdsCommandPlan, ads_encoded_cell_dir_name, find_cell_dir

__all__ = [
    "AdsCellRef",
    "AdsCommandPlan",
    "DatasetExportPlan",
    "DEFAULT_SETUP_VIEW",
    "EmSetupClonePlan",
    "LayoutImportPlan",
    "RfproFemPlan",
    "ads_encoded_cell_dir_name",
    "build_clone_command",
    "build_dataset_export_plan",
    "build_emsetup_clone_plan",
    "build_export_command",
    "build_import_command",
    "build_layout_import_plan",
    "build_rfpro_command",
    "build_rfpro_fem_plan",
    "dataset_path",
    "db_from_mag",
    "delimiter_text",
    "find_cell_dir",
    "load_layout_json",
    "load_p1_p2_locations",
    "load_port_locations",
    "parse_generated_dxf_subset",
    "phase_deg",
    "normalize_substrate_info",
    "patch_rfpro_setup_xml",
    "substrate_file_exists",
    "write_ads_display_like_table",
    "write_dataset_export",
    "write_full_table",
]
