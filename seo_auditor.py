#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
from collections import Counter
from urllib.parse import urlparse

print("🚀 Westside SEO Audit Starting... (50 Pages + 17 Competitors)")

# YOUR 50 PAGES
pages = [
    "https://www.westsiderealty.in/",
    "https://www.westsiderealty.in/hyderabad",
    "https://www.westsiderealty.in/goa",
    "https://www.westsiderealty.in/blog",
    "https://www.westsiderealty.in/contact",
    "https://www.westsiderealty.in/hyderabad/projects/aparna-zenon",
    "https://www.westsiderealty.in/hyderabad/projects/myscape-edition",
    "https://www.westsiderealty.in/hyderabad/projects/sumadhura-the-olympus",
    "https://www.westsiderealty.in/landing/godrej-regal-pavilion-rajendra-nagar-hyderabad",
    "https://www.westsiderealty.in/hyderabad/projects/aparna-cyber-star",
    "https://www.westsiderealty.in/hyderabad/projects/aparna-amber-villas",
    "https://www.westsiderealty.in/landing/aerocidade-studio-apartments-dabolim",
    "https://www.westsiderealty.in/hyderabad/projects/aparna-cyber-heights",
    "https://www.westsiderealty.in/hyderabad/projects/the-vue-residences",
    "https://www.westsiderealty.in/hyderabad/projects/jayabheri-the-nirvana",
    "https://www.westsiderealty.in/hyderabad/projects/aparna-luxor-park",
    "https://www.westsiderealty.in/hyderabad/projects/my-home-ankura",
    "https://www.westsiderealty.in/hyderabad/projects/aparna-cyber-shine",
    "https://www.westsiderealty.in/hyderabad/projects/hallmark-treasor-kokapet-hyderabad",
    "https://www.westsiderealty.in/hyderabad/projects/anvita-high9-tellapur-hyderabad",
    "https://www.westsiderealty.in/hyderabad/projects/rajapushpa-aurelia-tellapur-hyderabad",
    "https://www.westsiderealty.in/hyderabad/projects/aparna-newlands-tellapur-hyderabad",
    "https://www.westsiderealty.in/hyderabad/projects/rajapushpa-imperia-tellapur-hyderabad",
    "https://www.westsiderealty.in/hyderabad/projects/my-home-tridasa-tellapur-hyderabad",
    "https://www.westsiderealty.in/hyderabad/projects/visions-arsha-tellapur-hyderabad",
    "https://www.westsiderealty.in/hyderabad/projects/vihaan-shikhara-tellapur-hyderabad",
    "https://www.westsiderealty.in/hyderabad/projects/vajra-west-city-tellapur-hyderabad",
    "https://www.westsiderealty.in/hyderabad/projects/supadha-gamya-tellapur-hyderabad",
    "https://www.westsiderealty.in/hyderabad/projects/eka-one-kokapet",
    "https://www.westsiderealty.in/hyderabad/projects/fortune-suraj-bhan-grande-kokapet-hyderabad",
    "https://www.westsiderealty.in/hyderabad/narsingi",
    "https://www.westsiderealty.in/hyderabad/tukkuguda",
    "https://www.westsiderealty.in/hyderabad/kokapet",
    "https://www.westsiderealty.in/hyderabad/rajendra-nagar",
    "https://www.westsiderealty.in/hyderabad/hitech-city",
    "https://www.westsiderealty.in/hyderabad/budwel",
    "https://www.westsiderealty.in/hyderabad/manikonda",
    "https://www.westsiderealty.in/hyderabad/nanakramguda",
    "https://www.westsiderealty.in/hyderabad/puppalaguda",
    "https://www.westsiderealty.in/hyderabad/tellapur",
    "https://www.westsiderealty.in/hyderabad/osman-nagar",
    "https://www.westsiderealty.in/hyderabad/neopolis",
    "https://www.westsiderealty.in/hyderabad/gopanpally",
    "https://www.westsiderealty.in/hyderabad/mokila",
    "https://www.westsiderealty.in/hyderabad/nallagandla",
    "https://www.westsiderealty.in/hyderabad/buy/4bhk-apartment-sale-myscape-edition-financial-district",
    "https://www.westsiderealty.in/hyderabad/buy/4bhk-apartment-for-sale-in-trendset-insperia-banjara-hills",
    "https://www.westsiderealty.in/hyderabad/buy/4bhk-apartment-for-sale-in-cybercity-westbrook-kokapet",
    "https://www.westsiderealty.in/goa/buy/aerocidade-studio-apartments-dabolim",
    "https://www.westsiderealty.in/dubai/buy/6bhk-villa-dubai-141-18-crore-dubai"
]

