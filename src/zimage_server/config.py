from dataclasses import dataclass


@dataclass(frozen=True)
class Profile:
    width: int
    height: int
    steps: int
    guidance_scale: float


DEFAULT_PROFILE = "safe_512"
PROFILES = {
    "safe_512": Profile(width=512, height=512, steps=9, guidance_scale=0.0),
    "high_768": Profile(width=768, height=768, steps=9, guidance_scale=0.0),
}
