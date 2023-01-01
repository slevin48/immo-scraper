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