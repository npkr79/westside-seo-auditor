#!/usr/bin/env python3
"""
PHASE 3 FULL SITEMAP - FIXED IMPORTS
"""

import os  # ← FIXED #1
import requests
from bs4 import BeautifulSoup  # ← FIXED #2
import pandas as pd
import re
import time

print("🚀 PHASE 3 FULL - SITEMAP PROCESSING")

SITEMAP_URL = "https://www.westsiderealty.in/sitemap.xml"

def get_all_urls():
    """Parse sitemap → ALL your pages"""
    print("📡 Fetching sitemap...")
    r = requests.get(SITEMAP_URL, timeout=15)
    soup = BeautifulSoup(r.content, 'xml')
    
    urls = [loc.text for loc in soup.find_all('loc') if 'westsiderealty.in' in loc.text]
    
    # Filter real estate pages
    priority_patterns = [
        '/hyderabad/', '/landing/', '/properties/', '/godrej', '/neopolis', 
        '/kokapet', '/financial-district', '/gachibowli'
    ]
    
    priority_urls = []
    for url in urls:
        if any(pattern in url.lower() for pattern in priority_patterns):
            priority_urls.append(url)
    
    print(f"✅ Found {len(urls)} total | {len(priority_urls)} priority pages")
    return priority_urls[:100]  # Limit to avoid timeout

def smart_auto_audit(url):
    """Smart audit for each page"""
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.content, 'html.parser')
        title = soup.find('title')
        title = title.text.strip()[:100] if title else ""
        text = soup.get_text()
        word_count = len(text.split())
        
        keyword = url.split('/')[-1].replace('-', ' ').title()
        if '/hyderabad/' in url:
            keyword = url.split('/hyderabad/')[-1].split('/')[0].replace('-', ' ').title()
        
        if word_count > 3000:
            verdict = "Page is already optimized"
            needs_fix = "NO"
        elif word_count > 1500:
            verdict = "Strong foundation - add schema"
            needs_fix = "MEDIUM"
        else:
            verdict = "Major optimization needed"
            needs_fix = "HIGH"
        
        return {
            'url': url,
            'keyword': keyword,
            'title': title,
            'word_count': word_count,
            'verdict': verdict,
            'needs_fix': needs_fix,
            'audit_report': f"Title: {title}; Words: {word_count}; Verdict: {verdict}"
        }
    except Exception as e:
        return {'url': url, 'keyword': 'ERROR', 'title': str(e), 'word_count': 0, 'verdict': 'Error', 'needs_fix': 'ERROR'}

# MAIN
print("🔍 Analyzing sitemap pages...")
all_pages = get_all_urls()
results = []

for i, url in enumerate(all_pages, 1):
    print(f"[{i}/{len(all_pages)}] {url.split('/')[-1]}")
    result = smart_auto_audit(url)
    results.append(result)
    time.sleep(0.5)

df = pd.DataFrame(results)
df.to_csv('phase3_full_sitemap.csv', index=False)

high_priority = df[df['needs_fix'] == 'HIGH'].head(10)
medium_priority = df[df['needs_fix'] == 'MEDIUM'].head(10)
no_action = df[df['needs_fix'] == 'NO']

high_priority.to_csv('phase3_high_priority.csv', index=False)
medium_priority.to_csv('phase3_medium_priority.csv', index=False)
no_action.to_csv('phase3_no_action.csv', index=False)

print(f"\n🎉 COMPLETE! {len(df)} pages → phase3_full_sitemap.csv")
