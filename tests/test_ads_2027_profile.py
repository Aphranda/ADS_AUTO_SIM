from pathlib import Path

from simads.config import build_ads_env, get_ads_profile, validate_profile


def test_home_ads_2027_profile_exposes_mcp_executable() -> None:
    profile = get_ads_profile("home_2027")

    assert profile.ads_root == Path("D:/Hardware/Keysight/ADS2027")
    assert profile.ads_python == Path("D:/Hardware/Keysight/ADS2027/tools/python/python.exe")
    assert profile.mcp_executable == Path("D:/Hardware/Keysight/ADS2027/bin/ads-mcp.exe")
    assert profile.to_dict()["mcp_executable"] == str(profile.mcp_executable)

    checks = validate_profile(profile, require_mcp=True)
    mcp_checks = [check for check in checks if check.name == "mcp_executable"]

    assert len(mcp_checks) == 1
    assert mcp_checks[0].ok


def test_build_ads_env_uses_profile_root(monkeypatch) -> None:
    monkeypatch.setenv("HPEESOF_DIR", "D:/Temp/WrongADS")

    env = build_ads_env("home_2027")

    assert Path(env["HPEESOF_DIR"]) == Path("D:/Hardware/Keysight/ADS2027")
