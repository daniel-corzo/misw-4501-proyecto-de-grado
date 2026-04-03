from functools import lru_cache
from travelhub_common.config import BaseAppSettings, load_secrets


class Settings(BaseAppSettings):
    # Agrega aqui settings especificos de hoteles
    service_name: str = "hoteles"
    backend_api_url: str = "http://gateway:8080/api"  # URL del API Gateway, que redirige a los servicios correspondientes


@lru_cache
def get_settings() -> Settings:
    return load_secrets(Settings())
