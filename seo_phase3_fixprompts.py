#!/usr/bin/env python3
"""
PHASE 3.2 FULL - FIXED IMPORTS
"""

import os  # ← FIXED #1
import pandas as pd  # ← FIXED #2

print("🚀 PHASE 3.2 FULL - ALL 500+ Cursor Prompts")

if not os.path.exists('phase3_full_sitemap.csv'):
    print("❌ ERROR: Run seo_phase3_audit.py first!")
    exit(1)

df = pd.read_csv('phase3_full_sitemap.csv')
print(f"📊 Processing {len(df)} TOTAL pages...")

cursor_prompts = []
for idx, row in df.iterrows():
    url = row['url']
    keyword = row['keyword']
    verdict = row['verdict']
    word_count = row.get('word_count', 0)
    needs_fix = row.get('needs_fix', 'UNKNOWN')
    
    page_slug = keyword.lower().replace(' ', '-').replace('/', '')
    
    prompt = f"""🎯 SEO FIX: {keyword}

URL: {url} | Words: {word_count} | Verdict: {verdict}

File: app/{page_slug}/page.tsx

REQUIRED:
1. RealEstateListing schema
2. FAQ schema (8+ questions)
3. RERA table
4. Price trends 2025

KEEP: Tailwind CSS, hero, CTAs, mobile.

RETURN COMPLETE Next.js code."""

    cursor_prompts.append({
        'url': url,
        'keyword': keyword,
        'slug': page_slug,
        'word_count': word_count,
        'needs_fix': needs_fix,
        'file_path': f"app/{page_slug}/page.tsx",
        'cursor_prompt': prompt
    })

df_all = pd.DataFrame(cursor_prompts)
df_all.to_csv('phase3_all_cursor_prompts.csv', index=False)

high_priority = df_all[df_all['needs_fix'] == 'HIGH']
high_priority.to_csv('phase3_high_priority_prompts.csv', index=False)

print(f"✅ {len(df_all)} prompts → phase3_all_cursor_prompts.csv")
print(f"🔥 {len(high_priority)} HIGH priority → phase3_high_priority_prompts.csv")
