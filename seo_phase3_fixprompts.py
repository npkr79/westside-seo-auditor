#!/usr/bin/env python3
"""
PHASE 3.2: Audit → Cursor Fix Prompts
"""

import pandas as pd
import google.generativeai as genai
import os
import re

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

df = pd.read_csv('phase3_audits.csv')

cursor_prompts = []
for idx, row in df.iterrows():
    audit = row['audit_report']
    
    fix_prompt = f"""You are Cursor AI. Fix this page based on the SEO audit:

URL: {row['url']}
AUDIT: {audit[:3000]}...

GENERATE COMPLETE Next.js page code that implements ALL fixes from "Fix List":
1. Add RealEstateListing schema
2. RERA table  
3. Price trends section
4. H2 long-tail headers
5. Interactive map

Keep Tailwind CSS, hero image, CTAs exactly the same.
Preserve luxury design + mobile responsiveness.

RETURN COMPLETE PAGE CODE ONLY."""
    
    try:
        resp = model.generate_content(fix_prompt)
        cursor_prompts.append({
            'url': row['url'],
            'keyword': row['keyword'],
            'cursor_prompt': fix_prompt,
            'generated_fix': resp.text[:2000]
        })
    except:
        cursor_prompts.append({'url': row['url'], 'cursor_prompt': 'Error generating'})

pd.DataFrame(cursor_prompts).to_csv('phase3_cursor_prompts.csv', index=False)
print("✅ phase3_cursor_prompts.csv → COPY TO CURSOR!")
