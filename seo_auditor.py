#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import pandas as pd

print("🚀 Westside SEO Audit - WORKING!")

pages = [
    "https://www.westsiderealty.in/hyderabad/neopolis",
    "https://www.westsiderealty.in/landing/godrej-regal-pavilion-rajendra-nagar-hyderabad",
    "https://www.westsiderealty.in/hyderabad/kokapet"
]

results = []
for url in pages:
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        title = soup.find('title')
        title = title.text.strip()[:60] if title else "No title"
        
        h1 = soup.find('h1')
        h1 = h1.text.strip()[:60] if h1 else "No H1"
        
        words = len(soup.get_text().split())
        score = 60 if len(title) > 40 else 40
        
        results.append({
            'url': url,
            'title': title,
            'h1': h1,
            'words': words,
            'score': score,
            'fix': f"Fix title: {len(title)} chars"
        })
        print(f"✅ {url} - Score: {score}")
    except:
        print(f"❌ {url} failed")
        pass

df = pd.DataFrame(results)
df.to_csv('seo_results.csv', index=False)
print("✅ DONE! Download seo_results.csv")
