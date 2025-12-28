import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import json

genai.configure(api_key="your-gemini-key")
model = genai.GenerativeModel('gemini-pro')

def crawl_sitemap():
    sitemap = requests.get("https://www.westsiderealty.in/sitemap.xml").text
    urls = re.findall(r'<loc>(.*?)</loc>', sitemap)
    return [u for u in urls if 'westsiderealty.in' in u][:50]

def categorize_page(url, content):
    prompt = f"""
    Analyze this URL: {url}
    Page content preview: {content[:1000]}
    
    Categorize as ONE of: homepage, city-hub, micro-market, project, listing, blog, contact
    Return JSON: {{"category": "project", "primary_keyword": "3BHK Kokapet", "purpose": "project landing"}}
    """
    response = model.generate_content(prompt)
    return json.loads(response.text)

# MAIN PIPELINE
urls = crawl_sitemap()
results = []
for url in urls:
    content = requests.get(url).text
    category = categorize_page(url, content)
    results.append({"url": url, **category})

pd.DataFrame(results).to_csv('categorized_pages.csv')
