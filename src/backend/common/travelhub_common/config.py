import boto3
import json
from pydantic_settings import BaseSettings


class BaseAppSettings(BaseSettings):
    environment: str = "local"
    service_name: str = "travelhub-service"
    db_url: str = "postgresql+asyncpg://travelhub:travelhub@localhost/travelhub"
    jwt_secret: str = "local-secret-only"
    aws_region: str = "us-east-1"
    redis_url: str = "redis://localhost:6379"
    sqs_endpoint: str = "http://localhost:4566"

    class Config:
        env_file = ".env"


def get_secret(secret_name: str, region: str) -> dict:
    client = boto3.client("secretsmanager", region_name=region)
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])


def load_secrets(settings: BaseAppSettings) -> BaseAppSettings:
    if settings.environment not in ("local", "test"):
        secrets = get_secret(
            f"travelhub/{settings.environment}/{settings.service_name}",
            settings.aws_region,
        )
        settings.db_url = secrets.get("db_url", settings.db_url)
        settings.jwt_secret = secrets.get("jwt_secret", settings.jwt_secret)
    return settings
