name: 🚀 Daily SEO Audit → Email Cursor Prompts
on:
  schedule:
    - cron: '0 6 * * *'  # 6AM IST daily
  workflow_dispatch:

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install requests beautifulsoup4 pandas google-generativeai lxml
    
    - name: Run SEO Audit
      env:
        GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
      run: python seo_auditor.py
    
    - name: Create HTML Report
      run: |
        echo '<h1>🚀 Westside SEO Audit Results - $(date)</h1>' > report.html
        echo '<p>Generated: $(date)</p>' >> report.html
        if [ -f priority_seo_fixes.csv ]; then
          echo '<h2>Priority Pages (Copy to Cursor):</h2>' >> report.html
          python -c "
import pandas as pd
df = pd.read_csv('priority_seo_fixes.csv')
html = df.to_html(index=False, escape=False)
print(html, file=open('report.html', 'a'))
          "
        fi
    
    - name: Upload Results
      uses: actions/upload-artifact@v4
      with:
        name: seo-results-${{ github.run_number }}
        path: |
          priority_seo_fixes.*
          report.html
          seo_audit_*.csv
    
    - name: Send Email
      uses: dawidd6/action-send-mail@v3
      with:
        server_address: smtp.gmail.com
        server_port: 587
        username: ${{ secrets.EMAIL_USERNAME }}
        password: ${{ secrets.EMAIL_PASSWORD }}
        subject: "🚀 Westside SEO Audit - ${{ github.run_number }} | $(date '+%Y-%m-%d')"
        to: npkr79@gmail.com
        from: Westside SEO Bot <npkr79@gmail.com>
        body: file://report.html
        attachments: |
          priority_seo_fixes.csv
          report.html
        secure: true
