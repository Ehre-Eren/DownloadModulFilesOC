import os
import re
import sys
import subprocess

try:
    from playwright.sync_api import sync_playwright
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    from bs4 import BeautifulSoup
except ImportError:
    print("Dependencies missing. Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright", "beautifulsoup4"])
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
    from playwright.sync_api import sync_playwright
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    from bs4 import BeautifulSoup

CAMPUS_URL = "https://oc-digital.de/node/6100"
AUTH_FILE = "auth.json"
DOWNLOAD_DIR = "downloads"

def get_available_courses(page):
    print("Scanning Online-Campus for module cards...")
    page.wait_for_load_state("networkidle")
    page.wait_for_selector("h3, .card, [class*='course']", timeout=100000)
    
    extracted_data = page.evaluate("""
        () => {
            const results = [];
            const allElements = document.querySelectorAll('*');
            
            let currentSemester = "Allgemeine Module";
            
            allElements.forEach(el => {
                const text = el.innerText ? el.innerText.trim() : '';
                
                // Recognize semester group headers
                if (/^\\d{4}-(WS|SS)$/.test(text) && el.children.length === 0) {
                    currentSemester = text;
                }
                
                // Identify the course block by its title heading
                if ((el.tagName === 'H3' || el.tagName === 'H4') && el.innerText) {
                    let name = el.innerText.trim();
                    
                    // Clean up text
                    name = name.split(/Prof\\.|Dipl\\.-Inf\\.|M\\.Sc\\./i)[0].trim();
                    name = name.replace(/\\s*Nächste Veranstaltung.*$/i, '').trim();
                    name = name.replace(/\\n/g, ' ').trim();
                    
                    if (name.length > 4 && !name.includes("Anmeldung") && !name.includes("Veranstaltung")) {
                        
                        // Ascend to the parent card container
                        let card = el.closest('.card') || el.closest('[class*="course"]') || el.parentElement;
                        
                        // Search for the actual hyperlink (like the yellow arrow button) inside the card
                        let linkNode = card.querySelector('a');
                        
                        // Decide what element to interact with
                        let clickTarget = linkNode ? linkNode : card;
                        const customId = 'course-target-' + Math.random().toString(36).substr(2, 9);
                        clickTarget.setAttribute('data-custom-id', customId);
                        
                        results.push({
                            semester: currentSemester,
                            name: name,
                            selector: `[data-custom-id="${customId}"]`,
                            url: linkNode ? linkNode.href : ""
                        });
                    }
                }
            });
            
            // Deduplicate the resulting list
            const uniqueResults = [];
            const seenNames = new Set();
            results.forEach(r => {
                const uniqueKey = r.semester + '-' + r.name;
                if (!seenNames.has(uniqueKey)) {
                    seenNames.add(uniqueKey);
                    uniqueResults.push(r);
                }
            });
            
            return uniqueResults;
        }
    """)
    return extracted_data

def download_course_contents(target_page):
    print("Waiting for Moodle course contents to load...")
    # Allow up to 25 seconds for Moodle to finish generating the DOM tree
    target_page.wait_for_selector("li.modtype_resource", timeout=25000)
    
    html_content = target_page.content()
    soup = BeautifulSoup(html_content, "html.parser")
    resource_items = soup.find_all("li", class_=lambda c: c and "modtype_resource" in c)
    
    print(f"Resources found inside course: {len(resource_items)}")
    download_count = 0

    for item in resource_items:
        link_tag = item.find("a", href=True)
        if not link_tag:
            continue
            
        href = link_tag["href"]
        if "id=" in href:
            asset_id = href.split("id=")[-1].split("&")[0]
            download_url = f"https://lms.fom.de/mod/resource/view.php?id={asset_id}&redirect=1"
        else:
            continue

        instance_span = link_tag.find("span", class_="instancename")
        link_text = instance_span.get_text(strip=True) if instance_span else link_tag.get_text(strip=True)
        link_text = re.sub(r'(Datei|Aktivität|Resource)$', '', link_text, flags=re.IGNORECASE).strip()

        img_tag = item.find("img", class_="activityicon")
        extension = ".pdf"
        if img_tag and "src" in img_tag.attrs:
            img_src = img_tag["src"].lower()
            if "pdf" in img_src: extension = ".pdf"
            elif "text" in img_src or "txt" in img_src: extension = ".txt"
            elif "document" in img_src or "word" in img_src: extension = ".docx"
            elif "spreadsheet" in img_src or "excel" in img_src: extension = ".xlsx"
            elif "python" in img_src or "code" in img_src: extension = ".py"

        clean_filename = re.sub(r'[\\/*?:"<>|]', "", link_text)
        if not clean_filename.lower().endswith(('.pdf', '.txt', '.docx', '.xlsx', '.py')):
            clean_filename += extension

        file_path = os.path.join(DOWNLOAD_DIR, clean_filename)
        print(f"Downloading: {clean_filename} ...")

        try:
            with target_page.expect_download(timeout=4000) as download_info:
                try:
                    target_page.goto(download_url, wait_until="commit")
                except Exception:
                    pass
            download = download_info.value
            download.save_as(file_path)
            download_count += 1
        except Exception:
            try:
                page_text = target_page.locator("body").inner_text()
                if "Aktivität" not in page_text and "Dashboard" not in page_text:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(page_text)
                    download_count += 1
                else:
                    print(f" -> Failed: {clean_filename}")
            except Exception as e:
                print(f" -> Error: {clean_filename} ({e})")

    print(f"\nDone. {download_count} files successfully downloaded.")

