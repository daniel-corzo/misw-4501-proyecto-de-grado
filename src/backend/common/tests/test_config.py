import json
from unittest.mock import patch, MagicMock
from travelhub_common.config import BaseAppSettings, get_secret, load_secrets


def test_base_app_settings_defaults():
    settings = BaseAppSettings()
    assert settings.environment == "local"
    assert settings.service_name == "travelhub-service"
    assert settings.jwt_algorithm == "RS256"
    assert settings.jwt_expiration_minutes == 1440
    assert settings.aws_region == "us-east-1"
    assert settings.jwt_public_key == ""
    assert settings.jwt_private_key == ""


def test_base_app_settings_custom_values():
    settings = BaseAppSettings(
        environment="production",
        service_name="auth-service",
        jwt_algorithm="HS256",
        jwt_public_key="my-key",
    )
    assert settings.environment == "production"
    assert settings.service_name == "auth-service"
    assert settings.jwt_algorithm == "HS256"
    assert settings.jwt_public_key == "my-key"


def test_get_secret_calls_boto3():
    secret_data = {"username": "admin", "password": "secret"}
    mock_client = MagicMock()
    mock_client.get_secret_value.return_value = {
        "SecretString": json.dumps(secret_data)
    }

    with patch("boto3.client", return_value=mock_client):
        result = get_secret("my-secret", "us-east-1")

    mock_client.get_secret_value.assert_called_once_with(SecretId="my-secret")
    assert result == secret_data


def test_load_secrets_returns_settings():
    settings = BaseAppSettings()
    result = load_secrets(settings)
    assert result is settings
