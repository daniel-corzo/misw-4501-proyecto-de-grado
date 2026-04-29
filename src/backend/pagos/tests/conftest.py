import os

# Evitar inicializaciones de entorno non-test al importar app
os.environ.setdefault("ENVIRONMENT", "test")
