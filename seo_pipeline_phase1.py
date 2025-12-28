#!/usr/bin/env python3
"""
Phase 1 – Sitemap → 50 URLs → Category + Primary Keyword + Purpose (via Gemini)

Output: seo_phase1_categorized.csv
"""

import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
import google.generativeai as genai

SITE_ROOT = "https://www.westsiderealty.in"
SITEMAP_URL = f"{SITE_ROOT}/sitemap.xml"

# ------------- Gemini setup -------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")


def fetch_sitemap_urls(limit=50):
    """Read sitemap.xml and return up to `limit` URLs."""
    print(f"📥 Fetching sitemap: {SITEMAP_URL}")
    resp = requests.get(SITEMAP_URL, timeout=20)
    resp.raise_for_status()
    xml = resp.text

    urls = re.findall(r"<loc>(.*?)</loc>", xml)
    urls = [u.strip() for u in urls if u.strip().startswith(SITE_ROOT)]
    urls = urls[:limit]
    print(f"✅ Found {len(urls)} URLs from sitemap")
    return urls


def fetch_page_preview(url, max_chars=2000):
    """Fetch HTML and return title, h1, and text preview."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        r = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(r.content, "html.parser")

        title_el = soup.find("title")
        title = title_el.text.strip() if title_el else ""

        h1_el = soup.find("h1")
        h1 = h1_el.text.strip() if h1_el else ""

        text = soup.get_text(" ", strip=True)[:max_chars]

        return {
            "status": r.status_code,
            "title": title,
            "h1": h1,
            "preview": text,
        }
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        return {"status": 0, "title": "", "h1": "", "preview": ""}


def categorize_with_gemini(url, page):
    """
    Ask Gemini to:
    - categorize page type
    - infer primary keyword
    - summarize page purpose
    """
    prompt = f"""
You are an SEO strategist for a real-estate website.

Analyze this page and return JSON only.

URL: {url}
TITLE: {page['title']}
H1: {page['h1']}
CONTENT PREVIEW:
{page['preview'][:800]}

TASKS:
1) Choose ONE category from:
   "homepage", "city-hub", "micro-market", "developer", "project",
   "listing", "blog", "contact", "other"

2) Infer the primary search keyword this page should rank for.
3) Describe the page purpose in 1 short sentence.

Return STRICT JSON (no commentary), like:
{{
  "category": "micro-market",
  "primary_keyword": "neopolis hyderabad apartments",
  "purpose": "Neopolis micro-market overview with projects and prices"
}}
"""
    try:
        resp = model.generate_content(prompt)
        text = resp.text.strip()
        # remove code fences if present
        if text.startswith("```
            text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
            text = re.sub(r"```
        data = pd.io.json.loads(text)
        return {
            "category": data.get("category", "other"),
            "primary_keyword": data.get("primary_keyword", "").strip(),
            "purpose": data.get("purpose", "").strip(),
        }
    except Exception as e:
        print(f"⚠️ Gemini parse error for {url}: {e}")
        return {
            "category": "other",
            "primary_keyword": "",
            "purpose": "",
        }


def run_phase1(limit=50):
    urls = fetch_sitemap_urls(limit=limit)

    rows = []
    for i, url in enumerate(urls, start=1):
        print(f"\n[{i}/{len(urls)}] Analyzing {url}")
        page = fetch_page_preview(url)
        cat = categorize_with_gemini(url, page)

        rows.append(
            {
                "url": url,
                "status_code": page["status"],
                "title": page["title"],
                "h1": page["h1"],
                "category": cat["category"],
                "primary_keyword": cat["primary_keyword"],
                "purpose": cat["purpose"],
            }
        )
        print(f"   → {cat['category']} | {cat['primary_keyword']}")

    df = pd.DataFrame(rows)
    df.to_csv("seo_phase1_categorized.csv", index=False)
    print("\n✅ Phase 1 complete → seo_phase1_categorized.csv created")


if __name__ == "__main__":
    run_phase1(limit=50)
