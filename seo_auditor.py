#!/usr/bin/env python3
"""
Westside SEO Auditor - Manual Competitors + Google Gemini
Reads competitors.txt → Analyzes 50 pages → Emails Cursor prompts
"""

import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from google.generativeai import GenerativeModel
import os
from datetime import datetime
import re
from urllib.parse import urljoin
import sqlite3

class WestsideSEOAuditor:
    def __init__(self):
        self.client = GenerativeModel('gemini-pro', api_key=os.getenv("GEMINI_API_KEY"))
        self.site_url = "https://www.westsiderealty.in"
        self.db_path = "seo_audit.db"
        self.competitors = self.load_competitors()
        self.init_db()
    
    def load_competitors(self):
        """Load manual competitors from competitors.txt"""
        competitors = {}
        try:
            with open('competitors.txt', 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and line:
                        url, keywords = line.split('=', 1)
                        competitors[keywords.strip().lower()] = url.strip()
        except FileNotFoundError:
            print("⚠️  competitors.txt not found - using defaults")
            competitors = {
                'godrej regal pavilion': 'https://www.godrejsregalpavilion.com',
                'neopolis': 'https://www.squareyards.com/new-projects-in-neopolis-hyderabad',
                'kokapet': 'https://www.99acres.com/kokapet-hyderabad-overview-piffid',
            }
        print(f"✅ Loaded {len(competitors)} competitors from competitors.txt")
        return competitors
    
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
    
    def load_pages(self):
        """Load top 50 pages from top_50_pages.txt"""
        pages = []
        try:
            with open('top_50_pages.txt', 'r') as f:
                for line in f:
                    url = line.strip()
                    if url and url.startswith('http'):
                        pages.append(url)
        except FileNotFoundError:
            print("⚠️  top_50_pages.txt not found - using sample")
            pages = [
                "https://www.westsiderealty.in/hyderabad/neopolis",
                "https://www.westsiderealty.in/landing/godrej-regal-pavilion-rajendra-nagar-hyderabad",
                "https://www.westsiderealty.in/hyderabad/kokapet"
            ]
        print(f"✅ Loaded {len(pages)} pages from top_50_pages.txt")
        return pages
    
    def extract_seo_data(self, url):
        """Extract all SEO signals from a page"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Core SEO elements
            title = soup.find('title')
            title = title.text.strip()[:60] if title else ""
            
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            meta_desc = meta_desc['content'][:160] if meta_desc else ""
            
            h1 = soup.find('h1')
            h1 = h1.text.strip()[:80] if h1 else ""
            
            # Schema detection
            schema_types = []
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string or '{}')
                    if isinstance(data, dict):
                        schema_types.append(data.get('@type', 'Unknown'))
                    elif isinstance(data, list):
                        for item in 
                            schema_types.append(item.get('@type', 'Unknown'))
                except:
                    pass
            
            # Keyword extraction
            keywords = self.extract_keywords(title + " " + meta_desc + " " + h1)
            
            # Content metrics
            text = re.sub(r'\s+', ' ', soup.get_text())
            word_count = len(text.split())
            
            return {
                'url': url,
                'title': title,
                'meta_desc': meta_desc,
                'h1': h1,
                'word_count': word_count,
                'keywords': keywords,
                'schema_types': schema_types,
                'status_code': response.status_code
            }
        except Exception as e:
            print(f"❌ Error crawling {url}: {e}")
            return None
    
    def extract_keywords(self, text, max_keywords=3):
        """Extract primary keywords"""
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        common_words = {'the', 'and', 'for', 'with', 'are', 'this', 'from', 'that', 'hyderabad'}
        words = [w for w in words if w not in common_words and len(w) > 2]
        
        from collections import Counter
        return [word for word, count in Counter(words).most_common(max_keywords)]
    
    def find_competitor(self, url, main_keyword):
        """Find competitor from manual list"""
        keyword_lower = main_keyword.lower()
        for comp_keywords, comp_url in self.competitors.items():
            if comp_keywords in keyword_lower:
                print(f"   🥇 Matched: {comp_url}")
                return comp_url
        print(f"   ⚠️  No competitor match for '{main_keyword}'")
        return None
    
    def calculate_seo_score(self, page_data):
        """SEO score 0-100"""
        score = 50  # Base score
        
        # Title quality
        title_len = len(page_data['title'])
        if 50 <= title_len <= 60:
            score += 15
        elif 30 <= title_len <= 70:
            score += 10
            
        # H1 presence & quality
        if page_data['h1']:
            score += 10
            
        # Content length
        if page_data['word_count'] > 1500:
            score += 15
        elif page_data['word_count'] > 800:
            score += 10
            
        # Schema
        if page_data['schema_types']:
            score += 10
            
        return min(score, 100)
    
    def generate_cursor_prompt(self, page_data, competitor_url=None):
        """Generate production-ready Cursor prompt"""
        main_keyword = page_data['keywords'][0] if page_data['keywords'] else "project"
        score = self.calculate_seo_score(page_data)
        
        gaps = []
        if len(page_data['title']) > 60:
            gaps.append("Title too long - shorten to 55-60 chars")
        if len(page_data['title']) < 40:
            gaps.append("Title too short - expand to 55-60 chars with main keyword")
        if page_data['word_count'] < 1000:
            gaps.append("Add 2-3 H2 sections (Rajendra Nagar, project updates, FAQs)")
        if not page_data['schema_types']:
            gaps.append("Add RealEstateListing + FAQPage JSON-LD schema")
        
        prompt = f"""You are an expert SEO + Next.js developer optimizing: {page_data['url']}
MAIN KEYWORD: "{main_keyword}"

CURRENT SEO METRICS:
• Title: "{page_data['title']}" ({len(page_data['title'])} chars)
• H1: "{page_data['h1'][:60]}..."
• Words: {page_data['word_count']}
• Schema: {', '.join(page_data['schema_types'][:2]) or 'None'}
• Score: {score}/100

TOP PRIORITY FIXES:
"""
        
        for gap in gaps:
            prompt += f"• {gap}\n"
        
        if competitor_url:
            prompt += f"\n🥇 COMPETITOR ({competitor_url}): Has better {', '.join(gaps[:2])}\n"
        
        prompt += f"""
IMPLEMENTATION RULES:
• Keep ALL Tailwind classes, hero, CTAs, conversion elements unchanged
• Fix title/H1 to 55-60 chars: "{main_keyword.title()} Hyderabad – [Page Focus]"
• Add missing schema: RealEstateListing + FAQPage JSON-LD  
• Expand with 2 H2 sections: "Why [Location]" + "Latest Price Trends Q1 2026"
• Internal links: /hyderabad, /[micro-market]
• Add freshness: "Updated Dec 2025" near hero stats

Deliver: Complete updated page code, production-ready, drop-in replaceable."""
        
        return prompt
    
    def run_full_audit(self):
        """Run complete daily audit"""
        print("🚀 Starting Westside Realty SEO Audit...")
        print(f"📊 Competitors loaded: {len(self.competitors)}")
        
        pages = self.load_pages()
        audit_results = []
        
        for i, url in enumerate(pages[:20]):  # Limit to 20 for speed
            print(f"\n[{i+1}/20] Analyzing {url}")
            
            page_data = self.extract_seo_data(url)
            if not page_
                continue
            
            main_keyword = page_data['keywords'][0] if page_data['keywords'] else ""
            if not main_keyword:
                continue
            
            competitor = self.find_competitor(url, main_keyword)
            cursor_prompt = self.generate_cursor_prompt(page_data, competitor)
            
            score = self.calculate_seo_score(page_data)
            priority = score < 80  # Fix anything under 80
            
            audit_results.append({
                'url': url,
                'keyword': main_keyword,
                'competitor': competitor,
                'score': score,
                'title': page_data['title'],
                'word_count': page_data['word_count'],
                'priority': priority,
                'cursor_prompt': cursor_prompt[:1000]  # Truncate for CSV
            })
        
        # Save results
        df = pd.DataFrame(audit_results)
        df.to_csv('priority_seo_fixes.csv', index=False)
        
        # Priority fixes only
        priority_df = df[df['priority'] == True].head(10)
        priority_df[['url', 'keyword', 'score', 'cursor_prompt']].to_csv('priority_seo_fixes.csv', index=False)
        
        # Create HTML report
        html_content = f"""
        <h1>🚀 Westside SEO Audit - {datetime.now().strftime('%Y-%m-%d %H:%M IST')}</h1>
        <p><strong>Total pages:</strong> {len(audit_results)} | <strong>Priority fixes:</strong> {len(priority_df)}</p>
        <h2>🔥 TOP PRIORITY PAGES (Copy to Cursor)</h2>
        """
        
        for _, row in priority_df.iterrows():
            html_content += f"""
            <div style="border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 8px;">
                <h3><a href="{row['url']}" target="_blank">{row['url']}</a> <span style="color: orange;">Score: {row['score']}/100</span></h3>
                <p><strong>Keyword:</strong> {row['keyword']}</p>
                <details>
                    <summary>📋 Copy Cursor Prompt (Click)</summary>
                    <pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; font-size: 12px; white-space: pre-wrap;">{row['cursor_prompt']}</pre>
                </details>
            </div>
            """
        
        with open('priority_seo_fixes.html', 'w') as f:
            f.write(html_content)
        
        print(f"\n✅ Audit complete!")
        print(f"📧 {len(priority_df)} priority pages → priority_seo_fixes.csv + .html")
        print(f"📋 Check your email or download from GitHub Actions!")
        
        return priority_df

if __name__ == "__main__":
    auditor = WestsideSEOAuditor()
    auditor.run_full_audit()
