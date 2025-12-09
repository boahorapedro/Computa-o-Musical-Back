# src/api/v1/mix/schemas.py
from pydantic import BaseModel
from typing import Optional


class StemConfig(BaseModel):
    style_sound_id: Optional[str] = None
    volume: float = 1.0
    enabled: bool = True


class VocalsConfig(BaseModel):
    volume: float = 1.0
    enabled: bool = True


class MixConfig(BaseModel):
    drums: StemConfig = StemConfig()
    bass: StemConfig = StemConfig()
    other: StemConfig = StemConfig()
    vocals: VocalsConfig = VocalsConfig()


class MixSettings(BaseModel):
    grain_duration_ms: int = 120
    use_pitch_mapping: bool = True
    use_envelope: bool = True


class CreateMixRequest(BaseModel):
    project_id: str
    config: MixConfig
    settings: MixSettings = MixSettings()


class CreateMixResponse(BaseModel):
    mix_id: str
    status: str
    message: str


class MixStatusResponse(BaseModel):
    mix_id: str
    status: str
    config: dict
    created_at: str
    download_url: Optional[str] = None
