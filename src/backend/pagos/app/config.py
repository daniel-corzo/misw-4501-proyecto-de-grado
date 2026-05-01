from functools import lru_cache

from travelhub_common.config import BaseAppSettings, load_secrets


class Settings(BaseAppSettings):
    """Configuracion del servicio pagos."""

    service_name: str = "pagos"
    # PEM RSA privada (formato tradicional OpenSSL, BEGIN RSA PRIVATE KEY); mismo formato que utils/generate_keys.py
    pago_rsa_private_key_pem: str = ""


@lru_cache
def get_settings() -> Settings:
    return load_secrets(Settings())
