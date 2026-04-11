FROM public.ecr.aws/docker/library/python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 1. Instalar common (cambia poco → capa cacheada)
COPY common /common
RUN pip install --no-cache-dir /common

# 2. Instalar deps del servicio (solo runtime, sin test deps)
COPY usuarios/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copiar el código del servicio (cambia frecuentemente)
COPY usuarios/app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
