#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import pandas as pd
import google.generativeai as genai
import os
import re

print("🚀 Phase 1 FINAL - WORKING!")

# HARDCODE 3 PAGES - NO SITEMAP PROBLEMS
pages = [
    "https://www.westsiderealty.in/hyderabad/neopolis",
    "https://www.westsiderealty.in/landing/godrej-regal-pavilion-rajendra-nagar-hyderabad",
    "https://www.westsiderealty.in/hyderabad/kokapet"
]

# GEMINI SETUP - CORRECT WAY
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ NO GEMINI_API_KEY - using dummy data")
    genai.configure(api_key="dummy")
else:
    genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')

results = []
for i, url in enumerate(pages, 1):
    print(f"[{i}/3] {url}")
    
    # GET PAGE DATA
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.content, 'html.parser')
        title = soup.find('title')
        title = title.text.strip()[:60] if title else "No title"
        h1 = soup.find('h1')
        h1 = h1.text.strip()[:60] if h1 else "No H1"
        
        # GEMINI CATEGORY (SIMPLE)
        if api_key:
            prompt = f"Classify: {title} | {h1[:100]}\nOptions: project, micro-market, city-hub"
            try:
                resp = model.generate_content(prompt)
                category = resp.text.strip()
            except:
                category = "unknown"
        else:
            category = "no-gemini-key"
        
        results.append({
            'url': url,
            'title': title,
            'h1': h1,
            'category': category,
            'status': r.status_code
        })
        print(f"   ✅ {title[:40]}... | {category}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append({'url': url, 'title': 'ERROR', 'h1': str(e), 'category': 'error', 'status': 0})

# SAVE
df = pd.DataFrame(results)
df.to_csv('phase1_results.csv', index=False)
print(f"\n✅ SUCCESS! {len(results)} pages analyzed")
print("📊 phase1_results.csv ready!")
