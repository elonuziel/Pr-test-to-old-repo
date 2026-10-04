import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, Gecko) Chrome/120.0.0.0 Safari/537.36'
}

resp = requests.get('https://www.xistore.co.il/224382-OUTLET', headers=headers)
soup = BeautifulSoup(resp.content, 'html.parser')

print("Page title:", soup.title.text if soup.title else '')

# Find product blocks in XiStore
# Let's inspect links or cards
cards = soup.find_all('div', class_=re.compile(r'product|item|col'))
print(f"Total potential divs: {len(cards)}")

# Find all a tags with product hrefs
prod_links = soup.find_all('a', href=re.compile(r'/items/|\.html|/product/'))
print(f"Found {len(prod_links)} product links")

for a in prod_links[:10]:
    print("LINK:", a.get('href'), "| TEXT:", a.text.strip()[:60])
    # check parent container
    parent = a.find_parent('div', class_=re.compile(r'product|item|box|card|col'))
    if parent:
        img = parent.find('img')
        img_src = img.get('src') or img.get('data-src') if img else ''
        price = parent.find(class_=re.compile(r'price|cost|nis'))
        price_text = price.text.strip() if price else ''
        print("   PARENT:", parent.get('class'), "PRICE:", price_text, "IMG:", img_src[:50])

