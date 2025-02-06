#!/usr/bin/python

import fitparse
import gpxpy
import gpxpy.gpx
import os
from pathlib import Path
import tempfile
import shutil

import paramiko
from scp import SCPClient


def list_fit_files(directory):
    # Konvertiere den Pfad zu einem absoluten Pfad
    dir_path = Path(directory).expanduser()

    # Überprüfe, ob der Ordner existiert
    if not dir_path.exists():
        print(f"Das Verzeichnis {dir_path} existiert nicht.")
        return []

    # Suche nach allen .fit-Dateien
    fit_files = [str(file) for file in dir_path.glob("**/*.fit")]

    # Ergebnisse anzeigen
    if fit_files:
        print(f"Gefundene .fit-Dateien in {dir_path}:")
        for file in fit_files:
            print(file)
    else:
        print(f"Keine .fit-Dateien im Verzeichnis {dir_path} gefunden.")

    return fit_files


def fit_to_gpx(fit_file, gpx_file):
    fitfile = fitparse.FitFile(fit_file)

    # GPX-Datei erstellen
    with open(gpx_file, "w") as f:
        f.write("<?xml version='1.0' encoding='UTF-8'?>\n")
        f.write(
            '<gpx version="1.0" creator="wahoo2darwisch" xmlns="http://www.topografix.com/GPX/1/0">\n')

        # Optional: Zeitstempel der Datei als Metadaten
        time_created = None
        for message in fitfile.get_messages('file_id'):
            time_created = message.get_value('time_created')
            if time_created:
                f.write(f"  <time>{time_created.isoformat()}Z</time>\n")
                break
        # Initialisiere die min/max-Grenzen
        min_lat, min_lon = 90.0, 180.0
        max_lat, max_lon = -90.0, -180.0

        f.write("  <trk>\n")
        f.write("    <trkseg>\n")

        # Daten aus der FIT-Datei extrahieren
        for record in fitfile.get_messages("record"):
            # try:
            data = {field.name: field.value for field in record}
            lat = data.get("position_lat")
            lon = data.get("position_long")
            elevation = data.get("altitude")
            timestamp = data.get("timestamp")
            speed = data.get("speed")  # Geschwindigkeit in m/s

            # Semicircles in Grad umwandeln
            if lat and lon:
                lat = lat * (180 / 2**31)
                lon = lon * (180 / 2**31)

                # Aktualisiere die min/max-Werte
                min_lat = min(min_lat, lat)
                min_lon = min(min_lon, lon)
                max_lat = max(max_lat, lat)
                max_lon = max(max_lon, lon)

                # Geschwindigkeit in km/h umrechnen (optional)

                # GPX-Trkpt erstellen
                f.write(
                    f'      <trkpt lat="{lat:.9f}" lon="{lon:.9f}">\n')
                if elevation:
                    f.write(
                        f"        <ele>{elevation:.3f}</ele>\n")
                f.write(f"        <time>{timestamp.isoformat()}Z</time>\n")

                if speed is not None:
                    f.write(f"        <speed>{speed:.6f}</speed>\n")

                f.write(f"      </trkpt>\n")
            # except Exception as e:
            #    print(f"Fehler beim Verarbeiten eines Datensatzes: {e}")

        f.write("    </trkseg>\n")
        f.write("  </trk>\n")

        # Min/Max-Bounds hinzufügen
        f.write(
            f'  <bounds minlat="{min_lat:.9f}" minlon="{min_lon:.9f}" '
            f'maxlat="{max_lat:.9f}" maxlon="{max_lon:.9f}"/>\n'
        )

        f.write("</gpx>\n")
    print(f"GPX-Datei erfolgreich erstellt: {gpx_file}")


def copy_file(local_file, dest_path):
    try:
        shutil.copy(local_file, dest_path)
        print(f"Datei '{local_file}' erfolgreich nach '{dest_path}' kopiert.")
    except Exception as e:
        print(f"Fehler beim Kopieren der Datei '{local_file}': {e}")


dropbox_dir = os.environ['DROPBOX_DIR']
dest_dir = os.environ['DEST_DIR']

# Aufruf der Funktion
fit_files = list_fit_files(dropbox_dir)

temp_dir = tempfile.mkdtemp()
for fit_file in fit_files:
    base_name = os.path.basename(fit_file)
    okay_file = fit_file+'.done'
    if not os.path.exists(okay_file):
        # Ersetze .fit durch .gpx
        new_file_name_base = (os.path.splitext(base_name)[
                              0] + ".gpx").replace(' ', '_')
        new_file_name = os.path.join(
            temp_dir, new_file_name_base)
        try:
            fit_to_gpx(fit_file, new_file_name)
            print(f"{fit_file} -> {new_file_name}")
            copy_file(new_file_name, os.path.join(
                dest_dir, new_file_name_base))
            with open(okay_file, 'w') as file:
                file.write('')

        except Exception as e:
            print(f"Fehler beim Lesen der FIT-Datei '{fit_file}': {e}")


shutil.rmtree(temp_dir)
