# Verwende ein offizielles Python-Image als Basis
FROM python:3.13-slim

# Setze das Arbeitsverzeichnis im Container
WORKDIR /app

# Kopiere die requirements.txt in das Arbeitsverzeichnis
COPY requirements.txt .

# Installiere die Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den Rest des Anwendungscodes in das Arbeitsverzeichnis
COPY wahoo2dawarich.py .

# Setze die Umgebungsvariablen
ENV DROPBOX_DIR=/dropboxdir
ENV DEST_DIR=/dawarichdir

# Führe das Python-Skript aus
CMD ["python", "wahoo2dawarich.py"]
