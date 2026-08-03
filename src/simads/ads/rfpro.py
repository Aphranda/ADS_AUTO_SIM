"""RFPro FEM planning helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET

from simads.ads.workspace import AdsCellRef, AdsCommandPlan
from simads.config import AdsProfile


@dataclass(frozen=True)
class RfproFemPlan:
    profile_id: str
    layout: AdsCellRef
    emsetup_view: str = "emSetup"
    rfpro_view: str = "rfpro"
    analysis_name: str = "analysis1"
    start_freq: str = "4 GHz"
    stop_freq: str = "10 GHz"
    points: int = 121
    plan_type: str = "Adaptive"
    max_passes: int = 8
    output_csv: Path | None = None

    def to_manifest(self) -> dict[str, object]:
        return {
            "profile_id": self.profile_id,
            "workspace": str(self.layout.workspace),
            "library": self.layout.library,
            "cell": self.layout.cell,
            "layout_view": self.layout.view,
            "emsetup_view": self.emsetup_view,
            "rfpro_view": self.rfpro_view,
            "analysis_name": self.analysis_name,
            "start_freq": self.start_freq,
            "stop_freq": self.stop_freq,
            "points": self.points,
            "plan_type": self.plan_type,
            "max_passes": self.max_passes,
            "output_csv": str(self.output_csv) if self.output_csv else None,
        }


def build_rfpro_fem_plan(
    profile: AdsProfile,
    *,
    cell: str,
    output_csv: Path | None = None,
    emsetup_view: str | None = None,
    rfpro_view: str = "rfpro",
    analysis_name: str = "analysis1",
    start_freq: str = "4 GHz",
    stop_freq: str = "10 GHz",
    points: int = 121,
    plan_type: str = "Adaptive",
    max_passes: int = 8,
) -> RfproFemPlan:
    return RfproFemPlan(
        profile_id=profile.name,
        layout=AdsCellRef(profile.workspace, profile.library, cell, "layout"),
        emsetup_view=emsetup_view or profile.rfpro_emsetup_view,
        rfpro_view=rfpro_view,
        analysis_name=analysis_name,
        start_freq=start_freq,
        stop_freq=stop_freq,
        points=points,
        plan_type=plan_type,
        max_passes=max_passes,
        output_csv=output_csv,
    )


def substrate_file_exists(workspace_path: Path | str, substrate_lib: str, substrate_name: str) -> bool:
    workspace = Path(workspace_path)
    subst = Path(substrate_name)
    candidates = [
        workspace / substrate_lib / substrate_name,
        workspace / substrate_lib / f"{subst.stem}.subst",
    ]
    return any(path.exists() for path in candidates)


def normalize_substrate_info(
    workspace_path: Path | str,
    library_name: str,
    cell_name: str,
    substrate_ls: tuple[str, str],
    preferred_substrate_lib: str | None = None,
) -> tuple[str, str]:
    substrate_lib, substrate_name = substrate_ls
    substrate_names = [substrate_name]
    if ":" in substrate_name:
        substrate_names.append(substrate_name.split(":")[-1])
    stem_name = Path(substrate_names[-1]).stem
    if stem_name and stem_name not in substrate_names:
        substrate_names.append(stem_name)
    if stem_name:
        with_ext = f"{stem_name}.subst"
        if with_ext not in substrate_names:
            substrate_names.append(with_ext)

    search_libraries = [substrate_lib, preferred_substrate_lib, "Substrates", library_name]
    seen: set[str] = set()
    for candidate_lib in search_libraries:
        if not candidate_lib or candidate_lib in seen:
            continue
        seen.add(candidate_lib)
        for candidate_name in substrate_names:
            if substrate_file_exists(workspace_path, candidate_lib, candidate_name):
                return (candidate_lib, candidate_name)

    workspace = Path(workspace_path)
    for candidate_name in substrate_names:
        fallback = workspace / library_name / candidate_name
        fallback_with_ext = workspace / library_name / f"{Path(candidate_name).stem}.subst"
        if fallback.exists() or fallback_with_ext.exists():
            return (library_name, candidate_name)

    subst_files = sorted((workspace / library_name).glob("*.subst"))
    if subst_files:
        return (library_name, subst_files[0].name)

    raise RuntimeError(
        f"ADS substrate not found for {library_name}:{cell_name}; "
        f"reported {substrate_lib}:{substrate_name}"
    )


def patch_rfpro_setup_xml(setup_xml: Path, substrate_ls: tuple[str, str]) -> bool:
    if not setup_xml.exists():
        return False

    substrate_lib, substrate_name = substrate_ls
    tree = ET.parse(setup_xml)
    root = tree.getroot()
    changed = False
    for elem in root.findall(".//substrate/lib"):
        if elem.text != substrate_lib:
            elem.text = substrate_lib
            changed = True
    for elem in root.findall(".//substrate/name"):
        if elem.text != substrate_name:
            elem.text = substrate_name
            changed = True
    if changed:
        tree.write(setup_xml, encoding="utf-8", xml_declaration=False)
    return changed


def build_rfpro_command(
    plan: RfproFemPlan,
    *,
    ads_python: Path,
    script: Path,
) -> AdsCommandPlan:
    args = [
        "--workspace",
        str(plan.layout.workspace),
        "--library",
        plan.layout.library,
        "--cell",
        plan.layout.cell,
        "--emsetup-view",
        plan.emsetup_view,
        "--rfpro-view",
        plan.rfpro_view,
        "--analysis-name",
        plan.analysis_name,
        "--start",
        plan.start_freq,
        "--stop",
        plan.stop_freq,
        "--points",
        str(plan.points),
        "--plan-type",
        plan.plan_type,
        "--max-passes",
        str(plan.max_passes),
    ]
    if plan.output_csv:
        args.extend(["--out", str(plan.output_csv)])
    return AdsCommandPlan("ads_run_rfpro_fem", ads_python, script, tuple(args), cwd=script.parents[1])
