#!/usr/bin/env python3
"""
Multi-store vacuum cleaner outlet scraper for GitHub Pages.
Scrapes second-hand / renewed / outlet robot and handheld vacuum cleaners from:
1. https://www.mi-il.co.il/sale/outlet
2. https://www.xistore.co.il/224382-OUTLET
3. https://www.ronlight.co.il/product-category/brand/ronlight-outlet/%D7%A9%D7%95%D7%90%D7%91%D7%99-%D7%90%D7%91%D7%A7-%D7%A8%D7%95%D7%91%D7%95%D7%98%D7%99%D7%99%D7%9D-%D7%9E%D7%97%D7%95%D7%93%D7%A9%D7%99%D7%9D/
"""

import os
import json
import re
import datetime
import urllib.parse
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, Gecko) Chrome/120.0.0.0 Safari/537.36'
}

ROBOT_KEYWORDS = [
    'רובוט', 'רובוטי', 'רובוטיים', 'robot', 'freo', 'omni', 'deebot', 'yeedi', 's10', 's20', 'x20', 'x10', 'x1', 't30', 'dreame', 'roborock'
]

HANDHELD_KEYWORDS = [
    'אלחוטי', 'ידני', 'מוט', 'שוטף', 'מקרצף', 'handheld', 'stick', 'cordless', 'cleaner', 'g10', 'g11', 'g9', 'v10', 'v11', 'v12', 'h6', 'h7', 'jimmy', 'h14', 'h15', 'z30'
]

VACUUM_BASE_KEYWORDS = [
    'שואב', 'שואבים', 'vacuum', 'cleaner'
]

def is_vacuum_product(title, category=""):
    text = (title + " " + category).lower()
    
    exclusions = [
        'סמארטפון', 'טאבלט', 'קורקינט', 'שולחן', 'הליכון', 'ראוטר', 'router',
        'phone', 'watch', 'שעון', 'אוזניות', 'buds', 'tv box', 'מצלמ', 'מייבש שיער',
        'שיער', 'קלימה', 'nami', 'smarter'
    ]
    for exc in exclusions:
        if exc in text:
            return False, None

    has_vacuum_base = any(k in text for k in VACUUM_BASE_KEYWORDS) or 'רובוט' in text or 'robot' in text or 'deebot' in text or 'yeedi' in text or 'dreame' in text
    if not has_vacuum_base:
        return False, None

    is_robot = any(k in text for k in ROBOT_KEYWORDS)
    is_handheld = any(k in text for k in HANDHELD_KEYWORDS)
    
    if is_robot and not is_handheld:
        product_type = 'robot'
    elif is_handheld and not is_robot:
        product_type = 'handheld'
    elif is_robot:
        product_type = 'robot'
    else:
        product_type = 'robot'

    return True, product_type


GENERIC_IMAGE_PATTERNS = [
    'specials/38.png',
    'ronlight-outlet-black',
    'out-of-stock',
    'placeholder',
    'no-image',
    'default',
    'bg-2'
]

def is_generic_image(img_url):
    if not img_url:
        return True
    u = img_url.lower()
    return any(p in u for p in GENERIC_IMAGE_PATTERNS)

def parse_price(price_str):
    if not price_str:
        return 0, "N/A"
    
    matches = re.findall(r'(\d{1,3}(?:,\d{3})+|\d{3,5})', price_str)
    if matches:
        nums = [int(m.replace(',', '')) for m in matches]
        valid_nums = [n for n in nums if n >= 100]
        if valid_nums:
            sale_price = min(valid_nums)
            return sale_price, f"₪{sale_price:,}"
    return 0, "N/A"



MOPPING_KEYWORDS = [
    'שוטף', 'מקרצף', 'mop', 'wash', 'omni', 'combo', 'station', 'freo', 'floor3'
]

MANUAL_KEYWORDS = [
    'אלחוטי', 'ידני', 'מוט', 'stick', 'cordless', 'handheld', 'g10', 'g11', 'g9', 'v10', 'v11', 'v12', 'h13', 'h14', 'h15', 'z30'
]

def categorize_product(title, prod_type):
    """
    Categorizes vacuum products smartly into categories:
    - 'cleaners': Just cleaners (dry vacuuming without wet mopping)
    - 'mopping': Mopping / wet cleaning / scrubbing capability
    - 'manual': Handheld / stick / cordless / manual vacuums
    - 'robot': Robotic vacuums
    Returns categories array and primary category flags.
    """
    t = title.lower()
    is_mopping = any(k in t for k in MOPPING_KEYWORDS)
    is_manual = prod_type == 'handheld' or any(k in t for k in MANUAL_KEYWORDS)
    is_robot = prod_type == 'robot' or 'רובוט' in t or 'robot' in t

    categories = []
    if is_mopping:
        categories.append('mopping')
    else:
        categories.append('cleaners')

    if is_manual:
        categories.append('manual')
    if is_robot:
        categories.append('robot')

    return {
        'is_mopping': is_mopping,
        'is_cleaner_only': not is_mopping,
        'is_manual': is_manual,
        'is_robot': is_robot,
        'categories': categories
    }


