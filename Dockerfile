FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm as devcontainer

WORKDIR /workspace

COPY requirements.txt .
COPY requirements-dev.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-dev.txt

FROM python:3.12.4-slim-bookworm as production

WORKDIR /app

COPY requirements.txt .
COPY app.py .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["streamlit", "run", "app.py"]
