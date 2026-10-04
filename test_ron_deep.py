import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, Gecko) Chrome/120.0.0.0 Safari/537.36'
}

url = 'https://www.ronlight.co.il/product-category/brand/ronlight-outlet/%D7%A9%D7%95%D7%90%D7%91%D7%99-%D7%90%D7%91%D7%A7-%D7%A8%D7%95%D7%91%D7%95%D7%98%D7%99%D7%99%D7%9D-%D7%9E%D7%97%D7%95%D7%93%D7%A9%D7%99%D7%9D/'
resp = requests.get(url, headers=headers)
soup = BeautifulSoup(resp.content, 'html.parser')

# Check ul.products or container of products
prod_grid = soup.find('ul', class_=re.compile(r'products')) or soup.find('div', class_=re.compile(r'products'))
if prod_grid:
    items = prod_grid.find_all(['li', 'div'], recursive=False)
    print(f"Direct product items in grid: {len(items)}")
    for p in items[:5]:
        title = p.find(['h2', 'h3', 'a', 'span'], class_=re.compile(r'title|name|product_title|woocommerce-loop-product__title'))
        title_text = title.text.strip() if title else ''
        a_tag = p.find('a')
        link = a_tag['href'] if a_tag and a_tag.has_attr('href') else ''
        price = p.find(class_=re.compile(r'price'))
        price_text = price.text.strip() if price else ''
        img = p.find('img')
        img_src = (img.get('src') or img.get('data-src') or img.get('data-lazy-src') or '') if img else ''
        print(f"TITLE: {title_text} | PRICE: {price_text} | URL: {link} | IMG: {img_src[:50]}")

