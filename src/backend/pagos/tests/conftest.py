import os

# Forzar entorno test antes de que cualquier test importe app (evita startup con DB real si el
# shell tiene ENVIRONMENT=local). setdefault no sobreescribe eso.
os.environ["ENVIRONMENT"] = "test"