def main():
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    with sync_playwright() as p:
        has_auth = os.path.exists(AUTH_FILE)
        is_headless = True if has_auth else False
        
        browser = p.chromium.launch(
            headless=is_headless, 
            args=["--disable-blink-features=AutomationControlled"]
        )
        context_args = {"storage_state": AUTH_FILE} if has_auth else {}
        context = browser.new_context(**context_args)
        page = context.new_page()

        print("Navigating to Online-Campus Portal...")
        page.goto(CAMPUS_URL)

        try:
            page.wait_for_selector("h3, .card, [class*='course']", timeout=5000)
        except PlaywrightTimeoutError:
            print("\n[!] Session expired or login needed. Opening browser window for authentication...")
            browser.close()
            browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
            context = browser.new_context()
            page = context.new_page()
            page.goto(CAMPUS_URL)
            
            print("[!] Keep the browser open until you see your course overview dashboard layout...\n")
            
            while True:
                try:
                    if page.locator("h3, .card, [class*='course']").count() > 2:
                        page.wait_for_timeout(2000)
                        break
                except Exception:
                    pass
                page.wait_for_timeout(1000)
                
            context.storage_state(path=AUTH_FILE)
            print("Fresh session saved successfully.")

        courses = get_available_courses(page)
        
        if not courses:
            print("No courses detected. Check the browser window context layout view.")
            browser.close()
            return

        print("\n================ AVAILABLE COURSES ================")
        current_semester = ""
        for index, course in enumerate(courses):
            if course["semester"] != current_semester:
                current_semester = course["semester"]
                print(f"\n--- {current_semester} ---")
            print(f" [{index + 1}] {course['name']}")
        print("===================================================\n")

        while True:
            try:
                choice = input(f"Select a course number to download (1-{len(courses)}) or 'q' to quit: ").strip()
                if choice.lower() == 'q':
                    break
                
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(courses):
                    selected_course = courses[choice_idx]
                    print(f"\nSelected: {selected_course['name']} ({selected_course['semester']})")
                    
                    target_url = selected_course.get("url", "")
                    
                    # 1. Approach: Direct URL Navigation (Fastest & Safest)
                    if target_url and target_url.startswith("http"):
                        print("Navigating directly to extracted course link...")
                        page.goto(target_url)
                        download_course_contents(page)
                    
                    # 2. Approach: Fallback to physical interaction if JS hides the URL
                    else:
                        print("Executing native click on course element...")
                        try:
                            # Catch popup tab if the FOM portal decides to open one
                            with context.expect_page(timeout=3000) as popup_info:
                                page.click(selected_course["selector"])
                            moodle_page = popup_info.value
                            print("Processing within new popup tab frame...")
                            download_course_contents(moodle_page)
                            moodle_page.close()
                            
                        except PlaywrightTimeoutError:
                            # The click happened seamlessly in the current tab
                            print("Processing within current context frame...")
                            download_course_contents(page)
                    
                    # Finally, reset the viewport back to the dashboard for your next command
                    page.goto(CAMPUS_URL)
                    
                else:
                    print(f"Invalid range. Choose a number between 1 and {len(courses)}.")
            except ValueError:
                print("Please enter a valid number or 'q'.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                print("Attempting to recover browser state...")
                try:
                    browser = p.chromium.launch(headless=is_headless, args=["--disable-blink-features=AutomationControlled"])
                    context = browser.new_context(storage_state=AUTH_FILE if os.path.exists(AUTH_FILE) else None)
                    page = context.new_page()
                    page.goto(CAMPUS_URL)
                except Exception:
                    print("Critical environment crash. Please restart the script execution loop.")
                    break

        browser.close()

if __name__ == "__main__":
    main()