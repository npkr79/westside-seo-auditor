#!/usr/bin/env python3
"""
AI SEO Pipeline Phase 1 - SITEMAP + CATEGORIZATION
"""

import os
import re
import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
import google.generativeai as genai

print("🚀 Phase 1: Sitemap → Categorization")

# SETUP
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

SITEMAP_URL = "https://www.westsiderealty.in/sitemap.xml"

def fetch_sitemap(limit=10):
    resp = requests.get(SITEMAP_URL)
    urls = re.findall(r"<loc>(https://www\.westsiderealty\.in/[^<]+)</loc>", resp.text)
    return urls[:limit]

def get_page_data(url):
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.content, 'html.parser')
        title = soup.find('title')
        title = title.text.strip()[:100] if title else ""
        h1 = soup.find('h1')
        h1 = h1.text.strip()[:100] if h1 else ""
        text = soup.get_text()[:1000]
        return title, h1, text, r.status_code
    except:
        return "", "", "", 0

def categorize(url, title, h1, text):
    prompt = f"""URL: {url}
Title: {title}
H1: {h1}
Text: {text[:500]}

Return JSON only:
{{"category": "homepage|city-hub|micro-market|project|listing|blog|contact", "keyword": "primary keyword"}}"""
    
    try:
        response = model.generate_content(prompt)
        # Clean response
        text = response.text.strip()
        if '```
            text = text.split('```')[1]
        data = json.loads(text)
        return data
    except:
        return {"category": "unknown", "keyword": ""}

# MAIN
urls = fetch_sitemap(5)
results = []

for i, url in enumerate(urls, 1):
    print(f"[{i}/5] {url}")
    title, h1, text, status = get_page_data(url)
    cat = categorize(url, title, h1, text)
    
    results.append({
        'url': url,
        'title': title,
        'status': status,
        'category': cat.get('category', 'unknown'),
        'keyword': cat.get('keyword', '')
    })

df = pd.DataFrame(results)
df.to_csv('phase1_results.csv', index=False)

print(f"\n✅ Phase 1 COMPLETE! {len(results)} pages")
print("📥 Download: phase1_results.csv")
