import os
import re
from bs4 import BeautifulSoup
import requests

# Pfade festlegen
HTML_FILE = "Modul.html"
DOWNLOAD_DIR = "downloads"

def download_campus_files():
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    try:
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"Fehler: {HTML_FILE} fehlt.")
        return

    soup = BeautifulSoup(html_content, "html.parser")
    
    # Alle Moodle-Materialien holen
    resource_items = soup.find_all("li", class_=lambda c: c and "modtype_resource" in c)
    
    download_count = 0
    print(f"Gefundene Ressourcen: {len(resource_items)}")
    
    for item in resource_items:
        link_tag = item.find("a", href=True)
        if not link_tag:
            continue
            
        href = link_tag["href"]
        
        # Dateiname aus Instancename parsen und Moodle-Suffix fixen
        instance_span = link_tag.find("span", class_="instancename")
        if instance_span:
            link_text = instance_span.get_text(strip=True)
            link_text = link_text.replace(" Datei", "").strip()
        else:
            link_text = link_tag.get_text(strip=True)

        # Endung anhand des Moodle-Icons bestimmen
        img_tag = item.find("img", class_="activityicon")
        extension = ".pdf"
        if img_tag and "src" in img_tag.attrs:
            img_src = img_tag["src"].lower()
            if "pdf" in img_src:
                extension = ".pdf"
            elif "text" in img_src or "txt" in img_src:
                extension = ".txt"
            elif "document" in img_src or "word" in img_src:
                extension = ".docx"
            elif "spreadsheet" in img_src or "excel" in img_src:
                extension = ".xlsx"
            elif "python" in img_src or "code" in img_src:
                extension = ".py"

        # Zeichen säubern und Formatendung anhängen
        clean_filename = re.sub(r'[\\/*?:"<>|]', "", link_text)
        if not clean_filename.lower().endswith(('.pdf', '.txt', '.docx', '.xlsx', '.py')):
            clean_filename += extension

        file_path = os.path.join(DOWNLOAD_DIR, clean_filename)
        print(f"Lade: {clean_filename} ...")
        
        try:
            # Session-Cookie eintragen, wenn Moodle blockt
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                # "Cookie": "MoodleSession=DEIN_COOKIE_HIER" 
            }
            
            response = requests.get(href, headers=headers, stream=True)
            
            if response.status_code == 200:
                with open(file_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                download_count += 1
            else:
                print(f" -> HTTP-Fehler {response.status_code} (Cookie abgelaufen?)")
                
        except Exception as e:
            print(f" -> Fehler bei {clean_filename}: {e}")

    print(f"\nFertig. {download_count} Dateien geladen.")

if __name__ == "__main__":
    download_campus_files()