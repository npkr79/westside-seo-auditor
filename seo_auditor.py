#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
from collections import Counter

print("🚀 Westside SEO Audit Starting...")

pages = [
    "https://www.westsiderealty.in/hyderabad/neopolis",
    "https://www.westsiderealty.in/landing/godrej-regal-pavilion-rajendra-nagar-hyderabad",
    "https://www.westsiderealty.in/hyderabad/kokapet"
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

results = []
for i, url in enumerate(pages, 1):
    print(f"Analyzing {i}/{len(pages)}: {url}")
    page_data = extract_seo_data(url)
    
    if page_
        title_len = len(page_data['title'])
        score = 50
        if 50 <= title_len <= 60: score += 15
        if page_data['h1'] != "No H1": score += 10
        if page_data['word_count'] > 1000: score += 15
        
        priority = "YES" if score < 80 else "NO"
        main_keyword = page_data['keywords'][0] if page_data['keywords'] else "project"
        
        prompt = f"Fix {page_data['url']}\nKeyword: {main_keyword}\nScore: {score}\nTitle: {title_len} chars"
        
        results.append({
            'url': page_data['url'],
            'title': page_data['title'],
            'score': score,
            'priority': priority,
            'word_count': page_data['word_count'],
            'prompt': prompt
        })

df = pd.DataFrame(results)
df.to_csv('priority_seo_fixes.csv', index=False)

print(f"\n✅ SUCCESS! {len(results)} pages analyzed")
print("📊 priority_seo_fixes.csv ready for download!")
