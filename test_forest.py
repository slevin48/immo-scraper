import unittest
from unittest.mock import patch
import pandas as pd
from bs4 import BeautifulSoup
from forest import get_soup, get_prop, get_props

class TestUtils(unittest.TestCase):

    def test_get_soup(self):
        prop = get_soup()
        self.assertIsNotNone(prop)
        self.assertGreater(len(prop), 0)

    def test_get_prop(self):
        # Mock a BeautifulSoup object for testing with corrected HTML structure
        html = '''
        <div class="apartment-card">
            <div class="card-bottom">
                <span class="apartment__label">Apartment</span>
                <span class="apartment__price">300 000 €</span>
                <div class="group-flex">
                    <div class="font-bold text-sm">3 pièces</div>
                    <div class="font-bold text-sm">75 m²</div>
                    <div class="font-bold text-sm">2 chambres</div>
                </div>
                <a href="/property/12345">View</a>
            </div>
        </div>
        '''
        soup = BeautifulSoup(html, "html.parser")
        prop = soup.find(class_="card-bottom")
        result = get_prop(prop)
        self.assertEqual(result, ['Apartment', 300000, 75, 3, 2, 'https://www.laforet.com/property/12345'])

    @patch('forest.get_soup')
    def test_get_props(self, mock_get_soup):
        # Mock a BeautifulSoup object for testing with corrected HTML structure
        html = '''
        <div class="apartment-card">
            <div class="card-bottom">
                <span class="apartment__label">Apartment</span>
                <span class="apartment__price">300 000 €</span>
                <div class="group-flex">
                    <div class="font-bold text-sm">3 pièces</div>
                    <div class="font-bold text-sm">75 m²</div>
                    <div class="font-bold text-sm">2 chambres</div>
                </div>
                <a href="/property/12345">View</a>
            </div>
        </div>
        '''
        soup = BeautifulSoup(html, "html.parser")
        prop = soup.find(class_="card-bottom")
        # Mock get_soup to return a list with a single property
        mock_get_soup.return_value = [prop]
        
        result = get_props()
        self.assertEqual(len(result), 1)
        expected = ['Apartment', 300000, 75, 3, 2, 'https://www.laforet.com/property/12345']
        # Convert NumPy types to native Python types for comparison
        actual = result.iloc[0].tolist()
        expected_converted = [
            expected[0],
            int(expected[1]),
            int(expected[2]),
            int(expected[3]),
            int(expected[4]),
            expected[5]
        ]
        self.assertEqual(actual, expected_converted)

if __name__ == '__main__':
    unittest.main()

# To run the tests, execute the following command in your terminal:
# python -m unittest test_forest.py
