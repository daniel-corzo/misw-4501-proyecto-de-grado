from setuptools import setup, find_packages

setup(
    name="travelhub-common",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.135.1",
        "sqlalchemy[asyncio]>=2.0.40",
        "asyncpg>=0.30.0",
        "pydantic-settings>=2.8.1",
        "boto3>=1.37.1",
        "starlette>=0.46.0",
        "python-jose[cryptography]>=3.3.0",
    ],
)
