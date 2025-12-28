#!/usr/bin/env python3
"""
PHASE 3.1: Technical SEO Audit (Your exact prompt)
"""

import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import google.generativeai as genai

AUDIT_PROMPT = """Persona: Act as a Senior Technical SEO Architect specializing in high-competition real estate markets like Hyderabad.
Objective: Conduct a comprehensive On-Page and Technical SEO audit for: {url}
Benchmarking: Compare this page specifically against the current top-ranking competitors for "{keyword}" (e.g., Housing.com, MagicBricks, PropTiger).

Task List:
Technical Health: Core Web Vitals, mobile responsiveness, Real Estate Schema
On-Page Audit: Title, H1-H3, keyword density "Neopolis Hyderabad projects"
Competitive Gap Analysis: Information Gain opportunities (RERA, price graphs)
Local Authority: NAP consistency, Google Map embeds

Output Format EXACTLY:
Strengths: ...
Critical Weaknesses: ...
Fix List: |Priority|Task|Technical Requirement|
Verdict: ..."""

pages = [
    {"url": "https://www.westsiderealty.in/hyderabad/neopolis", "keyword": "Neopolis Hyderabad"},
    {"url": "https://www.westsiderealty.in/landing/godrej-regal-pavilion-rajendra-nagar-hyderabad", "keyword": "Godrej Regal Pavilion"},
    {"url": "https://www.westsiderealty.in/hyderabad/kokapet", "keyword": "Kokapet Hyderabad"}
]

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

results = []
for page in pages:
    print(f"Auditing {page['url']}")
    
    # Fetch page basics
    r = requests.get(page['url'], timeout=10)
    soup = BeautifulSoup(r.content, 'html.parser')
    title = soup.find('title')
    title = title.text.strip()[:100] if title else ""
    
    # Run YOUR exact audit prompt
    prompt = AUDIT_PROMPT.format(url=page['url'], keyword=page['keyword'])
    try:
        resp = model.generate_content(prompt)
        audit = resp.text
        results.append({
            'url': page['url'],
            'keyword': page['keyword'],
            'title': title,
            'audit_report': audit
        })
    except:
        results.append({'url': page['url'], 'keyword': page['keyword'], 'title': title, 'audit_report': 'Error'})

pd.DataFrame(results).to_csv('phase3_audits.csv', index=False)
print("✅ phase3_audits.csv ready!")
