# immo-scraper [![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/slevin48/immo-scraper) 
🏠 Real Estate opportunities in Meudon

![](img/scraping1.png)

```python
prop = soup.find_all(class_="card-bottom")
link = [a['href'] for a in prop]
i = prop[0].find(class_="title-price").children # iterator
prop_type = next(i).text.strip()
space = next(i)
price = next(i).text.strip().replace('\u202f', '').replace('\xa0', '')
```

Create serverless function to fetch info daily:

```
python -m venv env
.\env\Scripts\activate
```
Once activated, install Chalice and other req:
```
(env) pip install chalice beautifulsoup4 pandas
```
Create a project:
```
chalice new-project immo
cd immo
```
Finally, deploy:
```
chalice deploy
```

Resources:

* https://github.com/slevin48/automate
* https://github.com/slevin48/serverless