FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libldap2-dev \
    libsasl2-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY google_hash_service.py .

RUN useradd -r -u 1000 hashservice
USER hashservice

EXPOSE 8080

CMD ["python", "google_hash_service.py"]
