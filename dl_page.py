import streamlit as st
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

"""
## Web scraping on Streamlit Cloud with Selenium

[![Source](https://img.shields.io/badge/View-Source-<COLOR>.svg)](https://github.com/snehankekre/streamlit-selenium-chrome/)

This is a minimal, reproducible example of how to scrape the web with Selenium and Chrome on Streamlit's Community Cloud.

Fork this repo, and edit `/streamlit_app.py` to customize this app to your heart's desire. :heart:
"""


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

@st.cache_resource
def get_driver():
    return webdriver.Chrome(
        service=Service(
            ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
        ),
        options=options,
    )


def check_TRI_price():
    #driver = get_driver()
    url = 'https://www.set.or.th/en/market/index/tri/overview'
    driver.get(url)

    #SET50 TRI
    index_xpath = '/html/body/div[1]/div/div/div[2]/div/div[2]/div[2]/div/div/div/div/div[2]/div[2]/table/tbody/tr[2]/td[2]'
    index = driver.find_element(By.XPATH, index_xpath)
    update = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div[2]/div[2]/div/div/div/div/div[1]/span')

    index_float = float(index.text.replace(",",""))

    TRI = {'index':index_float, 'update':update.text[6:]}
    #driver.quit()
    return TRI

def check_SET50_price():
    #driver = get_driver()
    url = 'https://www.set.or.th/en/market/index/set50/overview'
    driver.get(url)

    index_xpath = '/html/body/div[1]/div/div/div[2]/div/div[1]/div[2]/div[2]/div[1]/div[2]/div[2]'
    update_xpath = '/html/body/div[1]/div/div/div[2]/div/div[1]/div[3]/div/div[1]/div[2]/span'
    index = driver.find_element(By.XPATH, index_xpath)
    index_update = driver.find_element(By.XPATH, update_xpath)

    index_float = float(index.text.replace(",",""))

    SET50 = {'index':index_float, 'update': index_update.text}

    #driver.quit()

    return SET50

def dl_set50(SET50_data):
    TRI = check_TRI_price()
    SET50 = check_SET50_price()
    check_TRI_date = datetime.strptime(TRI['update'], '%d %b %Y')
    check_data_date = datetime.strptime(SET50_data.index[-1], '%d/%m/%Y')

    if check_TRI_date > check_data_date:
        df_tri = pd.DataFrame({'SET50':[SET50['index']], 'SET50_TRI':[TRI['index']]}, index = [check_TRI_date.strftime("%d/%m/%Y")])
        df_tri.index.name = 'DATE'
        df_tri2 = pd.concat([SET50_data,df_tri])
    else:
        st.write('data is up to date')
    return df_tri2

def del_time(df_to_del):
    date_str = []
    for datee in list(df_to_del.index):
    # Convert to Pandas datetime object
        date_time_obj = pd.to_datetime(datee)

        # Remove time from the datetime object
        date_var = date_time_obj.date()

        # Convert the date object to a string
        date_str.append(date_var.strftime('%Y-%m-%d'))

    df_to_del.index = date_str
    return df_to_del

def download_pricedata(old_price_data):
    old_price_data = del_time(old_price_data)
    tic_list = old_price_data.columns.to_list()
    SET_MAI = []
    for ticker in tic_list:
        SET_MAI.append(ticker + ".BK")
    #get lastest date
    lastest_date = old_price_data.index[-1]
    lastest_date = datetime.strptime(lastest_date, '%Y-%m-%d')+ timedelta(days = 1)
    lastest_date = lastest_date.strftime('%Y-%m-%d')
    present_date = datetime.today().strftime('%Y-%m-%d')
    #download lastest to present date
    price_data2 = yf.download(SET_MAI, start=lastest_date, end=present_date )['Close']
    price_data2.columns = [col[:-3] for col in price_data2.columns]
    #combine
    price_data4 = del_time(old_price_data)
    price_data5 = del_time(price_data2)
    price_data3 = pd.concat([price_data4, price_data5])
    #price_data3 = price_data3.drop_duplicates(subset='Date')
    price_data3.index.name = 'Date'

    return price_data3

def download_new_ticker(new_ticker_file,price_data):
    not_in_list = []
    new_ticker = new_ticker_file['Symbol'].to_list()
    old_ticker = price_data.columns.to_list()
    for ticker in new_ticker:
        if ticker not in old_ticker:
            not_in_list.append(ticker)

    if not_in_list != []:
        first_date = price_data.index[0]
        lastest_date = price_data.index[-1]
        dl_price = yf.download(not_in_list, start=first_date, end=lastest_date )['Close']
        if len(not_in_list) == 1:
            dl_df = dl_price.to_frame(name = not_in_list[0])
        else:
            dl_df = dl_price
        
        combine_price_data = pd.concat([price_data, dl_df], axis = 1)
    else:
        combine_price_data = price_data

    return combine_price_data
def download_all(price_df, tri_df):

    try:
        df_tri = dl_set50(tri_df)
    except:
        st.warning("please reboot")
        st.stop

    if isinstance(df_tri, pd.DataFrame):
        new_price_data = download_pricedata(price_df)
        st.dataframe(df_tri)
        st.dataframe(new_price_data)    
    return [df_tri, new_price_data]
@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')



def select_option(option, tri_df, price_df, ticker_list):
    if option == 'Price':
        df = download_pricedata(price_df)
        name = 'SET_MAI_Close.csv'
    elif option == 'TRI':
        #try:
            #df = dl_set50(tri_df)
            #name = 'SET50TRI_Close.csv'
        #except:
            #st.warning("please reboot")
            df = dl_set50(tri_df)
            name = 'SET50TRI_Close.csv'  
    elif option == 'add new ticker to price':
        df = download_new_ticker(ticker_list)
        name = 'SET_MAI_Close.csv'
    csv = convert_df(df)
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name=name,
        mime="text/csv",
    )

    return df

options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--headless")
driver = get_driver()

st.subheader('download new price')
SET50_data = pd.read_csv('SET50TRI_Close.csv', index_col ='DATE')
price_data = pd.read_csv('SET_MAI_Close.csv', index_col='Date')
Ticker_list = pd.read_csv('listedCompanies_en_US.csv',skiprows=1, encoding = "ISO-8859-1")
#tri_price = download_all(SET50_data, price_data)

with st.form("choose"):
    option = st.selectbox("What file to download?", ("Price", "TRI", "add new ticker to price"))
    submitted = st.form_submit_button(label = 'get data')

if submitted:
    on_click=select_option(option, tri_df = SET50_data, price_df=price_data, ticker_list=Ticker_list)




#download new ticker
st.subheader('download and add new ticker')
st.write('upload price data file and ticker (csv) from set')
st.markdown('<a href = "https://www.set.or.th/en/market/information/securities-list/main">donwload here and save as to csv</p>', unsafe_allow_html=True)
st.write("don't forget to save as csv don't change file name!!!")
