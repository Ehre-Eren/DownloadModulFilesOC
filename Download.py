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
        
        # Parse clean filename from instancename
        instance_span = link_tag.find("span", class_="instancename")
        if instance_span:
            link_text = instance_span.get_text(strip=True)
        else:
            link_text = link_tag.get_text(strip=True)
            
        # Clean hidden Moodle text fragments
        link_text = re.sub(r'(Datei|Aktivität|Resource)$', '', link_text, flags=re.IGNORECASE).strip()

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
        
        try:
            # UNCOMMENT AND PASTE YOUR COOKIE HERE
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                # "Cookie": "MoodleSession=YOUR_COOKIE_HERE" 
            }
            
            # Use allow_redirects=False to catch Moodle trying to redirect to the login page
            response = requests.get(href, headers=headers, stream=True, allow_redirects=False)
            
            if response.status_code == 200:
                print(f"Downloading: {clean_filename} ...")
                with open(file_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                download_count += 1
            elif response.status_code in [302, 303]:
                print(f" -> Skipped: {clean_filename} (Auth failed, redirected to login. Check your Cookie string!)")
            else:
                print(f" -> HTTP Error {response.status_code} for {clean_filename}")
                
        except Exception as e:
            print(f" -> Error downloading {clean_filename}: {e}")

    print(f"\nDone. {download_count} files successfully downloaded.")

if __name__ == "__main__":
    download_campus_files()