#!/usr/bin/env python3
"""
PHASE 3.2 ULTRA-SIMPLE: Cursor Prompts ONLY (No Gemini!)
"""

import pandas as pd
import re

print("🚀 PHASE 3.2 - Cursor Prompts (100% WORKING!)")

# Read audits (Phase 3.1 success)
df = pd.read_csv('phase3_audits.csv')

cursor_prompts = []
for idx, row in df.iterrows():
    url = row['url']
    keyword = row['keyword']
    audit = row['audit_report']
    verdict = row['verdict']
    
    print(f"📝 {keyword[:30]} → {verdict[:30]}")
    
    # SMART CURSOR PROMPTS (No AI needed!)
    if 'no changes required' in str(verdict).lower() or 'optimized' in str(verdict).lower():
        prompt = f"""✅ {keyword} = PERFECT PAGE! 🎉

URL: {url}
Verdict: "{verdict}"

✅ Action: Submit to Google Search Console
✅ Status: Monitor rankings (already elite!)"""
        needs_fix = "NO"
        
    else:
        # Extract fixes from audit
        fixes = re.findall(r'\d+\.\s*([^\n]+)', audit)
        fix_list = "\n".join(f"- {f.strip()}" for f in fixes[:5])
        
        prompt = f"""🎯 CURSOR AI: Optimize {keyword} for TOP Google rankings

URL: {url}
AUDIT: {audit[:600]}...

FIXES TO IMPLEMENT:
{fix_list}

TEMPLATE REQUIREMENTS:
1. RealEstateListing JSON-LD schema (price range)
2. RERA projects table  
3. Price trends section (2025 data)
4. Long-tail H2 headers (e.g. "{keyword} investment ROI")

KEEP UNCHANGED:
✅ Tailwind CSS styling
✅ Hero image + CTAs  
✅ Mobile responsiveness
✅ Current content structure

RETURN: COMPLETE Next.js page code ready to deploy."""

        needs_fix = "YES"
    
    cursor_prompts.append({
        'url': url,
        'keyword': keyword,
        'verdict': verdict,
        'needs_fix': needs_fix,
        'priority': 'HIGH' if needs_fix == 'YES' else 'NONE',
        'cursor_prompt': prompt[:2000]  # Truncate for CSV
    })

# SAVE FILES
df_prompts = pd.DataFrame(cursor_prompts)
df_prompts.to_csv('phase3_cursor_prompts.csv', index=False)

# ONLY PAGES NEEDING FIXES
needs_fix = df_prompts[df_prompts['needs_fix'] == 'YES']
needs_fix.to_csv('phase3_fix_only.csv', index=False)

print(f"\n🎉 SUCCESS!")
print(f"📊 Total prompts: {len(cursor_prompts)}")
print(f"🔥 Needs fix: {len(needs_fix)} → phase3_fix_only.csv")
print(f"✅ Perfect: {len(df_prompts)-len(needs_fix)} pages")
