import os
import sys
import requests
import time
import re
from pathlib import Path

def get_stored_api_key():
    """Reads the SerpApi key from the text file right next to the executable bundle."""
    # 🔍 DYNAMIC MULTI-OS PATH DETECTOR (Fixes Mac .app Bundle isolation layer)
    if getattr(sys, 'frozen', False):
        current_dir = Path(sys.executable).parent
        # If running inside a macOS bundle container, jump out to the visible folder level
        if "Contents/MacOS" in str(current_dir):
            current_dir = current_dir.parent.parent.parent
    else:
        current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        
    key_file_path = current_dir / "serp_api.txt"
    
    if key_file_path.exists():
        try:
            with open(key_file_path, "r", encoding="utf-8") as file:
                return file.read().strip()
        except Exception as e:
            print(f"⚠️ Error reading 'serp_api.txt': {str(e)}")
            
    return os.environ.get("SERPAPI_KEY")

def fetch_live_parameter_builder():
    """
    In-Built Updater Layer: Downloads the latest python code block 
    from GitHub to seamlessly adjust to changing SerpApi rules.
    """
    # 🎯 PERMANENT RAW URL FIXED TO ALWAYS GRAB YOUR LATEST EDITS AUTOMATICALLY:
    remote_code_url = "https://gist.githubusercontent.com/skengeneral/923e8a43be9bf78c309f44a070bdb0f1/raw/parameter_builder.py"
    
    try:
        response = requests.get(remote_code_url, timeout=4)
        if response.status_code == 200:
            local_namespace = {}
            exec(response.text, globals(), local_namespace)
            if "build_live_parameters" in local_namespace:
                return local_namespace["build_live_parameters"]
    except Exception as e:
        print(f"⚠️ Live patch link unreached ({str(e)}). Deploying built-in recovery parameters...")
    
    def fallback_builder(search_query, target_city, api_key, start_offset):
        full_search_string = search_query
        if target_city and target_city.strip():
            full_search_string = f"{search_query}, {target_city.strip()}"
        return {
            "engine": "google_maps",
            "q": full_search_string,
            "type": "search",
            "api_key": api_key,
            "start": start_offset
        }
    return fallback_builder

def extract_socials_from_website(website_url):
    """Scans the home page of a business website to discover official social media profile links."""
    socials = {"Facebook": "Not Provided", "Instagram": "Not Provided", "LinkedIn": "Not Provided", "Twitter/X": "Not Provided"}
    if not website_url or "No Website" in website_url or not website_url.startswith("http"):
        return socials
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(website_url, headers=headers, timeout=5)
        if response.status_code == 200:
            html_content = response.text
            fb_match = re.search(r'href=["\'](https?://(?:www\.)?facebook\.com/[a-zA-Z0-9_\-\.]+)/?["\']', html_content, re.IGNORECASE)
            ig_match = re.search(r'href=["\'](https?://(?:www\.)?instagram\.com/[a-zA-Z0-9_\-\.]+)/?["\']', html_content, re.IGNORECASE)
            li_match = re.search(r'href=["\'](https?://(?:www\.)?linkedin\.com/(?:in|company)/[a-zA-Z0-9_\-\.]+)/?["\']', html_content, re.IGNORECASE)
            tw_match = re.search(r'href=["\'](https?://(?:www\.)?(?:twitter|x)\.com/[a-zA-Z0-9_\-\.]+)/?["\']', html_content, re.IGNORECASE)
            if fb_match: socials["Facebook"] = fb_match.group(1)
            if ig_match: socials["Instagram"] = ig_match.group(1)
            if li_match: socials["LinkedIn"] = li_match.group(1)
            if tw_match: socials["Twitter/X"] = tw_match.group(1)
    except:
        pass
    return socials

