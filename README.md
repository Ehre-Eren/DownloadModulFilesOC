# Moodle Course Downloader

A lightweight Python script to batch download all course documents (PDFs, source code, worksheets) from Moodle (e.g., FOM Online-Campus) instead of clicking them one by one.

---

## Deutsch

### Anleitung

1. **Kursseite speichern:** Geh auf die Kursseite im Browser, drücke `Strg + S` (Windows) bzw. `Cmd + S` (Mac) und speichere sie als **"Webseite, nur HTML"** unter dem Namen `Modul.html`.
2. **Setup:** Pack die `Download.py` in denselben Ordner wie die `Modul.html`.
3. **Session-Cookie eintragen:(OPTIONAL)**
   * Drücke auf der Kursseite `F12` und wechsle auf den Reiter **Netzwerk** (Network).
   * Seite neu laden (`F5`).
   * Klicke auf den ersten Eintrag (`view.php...`) und suche unter *Request Headers* nach `Cookie:`.
   * Kopiere den gesamten String (z. B. `MoodleSession=xxxx...`), entferne im Skript die Raute `#` vor `"Cookie"` und füge den Wert dort ein.
4. **Starten:** Skript ausführen, der Rest läuft von selbst.

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
3. **Add Session Cookie:(OPTIONAL)**
   * Open DevTools (`F12`) on the Moodle page and go to the **Network** tab.
   * Reload the page (`F5`).
   * Click the first request (`view.php...`) and look for `Cookie:` under *Request Headers*.
   * Copy the entire string (e.g., `MoodleSession=xxxx...`), uncomment the `"Cookie"` line in the script, and paste your value.
4. **Run:** Execute the script to start the download.

### Requirements

```bash
pip install beautifulsoup4 requests
```

### Features

* Auto-detects file types (.pdf, .txt, .docx, .xlsx, .py) based on Moodle's assets.
* Strips messy system suffixes from file names.
* Purely local parser – no heavy automation tools like Selenium required.