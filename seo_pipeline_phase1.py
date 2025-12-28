#!/usr/bin/env python3
"""
AI SEO Pipeline - PHASE 1+2 COMPLETE
1. Sitemap → Categorize → Keywords
2. Gemini finds competitors → Gap analysis → Cursor prompts
NO SERPAPI NEEDED!
"""

import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
import google.generativeai as genai

SITE_ROOT = "https://www.westsiderealty.in"
SITEMAP_URL = f"{SITE_ROOT}/sitemap.xml"

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

def fetch_sitemap_urls(limit=10):
    """Get first N URLs from sitemap"""
    resp = requests.get(SITEMAP_URL, timeout=20)
    urls = re.findall(r"<loc>(.*?)</loc>", resp.text)
    urls = [u.strip() for u in urls if u.strip().startswith(SITE_ROOT)][:limit]
    print(f"✅ {len(urls)} URLs from sitemap")
    return urls

def fetch_page_preview(url):
    """Get page data for analysis"""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.content, "html.parser")
        
        title = soup.find("title")
        title = title.text.strip()[:100] if title else ""
        
        h1 = soup.find("h1")
        h1 = h1.text.strip()[:100] if h1 else ""
        
        text = soup.get_text(" ", strip=True)[:1500]
        
        return {
            "status": r.status_code,
            "title": title,
            "h1": h1,
            "preview": text,
        }
    except:
        return {"status": 0, "title": "", "h1": "", "preview": ""}

def analyze_page(url, page_data):
    """Gemini: Categorize + Keywords + Competitors + Gaps"""
    prompt = f"""
REAL ESTATE SEO EXPERT MODE:

URL: {url}
Title: {page_data['title']}
H1: {page_data['h1']}
Content: {page_data['preview'][:1000]}

ANALYZE & RETURN JSON ONLY:

{{
  "category": "micro-market|project|listing|city-hub|blog|homepage|contact",
  "primary_keyword": "main search term this page targets",
  "competitors": ["top competitor 1 URL", "top competitor 2 URL", "top competitor 3 URL"],
  "strengths": ["what this page does well"],
  "gaps": ["title too long", "missing FAQ schema", "add H2 sections"],
  "cursor_prompt": "DETAILED 200-word prompt to fix this page in Cursor AI"
}}

Real estate examples:
- Neopolis → category: "micro-market", keyword: "neopolis hyderabad apartments"
- Godrej project → category: "project", keyword: "godrej regal pavilion price"
"""
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Clean JSON
        text = re.sub(r"^```
        text = re.sub(r"\s*```$", "", text, flags=re.DOTALL)
        data = json.loads(text)
        return data
    except Exception as e:
        print(f"❌ Gemini error: {e}")
        return {
            "category": "unknown",
            "primary_keyword": "",
            "competitors": [],
            "strengths": [],
            "gaps": ["analysis failed"],
            "cursor_prompt": "Error - manual review needed"
        }

def main():
    print("🚀 PHASE 1+2: Sitemap → AI Analysis → Cursor Prompts")
    
    urls = fetch_sitemap_urls(limit=5)  # Start small
    results = []
    
    for i, url in enumerate(urls, 1):
        print(f"\n🔍 [{i}/5] {url}")
        
        page_data = fetch_page_preview(url)
        analysis = analyze_page(url, page_data)
        
        results.append({
            "url": url,
            "status": page_data["status"],
            "title": page_data["title"][:50],
            "category": analysis.get("category", "unknown"),
            "keyword": analysis.get("primary_keyword", ""),
            "competitors": "; ".join(analysis.get("competitors", [])),
            "strengths": "; ".join(analysis.get("strengths", [])),
            "gaps": "; ".join(analysis.get("gaps", [])),
            "cursor_prompt": analysis.get("cursor_prompt", "")[:500] + "..."
        })
        
        print(f"   Category: {analysis.get('category')}")
        print(f"   Keyword: {analysis.get('primary_keyword')}")
        print(f"   Top competitor: {analysis.get('competitors', [''])[0] if analysis.get('competitors') else 'None'}")
    
    # SAVE MASTER RESULTS
    df = pd.DataFrame(results)
    df.to_csv("seo_full_analysis.csv", index=False)
    
    # PRIORITY FIXES ONLY
    priority_df = df[df['gaps'].str.contains("missing|short|add|improve", case=False, na=False)]
    priority_df.to_csv("seo_priority_fixes.csv", index=False)
    
    print(f"\n🎉 ANALYSIS COMPLETE!")
    print(f"📊 Total: {len(results)} pages")
    print(f"🔥 Priority fixes: {len(priority_df)} pages")
    print("⬇️ Download: seo_full_analysis.csv + seo_priority_fixes.csv")

if __name__ == "__main__":
    main()
