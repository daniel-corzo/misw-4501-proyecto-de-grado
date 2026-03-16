from functools import lru_cache
from travelhub_common.config import BaseAppSettings, load_secrets


class Settings(BaseAppSettings):
    # Agrega aqui settings especificos de reservas
    service_name: str = "reservas"


@lru_cache
def get_settings() -> Settings:
    return load_secrets(Settings())
