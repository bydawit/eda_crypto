from typing import KeysView
import streamlit as st
from PIL import Image
import pandas as pd
import base64
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import json
import time
import PIL.ImageOps

# Page layout
## full width
st.set_page_config(layout="wide")

# Title
image = Image.open('logo.png')
st.image(image, width=500)
st.title("Crypto Price App")
st.markdown("""
This app retrieves cryptocurrency prices for the top 100 cryptocurrency from the **CoinMarketCap**!
""")

# About
expander_bar = st.expander("About")
expander_bar.markdown("""
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn, BeautifulSoup, requests, json, time
* **Data source:** [CoinMarketCap](http://coinmarketcap.com).
* **Credit:** Web scraper adapted from the Medium article *[Web Scraping Crypto Prices With Python](https://towardsdatascience.com/web-scraping-crypto-prices-with-python-41072ea5b5bf)* written by [Bryan Feng](https://medium.com/@bryanf).
""")

# Divide page to 3 columns
col1 = st.sidebar
col2, col3 = st.columns((2,1))

# Sidebar + Main Panel
col1.header("Input Options")

##  Sidebar - Currency Price Unit
currency_price_unit = col1.selectbox('Select currency for price', ('USD', 'BTC', 'ETH'))
key_id = {
    'slug' : 125, 'symbol': 126,
    'quote.BTC.market_cap':19, 'quote.ETH.market_cap':37, 'quote.USD.market_cap':55,
    'quote.BTC.percent_change_1h': 22, 'quote.ETH.percent_change_1h': 40, 'quote.USD.percent_change_1h': 58,
    'quote.BTC.percent_change_24h': 22, 'quote.ETH.percent_change_24h': 40, 'quote.USD.percent_change_24h': 58,
    'quote.BTC.percent_change_7d': 22, 'quote.ETH.percent_change_7d': 40, 'quote.USD.percent_change_7d': 58,
    'quote.BTC.percent_change_30d': 22, 'quote.ETH.percent_change_30d': 40, 'quote.USD.percent_change_30d': 58,
    'quote.BTC.percent_change_90d': 22, 'quote.ETH.percent_change_90d': 40, 'quote.USD.percent_change_90d': 58,
    'quote.BTC.price': 22, 'quote.ETH.price': 40, 'quote.USD.price': 58,
    'quote.BTC.volume_24h': 22, 'quote.ETH.volume_24h': 40, 'quote.USD.volume_24h': 58,

    }
# Webscraping CoinMarketCap data
@st.cache(suppress_st_warning=True)
def load_data():
    cmc = requests.get('https://coinmarketcap.com')
    soup = BeautifulSoup(cmc.content, 'html.parser')

    data = soup.find('script', id='__NEXT_DATA__', type='application/json')
    coins = {}
    coin_data = json.loads(data.contents[0])
    listings = coin_data['props']['initialState']['cryptocurrency']['listingLatest']['data']
    for count, value in enumerate(listings):
        if count == 0:
            continue
        coins[str(value[125])] = value[125]

    coin_name = []
    coin_symbol = []
    market_cap = []
    percent_change_1h = []
    percent_change_24h = []
    percent_change_7d = []
    percent_change_30d = []
    percent_change_90d = []
    price = []
    volume_24h = []

    for i, value in enumerate(listings):
        if i == 0:
            continue
        coin_name.append(value[key_id['slug']])
        coin_symbol.append(value[key_id['symbol']])
        market_cap.append(value[key_id['quote.'+currency_price_unit+'.market_cap']])
        percent_change_1h.append(value[key_id['quote.'+currency_price_unit+'.percent_change_1h']])
        percent_change_24h.append(value[key_id['quote.'+currency_price_unit+'.percent_change_24h']])
        percent_change_7d.append(value[key_id['quote.'+currency_price_unit+'.percent_change_7d']])
        percent_change_30d.append(value[key_id['quote.'+currency_price_unit+'.percent_change_30d']])
        percent_change_90d.append(value[key_id['quote.'+currency_price_unit+'.percent_change_90d']])
        price.append(value[key_id['quote.'+currency_price_unit+'.price']])
        volume_24h.append(value[key_id['quote.'+currency_price_unit+'.volume_24h']])

    df = pd.DataFrame(columns=['coin_name', 'coin_symbol', 'market_cap', 'percent_change_1h', 'percent_change_24h', 'percent_change_7d', 'percent_change_30d', 'percent_change_90d', 'price', 'volume_24h'])
    df['coin_name'] = coin_name
    df['coin_symbol'] = coin_symbol
    df['market_cap'] = market_cap
    df['percent_change_1h'] = percent_change_1h
    df['percent_change_24h'] = percent_change_24h
    df['percent_change_7d'] = percent_change_7d
    df['percent_change_30d'] = percent_change_30d
    df['percent_change_90d'] = percent_change_90d
    df['price'] = price
    df['volume_24h'] = volume_24h
    return df

df = load_data()
