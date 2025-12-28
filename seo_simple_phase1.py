#!/usr/bin/env python3
import requests
import re
import json
import pandas as pd
from bs4 import BeautifulSoup
import google.generativeai as genai

print("🚀 Phase 1 - SIMPLIFIED")

genai.configure(api_key=os.environ['GEMINI_API_KEY'])
model = genai.GenerativeModel('gemini-pro')

# HARDCODE YOUR 3 PAGES (NO SITEMAP)
pages = [
    "https://www.westsiderealty.in/hyderabad/neopolis",
    "https://www.westsiderealty.in/landing/godrej-regal-pavilion-rajendra-nagar-hyderabad",
    "https://www.westsiderealty.in/hyderabad/kokapet"
]

results = []
for url in pages:
    print(f"Analyzing: {url}")
    
    # Fetch page
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.content, 'html.parser')
    
    title = soup.find('title')
    title = title.text.strip()[:60] if title else "No title"
    
    h1 = soup.find('h1')
    h1 = h1.text.strip()[:60] if h1 else "No H1"
    
    # Gemini categorize
    prompt = f"URL: {url}\nTitle: {title}\nH1: {h1}\n\nCategory? (project/micro-market/blog):"
    try:
        resp = model.generate_content(prompt)
        category = resp.text.strip()
    except:
        category = "unknown"
    
    results.append({
        'url': url,
        'title': title,
        'h1': h1,
        'category': category
    })

df = pd.DataFrame(results)
df.to_csv('phase1_results.csv', index=False)
print("✅ SAVED phase1_results.csv")
