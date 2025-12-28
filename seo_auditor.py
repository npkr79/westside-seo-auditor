#!/usr/bin/env python3
"""
Westside SEO Auditor - Pure Python Analysis (NO AI Dependencies)
Analyzes 50 pages → Scores → Generates Cursor prompts → CSV output
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime
import re
from collections import Counter
from urllib.parse import urlparse

class WestsideSEOAuditor:
    def __init__(self):
        self.site_url = "https://www.westsiderealty.in"
        self.competitors = self.load_competitors()
    
    def load_competitors(self):
        """Load manual competitors from competitors.txt"""
        competitors = {
            'godrej regal pavilion': 'https://www.godrejsregalpavilion.com',
            'neopolis': 'https://www.squareyards.com/new-projects-in-neopolis-hyderabad',
            'kokapet': 'https://www.99acres.com/kokapet-hyderabad-overview-piffid',
            'rajendra nagar': 'https://www.magicbricks.com/rajendra-nagar-hyderabad',
            'financial district': 'https://www.99acres.com/financial-district-gachibowli-hyderabad-overview-piffid',
            'gachibowli': 'https://www.magicbricks.com/gachibowli-hyderabad',
        }
        try:
            with open('competitors.txt', 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line:
                        url, keywords = line.split('=', 1)
                        competitors[keywords.strip().lower()] = url.strip()
        except:
            pass
        print(f"✅ Loaded {len(competitors)} competitors")
        return competitors
    
    def load_pages(self):
        """Load pages from top_50_pages.txt"""
        pages = []
        try:
            with open('top_50_pages.txt', 'r') as f:
                for line in f:
                    url = line.strip()
                    if url.startswith('http'):
                        pages.append(url)
        except:
            pages = [
                "https://www.westsiderealty.in/hyderabad/neopolis",
                "https://www.westsiderealty.in/landing/godrej-regal-pavilion-rajendra-nagar-hyderabad",
                "https://www.westsiderealty.in/hyderabad/kokapet"
            ]
        print(f"✅ Loaded {len(pages)} pages")
        return pages[:20]  # Limit to 20 for speed
    
    def extract_seo_data(self, url):
        """Extract SEO metrics from page"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = soup.find('title')
            title = title.text.strip()[:60] if title else ""
            
            meta_desc = soup.find('meta', {'name': 'description'})
            meta_desc = meta_desc['content'][:160] if meta_desc else ""
            
            h1 = soup.find('h1')
            h1 = h1.text.strip()[:80] if h1 else ""
            
            text = re.sub(r'\s+', ' ', soup.get_text())
            word_count = len(text.split())
            
            keywords = self.extract_keywords(title + " " + meta_desc + " " + h1)
            
            schema_types = []
            scripts = soup.find_all('script', {'type': 'application/ld+json'})
            for script in scripts:
                try:
                    data = script.string
                    if data and '"@type"' in 
                        schema_types.append('Schema Found')
                except:
                    pass
            
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
        except:
            return None
    
    def extract_keywords(self, text, max_keywords=3):
        """Extract main keywords"""
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        stop_words = {'the', 'and', 'for', 'with', 'are', 'this', 'from', 'that', 'hyderabad'}
        words = [w for w in words if w not in stop_words and len(w) > 2]
        return [word for word, _ in Counter(words).most_common(max_keywords)]
    
    def find_competitor(self, main_keyword):
        """Match competitor from list"""
        keyword_lower = main_keyword.lower()
        for comp_keywords, comp_url in self.competitors.items():
            if comp_keywords in keyword_lower:
                return comp_url
        return None
    
    def calculate_seo_score(self, page_data):
        """Calculate SEO score 0-100"""
        score = 50
        
        # Title
        title_len = len(page_data['title'])
        if 50 <= title_len <= 60:
            score += 15
        elif 40 <= title_len <= 70:
            score += 10
        
        # H1
        if page_data['h1']:
            score += 10
        
        # Content
        if page_data['word_count'] > 1500:
            score += 15
        elif page_data['word_count'] > 800:
            score += 10
        
        # Schema
        if page_data['schema_types']:
            score += 10
        
        return min(score, 100)
    
    def generate_cursor_prompt(self, page_data):
        """Generate Cursor AI prompt"""
        main_keyword = page_data['keywords'][0] if page_data['keywords'] else "project"
        score = self.calculate_seo_score(page_data)
        
        gaps = []
        title_len = len(page_data['title'])
        if title_len > 60:
            gaps.append("Title too long - shorten to 55-60 chars")
        if title_len < 40:
            gaps.append("Title too short - expand to 55-60 chars")
        if page_data['word_count'] < 1000:
            gaps.append("Add 2-3 H2 sections: locality guide, price trends, FAQs")
        if not page_data['schema_types']:
            gaps.append("Add RealEstateListing + FAQPage JSON-LD")
        
        prompt = f"""Fix SEO for: {page_data['url']}
KEYWORD: "{main_keyword}"

METRICS:
• Title: "{page_data['title']}" ({title_len} chars)
• Words: {page_data['word_count']}
• Score: {score}/100

FIX:
"""
        for gap in gaps:
            prompt += f"• {gap}\n"
        
        prompt += """
RULES:
• Keep ALL Tailwind, hero, CTAs unchanged
• Title/H1: 55-60 chars with keyword first
• Add schema JSON-LD
• 2 new H2 sections (400+ words)
• Internal links: /hyderabad, /hyderabad/[locality]

Return: Complete updated page code."""
        
        return prompt
    
    def run_full_audit(self):
        """Run complete audit"""
        print("🚀 Westside SEO Audit Starting...")
        pages = self.load_pages()
        results = []
        
        for i, url in enumerate(pages):
            print(f"[{i+1}/{len(pages)}] {url}")
            page_data = self.extract_seo_data(url)
            
            if not page_
                continue
            
            main_keyword = page_data['keywords'][0] if page_data['keywords'] else ""
            if not main_keyword:
                continue
            
            competitor = self.find_competitor(main_keyword)
            score = self.calculate_seo_score(page_data)
            priority = score < 80
            
            cursor_prompt = self.generate_cursor_prompt(page_data)
            
            results.append({
                'url': url,
                'keyword': main_keyword,
                'competitor': competitor or '',
                'score': score,
                'title': page_data['title'],
                'word_count': page_data['word_count'],
                'priority': 'YES' if priority else 'NO',
                'cursor_prompt': cursor_prompt[:500] + '...'
            })
        
        # Save results
        df = pd.DataFrame(results)
        df.to_csv('priority_seo_fixes.csv', index=False)
        
        priority_df = df[df['priority'] == 'YES'].head(10)
        priority_df.to_csv('priority_seo_fixes_top10.csv', index=False)
        
        print(f"\n✅ COMPLETE! {len(results)} pages analyzed")
        print(f"📊 {len(priority_df)} priority fixes → priority_seo_fixes.csv")
        print("⬇️  Download from Actions tab!")

if __name__ == "__main__":
    auditor = WestsideSEOAuditor()
    auditor.run_full_audit()
