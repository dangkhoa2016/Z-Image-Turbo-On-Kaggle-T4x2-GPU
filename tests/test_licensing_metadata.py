from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_model_license_and_third_party_notices_are_present():
    notice = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    model_license = (ROOT / "docs" / "model-license.md").read_text(encoding="utf-8")
    model_license_vi = (ROOT / "docs" / "model-license.vi.md").read_text(encoding="utf-8")
    apache = (ROOT / "licenses" / "Apache-2.0.txt").read_text(encoding="utf-8")

    revision = "f332072aa78be7aecdf3ee76d5c247082da564a6"
    upstream = "Tongyi-MAI/Z-Image-Turbo"

    assert upstream in notice
    assert revision in notice
    assert "Apache License 2.0" in notice
    assert upstream in model_license and revision in model_license
    assert upstream in model_license_vi and revision in model_license_vi
    assert "Apache License" in apache and "Version 2.0" in apache
