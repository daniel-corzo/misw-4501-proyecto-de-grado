import boto3
import json
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseAppSettings(BaseSettings):
    environment: str = "local"
    service_name: str = "travelhub-service"
    db_url: str = "postgresql+asyncpg://travelhub:travelhub@localhost/travelhub"
    jwt_secret: str = "local-secret-only"
    jwt_public_key: str = ""
    jwt_private_key: str = ""
    jwt_algorithm: str = "RS256"
    jwt_expiration_minutes: int = 1440 # 24 hours
    aws_region: str = "us-east-1"
    redis_url: str = "redis://localhost:6379"
    sqs_endpoint: str = "http://localhost:4566"

    model_config = SettingsConfigDict(env_file=".env")


def get_secret(secret_name: str, region: str) -> dict:
    client = boto3.client("secretsmanager", region_name=region)
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])


def load_secrets(settings: BaseAppSettings) -> BaseAppSettings:
    return settings