def scrape_mi_il():
    url = 'https://www.mi-il.co.il/sale/outlet'
    print(f"[*] Scraping Mi-IL: {url}")
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.content, 'html.parser')
        cubes = soup.find_all('div', class_=re.compile(r'product-cube'))
        
        for c in cubes:
            cat_name = c.get('data-category', '')
            fullname = c.get('data-fullname') or c.get('data-fullName', '')
            link_tag = c.find('a', class_='product') or c.find('a', href=re.compile(r'/product/'))
            
            title = fullname or (link_tag.text.strip() if link_tag else '')
            if not title:
                continue

            valid, prod_type = is_vacuum_product(title, cat_name)
            if not valid:
                continue

            href = link_tag['href'] if link_tag and link_tag.has_attr('href') else ''
            prod_url = f"https://www.mi-il.co.il{href}" if href and not href.startswith('http') else href

            img_tag = c.find('img')
            img_src = ''
            if img_tag:
                img_src = img_tag.get('src') or img_tag.get('data-src') or ''
                if img_src and not img_src.startswith('http'):
                    img_src = f"https://www.mi-il.co.il{img_src}"

            if is_generic_image(img_src) and prod_url:
                try:
                    p_resp = requests.get(prod_url, headers=HEADERS, timeout=10)
                    p_soup = BeautifulSoup(p_resp.content, 'html.parser')
                    og = p_soup.find('meta', property='og:image')
                    if og and og.get('content'):
                        candidate = og.get('content').strip()
                        if candidate and not candidate.startswith('http'):
                            candidate = f"https://www.mi-il.co.il{candidate}"
                        if not is_generic_image(candidate):
                            img_src = candidate
                except Exception as ex:
                    print(f"[!] Error fetching Mi-IL detail image for {prod_url}: {ex}")

            price_tag = c.find('div', class_='price') or c.find('span', class_='price') or c.find('div', class_='outlet-price')
            price_text = price_tag.text.strip() if price_tag else c.get_text()
            price_val, price_formatted = parse_price(price_text)

            cat_info = categorize_product(title, prod_type)
            items.append({
                'id': f"mi_{c.get('data-prodid', len(items))}",
                'store': 'Mi-IL',
                'title': title,
                'url': prod_url,
                'image': img_src,
                'price': price_val,
                'price_formatted': price_formatted,
                'type': prod_type,
                'in_stock': True,
                **cat_info
            })
    except Exception as e:
        print(f"[!] Error scraping Mi-IL: {e}")
    print(f"[+] Found {len(items)} valid vacuum products from Mi-IL")
    return items


def scrape_xistore():
    url = 'https://www.xistore.co.il/224382-OUTLET'
    print(f"[*] Scraping XiStore: {url}")
    items = []
    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        session.headers.update({'Referer': 'https://www.google.com/'})
        resp = session.get(url, timeout=15)
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        cards = soup.find_all('div', class_=re.compile(r'layout_list_item'))
        seen_urls = set()

        for card in cards:
            title_el = card.find(class_='list_item_title_with_brand') or card.find('h3')
            title = title_el.get_text(strip=True) if title_el else ''
            
            link_el = card.find('a', href=re.compile(r'/items/'))
            href = link_el['href'].strip() if link_el else ''
            if not href or href in seen_urls:
                continue

            full_url = f"https://www.xistore.co.il{href}" if not href.startswith('http') else href

            if not title or len(title) < 3:
                title = link_el.get_text(strip=True) if link_el else ''

            valid, prod_type = is_vacuum_product(title)
            if not valid:
                continue

            seen_urls.add(href)

            img_tag = card.find('img')
            img_src = ''
            if img_tag:
                img_src = img_tag.get('src') or img_tag.get('data-src') or ''

            price_tag = card.find(class_=re.compile(r'price|cost|show_price'))
            price_text = price_tag.get_text(strip=True) if price_tag else ''
            price_val, price_formatted = parse_price(price_text)

            # Fallback to detail page if price is 0 or image is generic/missing
            if (price_val == 0 or is_generic_image(img_src)) and full_url:
                try:
                    p_resp = session.get(full_url, timeout=10)
                    p_soup = BeautifulSoup(p_resp.content, 'html.parser')
                    if price_val == 0:
                        p_el = p_soup.find('span', class_='price_value') or p_soup.find(class_='wrap_price') or p_soup.find(class_='main_price_and_btn')
                        if p_el:
                            price_val, price_formatted = parse_price(p_el.get_text())
                    if is_generic_image(img_src):
                        og = p_soup.find('meta', property='og:image')
                        if og and og.get('content') and not is_generic_image(og.get('content')):
                            img_src = og.get('content').strip()
                except Exception as ex:
                    print(f"[!] Error fetching XiStore detail info for {full_url}: {ex}")

            cat_info = categorize_product(title, prod_type)
            items.append({
                'id': f"xi_{len(items)}",
                'store': 'XiStore',
                'title': title,
                'url': full_url,
                'image': img_src,
                'price': price_val,
                'price_formatted': price_formatted,
                'type': prod_type,
                'in_stock': True,
                **cat_info
            })
    except Exception as e:
        print(f"[!] Error scraping XiStore: {e}")
    print(f"[+] Found {len(items)} valid vacuum products from XiStore")
    return items


