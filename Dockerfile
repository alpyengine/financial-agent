FROM python:3.11-slim

WORKDIR /app

# Dependencias primero (mejor cache de capas)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código
COPY . .

# El agente corre en bucle con su propio scheduler interno.
CMD ["python", "-m", "src.runner"]
