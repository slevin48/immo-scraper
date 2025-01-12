from bs4 import BeautifulSoup
import requests as rq
import re
import pandas as pd

# def get_soup():
#     # Get the beautiful soup object 
#     urlbase = 'https://www.century21-adc-meudon.com/'
#     urlbuy = 'annonces/achat/'
#     page = rq.get(urlbase+urlbuy)
#     soup = BeautifulSoup(page.content, "html.parser")
#     prop = soup.find_all(class_="c-the-property-thumbnail-with-content")
#     return prop

import re
from typing import List, Dict, Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup


def fetch_page(url: str) -> Optional[BeautifulSoup]:
    """
    Fetches the content of the given URL and returns a BeautifulSoup object.

    Args:
        url (str): The URL to fetch.

    Returns:
        Optional[BeautifulSoup]: Parsed HTML content or None if the request fails.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def get_property_elements(soup: BeautifulSoup, css_class: str) -> List[BeautifulSoup]:
    """
    Retrieves all property elements from the soup based on the provided CSS class.

    Args:
        soup (BeautifulSoup): Parsed HTML content.
        css_class (str): The CSS class to search for.

    Returns:
        List[BeautifulSoup]: A list of property elements.
    """
    return soup.find_all(class_=css_class)


def extract_links(properties: List[BeautifulSoup], base_url: str) -> List[str]:
    """
    Extracts the href links from property elements.

    Args:
        properties (List[BeautifulSoup]): List of property elements.
        base_url (str): The base URL to prepend if needed.

    Returns:
        List[str]: List of full property URLs.
    """
    links = []
    for prop in properties:
        relative_link = prop.a.get('href', '')
        full_link = relative_link if relative_link.startswith('http') else f"{base_url}{relative_link}"
        links.append(full_link)
    return links


def extract_titles(soup: BeautifulSoup, css_class: str) -> List[str]:
    """
    Extracts the titles from the soup based on the provided CSS class.

    Args:
        soup (BeautifulSoup): Parsed HTML content.
        css_class (str): The CSS class to search for.

    Returns:
        List[str]: List of property titles.
    """
    title_elements = soup.find_all(class_=css_class)
    return [title.get_text() for title in title_elements]


def parse_title(title: str) -> Dict[str, Optional[str]]:
    """
    Parses the property title using regex to extract details.

    Args:
        title (str): The title string to parse.

    Returns:
        Dict[str, Optional[str]]: Extracted details or None if parsing fails.
    """
    pattern = re.compile(
        r'(?P<location>[A-Za-z\s]+)\s+'                  # Location
        r'(?P<zipcode>\d{2,5})\s+'                      # Zipcode (2 to 5 digits)
        r'(?P<area>\d+[.,]?\d*)\s*m2'                    # Area in m²
        r'(?:,\s*(?P<rooms>\d+)\s*pièces)?\s*'           # Optional: Rooms
        r'Ref\s*:\s*(?P<ref>\d+)',                      # Reference number
        re.IGNORECASE
    )
    match = pattern.search(title)
    if match:
        location = match.group('location').strip()
        zipcode = match.group('zipcode')
        if zipcode:
            location_full = f"{location} {zipcode}"
        else:
            location_full = location

        # Replace comma with dot in the area for standard decimal format
        area_str = match.group('area').replace(',', '.')
        try:
            area = float(area_str)
        except ValueError:
            area = None

        # Handle optional rooms
        rooms_str = match.group('rooms')
        if rooms_str:
            try:
                rooms = int(rooms_str)
            except ValueError:
                rooms = None
        else:
            rooms = None  # Assign None if rooms info is missing

        reference = match.group('ref')

        return {
            "location": location_full,
            "area": area,
            "rooms": rooms,
            "reference": reference
        }
    else:
        print(f"Failed to parse title: {title}")
        return {
            "location": None,
            "area": None,
            "rooms": None,
            "reference": None
        }


def extract_prices(soup: BeautifulSoup, css_class: str) -> List[int]:
    """
    Extracts and cleans the price information from the soup.

    Args:
        soup (BeautifulSoup): Parsed HTML content.
        css_class (str): The CSS class to search for price elements.

    Returns:
        List[int]: List of prices as integers.
    """
    price_elements = soup.find_all(class_=css_class)
    prices = []
    for price in price_elements:
        price_text = price.get_text(strip=True).replace(' ', '').replace(u'\xa0€', '')
        try:
            prices.append(int(price_text))
        except ValueError:
            print(f"Invalid price format: {price_text}")
            prices.append(None)
    return prices


def scrape_properties(city: str = 'meudon', action: str = 'achat') -> pd.DataFrame:
    """
    Scrapes property listings based on the city and action (buy/sell).

    Args:
        city (str): The city to search in.
        action (str): The action, e.g., 'acheter' for buying.

    Returns:
        pd.DataFrame: DataFrame containing property details.
    """
    base_url = 'https://www.century21-adc-meudon.com/'
    action_url = f'annonces/{action}/'
    full_url = f"{base_url}{action_url}"

    soup = fetch_page(full_url)
    if not soup:
        return pd.DataFrame()  # Return empty DataFrame on failure

    property_css_class = "c-the-property-thumbnail-with-content"
    properties = get_property_elements(soup, property_css_class)
    if not properties:
        print("No properties found.")
        return pd.DataFrame()

    links = extract_links(properties, base_url)

    title_css_class = "c-text-theme-heading-4 tw-text-c21-grey-darker tw-font-semibold"
    titles = extract_titles(soup, title_css_class)

    # Parse titles to extract detailed information
    parsed_details = [parse_title(title) for title in titles]

    price_css_class = "c-text-theme-heading-1 is-constant-size-on-mobile tw-mt-2 tablet-landscape:tw-mt-0 tw-whitespace-nowrap"
    prices = extract_prices(soup, price_css_class)

    # Combine all data into a DataFrame
    data = []
    for detail, price, link in zip(parsed_details, prices, links):
        if all(v is not None for v in detail.values()):
            data.append({
                "Location": detail["location"],
                "Area (m²)": detail["area"],
                "Rooms": detail["rooms"],
                "Reference Number": detail["reference"],
                "Price (€)": price,
                "Link": link
            })

    df = pd.DataFrame(data)
    return df


if __name__ == "__main__":
    # Scrape properties and display the DataFrame
    properties_df = scrape_properties(city='meudon', action='achat')
    print(properties_df)
