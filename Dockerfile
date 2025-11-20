# Dockerfile
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY app.py /app/

# ansible-core bevat de 'ansible-vault' CLI
RUN pip install --no-cache-dir --root-user-action=ignore ansible-core

CMD ["python", "app.py"]
