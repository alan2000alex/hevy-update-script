import os
from dataclasses import dataclass

BASE_URL = "https://api.hevyapp.com"
PAGE_SIZE = 10


@dataclass
class Config:
    api_key: str
    base_url: str = BASE_URL
    page_size: int = PAGE_SIZE


def load_config(api_key: str | None = None) -> Config:
    key = api_key or os.environ.get("HEVY_API_KEY", "")
    if not key:
        raise ValueError(
            "HEVY_API_KEY is required. Set via HEVY_API_KEY env var or --api-key flag."
        )
    return Config(api_key=key)
