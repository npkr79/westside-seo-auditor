#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from collections import Counter
from urllib.parse import urlparse

print("🚀 Westside SEO Audit - PRODUCTION READY")

pages = [
    "https://www.westsiderealty.in/",
    "https://www.westsiderealty.in/hyderabad",
    "https://www.westsiderealty.in/goa",
    "https://www.westsiderealty.in/hyderabad/neopolis",
    "https://www.westsiderealty.in/landing/godrej-regal-pavilion-rajendra-nagar-hyderabad"
]

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
        keywords = keywords[:3]
        
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

results = []
for i, url in enumerate(pages, 1):
    print(f"[{i}/5] {url}")
    page_data = extract_seo_data(url)
    
    if page_
        title_len = len(page_data['title'])
        score = 50
        if 50 <= title_len <= 60: score += 15
        if page_data['h1'] != "No H1": score += 10
        if page_data['word_count'] > 1000: score += 15
        
        priority = "YES" if score < 80 else "NO"
        keyword = page_data['keywords'][0] if page_data['keywords'] else "project"
        
        results.append({
            'url': page_data['url'],
            'title': page_data['title'],
            'score': score,
            'priority': priority,
            'word_count': page_data['word_count'],
            'keyword': keyword,
            'prompt': f"Fix {page_data['url']} | Score: {score} | Keyword: {keyword}"
        })

df = pd.DataFrame(results)
df.to_csv('priority_seo_fixes.csv', index=False)

print(f"\n✅ SUCCESS! {len(results)} pages done")
print("📊 Download: priority_seo_fixes.csv")
