import streamlit as st
from bs4 import BeautifulSoup
import requests as rq
import pandas as pd

# #Century21
# urlbase = 'https://www.century21-adc-meudon.com/'
# page = rq.get(urlbase+'annonces/achat/')
# soup = BeautifulSoup(page.content, "html.parser")

# prop = soup.find_all(class_="c-the-property-thumbnail-with-content")
# link = [k.a['href'] for k in prop]
# h = soup.find_all(class_="c-text-theme-heading-3 tw-tracking-c21-theme-0 tw-leading-none tw-text-c21-grey-darker")
# title = [k.get_text(strip=True) for k in h]
# p = soup.find_all(class_="c-text-theme-heading-1 is-constant tw-tracking-c21-theme-40 tw-mt-2 tablet-landscape:tw-mt-0")
# price = [int(k.get_text(strip=True).replace(' ', '').replace(u'\xa0€', u'')) for k in p]

# df = pd.DataFrame(zip(title,price,link),columns=["title","price","link"])

# st.markdown('## Century 21')
# df

#Orpi Viro
urlorpi = 'https://www.orpi.com/'
page = rq.get(urlorpi+'viroflay/acheter')
soup = BeautifulSoup(page.content, "html.parser")
h = soup.find_all(class_="u-link-unstyled c-overlay__link")
title = [k.get_text(strip=True) for k in h]
l = soup.find_all(class_="u-link-unstyled c-overlay__link")
link = [k['href'] for k in l]
i = soup.find_all(class_="c-overlay__zoom")
img = [k['data-src'] for k in i]
p = soup.find_all(class_="u-text-md u-color-primary")
price = [int(k.get_text(strip=True).replace(u'\xa0', u'').replace(u'€', u'')) for k in p]

df = pd.DataFrame(zip(title,price,link),columns=["title","price","link"])

st.markdown('## Orpi')
df