def scrape_ronlight_product_page(prod_url):
    try:
        resp = requests.get(prod_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Extract precise title
        h1 = soup.find('h1')
        title = h1.get_text(strip=True) if h1 else ''
        
        # Extract price
        price_val, price_formatted = 0, "N/A"
        # Find price element inside entry-summary or summary
        summary = soup.find(class_=re.compile(r'summary|product-info'))
        if summary:
            price_el = summary.find(class_=re.compile(r'price'))
            if price_el:
                price_val, price_formatted = parse_price(price_el.get_text())

        # If summary didn't catch price, search whole page for ₪ prices
        if price_val == 0:
            prices = soup.find_all('span', class_=re.compile(r'amount|price'))
            for p in prices:
                v, fmt = parse_price(p.get_text())
                if v > 0:
                    price_val, price_formatted = v, fmt
                    break

        # Extract main product image from og:image meta tag
        img_src = ''
        og = soup.find('meta', property='og:image')
        if og and og.get('content') and not is_generic_image(og.get('content')):
            img_src = og.get('content').strip()

        # Fallback to product gallery / post image
        if is_generic_image(img_src):
            img_el = soup.find('img', class_=re.compile(r'wp-post-image|attachment-woocommerce')) or soup.select_one('.woocommerce-product-gallery img')
            if img_el:
                candidate = img_el.get('src') or img_el.get('data-src') or ''
                if not is_generic_image(candidate):
                    img_src = candidate

        return title, price_val, price_formatted, img_src
    except Exception as e:
        print(f"[!] Error fetching Ronlight product page {prod_url}: {e}")
        return '', 0, "N/A", ''


def scrape_ronlight():
    url = 'https://www.ronlight.co.il/product-category/brand/ronlight-outlet/%D7%A9%D7%95%D7%90%D7%91%D7%99-%D7%90%D7%91%D7%A7-%D7%A8%D7%95%D7%91%D7%95%D7%98%D7%99%D7%99%D7%9D-%D7%9E%D7%97%D7%95%D7%93%D7%A9%D7%99%D7%9D/'
    print(f"[*] Scraping Ronlight: {url}")
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.content, 'html.parser')

        prod_links = soup.find_all('a', href=re.compile(r'/product/'))
        seen_urls = set()

        for a in prod_links:
            href = a.get('href', '')
            if not href or href in seen_urls:
                continue

            parent = a.find_parent('li') or a.find_parent('div')
            initial_title = ''
            catalog_img = ''
            if parent:
                title_el = parent.find(['h2', 'h3', 'h4'])
                if title_el:
                    initial_title = title_el.get_text(strip=True)
                for img_t in parent.find_all('img'):
                    src = img_t.get('src') or img_t.get('data-src') or img_t.get('data-lazy-src') or ''
                    if src and not is_generic_image(src):
                        catalog_img = src
                        break
            
            if not initial_title or initial_title == 'אזל מהמלאי':
                initial_title = a.get_text(strip=True)
            if not initial_title or initial_title == 'אזל מהמלאי':
                slug = urllib.parse.unquote(href).rstrip('/').split('/')[-1].replace('-', ' ')
                initial_title = slug

            is_out_of_stock = False
            if parent and ('אזל מהמלאי' in parent.get_text() or 'out-of-stock' in str(parent)):
                is_out_of_stock = True

            valid, prod_type = is_vacuum_product(initial_title)
            if not valid:
                continue

            seen_urls.add(href)

            # Deep scrape product page for price and full title
            p_title, p_val, p_fmt, p_img = scrape_ronlight_product_page(href)
            title = p_title if p_title else initial_title
            
            img_src = catalog_img if catalog_img else p_img

            cat_info = categorize_product(title, prod_type)
            items.append({
                'id': f"ron_{len(items)}",
                'store': 'Ronlight',
                'title': title,
                'url': href,
                'image': img_src,
                'price': p_val,
                'price_formatted': p_fmt,
                'type': prod_type,
                'in_stock': not is_out_of_stock,
                **cat_info
            })
    except Exception as e:
        print(f"[!] Error scraping Ronlight: {e}")
    print(f"[+] Found {len(items)} valid vacuum products from Ronlight")
    return items


def main():
    all_products = []
    all_products.extend(scrape_mi_il())
    all_products.extend(scrape_xistore())
    all_products.extend(scrape_ronlight())

    os.makedirs('data', exist_ok=True)
    out_data = {
        'last_updated': datetime.datetime.now().strftime('%d/%m/%Y %H:%M'),
        'total_count': len(all_products),
        'products': all_products
    }

    with open('data/products.json', 'w', encoding='utf-8') as f:
        json.dump(out_data, f, ensure_ascii=False, indent=2)

    print(f"\n[✓] Scraped {len(all_products)} products successfully into data/products.json")

if __name__ == '__main__':
    main()
