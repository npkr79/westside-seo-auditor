#!/usr/bin/env python3
"""
PHASE 2 SIMPLE - Competitor Analysis for 3 pages
"""

import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import google.generativeai as genai

print("🚀 PHASE 2 SIMPLE - Working!")

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')

pages = [
    {"url": "https://www.westsiderealty.in/hyderabad/neopolis", "name": "Neopolis"},
    {"url": "https://www.westsiderealty.in/landing/godrej-regal-pavilion-rajendra-nagar-hyderabad", "name": "Godrej Regal"},
    {"url": "https://www.westsiderealty.in/hyderabad/kokapet", "name": "Kokapet"}
]

results = []
for page in pages:
    print(f"\nAnalyzing {page['name']}")
    
    # Get YOUR page data
    r = requests.get(page['url'], timeout=10)
    soup = BeautifulSoup(r.content, 'html.parser')
    title = soup.find('title')
    title = title.text.strip()[:60] if title else ""
    words = len(soup.get_text().split())
    
    # Gemini analysis
    prompt = f"""Page: {page['name']}
URL: {page['url']}
Title: {title}
Words: {words}

Give 3 competitors + 3 gaps + 1 Cursor prompt.

Format:
COMPETITORS: url1, url2, url3
GAPS: gap1, gap2, gap3
CURSOR: [prompt]"""
    
    try:
        resp = model.generate_content(prompt)
        analysis = resp.text
        
        results.append({
            'page': page['name'],
            'url': page['url'],
            'title': title,
            'words': words,
            'analysis': analysis[:500]
        })
        print(f"✅ {page['name']}: {analysis[:100]}...")
    except:
        results.append({
            'page': page['name'],
            'url': page['url'],
            'title': title,
            'words': words,
            'analysis': 'Gemini error'
        })

df = pd.DataFrame(results)
df.to_csv('phase2_simple.csv', index=False)
print("\n✅ Phase 2 COMPLETE! phase2_simple.csv ready!")
