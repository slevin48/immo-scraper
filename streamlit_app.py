import streamlit as st
from bs4 import BeautifulSoup
import requests as rq
import pandas as pd
import forest, century21, orpi

@st.cache_data
def convert_df(df):
     # IMPORTANT: Cache the conversion to prevent computation on every rerun
     return df.to_csv().encode('utf-8')

st.sidebar.title('Real Estate Web Scraping')

ag = st.sidebar.radio('Choose the agency', ['Laforet', 'Century21', 'Orpi'])

if ag == 'Laforet':
     # #Laforet
     # urlbase = 'https://www.laforet.com'
     # urlbuy = '/agence-immobiliere/meudon/acheter'
     st.markdown('## Laforet')
     city = st.selectbox('Choose the city', ['bourglareine', 'fontenayauxroses', 'le-plessis-robinson', 'meudon', 'massy', 'versailles', 'viroflay'])
     df = forest.get_props(city)
     st.write(df)

elif ag == 'Century21':
     # #Century21
     # urlbase = 'https://www.century21-adc-meudon.com/'
     st.markdown('## Century 21')
     df = century21.scrape_properties(city='meudon', action='achat')
     st.write(df)

elif ag == 'Orpi':
     #Orpi Viro
     # urlorpi = 'https://www.orpi.com/'
     # endpoint = 'agenceorangerie/acheter'
     st.markdown('## Orpi')
     df = orpi.get_props()
     st.write(df)

csv = convert_df(df)

st.download_button(
     label="Download data as CSV",
     data=csv,
     file_name=f'{ag}_.csv',
     mime='text/csv',
 )