def extract_local_leads(search_query, allowed_ratings, target_city=None):
    """Queries SerpApi Google Maps utilizing live updated script injection rules."""
    api_key = get_stored_api_key()
    if not api_key:
        print("❌ ERROR: No API key found inside your 'serp_api.txt' file.")
        return {"data": [], "columns_layout": None}
        
    filtered_leads = []
    endpoint = "https://serpapi.com/search.json"
    
    build_parameters = fetch_live_parameter_builder()
    
    current_page = 1
    max_pages = 5  # Safe local baseline depth fallback
    results_per_page = 20
    live_columns_layout = None
    
    print("🚀 Initializing Dynamic Patched Engine...")

    while current_page <= max_pages:
        start_offset = (current_page - 1) * results_per_page
        params = build_parameters(search_query, target_city, api_key, start_offset)
        
        # 🛡️ THE CLOUD METADATA LAYER: Extract depth and structures from GitHub payload
        if live_columns_layout is None:
            max_pages = params.pop("MAX_PAGES_OVERRIDE", 5)
            live_columns_layout = params.pop("ALLOWED_COLUMNS_MATRIX", None)
        else:
            params.pop("MAX_PAGES_OVERRIDE", None)
            params.pop("ALLOWED_COLUMNS_MATRIX", None)

        print(f"📄 Scraping Page {current_page} of {max_pages} (Record Offset: {start_offset})...")
        
        try:
            response = requests.get(endpoint, params=params, timeout=20)
            if response.status_code != 200:
                print(f"⚠️ Server returned error status: {response.status_code}. Breaking loop.")
                break
                
            data = response.json()
            raw_results = data.get("local_results", [])
            if not raw_results:
                print("🏁 No additional local entries returned from Google Maps data pools.")
                break
                
            for biz in raw_results:
                title = biz.get("title") or biz.get("name") or "Unknown Firm"
                raw_rating = biz.get("rating", 0)
                try: rating_val = float(raw_rating)
                except: rating_val = 0.0
                
                rating_matches = False
                if "ALL" in allowed_ratings:
                    rating_matches = True
                else:
                    for selected_rate in allowed_ratings:
                        try:
                            target_int = int(selected_rate)
                            if target_int == 5 and rating_val == 5.0:
                                rating_matches = True
                                break
                            elif target_int <= rating_val < (target_int + 1):
                                rating_matches = True
                                break
                        except ValueError: continue
                
                if rating_matches:
                    full_address = biz.get("address", "") or "Not Provided"
                    website_link = biz.get("website") or "No Website"
                    found_socials = {"Facebook": "Not Provided", "Instagram": "Not Provided", "LinkedIn": "Not Provided", "Twitter/X": "Not Provided"}
                    
                    native_links = biz.get("links", {})
                    if isinstance(native_links, dict):
                        for platform, link in native_links.items():
                            if "facebook" in platform.lower(): found_socials["Facebook"] = link
                            elif "instagram" in platform.lower(): found_socials["Instagram"] = link
                            elif "linkedin" in platform.lower(): found_socials["LinkedIn"] = link
                            elif "twitter" in platform.lower() or "x.com" in platform.lower(): found_socials["Twitter/X"] = link
                    
                    if all(v == "Not Provided" for v in found_socials.values()):
                        found_socials = extract_socials_from_website(website_link)
                    
                    gps_hours = biz.get("operating_hours", {})
                    hours_string = "Not Provided"
                    if isinstance(gps_hours, dict) and gps_hours:
                        hours_string = " | ".join([f"{day.capitalize()}: {time_str}" for day, time_str in gps_hours.items()])
                    
                    lead_card = {
                        "Business Name": title, "Google Rating": rating_val, "Complete Address": full_address,
                        "Operating Hours Matrix": hours_string, "Website Link": website_link,
                        "Phone Number": biz.get("phone") or "Not Provided",
                        "Google Plus Code": biz.get("gps_coordinates", {}).get("plus_code") or "Not Provided",
                        "Facebook Handle": found_socials["Facebook"], "Instagram Handle": found_socials["Instagram"],
                        "LinkedIn Handle": found_socials["LinkedIn"], "Twitter/X Handle": found_socials["Twitter/X"]
                    }
                    filtered_leads.append(lead_card)
            
            # 🔄 ADVANCED MULTI-TOKEN MAPS PAGINATION TRACKER
            serp_pagination = data.get("serpapi_pagination", {})
            has_next_indicator = (
                "next" in serp_pagination or 
                "next_page_token" in serp_pagination or 
                "next_page_token" in data
            )
            
            if not has_next_indicator:
                print("🏁 Google Maps indicates no more pages exist for this keyword framework.")
                break
                
            current_page += 1
            time.sleep(1.2) # Friendly pacing delay to stabilize scrapers
            
        except Exception as e:
            print(f"❌ Extraction anomaly: {str(e)}")
            break

    print(f"🎉 Complete! Successfully extracted {len(filtered_leads)} leads.")
    
    return {
        "data": filtered_leads,
        "columns_layout": live_columns_layout
    }