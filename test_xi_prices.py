import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, Gecko) Chrome/120.0.0.0 Safari/537.36'
}

resp = requests.get('https://www.xistore.co.il/224382-OUTLET', headers=headers)
soup = BeautifulSoup(resp.content, 'html.parser')

items = soup.find_all('div', class_=re.compile(r'list_item_block|product_box|item_block'))
print("Found blocks:", len(items))

for item in items[:5]:
    title = item.find(class_=re.compile(r'title|name'))
    price = item.find(class_=re.compile(r'price'))
    img = item.find('img')
    link = item.find('a', href=re.compile(r'/items/'))
    
    print('TITLE:', title.text.strip() if title else 'N/A')
    print('PRICE:', price.text.strip() if price else 'N/A')
    print('IMG:', img.get('src') or img.get('data-src') if img else 'N/A')
    print('LINK:', link['href'] if link else 'N/A')
    print('---')

