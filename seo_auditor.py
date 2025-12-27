#!/usr/bin/env python3
"""
RE/MAX Westside Realty AI SEO Auditor
Crawls 500+ pages → finds competitors → generates Cursor prompts
"""

import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from serpapi import GoogleSearch
from openai import OpenAI
import os
from datetime import datetime
import re
from urllib.parse import urljoin, urlparse
import sqlite3
from pathlib import Path

class WestsideSEOAuditor:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        self.site_url = "https://www.westsiderealty.in"
        self.db_path = "seo_audit.db"
        self.init_db()
    
    def init_db(self):
        """Initialize SQLite for audit history"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audits (
                id INTEGER PRIMARY KEY,
                date TEXT,
                page_url TEXT,
                main_keyword TEXT,
                competitor_url TEXT,
                rank_score INTEGER,
                issues TEXT,
                cursor_prompt TEXT,
                status TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def crawl_site(self, max_pages=50):
        """Crawl top pages from sitemap or GSC"""
        sitemap_url = f"{self.site_url}/sitemap.xml"
        response = requests.get(sitemap_url)
        soup = BeautifulSoup(response.content, 'xml')
        
        urls = []
        for url_tag in soup.find_all('loc')[:max_pages]:
            urls.append(url_tag.text)
        
        pages_data = []
        for url in urls:
            try:
                page_data = self.extract_seo_data(url)
                pages_data.append(page_data)
            except:
                continue
        
        return pd.DataFrame(pages_data)
    
    def extract_seo_data(self, url):
        """Extract all SEO signals from a page"""
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Core SEO elements
        title = soup.find('title')
        title = title.text.strip() if title else ""
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_desc = meta_desc['content'] if meta_desc else ""
        
        h1 = soup.find('h1')
        h1 = h1.text.strip() if h1 else ""
        
        # Schema detection
        schema = {}
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                schema.update(data)
            except:
                pass
        
        # Keyword extraction (title + meta + h1)
        keywords = self.extract_keywords(title + " " + meta_desc + " " + h1)
        
        # Content metrics
        word_count = len(soup.get_text().split())
        headings = [h.text.strip() for h in soup.find_all(['h1','h2','h3'])]
        
        return {
            'url': url,
            'title': title,
            'meta_desc': meta_desc,
            'h1': h1,
            'word_count': word_count,
            'headings': headings,
            'keywords': keywords,
            'schema': schema,
            'status_code': response.status_code
        }
    
    def extract_keywords(self, text, max_keywords=5):
        """Extract primary keywords using simple TF-IDF"""
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        common_words = {'the', 'and', 'for', 'with', 'are', 'this', 'from', 'that'}
        words = [w for w in words if w not in common_words and len(w) > 3]
        
        from collections import Counter
        return [word for word, count in Counter(words).most_common(max_keywords)]
    
    def find_competitor(self, url, main_keyword):
        """Find #1 competitor for this page's main keyword"""
        params = {
            "q": main_keyword,
            "location": "India",
            "hl": "en",
            "gl": "in",
            "num": 1,
            "api_key": self.serpapi_key
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if 'organic_results' in results:
            competitor = results['organic_results'][0]
            return competitor.get('link', '')
        
        return None
    
    def analyze_competitor_gap(self, your_page, competitor_url):
        """Deep analysis of competitor vs your page"""
        if not competitor_url:
            return "No competitor found"
        
        try:
            comp_response = requests.get(competitor_url)
            comp_soup = BeautifulSoup(comp_response.content, 'html.parser')
            
            your_score = self.calculate_seo_score(your_page)
            comp_score = self.calculate_seo_score({
                'url': competitor_url,
                'title': comp_soup.find('title').text if comp_soup.find('title') else '',
                'meta_desc': '',
                'h1': comp_soup.find('h1').text if comp_soup.find('h1') else '',
                'word_count': len(comp_soup.get_text().split()),
                'headings': [],
                'schema': {}
            })
            
            gaps = self.identify_gaps(your_page, comp_soup)
            return {
                'your_score': your_score,
                'comp_score': comp_score,
                'gaps': gaps
            }
        except:
            return "Competitor analysis failed"
    
    def calculate_seo_score(self, page_data):
        """Simple SEO scoring (0-100)"""
        score = 0
        
        # Title quality
        if 30 <= len(page_data['title']) <= 60:
            score += 20
        
        # H1 presence
        if page_data['h1']:
            score += 15
            
        # Content length
        if page_data['word_count'] > 1000:
            score += 25
        elif page_data['word_count'] > 500:
            score += 15
            
        # Keywords in title
        if page_data['keywords']:
            score += 20
            
        # Schema presence
        if page_data['schema']:
            score += 20
            
        return min(score, 100)
    
    def identify_gaps(self, your_page, comp_soup):
        """Identify specific optimization opportunities"""
        gaps = []
        
        # Title length gap
        if len(your_page['title']) > 60:
            gaps.append("Title too long - shorten to 55-60 chars")
        
        # Missing schema types
        your_schema_types = set()
        if your_page['schema']:
            if isinstance(your_page['schema'], list):
                for item in your_page['schema']:
                    your_schema_types.add(item.get('@type', ''))
            else:
                your_schema_types.add(your_page['schema'].get('@type', ''))
        
        comp_schema_types = set()
        comp_scripts = comp_soup.find_all('script', type='application/ld+json')
        for script in comp_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    for item in 
                        comp_schema_types.add(item.get('@type', ''))
                else:
                    comp_schema_types.add(data.get('@type', ''))
            except:
                pass
        
        missing_schemas = comp_schema_types - your_schema_types
        if missing_schemas:
            gaps.append(f"Add schema: {', '.join(list(missing_schemas)[:2])}")
        
        # Content length gap
        if your_page['word_count'] < 1500 and len(comp_soup.get_text().split()) > 2000:
            gaps.append("Add locality sections (Rajendra Nagar, Gaganpahad, etc.)")
        
        return gaps
    
    def generate_cursor_prompt(self, page_data, analysis):
        """Generate production-ready Cursor prompt"""
        gaps = analysis.get('gaps', [])
        main_keyword = page_data['keywords'][0] if page_data['keywords'] else "project name"
        
        prompt = f"""You are fixing SEO for: {page_data['url']}
Main keyword: "{main_keyword}"

TOP COMPETITOR GAPS TO FIX:
"""
        
        for gap in gaps:
            prompt += f"- {gap}\n"
        
        prompt += f"""
CURRENT METRICS:
- Title: "{page_data['title'][:60]}..."
- H1: "{page_data['h1'][:60]}..."
- Words: {page_data['word_count']}
- Score: {analysis.get('your_score', 0)}/100

IMPLEMENTATION RULES:
- Keep ALL existing Tailwind classes, hero, CTAs, conversion elements
- Fix title/H1 to 55-60 chars with exact keyword match
- Add missing schema types in JSON-LD
- Expand content with 2-3 H2 sections (500+ words total)
- Add internal links: /hyderabad, /hyderabad/[locality]
- Maintain luxury design styling

Deliver: Complete updated page code, production-ready."""
        
        return prompt
    
    def run_full_audit(self):
        """Run complete daily audit"""
        print("🚀 Starting Westside Realty SEO Audit...")
        
        # 1. Crawl your pages
        pages_df = self.crawl_site(max_pages=50)
        print(f"✅ Crawled {len(pages_df)} pages")
        
        audit_results = []
        
        for _, page in pages_df.iterrows():
            main_keyword = page['keywords'][0] if page['keywords'] else ""
            
            if not main_keyword:
                continue
            
            # 2. Find competitor
            competitor = self.find_competitor(page['url'], main_keyword)
            print(f"🔍 {page['url']} → Competitor: {competitor}")
            
            # 3. Analyze gaps
            analysis = self.analyze_competitor_gap(page, competitor)
            
            # 4. Generate Cursor prompt
            cursor_prompt = self.generate_cursor_prompt(page, analysis)
            
            audit_results.append({
                'url': page['url'],
                'keyword': main_keyword,
                'competitor': competitor,
                'analysis': analysis,
                'cursor_prompt': cursor_prompt,
                'priority': analysis.get('your_score', 0) < 70  # Fix low scorers first
            })
        
        # 5. Save results
        df_results = pd.DataFrame(audit_results)
        df_results.to_json(f"seo_audit_{datetime.now().strftime('%Y%m%d')}.json", orient='records')
        
        # 6. Save top 10 priority fixes
        priority_fixes = df_results[df_results['priority'] == True].head(10)
        priority_fixes[['url', 'keyword', 'cursor_prompt']].to_csv('priority_seo_fixes.csv')
        
        print(f"✅ Audit complete! {len(priority_fixes)} priority pages ready for Cursor")
        print("\n📋 Next steps:")
        print("1. Review priority_seo_fixes.csv")
        print("2. Copy/paste Cursor prompts to fix top pages")
        print("3. Deploy via Vercel → re-run tomorrow")
        
        return priority_fixes

if __name__ == "__main__":
    auditor = WestsideSEOAuditor()
    auditor.run_full_audit()
