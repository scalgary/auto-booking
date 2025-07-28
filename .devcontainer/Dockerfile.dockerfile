FROM mcr.microsoft.com/devcontainers/python:1-3.12

# Installe les dépendances système utiles pour Selenium
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        libnss3 \
        libgconf-2-4 \
        libfontconfig1 \
        libxss1 \
        libasound2 \
        wget \
    && rm -rf /var/lib/apt/lists/*

# Copie les dépendances Python
COPY requirements.txt /tmp/pip-tmp/
RUN pip install --upgrade pip && pip install -r /tmp/pip-tmp/requirements.txt