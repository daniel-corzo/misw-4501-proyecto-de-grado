from functools import lru_cache
from travelhub_common.config import BaseAppSettings, load_secrets


class Settings(BaseAppSettings):
    # Agrega aqui settings especificos de busqueda
    service_name: str = "busqueda"


@lru_cache
def get_settings() -> Settings:
    return load_secrets(Settings())
