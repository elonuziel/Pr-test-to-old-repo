#!/usr/bin/env python3
import json
import unittest

class TestProductData(unittest.TestCase):
    def setUp(self):
        with open('data/products.json', 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.products = self.data.get('products', [])

    def test_products_exist(self):
        self.assertGreater(len(self.products), 0, "Products list should not be empty")
        self.assertEqual(self.data.get('total_count'), len(self.products))

    def test_all_products_have_price(self):
        for p in self.products:
            self.assertIn('price', p, f"Product {p.get('id')} missing price field")
            self.assertGreater(p['price'], 0, f"Product '{p.get('title')}' has invalid price: {p['price']}")
            self.assertIn('price_formatted', p, f"Product {p.get('id')} missing price_formatted field")
            self.assertTrue(p['price_formatted'].startswith('₪'), f"Price formatted '{p['price_formatted']}' does not start with ₪")

    def test_smart_categories(self):
        valid_cats = {'cleaners', 'mopping', 'manual', 'robot'}
        for p in self.products:
            self.assertIn('categories', p, f"Product {p.get('id')} missing categories")
            self.assertIsInstance(p['categories'], list)
            self.assertGreater(len(p['categories']), 0, f"Product {p.get('id')} has empty categories")
            for c in p['categories']:
                self.assertIn(c, valid_cats, f"Category '{c}' in product {p.get('id')} is not valid")

            # Check boolean flags
            self.assertIn('is_mopping', p)
            self.assertIn('is_cleaner_only', p)
            self.assertIn('is_manual', p)
            self.assertIn('is_robot', p)

            # Verification of logic
            if p['is_mopping']:
                self.assertIn('mopping', p['categories'])
                self.assertNotIn('cleaners', p['categories'])
            else:
                self.assertIn('cleaners', p['categories'])
                self.assertNotIn('mopping', p['categories'])

            if p['is_manual']:
                self.assertIn('manual', p['categories'])
            if p['is_robot']:
                self.assertIn('robot', p['categories'])


    def test_product_images(self):
        generic_patterns = ['specials/38.png', 'ronlight-outlet-black', 'out-of-stock', 'placeholder', 'no-image', 'default']
        for p in self.products:
            self.assertIn('image', p, f"Product {p.get('id')} missing image field")
            img = p['image']
            self.assertTrue(img and img.startswith('http'), f"Product '{p.get('title')}' has invalid image URL: {img}")
            for gen in generic_patterns:
                self.assertNotIn(gen, img.lower(), f"Product '{p.get('title')}' uses generic placeholder image: {img}")

    def test_product_urls_and_titles(self):
        for p in self.products:
            self.assertTrue(p['title'], "Product title should not be empty")
            self.assertTrue(p['url'].startswith('http'), f"Product URL invalid: {p['url']}")

if __name__ == '__main__':
    unittest.main()
