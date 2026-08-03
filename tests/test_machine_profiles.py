from pathlib import Path

from simads.config import detect_machine_profile, get_ads_profile, mac_hash, resolve_backend_profile


def test_detect_machine_profile_from_mac_hash(tmp_path: Path, monkeypatch) -> None:
    config = tmp_path / "machine_profiles.json"
    digest = mac_hash("AA-BB-CC-11-22-33")
    config.write_text(
        """
{
  "schema_version": "0.1.0",
  "profiles": {
    "company": {
      "mac_sha256_16": ["%s"],
      "ads_profile": "company_standard",
      "hfss_profile": "company"
    }
  }
}
"""
        % digest,
        encoding="utf-8",
    )
    monkeypatch.setattr("simads.config.machine.local_mac_hashes", lambda: (digest,))

    detection = detect_machine_profile(config)

    assert detection.selected == "company"
    assert detection.source == "mac_sha256_16"


def test_auto_ads_profile_uses_machine_mapping(monkeypatch) -> None:
    monkeypatch.setenv("SIMADS_MACHINE_PROFILE", "company")

    assert resolve_backend_profile("ads", "auto") == "company_standard"
    assert get_ads_profile("auto").name == "company_standard"
