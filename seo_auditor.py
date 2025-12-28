#!/usr/bin/env python3
"""
Westside SEO Auditor - BULLETPROOF VERSION
No file dependencies - works instantly
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
from collections import Counter

class WestsideSEOAuditor:
    def __init__(self):
        self.pages = [
            "https://www.westsiderealty.in/hyderabad/neopolis",
            "https://www.westsiderealty.in/landing/godrej-regal-pavilion-rajendra-nagar-hyderabad",
            "https://www.westsiderealty.in/hyderabad/kokapet",
            "https://www.westsiderealty.in/hyderabad/financial-district",
            "https://www.westsiderealty.in/hyderabad/gachibowli"
        ]
        print(f"✅ Using {len(self.pages)} built-in pages")
    
    def extract_seo_data(self, url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = soup.find('title')
            title = title.text.strip()[:60] if title else "No title"
            
            h1 = soup.find('h1')
            h1 = h1.text.strip()[:80] if h1 else "No H1"
            
            text = re.sub(r'\s+', ' ', soup.get_text())
            word_count = len(text.split())
            
            keywords = self.extract_keywords(title + " " + h1)
            
            return {
                'url': url,
                'title': title,
                'h1': h1,
                'word_count': word_count,
                'keywords': keywords,
                'status_code': response.status_code
            }
        except Exception as e:
            print(f"❌ Error {url}: {e}")
            return None
    
    def extract_keywords(self, text, max_keywords=3):
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        stop_words = {'the', 'and', 'for', 'with', 'are', 'this', 'from', 'that'}
        words = [w for w in words if w not in stop_words]
        return [word for word, _ in Counter(words).most_common(max_keywords)]
    
    def calculate_seo_score(self, page_data):
        score = 50
        title_len = len(page_data['title'])
        if 50 <= title_len <= 60: score += 15
        elif 40 <= title_len <= 70: score += 10
        if page_data['h1'] != "No H1": score += 10
        if page_data['word_count'] > 1000: score += 15
        elif page_data['word_count'] > 500: score += 10
        return min(score, 100)
    
    def generate_cursor_prompt(self, page_data):
        main_keyword = page_data['keywords'][0] if page_data['keywords'] else "project"
        score = self.calculate_seo_score(page_data)
        title_len = len(page_data['title'])
        
        gaps = []
        if title_len > 60: gaps.append("SHORTEN title to 55-60 chars")
        if title_len < 40: gaps.append("EXPAND title to 55-60 chars") 
        if page_data['word_count'] < 1000: gaps.append("ADD 2 H2 sections: locality + prices")
        
        prompt = f"SEO FIX: {page_data['url']}\n"
        prompt += f"Keyword: {main_keyword}\nScore: {score}/100\n\n"
        prompt += "FIXES:\n" + "\n".join([f"• {gap}" for gap in gaps])
        prompt += "\n\nKeep ALL design/CTAs. Return full page code."
        
        return prompt
    
    def run_full_audit(self):
        print("🚀 Westside SEO Audit STARTING...")
        results = []
        
        for i, url in enumerate(self.pages, 1):
            print(f"Analyzing {i}/{len(self.pages)}: {url}")
            page_data = self.extract_seo_data(url)
            
            if page_
                score = self.calculate_seo_score(page_data)
                priority = score < 80
                cursor_prompt = self.generate_cursor_prompt(page_data)
                
                results.append({
                    'url': page_data['url'],
                    'title': page_data['title'],
                    'score': score,
                    'priority': 'YES' if priority else 'NO',
                    'word_count': page_data['word_count'],
                    'cursor_prompt': cursor_prompt[:300]
                })
        
        df = pd.DataFrame(results)
        df.to_csv('priority_seo_fixes.csv', index=False)
        
        print(f"\n✅ SUCCESS! {len(results)} pages analyzed")
        print(f"📊 Files saved: priority_seo_fixes.csv")
        print("⬇️ Download from Artifacts tab!")

if __name__ == "__main__":
    auditor = WestsideSEOAuditor()
    auditor.run_full_audit()
