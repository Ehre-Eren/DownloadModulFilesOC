import os
import re
import sys
import subprocess

# Auto-install dependencies if missing
try:
    from bs4 import BeautifulSoup
    import requests
except ImportError:
    print("Dependencies missing. Installing 'requests' and 'beautifulsoup4'...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4", "requests"])
    # Re-import after installation
    from bs4 import BeautifulSoup
    import requests

# Paths config
HTML_FILE = "Modul.html"
DOWNLOAD_DIR = "downloads"

def download_campus_files():
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    try:
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"Error: {HTML_FILE} not found.")
        return

    soup = BeautifulSoup(html_content, "html.parser")
    
    # Fetch all Moodle course assets
    resource_items = soup.find_all("li", class_=lambda c: c and "modtype_resource" in c)
    
    download_count = 0
    print(f"Resources found: {len(resource_items)}")
    
    for item in resource_items:
        link_tag = item.find("a", href=True)
        if not link_tag:
            continue
            
        href = link_tag["href"]
        
        # Parse filename from instancename and strip Moodle suffix
        instance_span = link_tag.find("span", class_="instancename")
        if instance_span:
            link_text = instance_span.get_text(strip=True)
            link_text = link_text.replace(" Datei", "").strip()
        else:
            link_text = link_tag.get_text(strip=True)

        # Detect file extension using the Moodle icon
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

        # Sanitize filename and append file extension
        clean_filename = re.sub(r'[\\/*?:"<>|]', "", link_text)
        if not clean_filename.lower().endswith(('.pdf', '.txt', '.docx', '.xlsx', '.py')):
            clean_filename += extension

        file_path = os.path.join(DOWNLOAD_DIR, clean_filename)
        print(f"Downloading: {clean_filename} ...")
        
        try:
            # Add session cookie here if Moodle requires authentication
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                # "Cookie": "MoodleSession=YOUR_COOKIE_HERE" 
            }
            
            response = requests.get(href, headers=headers, stream=True)
            
            if response.status_code == 200:
                with open(file_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                download_count += 1
            else:
                print(f" -> HTTP Error {response.status_code} (Cookie expired?)")
                
        except Exception as e:
            print(f" -> Error downloading {clean_filename}: {e}")

    print(f"\nDone. {download_count} files downloaded.")

if __name__ == "__main__":
    download_campus_files()