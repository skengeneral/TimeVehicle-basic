import os
import sys
import time
import re
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse

# Import Playwright's synchronous API
from playwright.sync_api import sync_playwright

def get_local_api_key():
    if getattr(sys, 'frozen', False):
        current_dir = Path(sys.executable).parent
    else:
        current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    key_file_path = current_dir / "serp_api.txt"
    if key_file_path.exists():
        try:
            with open(key_file_path, "r", encoding="utf-8") as file:
                return file.read().strip()
        except: pass
    return os.environ.get("SERPAPI_KEY")

def get_stored_api_key():
    """Maps directly to local loader to handle dynamic cross-calls flawlessly."""
    return get_local_api_key()

def extract_emails_from_text(text_content):
    if not text_content:
        return None
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}'
    raw_emails = re.findall(email_pattern, text_content)
    
    mailto_emails = re.findall(r'href=["\']mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6})', text_content, re.IGNORECASE)
    all_found = raw_emails + mailto_emails
    
    if all_found:
        clean_emails = []
        for e in all_found:
            e_lower = e.lower()
            garbage_keywords = ['sentry', 'wixpress', 'example', 'yourdomain', 'template', 'email', 'domain', 'magicpin', 'baidyanath', 'dfat.gov']
            asset_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.css', '.js', '.html')
            
            if not e_lower.endswith(asset_extensions):
                if not any(bad_word in e_lower for bad_word in garbage_keywords):
                    clean_emails.append(e_lower)
        if clean_emails:
            clean_emails.sort(key=len)
            return clean_emails[0]
    return None

