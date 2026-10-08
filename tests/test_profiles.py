from zimage_server.config import PROFILES, DEFAULT_PROFILE


def test_profiles_are_explicit_and_bounded():
    assert DEFAULT_PROFILE == "safe_512"
    assert set(PROFILES) == {"safe_512", "high_768"}
    safe = PROFILES["safe_512"]
    high = PROFILES["high_768"]
    assert (safe.width, safe.height, safe.steps, safe.guidance_scale) == (512, 512, 9, 0.0)
    assert (high.width, high.height, high.steps, high.guidance_scale) == (768, 768, 9, 0.0)
    assert "high_1024" not in PROFILES
