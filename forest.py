import re
from bs4 import BeautifulSoup
import pandas as pd
import urllib.request

def get_soup(city = 'meudon', action = 'acheter'):
    # Get the beautiful soup object 
    urlbase = 'https://www.laforet.com'
    urlbuy = '/agence-immobiliere/{city}/{action}'.format(city=city, action=action)
    with urllib.request.urlopen(urlbase + urlbuy) as response:
        page = response.read()
    soup = BeautifulSoup(page, "html.parser")
    prop = soup.find_all(class_="card-bottom")
    return prop


def get_prop(prop, urlbase = "https://www.laforet.com"):
    # Extract the type from the <span> with class 'apartment__label'
    type_tag = prop.find('span', class_='apartment__label')
    type_ = type_tag.get_text(strip=True) if type_tag else 'N/A'

    # Extract the price from the <span> with class 'apartment__price'
    price_tag = prop.find('span', class_='apartment__price')
    if price_tag:
        price_text = price_tag.get_text(strip=True)
        # Remove non-breaking spaces and the euro symbol
        price_numeric = price_text.replace('\u202f', '').replace('\xa0€', '').replace('€', '').replace(' ', '')
        try:
            price = int(price_numeric)
        except ValueError:
            price = 0  # Default value if conversion fails
    else:
        price = 0  # Default value if price_tag is not found

    # Extract features from the 'group-flex' div
    group_flex = prop.find('div', class_='group-flex')
    features = group_flex.find_all('div', class_='font-bold text-sm') if group_flex else []

    # Initialize variables
    rooms = size = bed = 0

    # Iterate through each feature and assign appropriately using regex
    for feature in features:
        text = feature.get_text(strip=True).lower()
        # Extract digits using regex
        number_match = re.search(r'(\d+)', text)
        number = int(number_match.group(1)) if number_match else 0

        if 'pièce' in text:
            rooms = number
        elif 'm²' in text or 'm2' in text:
            size = number
        elif 'chambre' in text:
            bed = number

    # Extract the link from the parent 'apartment-card' div's <a> tag
    apartment_card = prop.find_parent('div', class_='apartment-card')
    if apartment_card:
        a_tag = apartment_card.find('a', href=True)
        link = urlbase + a_tag['href'] if a_tag else 'N/A'
    else:
        link = 'N/A'

    return [type_, price, size, rooms, bed, link]

def get_props(city = 'meudon', action = 'acheter'):
    # Extract all properties from the soup
    prop = get_soup(city)
    return pd.DataFrame([get_prop(p) for p in prop],columns=['type','price','size', 'rooms', 'bed','link'])