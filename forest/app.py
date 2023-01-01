from chalice import Chalice, Rate
from bs4 import BeautifulSoup
import requests as rq
# import pandas as pd
import json

urlbase = 'https://www.laforet.com'
urlbuy = '/agence-immobiliere/meudon/acheter'
page = rq.get(urlbase+urlbuy)
soup = BeautifulSoup(page.content, "html.parser")

app = Chalice(app_name='forest')

def get_prop(prop):
        items = prop.find_all('p')
        type = items[0].get_text(strip=True)
        price = int(items[1].text.strip().replace('\u202f', '').replace('\xa0€', ''))
        c = prop.find(class_='group-flex').children
        size = int(next(c).get_text(strip=True).replace(' m²',''))
        rooms = int(next(c).get_text(strip=True).replace(' pièce','').replace('s',''))
        try:
            bed = int(next(c).get_text(strip=True).replace(' chambre','').replace('s',''))
        except:
            bed = ''
        link = urlbase + prop['href']
        return [type,price,size, rooms, bed, link]

# @app.schedule(Rate(1, unit=Rate.MINUTES))
@app.route('/')
def index():
    prop = soup.find_all(class_="card-bottom")
    # df = pd.DataFrame([get_prop(p) for p in prop],columns=['type','price','size', 'rooms', 'bed','link'])
    # Turn the list into JSON
    json_data = json.dumps([get_prop(p) for p in prop])
    return json_data
