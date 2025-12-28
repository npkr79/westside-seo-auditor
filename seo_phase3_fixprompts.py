#!/usr/bin/env python3
"""
PHASE 3.2 FULL: Cursor Prompts for ALL 500+ pages
"""

import pandas as pd
import re
import os

print("🚀 PHASE 3.2 FULL - ALL 500+ Cursor Prompts")

# Process ALL pages from full sitemap audit
df = pd.read_csv('phase3_full_sitemap.csv')

print(f"📊 Processing {len(df)} TOTAL pages...")

cursor_prompts = []
for idx, row in df.iterrows():
    url = row['url']
    keyword = row['keyword']
    verdict = row['verdict']
    word_count = row.get('word_count', 0)
    needs_fix = row.get('needs_fix', 'UNKNOWN')
    
    print(f"[{idx+1}/{len(df)}] {keyword[:30]} ({needs_fix})")
    
    # FULL MASTER CURSOR PROMPT FOR EVERY PAGE
    page_slug = keyword.lower().replace(' ', '-').replace('/', '')
    
    prompt = f"""🎯 SEO OPTIMIZATION: {keyword}

📍 URL: {url}
📝 Words: {word_count}
🎯 Verdict: {verdict}
🔧 Priority: {needs_fix}

GENERATE COMPLETE Next.js page:

✅ REQUIRED IMPLEMENTATION:
1. RealEstateListing JSON-LD schema
2. FAQPage schema (8+ questions)  
3. RERA projects table (if applicable)
4. Price trends section (Hyderabad 2025)
5. H2: "{keyword} Investment ROI 2026"

✅ PRESERVE 100%:
- Tailwind CSS styling
- Hero image + CTAs
- Mobile responsiveness  
- Current page structure

📁 File path: app/{page_slug}/page.tsx

RETURN: COMPLETE READY-TO-DEPLOY Next.js code."""

    cursor_prompts.append({
        'url': url,
        'keyword': keyword,
        'slug': page_slug,
        'word_count': word_count,
        'verdict': verdict,
        'needs_fix': needs_fix,
        'priority': 'HIGH' if needs_fix in ['HIGH', 'MEDIUM'] else 'LOW',
        'file_path': f"app/{page_slug}/page.tsx",
        'cursor_prompt': prompt
    })

# SAVE ALL FILES
df_all = pd.DataFrame(cursor_prompts)
df_all.to_csv('phase3_all_cursor_prompts.csv', index=False)  # ALL 500+

# PRIORITY FILES (Your daily work)
high_priority = df_all[df_all['priority'] == 'HIGH']
medium_priority = df_all[df_all['priority'] == 'HIGH']
low_priority = df_all[df_all['priority'] == 'LOW']

high_priority.to_csv('phase3_high_priority_prompts.csv', index=False)
medium_priority.to_csv('phase3_medium_priority_prompts.csv', index=False)
low_priority.to_csv('phase3_low_priority_prompts.csv', index=False)

print(f"\n🎉 FULL SITEMAP SEO AUDIT COMPLETE!")
print(f"📊 TOTAL prompts: {len(df_all)} → phase3_all_cursor_prompts.csv")
print(f"🔥 HIGH priority: {len(high_priority)} → phase3_high_priority_prompts.csv")
print(f"⚡ MEDIUM: {len(medium_priority)} → phase3_medium_priority_prompts.csv")
print(f"📈 LOW: {len(low_priority)} → phase3_low_priority_prompts.csv")
