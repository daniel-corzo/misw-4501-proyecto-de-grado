from functools import lru_cache
from travelhub_common.config import BaseAppSettings, load_secrets


class Settings(BaseAppSettings):
    # Agrega aqui settings especificos de reservas
    service_name: str = "reservas"
    backend_api_url: str = "http://gateway:8080/api"


@lru_cache
def get_settings() -> Settings:
    return load_secrets(Settings())
