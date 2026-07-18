# Moodle Course Downloader

A lightweight Python script to batch download all course documents (PDFs, source code, worksheets) from Moodle (e.g., FOM Online-Campus) instead of clicking them one by one.

---

## Deutsch

### Anleitung

1. **Kursseite speichern:** Geh auf die Kursseite im Browser, drücke `Strg + S` (Windows) bzw. `Cmd + S` (Mac) und speichere sie als **"Webseite, nur HTML"** unter dem Namen `Modul.html`.
2. **Setup:** Pack die `Download.py` in denselben Ordner wie die `Modul.html`.
3. **Starten:** Skript ausführen, der Rest läuft von selbst.

### Abhängigkeiten

```bash
pip install beautifulsoup4 requests
```

### Features

* Erkennt Dateiendungen (.pdf, .txt, .docx, .xlsx, .py) automatisch anhand der Icons.
* Bereinigt Dateinamen von störenden Plattform-Zusätzen.
* Läuft rein lokal – kein Selenium oder WebDriver-Setup nötig.

---

## English

### How to use

1. **Save Course Page:** Open the course page in your browser, press `Ctrl + S` (Windows) or `Cmd + S` (Mac), and save it as **"Webpage, HTML only"** named `Modul.html`.
2. **Setup:** Place `Download.py` in the same directory as `Modul.html`.
3. **Run:** Execute the script to start the download.

### Requirements

```bash
pip install beautifulsoup4 requests
```

### Features

* Auto-detects file types (.pdf, .txt, .docx, .xlsx, .py) based on Moodle's assets.
* Strips messy system suffixes from file names.
* Purely local parser – no heavy automation tools like Selenium required.