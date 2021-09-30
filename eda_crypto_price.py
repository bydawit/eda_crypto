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

## sidebar - crypotocurrency selections
sorted_coin = sorted(df['coin_symbol'])
show_all_coins = col1.selectbox("Start with", ['Selected Coins Only', 'All Coins'])
if show_all_coins == 'All Coins':
    selected_coin = col1.multiselect('Cryptocurrency', sorted_coin, sorted_coin)
else:
    selected_coin = col1.multiselect('Cryptocurrency', sorted_coin, [])

df_selected_coin = df[df['coin_symbol'].isin(selected_coin)]


##sidebar number of coins to display
num_coin = col1.slider('Display Top N Coins', 1, 100, len(selected_coin))
df_coins = df_selected_coin[:num_coin]

## Sidebar - Percent Chnage timeframe
percent_timeframe = col1.selectbox("% change time frame", ['1h', '24h', '7d', '1m', '3m'])
percent_dict = {"3m":'percent_change_90d',"1m":'percent_change_30d',"7d":'percent_change_7d',"24h":'percent_change_24h',"1h":'percent_change_1h'}
selected_percent_timeframe = percent_dict[percent_timeframe]

## Sidebar - Sorting values
sort_value = col1.selectbox('Sort values?', ['Yes', 'No'])

## Sidebar - Plot theme
plot_mode= col1.selectbox('Bar Plot Theme', ['White', 'Dark' ])
if plot_mode == 'Dark':
    plt.style.use('dark_background')
else:
    plt.style.use('default')

col2.subheader("Price Data of Selected Cryptocurrency")
col2.write("Data Dimension: " + str(df_selected_coin.shape[0])+ ' rows and ' + str(df_selected_coin.shape[1]) + ' columns.')

col2.dataframe(df_coins)


# Download CSV data
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="crypto.csv">Download CSV File</a>'
    return href

col2.markdown(filedownload(df_selected_coin), unsafe_allow_html=True)

# Preparing data for Bar plot of % Price change
col2.subheader('Table of % Price Change')
df_change = pd.concat([df_coins.coin_symbol, df_coins.percent_change_1h, df_coins.percent_change_24h, df_coins.percent_change_7d, df_coins.percent_change_30d, df_coins.percent_change_90d], axis = 1)
df_change = df_change.set_index("coin_symbol")
df_change['positive_percent_change_1h'] = df_change['percent_change_1h'] > 0
df_change['positive_percent_change_24h'] = df_change['percent_change_24h'] > 0
df_change['positive_percent_change_7d'] = df_change['percent_change_7d'] > 0
df_change['positive_percent_change_30d'] = df_change['percent_change_30d'] > 0
df_change['positive_percent_change_90d'] = df_change['percent_change_90d'] > 0
col2.dataframe(df_change)

# Conditional creation of Bar plot (time frame)
if len(selected_coin) > 0:
    col3.subheader('Bar plot of % Price change')

    if percent_timeframe == '1h':
        if sort_value == 'Yes':
            df_change = df_change.sort_values(by = ['percent_change_1h'])
        col3.write('*1 hour period*')
        plt.figure(figsize=(5,25))
        plt.subplots_adjust(top = 1 , bottom= 0)
        df_change['percent_change_1h'].plot(kind = 'barh', color = df_change.positive_percent_change_1h.map({True: 'g', False: 'r'}))
        col3.pyplot(plt)
    elif percent_timeframe == '24h':
        if sort_value == 'Yes':
            df_change = df_change.sort_values(by = ['percent_change_24h'])
        col3.write('*24 hour period*')
        plt.figure(figsize=(5,25))
        plt.subplots_adjust(top = 1 , bottom= 0)
        df_change['percent_change_24h'].plot(kind = 'barh', color = df_change.positive_percent_change_24h.map({True: 'g', False: 'r'}))
        col3.pyplot(plt)
    elif percent_timeframe == '7d':
        if sort_value == 'Yes':
            df_change = df_change.sort_values(by = ['percent_change_7d'])
        col3.write('*7 day period*')
        plt.figure(figsize=(5,25))
        plt.subplots_adjust(top = 1 , bottom= 0)
        df_change['percent_change_7d'].plot(kind = 'barh', color = df_change.positive_percent_change_7d.map({True: 'g', False: 'r'}))
        col3.pyplot(plt)
    elif percent_timeframe == '1m':
        if sort_value == 'Yes':
            df_change = df_change.sort_values(by = ['percent_change_30d'])
        col3.write('*1 month period*')
        plt.figure(figsize=(5,25))
        plt.subplots_adjust(top = 1 , bottom= 0)
        df_change['percent_change_30d'].plot(kind = 'barh', color = df_change.positive_percent_change_30d.map({True: 'g', False: 'r'}))
        col3.pyplot(plt)
    else:
        if sort_value == 'Yes':
            df_change = df_change.sort_values(by = ['percent_change_90d'])
        col3.write('*3 month period*')
        plt.figure(figsize=(5,25))
        plt.subplots_adjust(top = 1 , bottom= 0)
        df_change['percent_change_90d'].plot(kind = 'barh', color = df_change.positive_percent_change_90d.map({True: 'g', False: 'r'}))
        col3.pyplot(plt)