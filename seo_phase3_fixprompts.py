#!/usr/bin/env python3
"""
PHASE 3.2: SITEMAP Cursor Prompts (Top 20 only)
"""

import pandas as pd
import re

print("🚀 PHASE 3.2 - SITEMAP Cursor Prompts")

# Process high + medium priority only
high_df = pd.read_csv('phase3_high_priority.csv') if os.path.exists('phase3_high_priority.csv') else pd.DataFrame()
medium_df = pd.read_csv('phase3_medium_priority.csv') if os.path.exists('phase3_medium_priority.csv') else pd.DataFrame()

priority_pages = pd.concat([high_df, medium_df]).drop_duplicates('url').head(20)  # Top 20

cursor_prompts = []
for idx, row in priority_pages.iterrows():
    keyword = row['keyword']
    url = row['url']
    verdict = row['verdict']
    word_count = row['word_count']
    
    # MASTER CURSOR PROMPT TEMPLATE
    prompt = f"""🎯 MASTER SEO FIX: {keyword}

URL: {url}
Word Count: {word_count}
Verdict: {verdict}

IMPLEMENT THESE CRITICAL FIXES:
1. RealEstateListing JSON-LD schema (price range + RERA)
2. RERA projects table (3-5 projects with IDs)  
3. Price trends section (2025 Hyderabad data)
4. FAQ schema (8+ questions)
5. Long-tail H2: "{keyword} investment ROI 2026"

KEEP 100%:
✅ Tailwind CSS + current design
✅ Hero image + all CTAs  
✅ Mobile responsiveness
✅ Existing content structure

File path: app/hyderabad/{keyword.lower().replace(' ', '-')}/page.tsx

RETURN: COMPLETE Next.js page code ready-to-deploy."""

    cursor_prompts.append({
        'url': url,
        'keyword': keyword,
        'priority': row['needs_fix'],
        'word_count': word_count,
        'cursor_prompt': prompt
    })

df_prompts = pd.DataFrame(cursor_prompts)
df_prompts.to_csv('phase3_cursor_prompts.csv', index=False)

print(f"✅ TOP {len(cursor_prompts)} Cursor prompts ready!")
print("📋 Copy from phase3_cursor_prompts.csv → Cursor AI!")
