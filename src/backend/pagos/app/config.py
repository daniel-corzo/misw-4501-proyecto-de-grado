from functools import lru_cache

from travelhub_common.config import BaseAppSettings, load_secrets


class Settings(BaseAppSettings):
    """Configuracion del servicio pagos."""

    service_name: str = "pagos"
    backend_api_url: str = "http://gateway:8080/api"


@lru_cache
def get_settings() -> Settings:
    return load_secrets(Settings())