def fetch_email_via_google_search(api_key, business_name, full_address=None, target_city=None):
    endpoint = "https://serpapi.com/search.json"
    geo_tail = ""
    if full_address and full_address != "Not Provided":
        address_parts = [p.strip() for p in full_address.split(',')]
        if len(address_parts) >= 2:
            geo_tail = f"{address_parts[-2]}, {address_parts[-1]}"
            
    if not geo_tail and target_city:
        geo_tail = target_city.strip()
        
    if not geo_tail:
        geo_tail = "USA"
        
    search_query = f"{business_name}, {geo_tail} email id"
    
    params = {"engine": "google", "q": search_query, "api_key": api_key}
    try:
        response = requests.get(endpoint, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            answer_box = data.get("answer_box", {})
            answer_text = str(answer_box.get("answer") or answer_box.get("snippet") or "")
            found = extract_emails_from_text(answer_text)
            if found: return found
                
            organic_results = data.get("organic_results", [])
            for result in organic_results[:4]:
                found = extract_emails_from_text(result.get("snippet", ""))
                if found: return found
    except: pass
    return "Not Provided"

def scrape_page_with_browser(browser_context, target_url):
    try:
        page = browser_context.new_page()
        page.set_viewport_size({"width": 1280, "height": 800})
        response = page.goto(target_url, timeout=12000, wait_until="load")
        if not response or response.status != 200:
            page.close()
            return None
        time.sleep(1)
        rendered_content = page.content()
        page.close()
        return rendered_content
    except:
        return None

# 🟢 STEP 1: DEFINE CRAWLER UTILITY HIGHER UP IN FILE SO IT IS COMPILED FIRST
def extract_contact_metrics_from_website(playwright_instance, website_url):
    socials = {
        "Facebook": "Not Provided", "Instagram": "Not Provided", 
        "LinkedIn": "Not Provided", "Twitter/X": "Not Provided",
        "Email ID": "Not Provided"
    }
    if not website_url or "No Website" in website_url or not website_url.startswith("http"):
        return socials
        
    if website_url.startswith("http://"):
        website_url = website_url.replace("http://", "https://", 1)
        
    try:
        browser = playwright_instance.chromium.launch(headless=True, channel="chrome")
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        homepage_html = scrape_page_with_browser(context, website_url)
        if not homepage_html:
            browser.close()
            return socials
            
        found_email = extract_emails_from_text(homepage_html)
        if found_email: socials["Email ID"] = found_email
            
        fb_match = re.search(r'href=["\'](https?://(?:www\.)?facebook\.com/[a-zA-Z0-9_\-\.]+)/?["\']', homepage_html, re.IGNORECASE)
        ig_match = re.search(r'href=["\'](https?://(?:www\.)?instagram\.com/[a-zA-Z0-9_\-\.]+)/?["\']', homepage_html, re.IGNORECASE)
        li_match = re.search(r'href=["\'](https?://(?:www\.)?linkedin\.com/(?:in|company)/[a-zA-Z0-9_\-\.]+)/?["\']', homepage_html, re.IGNORECASE)
        tw_match = re.search(r'href=["\'](https?://(?:www\.)?(?:twitter|x)\.com/[a-zA-Z0-9_\-\.]+)/?["\']', homepage_html, re.IGNORECASE)
        
        if fb_match: socials["Facebook"] = fb_match.group(1)
        if ig_match: socials["Instagram"] = ig_match.group(1)
        if li_match: socials["LinkedIn"] = li_match.group(1)
        if tw_match: socials["Twitter/X"] = tw_match.group(1)
        
        if socials["Email ID"] == "Not Provided":
            contact_links = set()
            raw_links = re.findall(r'href\s*=\s*["\']([^"\']+)["\']', homepage_html, re.IGNORECASE)
            for link in raw_links:
                if any(k in link.lower() for k in ['contact', 'about', 'register', 'info', 'reach']):
                    contact_links.add(link)
            parsed_base = urlparse(website_url)
            base_domain = f"{parsed_base.scheme}://{parsed_base.netloc}"
            
            if len(contact_links) == 0:
                for route in ['/contact-us', '/contact', '/about-us', '/about']:
                    contact_links.add(route)
            processed_subpages = set()
            for link in contact_links:
                full_subpage_url = urljoin(website_url, link) if (link.startswith('/') or link.startswith('http')) else f"{base_domain.rstrip('/')}/{link.lstrip('/')}"
                if base_domain in full_subpage_url and full_subpage_url not in processed_subpages:
                    processed_subpages.add(full_subpage_url)
                    subpage_html = scrape_page_with_browser(context, full_subpage_url)
                    if subpage_html:
                        sub_email = extract_emails_from_text(subpage_html)
                        if sub_email:
                            socials["Email ID"] = sub_email
                            break
        browser.close()
    except: pass
    return socials

# 🟢 STEP 2: MAIN ENGINE RUNS AFTER HELPER FUNCTIONS ARE COMPILED
def extract_local_leads(search_query, allowed_ratings, target_city=None):
    api_key = get_local_api_key()
    if not api_key:
        print("❌ ERROR: No API key found.")
        return {"data": [], "columns_layout": None}
        
    filtered_leads = []
    processed_titles = set()
    endpoint = "https://serpapi.com/search.json"
    current_page = 1
    max_pages = 5                  
    results_per_page = 20

    with sync_playwright() as p:
        while current_page <= max_pages:
            start_offset = (current_page - 1) * results_per_page
            full_search_string = search_query
            if target_city and target_city.strip():
                full_search_string = f"{search_query}, {target_city.strip()}"
                
            params = {
                "engine": "google_maps",
                "q": full_search_string,
                "type": "search",
                "api_key": api_key,
                "start": start_offset
            }

            try:
                response = requests.get(endpoint, params=params, timeout=20)
                if response.status_code != 200: break
                data = response.json()
                raw_results = data.get("local_results", [])
                if not raw_results: break
                    
                for biz in raw_results:
                title = biz.get("title") or biz.get("name") or "Unknown Firm"
                if title.lower().strip() in processed_titles: continue
                
                # 🚀 DYNAMIC SMART FILTER
                search_terms = [t.lower() for t in search_query.split() if len(t) > 2]
                exclude_words = ['nagole', 'india', 'city', 'town', 'area']
                search_terms = [t for t in search_terms if t not in exclude_words]

                if search_terms and not any(term in title.lower() for term in search_terms):
                    continue
                
                # 1. Rating Logic
                try: rating_val = float(biz.get("rating", 0))
                except: rating_val = 0.0
                
                rating_matches = False
                if "ALL" in allowed_ratings:
                    rating_matches = True
                else:
                    for selected_rate in allowed_ratings:
                        try:
                            target_int = int(selected_rate)
                            if target_int == 5 and rating_val == 5.0:
                                rating_matches = True; break
                            elif target_int <= rating_val < (target_int + 1):
                                rating_matches = True; break
                        except ValueError: continue

                if rating_matches:
                    processed_titles.add(title.lower().strip())
                    website_link = biz.get("website") or "No Website"
                    full_address = biz.get("address", "") or "Not Provided"
                    
                    # 2. Extract Data
                    found_metrics = extract_contact_metrics_from_website(website_link)
                    email_id = found_metrics["Email ID"]
                    
                    # 3. Email Deep Search Fallback
                    if email_id == "Not Provided":
                        email_id = fetch_email_via_google_search(api_key, title, full_address, target_city)
                    
                    # 4. Hours Matrix
                    gps_hours = biz.get("operating_hours", {})
                    hours_string = " | ".join([f"{day.capitalize()}: {t}" for day, t in gps_hours.items()]) if isinstance(gps_hours, dict) else "Not Provided"
                    
                    lead_card = {
                        "Business Name": title, "Google Rating": rating_val, 
                        "Complete Address": full_address, "Operating Hours Matrix": hours_string, 
                        "Website Link": website_link, "Email ID": email_id,
                        "Phone Number": biz.get("phone") or "Not Provided",
                        "Facebook Handle": found_metrics["Facebook"], "Instagram Handle": found_metrics["Instagram"],
                        "LinkedIn Handle": found_metrics["LinkedIn"], "Twitter/X Handle": found_metrics["Twitter/X"]
                    }
                    filtered_leads.append(lead_card)
                
                serp_pagination = data.get("serpapi_pagination", {})
                if "next" not in serp_pagination: break
                current_page += 1
                time.sleep(1)
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                break

    return {"data": filtered_leads, "columns_layout": None}
