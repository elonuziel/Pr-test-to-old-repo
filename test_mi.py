import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, Gecko) Chrome/120.0.0.0 Safari/537.36'
}

resp = requests.get('https://www.mi-il.co.il/sale/outlet', headers=headers)
soup = BeautifulSoup(resp.content, 'html.parser')

items = []
cubes = soup.find_all('div', class_=re.compile(r'product-cube'))
print(f"Total product cubes found: {len(cubes)}")

for c in cubes:
    prod_id = c.get('data-prodid') or c.get('data-productId')
    cat_name = c.get('data-category', '')
    fullname = c.get('data-fullname') or c.get('data-fullName', '')
    
    # Title & Link
    link_tag = c.find('a', class_='product') or c.find('a', href=re.compile(r'/product/'))
    title = fullname or (link_tag.text.strip() if link_tag else '')
    href = link_tag['href'] if link_tag and link_tag.has_attr('href') else ''
    url = f"https://www.mi-il.co.il{href}" if href and not href.startswith('http') else href
    
    # Image
    img_tag = c.find('img')
    img_src = ''
    if img_tag:
        img_src = img_tag.get('src') or img_tag.get('data-src') or ''
        if img_src and not img_src.startswith('http'):
            img_src = f"https://www.mi-il.co.il{img_src}"
            
    # Price
    # Inspect price tags
    price_tag = c.find('div', class_='price') or c.find('span', class_='price') or c.find('div', class_='outlet-price')
    price_text = price_tag.text.strip() if price_tag else ''
    
    # Also look inside all text inside cube for price
    if not price_text:
        text = c.get_text()
        m = re.search(r'₪\s*[\d,]+|[\d,]+\s*₪', text)
        if m:
            price_text = m.group(0)

    items.append({
        'id': prod_id,
        'category': cat_name,
        'title': title,
        'url': url,
        'img': img_src,
        'price': price_text,
        'cube_html': str(c)[:300]
    })

for item in items[:5]:
    print(item)
