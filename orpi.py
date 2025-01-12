from bs4 import BeautifulSoup
import requests
import pandas as pd

def get_full_url(base, endpoint):
    """Construct the full URL from base and endpoint."""
    return f"{base}{endpoint}"

def get_headers(referer):
    """Define the request headers."""
    return {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/90.0.4430.93 Safari/537.36'
        ),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': referer
    }

def fetch_page(url, headers):
    """Fetch the content of the webpage."""
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
        return None

def parse_html(content):
    """Parse the HTML content using BeautifulSoup."""
    return BeautifulSoup(content, "html.parser")

def extract_titles(soup, class_name="u-link-unstyled c-overlay__link"):
    """Extract property titles."""
    elements = soup.find_all(class_=class_name)
    return [element.get_text(strip=True) for element in elements]

def extract_links(soup, class_name="u-link-unstyled c-overlay__link"):
    """Extract property links."""
    elements = soup.find_all(class_=class_name)
    return [element['href'] for element in elements if 'href' in element.attrs]

def extract_images(soup, class_name="c-overlay__zoom"):
    """Extract image URLs."""
    elements = soup.find_all(class_=class_name)
    return [element.get('data-src') for element in elements if element.get('data-src')]

def extract_prices(soup, class_name="c-estate-thumb__price-tag"):
    """Extract property prices."""
    elements = soup.find_all(class_=class_name)
    prices = []
    for element in elements:
        text = element.get_text(strip=True)
        # Remove non-breaking spaces and euro symbols, then convert to integer
        clean_text = text.replace(u'\xa0', u'').replace(u'€', u'')
        try:
            price = int(clean_text)
            prices.append(price)
        except ValueError:
            prices.append(None)  # Handle cases where conversion fails
    return prices

def create_dataframe(titles, prices, links, images=None):
    """Create a pandas DataFrame from the extracted data."""
    data = {
        "title": titles,
        "price": prices,
        "link": links
    }
    if images:
        data["image"] = images
    return pd.DataFrame(data)

def get_props(agency = 'agenceorangerie'):
    # Configuration
    base_url = 'https://www.orpi.com/'
    endpoint = f'{agency}/acheter'
    full_url = get_full_url(base_url, endpoint)
    headers = get_headers(base_url)

    # Fetch and parse the page
    page_content = fetch_page(full_url, headers)
    if not page_content:
        return  # Exit if page couldn't be fetched

    soup = parse_html(page_content)

    # Extract data
    titles = extract_titles(soup)
    links = extract_links(soup)
    images = extract_images(soup)
    prices = extract_prices(soup)

    # Create DataFrame
    df = create_dataframe(titles, prices, links, images)
    return df

if __name__ == "__main__":
    print(get_props())
