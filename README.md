# FOM Online-Campus & Moodle Downloader

A smart, interactive Python script to batch download all course documents (PDFs, source code, worksheets) directly from the FOM Online-Campus instead of clicking them one by one.

---

## Deutsch

### Anleitung

1. **Setup:** Platziere die `Download.py` in deinem gewünschten Studienordner.
2. **Starten:** Führe das Skript über das Terminal aus:
   ```bash
   python Download.py
   ```


3. **Login & Session:** Beim ersten Start (oder wenn deine Session abgelaufen ist) öffnet sich automatisch ein Browserfenster. Logge dich ganz normal mit deinen FOM-Zugangsdaten ein. Sobald das Dashboard geladen ist, speichert das Skript die Sitzung in einer `auth.json` ab und schließt das Fenster. Bei zukünftigen Starts läuft das Skript komplett unsichtbar im Hintergrund.
4. **Kurs auswählen:** Das Skript listet dir alle verfügbaren Module sauber sortiert nach Semestern im Terminal auf. Tippe einfach die Nummer des gewünschten Kurses ein und drücke Enter, um den Download zu starten.
5. **Beenden:** Tippe `q` ein, um das Programm zu schließen.

### Abhängigkeiten

Werden vom Skript automatisch beim ersten Start geprüft und installiert. Manuell:

```bash
pip install playwright beautifulsoup4
```


### Features

* **Semester-Sortierung:** Listet alle Kurse gruppiert nach den jeweiligen Semestern (z. B. 2026-SS, 2025-WS) direkt vom Online-Campus Dashboard auf.
* **Smart Session Management:** Erfordert den Login nur einmalig über ein automatisches Browserfenster. Die Session wird lokal zwischengespeichert.
* **Dateityp-Erkennung:** Erkennt Dateiendungen (.pdf, .txt, .docx, .xlsx, .py) automatisch anhand der Moodle-Struktur.
* **Moodle-Inline-Bypass:** Fängt Dateien, die von Moodle standardmäßig nur als Text im Browser angezeigt werden (z. B. Python-Code), ab und speichert sie als korrekte lokale Dateien.

---

## English

### How to use

1. **Setup:** Place `Download.py` in your preferred study directory.
2. **Run:** Execute the script via your terminal:

```bash
python Download.py
```

3. **Login & Session:** On the first run (or if your session expires), a browser window will automatically open. Log in using your FOM credentials. Once the dashboard loads, the script saves your session into an `auth.json` file and closes the browser. On subsequent runs, the script operates completely invisibly in headless mode.
4. **Select Course:** The script lists all available modules in the terminal, cleanly sorted by semester. Simply type the number of the course you want and press Enter to start downloading all files.
5. **Quit:** Type `q` to exit the program.

### Requirements

Automatically handled by the script on the first run. Manual install:

```bash
pip install playwright beautifulsoup4
```

### Features

* **Semester Grouping:** Displays all modules grouped by their respective semesters (e.g., 2026-SS, 2025-WS) extracted straight from the Online-Campus dashboard.
* **Smart Session Management:** Requires authentication only once via an automated browser pop-up. The session context is securely cached locally.
* **File Type Auto-Detection:** Automatically maps correct extensions (.pdf, .txt, .docx, .xlsx, .py) based on Moodle's resource layout.
* **Moodle Inline Bypass:** Intercepts files that Moodle usually displays as raw text in the browser (e.g., Python code templates) and saves them as proper local files.