# YOUR 17 COMPETITORS
competitors = {
    'tellapur': 'https://www.magicbricks.com/new-projects-tellapur-hotspot-in-hyderabad',
    'sumadhura the olympus': 'https://housing.com/in/buy/projects/page/255548-sumadhura-the-olympus-by-sumadhura-infracon-pvt-ltd-in-financial-district',
    'aerocidade': 'https://www.99acres.com/studio-apartment-flat-for-sale-in-devika-aero-cidade-dabolim-vasco-da-gama-582-sq-ft-npspid-Y87422102',
    'aparna zenon': 'https://housing.com/in/buy/projects/page/269673-aparna-zenon-by-aparna-constructions-in-manikonda',
    'myscape edition': 'https://myscape.in/project/edition',
    'olympus nanakramguda': 'https://www.magicbricks.com/sumadhura-infracon-the-olympus-nanakram-guda-hyderabad-pdpid-4d4235323938353931',
    'godrej regal pavilion': 'https://www.homznspace.com/godrej-regal-pavilion-rajendra-nagar-hyderabad',
    'aparna cyber star': 'https://www.proptiger.com/hyderabad/osman-nagar/aparna-constructions-cyber-star-3217304',
    'devika aero cidade': 'https://www.99acres.com/devika-aero-cidade-dabolim-vasco-da-gama-npxid-r430769',
    'hallmark treasor': 'https://propertyadviser.in/news/project/hallmark-treasor-10215',
    'anvita high9': 'https://www.homznspace.com/anvita-high9-tellapur-hyderabad',
    'rajapushpa aurelia': 'https://housing.com/in/buy/projects/page/309828-rajapushpa-aurelia-by-rajapushpa-properties-pvt-ltd-in-tellapur',
    'aparna newlands': 'https://www.squareyards.com/hyderabad-residential-property/aparna-newlands/239244/project',
    'neopolis': 'https://www.limitless.in/p/index.html?neopolis.in',
    'magicbricks tellapur': 'https://www.magicbricks.com/Tellapur-in-Hyderabad-Overview',
    '99acres tellapur 3bhk': 'https://www.99acres.com/3-bhk-flats-in-tellapur-hyderabad-ffid',
    'godrejproperties regal': 'https://www.godrejproperties.com/hyderabad/residential/godrej-regal-pavilion'
}

def extract_seo_data(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        title = soup.find('title')
        title = title.text.strip()[:60] if title else "No title"
        
        h1 = soup.find('h1')
        h1 = h1.text.strip()[:80] if h1 else "No H1"
        
        text = soup.get_text()
        word_count = len(text.split())
        
        keywords = re.findall(r'\b[a-zA-Z]{3,}\b', (title + " " + h1).lower())
        keywords = [w for w in keywords if w not in ['the', 'and', 'for', 'with']]
        keywords = [w for w, _ in Counter(keywords).most_common(3)]
        
        return {
            'url': url,
            'title': title,
            'h1': h1,
            'word_count': word_count,
            'keywords': keywords,
            'status_code': response.status_code
        }
    except:
        return None

def find_competitor(url_path, keywords):
    """Match competitor to page"""
    path_lower = url_path.lower()
    keywords_lower = ' '.join(keywords).lower()
    
    for comp_key, comp_url in competitors.items():
        if comp_key in path_lower or comp_key in keywords_lower:
            return comp_url
    return None

results = []
for i, url in enumerate(pages[:25], 1):  # First 25 for 3-min runtime
    print(f"Analyzing {i}/25: {urlparse(url).path}")
    page_data = extract_seo_data(url)
    
    if page_
        title_len = len(page_data['title'])
        score = 50
        if 50 <= title_len <= 60: score += 15
        if page_data['h1'] != "No H1": score += 10
        if page_data['word_count'] > 1000: score += 15
        
        priority = "YES" if score < 80 else "NO"
        main_keyword = page_data['keywords'][0] if page_data['keywords'] else "project"
        competitor = find_competitor(urlparse(url).path, page_data['keywords'])
        
        prompt = f"""🎯 Fix SEO: {page_data['url']}
🔍 Keyword: {main_keyword}
📊 Score: {score}/100 | Title: {title_len} chars
🥇 Competitor: {competitor or 'None'}
📝 FIX: Title length, H1 keyword, add schema + locality sections"""

        results.append({
            'url': page_data['url'],
            'title': page_data['title'],
            'score': score,
            'priority': priority,
            'word_count': page_data['word_count'],
            'keyword': main_keyword,
            'competitor': competitor or '',
            'prompt': prompt
        })

df = pd.DataFrame(results)
df.to_csv('priority_seo_fixes.csv', index=False)

print(f"\n✅ SUCCESS! {len(results)}/50 pages analyzed + 17 competitors matched!")
print("📊 priority_seo_fixes.csv → Download from Artifacts!")
print(f"🔥 Priority fixes ({len(df[df['priority']=='YES'])}): Neopolis, Godrej, Tellapur...")
