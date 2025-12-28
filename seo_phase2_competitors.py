#!/usr/bin/env python3
"""
PHASE 2: Competitor Analysis + Gap Detection + Cursor Prompts
For your top 3 pages: Neopolis, Godrej, Kokapet
"""

import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import google.generativeai as genai

print("🚀 PHASE 2: COMPETITOR ANALYSIS + CURSOR PROMPTS")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

# YOUR TOP 3 PAGES
TOP_PAGES = [
    {
        "url": "https://www.westsiderealty.in/hyderabad/neopolis",
        "name": "Neopolis Micro-Market Hub",
        "expected_keyword": "neopolis hyderabad apartments"
    },
    {
        "url": "https://www.westsiderealty.in/landing/godrej-regal-pavilion-rajendra-nagar-hyderabad",
        "name": "Godrej Regal Pavilion Project",
        "expected_keyword": "godrej regal pavilion rajendra nagar"
    },
    {
        "url": "https://www.westsiderealty.in/hyderabad/kokapet",
        "name": "Kokapet Locality Hub", 
        "expected_keyword": "kokapet hyderabad apartments"
    }
]

def analyze_page(url):
    """Extract page SEO data"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        title = soup.find('title')
        title = title.text.strip()[:100] if title else ""
        
        h1 = soup.find('h1')
        h1 = h1.text.strip()[:100] if h1 else ""
        
        word_count = len(soup.get_text().split())
        schema = bool(soup.find('script', type='application/ld+json'))
        
        return {
            'title': title,
            'h1': h1,
            'word_count': word_count,
            'has_schema': schema,
            'status': r.status_code
        }
    except:
        return {'title': '', 'h1': '', 'word_count': 0, 'has_schema': False, 'status': 0}

def get_competitor_analysis(page_info):
    """Gemini: Find competitors + gaps + Cursor prompt"""
    prompt = f"""
REAL ESTATE SEO EXPERT:

PAGE: {page_info['name']}
URL: {page_info['url']}
Keyword: {page_info['expected_keyword']}
Your page: {page_info['page_data']['title'][:80]} | {page_info['page_data']['word_count']} words

TASK: Real estate SEO audit vs top competitors.

RETURN JSON ONLY:
{{
  "top_competitors": [
    {{"name": "SquareYards Neopolis", "url": "https://www.squareyards.com/new-projects-in-neopolis-hyderabad"}},
    {{"name": "Magicbricks Neopolis", "url": "https://www.magicbricks.com/neopolis-hyderabad"}},
    {{"name": "99acres Neopolis", "url": "https://www.99acres.com/neopolis-hyderabad"}}
  ],
  "strengths": ["Perfect title length", "Good H1 keyword"],
  "gaps": ["Missing FAQ schema", "Add price comparison table", "3 H2 locality sections missing"],
  "cursor_prompt": "COMPLETE 300-word Cursor AI prompt to fix this page..."
}}

Real estate priorities:
1. RealEstateListing schema
2. FAQPage JSON-LD (8+ questions)
3. Price tables (₹/sqft, payment plans)
4. Locality connectivity H2s
5. Internal links to related projects
"""
    
    try:
        response = model.generate_content(prompt)
        # Clean JSON response
        text = response.text.strip()
        text = re.sub(r'``````', '', text).strip()
        data = json.loads(text)
        return data
    except Exception as e:
        print(f"Gemini error: {e}")
        return {
            "top_competitors": [],
            "strengths": [],
            "gaps": ["analysis failed"],
            "cursor_prompt": "Manual review needed"
        }

# MAIN ANALYSIS
results = []
for page_info in TOP_PAGES:
    print(f"\n🔍 Analyzing: {page_info['name']}")
    
    # Get your page data
    page_data = analyze_page(page_info['url'])
    print(f"   Your page: {page_data['title'][:50]} | {page_data['word_count']} words")
    
    # Gemini competitor analysis
    analysis = get_competitor_analysis({
        'name': page_info['name'],
        'url': page_info['url'],
        'expected_keyword': page_info['expected_keyword'],
        'page_data': page_data
    })
    
    results.append({
        'page': page_info['name'],
        'url': page_info['url'],
        'your_title': page_data['title'],
        'your_words': page_data['word_count'],
        'competitors': '; '.join([c.get('name', '') for c in analysis.get('top_competitors', [])]),
        'strengths': '; '.join(analysis.get('strengths', [])),
        'gaps': '; '.join(analysis.get('gaps', [])),
        'cursor_prompt': analysis.get('cursor_prompt', '')[:800]
    })
    
    print(f"   Competitors: {analysis.get('top_competitors', [{}])[0].get('name', 'None')}")
    print(f"   Gaps: {analysis.get('gaps', [])}")

# SAVE RESULTS
df = pd.DataFrame(results)
df.to_csv('phase2_competitor_analysis.csv', index=False)

# PRIORITY PROMPTS ONLY
priority_df = df[df['gaps'].str.contains('missing|add|improve', case=False, na=False)]
priority_df.to_csv('phase2_cursor_prompts.csv', index=False)

print(f"\n🎉 PHASE 2 COMPLETE!")
print(f"📊 Full analysis: phase2_competitor_analysis.csv")
print(f"🔥 Cursor prompts: phase2_cursor_prompts.csv ({len(priority_df)} pages)")
