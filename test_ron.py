import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, Gecko) Chrome/120.0.0.0 Safari/537.36'
}

url = 'https://www.ronlight.co.il/product-category/brand/ronlight-outlet/%D7%A9%D7%95%D7%90%D7%91%D7%99-%D7%90%D7%91%D7%A7-%D7%A8%D7%95%D7%91%D7%95%D7%98%D7%99%D7%99%D7%9D-%D7%9E%D7%97%D7%95%D7%93%D7%A9%D7%99%D7%9D/'
resp = requests.get(url, headers=headers)
soup = BeautifulSoup(resp.content, 'html.parser')

products = soup.find_all('li', class_=re.compile(r'product'))
print(f"Total products found in Ronlight: {len(products)}")

for p in products[:10]:
    # Title
    title_tag = p.find('h2') or p.find('h3') or p.find('a', class_=re.compile(r'title|loop'))
    title = title_tag.text.strip() if title_tag else ''
    
    # URL
    a_tag = p.find('a', href=re.compile(r'/product/|https://www.ronlight.co.il/'))
    href = a_tag['href'] if a_tag else ''
    
    # Image
    img_tag = p.find('img')
    img_src = ''
    if img_tag:
        img_src = img_tag.get('src') or img_tag.get('data-src') or img_tag.get('srcset', '').split(' ')[0]
        
    # Price
    price_tag = p.find('span', class_=re.compile(r'price|amount'))
    price_text = price_tag.text.strip() if price_tag else ''
    
    print(f"TITLE: {title} | PRICE: {price_text} | URL: {href} | IMG: {img_src[:60]}")

