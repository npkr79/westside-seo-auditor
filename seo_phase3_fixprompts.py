#!/usr/bin/env python3
"""
PHASE 3.2 FIXED: Cursor Prompts - BULLETPROOF
"""

import pandas as pd
import os
import re
import google.generativeai as genai
import time

print("🚀 PHASE 3.2 - Cursor Prompts (No Errors!)")

df = pd.read_csv('phase3_audits.csv')

cursor_prompts = []
api_key = os.getenv("GEMINI_API_KEY")

for idx, row in df.iterrows():
    url = row['url']
    keyword = row['keyword']
    audit = row['audit_report']
    verdict = row['verdict']
    
    print(f"Generating prompt for {keyword[:30]}")
    
    # SMART LOGIC - No Gemini if "optimized"
    if 'no changes required' in verdict.lower() or 'optimized' in verdict.lower():
        cursor_prompt = f"""✅ {keyword} PAGE PERFECT - NO ACTION NEEDED

URL: {url}
Verdict: "{verdict}"

Action: Submit to Google Search Console for fresh indexing.
Status: MONITOR RANKINGS"""
        
    else:
        # ONLY generate fix prompts for pages needing work
        cursor_prompt = f"""🎯 CURSOR AI: Fix {keyword} page based on SEO audit

URL: {url}
AUDIT SUMMARY: {audit[:800]}...

IMPLEMENT EXACTLY from Fix List:
{re.findall(r'\d+\.\s*([^\n]+)', audit)[:5]}

KEEP:
✅ Tailwind CSS + luxury design  
✅ Hero image + CTAs
✅ Mobile responsiveness

ADD:
1. RealEstateListing JSON-LD schema
2. RERA projects table  
3. Price trends section
4. Long-tail H2 headers

RETURN COMPLETE Next.js page code."""
    
    # TRY Gemini code generation → FALLBACK to prompt only
    generated_fix = "Prompt ready - paste to Cursor AI"
    if api_key and 'no changes' not in verdict.lower():
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            resp = model.generate_content(cursor_prompt[:1500])  # Shorten prompt
            generated_fix = resp.text[:1000] + "..."
        except:
            generated_fix = "Use prompt above in Cursor AI"
    
    cursor_prompts.append({
        'url': url,
        'keyword': keyword,
        'verdict': verdict,
        'needs_fix': 'NO' if 'no changes' in verdict.lower() else 'YES',
        'cursor_prompt': cursor_prompt,
        'generated_fix': generated_fix
    })
    
    print(f"   {row['verdict'][:40]}")

df_prompts = pd.DataFrame(cursor_prompts)

# SAVE ALL + FILTER NEEDS FIX
df_prompts.to_csv('phase3_cursor_prompts.csv', index=False)

needs_fix = df_prompts[df_prompts['needs_fix'] == 'YES']
needs_fix.to_csv('phase3_fix_only.csv', index=False)

print(f"\n✅ TOTAL: {len(cursor_prompts)} prompts")
print(f"🔥 NEEDS FIX: {len(needs_fix)} pages → phase3_fix_only.csv")
print(f"✅ PERFECT: {len(df_prompts) - len(needs_fix)} pages")
