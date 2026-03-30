FROM public.ecr.aws/docker/library/python:3.12-slim

WORKDIR /app

COPY common /common
RUN pip install --no-cache-dir -e /common

COPY busquedas/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY busquedas/app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
