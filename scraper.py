import requests
import time
import json
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple
from datetime import datetime

class SheypoorScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36',
            'Accept': 'application/vnd.api+json, application/json',
            'Content-Type': 'application/json',
            'Origin': 'https://www.sheypoor.com',
        })
        self.api_base = "https://www.sheypoor.com/api/v10.0.0"
        self.base_url = "https://www.sheypoor.com"
        self.delay = 3

    def get_phone_number(self, ad_id: str, ad_link: str) -> Optional[str]:
        url = f"{self.api_base}/listings/{ad_id}/number"
        headers = {'Referer': ad_link}
        
        try:
            response = self.session.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return data.get('data', {}).get('attributes', {}).get('phoneNumber')
        except:
            pass
        return None

    def get_listings_from_html(self, city_slug: str = "tehran", page: int = 1) -> Tuple[List[Dict], bool]:
        url = f"{self.base_url}/s/{city_slug}" + (f"?page={page}" if page > 1 else "")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            ad_items = soup.find_all('a', attrs={'data-test-id': re.compile(r'^ad-item-')})
            
            if not ad_items:
                return [], False
            
            listings = []
            for ad in ad_items:
                try:
                    test_id = ad.get('data-test-id', '')
                    ad_id_match = re.search(r'ad-item-(\d+)', test_id)
                    ad_id = ad_id_match.group(1) if ad_id_match else None
                    if not ad_id:
                        continue
                    
                    title_tag = ad.find('h2')
                    title = title_tag.get_text(strip=True) if title_tag else "No title"
                    
                    price_span = ad.find('span', class_=re.compile(r'text-heading-4-bolder'))
                    price = price_span.get_text(strip=True) if price_span else "Negotiable"
                    
                    href = ad.get('href', '')
                    if href and not href.startswith('http'):
                        href = self.base_url + href
                    
                    listings.append({
                        'id': ad_id,
                        'title': title,
                        'price': price,
                        'link': href,
                        'source': 'sheypoor',
                        'phone': None
                    })
                except:
                    continue
            
            has_next = soup.find('a', string=re.compile(r'بعدی|next', re.I)) is not None
            return listings, has_next
        except:
            return [], False

    def scrape(self, city: str = "tehran", target_count: int = 30) -> List[Dict]:
        all_ads = []
        page = 1
        
        while len(all_ads) < target_count:
            listings, has_next = self.get_listings_from_html(city, page)
            if not listings:
                break
            
            needed = target_count - len(all_ads)
            all_ads.extend(listings[:needed])
            
            if len(all_ads) >= target_count or not has_next:
                break
            
            page += 1
            time.sleep(self.delay)
        
        for i, ad in enumerate(all_ads):
            phone = self.get_phone_number(ad['id'], ad['link'])
            ad['phone'] = phone if phone else "Not found"
            ad['extracted_at'] = datetime.now().isoformat()
            time.sleep(self.delay)
        
        return all_ads

class DivarScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        })
        self.api_base = "https://api.divar.ir/v8"
        self.base_url = "https://divar.ir"
        self.delay = 2

    def search_ads(self, city: str = "tehran", category: str = "real-estate", limit: int = 30) -> List[Dict]:
        url = f"{self.api_base}/web-search/{city}/{category}"
        
        all_ads = []
        last_post_date = None
        
        for _ in range(limit // 25 + 1):
            try:
                params = {"last-post-date": last_post_date} if last_post_date else {}
                response = self.session.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    widgets = data.get('widgets', [])
                    
                    for widget in widgets:
                        if widget.get('widget_type') == 'TOKEN_GRID_VIEW':
                            for item in widget.get('items', []):
                                ad_data = item.get('data', {})
                                all_ads.append({
                                    'id': ad_data.get('token'),
                                    'title': ad_data.get('title', 'No title'),
                                    'price': ad_data.get('price', {}).get('display', 'Negotiable'),
                                    'link': f"{self.base_url}/v/{ad_data.get('token')}",
                                    'source': 'divar',
                                    'phone': None
                                })
                                if len(all_ads) >= limit:
                                    break
                    
                    next_data = data.get('next_data')
                    if next_data and next_data.get('last_post_date'):
                        last_post_date = next_data['last_post_date']
                    else:
                        break
                    
                    time.sleep(self.delay)
            except:
                break
        
        return all_ads[:limit]

    def get_phone_number(self, ad_token: str) -> Optional[str]:
        url = f"{self.api_base}/web/post/{ad_token}"
        
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                
                for widget in data.get('widgets', []):
                    if widget.get('widget_type') == 'SELLER_CONTACT_WIDGET':
                        contact_data = widget.get('data', {})
                        phone = contact_data.get('phone_number')
                        if phone:
                            return phone
                        
                        chat_info = contact_data.get('chat_info', {})
                        if chat_info.get('phone_number'):
                            return chat_info.get('phone_number')
        except:
            pass
        return None

    def scrape(self, city: str = "tehran", category: str = "real-estate", target_count: int = 30) -> List[Dict]:
        ads = self.search_ads(city, category, target_count)
        
        for i, ad in enumerate(ads):
            phone = self.get_phone_number(ad['id'])
            ad['phone'] = phone if phone else "Not found"
            ad['extracted_at'] = datetime.now().isoformat()
            time.sleep(self.delay)
        
        return ads

class ScraperManager:
    def __init__(self):
        self.sheypoor = SheypoorScraper()
        self.divar = DivarScraper()
    
    def run_sheypoor(self, city: str = "tehran", count: int = 30) -> Dict:
        results = self.sheypoor.scrape(city, count)
        return {"success": True, "source": "sheypoor", "count": len(results), "data": results}
    
    def run_divar(self, city: str = "tehran", category: str = "real-estate", count: int = 30) -> Dict:
        results = self.divar.scrape(city, category, count)
        return {"success": True, "source": "divar", "count": len(results), "data": results}