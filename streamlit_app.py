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

with st.echo():
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
    
    def dl_set50():
        TRI = check_TRI_price()
        SET50 = check_SET50_price()
        check_TRI_date = datetime.strptime(TRI['update'], '%d %b %Y')
        df = pd.DataFrame({'SET50':[SET50['index']], 'SET50_TRI':[TRI['index']]}, index = [check_TRI_date.strftime("%d/%m/%Y")])

        return df

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
        old_price_data = pd.read_csv("SET_MAI_Close.csv", index_col='Date')
        old_price_data = del_time(old_price_data)
        tic_list = old_price_data.columns.to_list()
        SET_MAI = []
        for ticker in tic_list:
            SET_MAI.append(ticker + ".BK")
        #get lastest date
        lastest_date = old_price_data.index[-1]
        lastest_date = datetime.strptime(lastest_date, '%Y-%m-%d')+ timedelta(days = 1)
        lastest_date = lastest_date.strftime('%Y-%m-%d')
        #present_date = (datetime.today() - timedelta(days = 1)).strftime('%Y-%m-%d')
        present_date = datetime.today().strftime('%Y-%m-%d')
        #download lastest to present date
        price_data2 = yf.download(SET_MAI, start=lastest_date, end=present_date )['Close']
        price_data2.columns = [col[:-3] for col in price_data2.columns]
        #combine
        price_data4 = del_time(price_data)
        price_data5 = del_time(price_data2)
        price_data3 = pd.concat([price_data4, price_data5])
        #price_data3 = price_data3.drop_duplicates(subset='Date')
        price_data3.index.name = 'Date'

        return price_data
    def download_set50():
        options = Options()
        options.add_argument("--disable-gpu")
        options.add_argument("--headless")
        driver = get_driver()
        TRI_url = 'https://www.set.or.th/en/market/index/tri/overview'
        driver.get(TRI_url)

        #SET50 TRI
        index_xpath = '/html/body/div[1]/div/div/div[2]/div/div[2]/div[2]/div/div/div/div/div[2]/div[2]/table/tbody/tr[2]/td[2]'
        index = driver.find_element(By.XPATH, index_xpath)
        update = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div[2]/div[2]/div/div/div/div/div[1]/span')

        index_float = float(index.text.replace(",",""))

        TRI = {'index':index_float, 'update':update.text[6:]}


        SET50_url = 'https://www.set.or.th/en/market/index/set50/overview'
        driver.get(SET50_url)

        index_xpath = '/html/body/div[1]/div/div/div[2]/div/div[1]/div[2]/div[2]/div[1]/div[2]/div[2]'
        update_xpath = '/html/body/div[1]/div/div/div[2]/div/div[1]/div[3]/div/div[1]/div[2]/span'
        index = driver.find_element(By.XPATH, index_xpath)
        index_update = driver.find_element(By.XPATH, update_xpath)

        index_float = float(index.text.replace(",",""))

        SET50 = {'index':index_float, 'update': index_update.text}

        check_TRI_date = datetime.strptime(TRI['update'], '%d %b %Y')
        df = pd.DataFrame({'SET50':[SET50['index']], 'SET50_TRI':[TRI['index']]}, index = [check_TRI_date.strftime("%d/%m/%Y")])

        return df


    try:
        df_tri = download_set50()
        st.dataframe(df_tri)
    except:
        st.write("please reboot")




    uploaded_files = st.file_uploader("Choose a CSV file", accept_multiple_files=True)
    if len(uploaded_files) == 2:

        st.write(uploaded_files)

        if uploaded_files[0].name == 'SET50TRI_Close.csv':
            SET50_data = pd.read_csv(uploaded_files[0], index_col ='DATE')
            price_data = pd.read_csv(uploaded_files[1], index_col='Date')
        else:
            SET50_data = pd.read_csv(uploaded_files[1], index_col ='Date')
            price_data = pd.read_csv(uploaded_files[0], index_col='DATE')

        st.dataframe(SET50_data.tail())
        st.dataframe(price_data.tail())

    #pd.read_excel('https://www.set.or.th/dat/eod/listedcompany/static/listedCompanies_th_TH.xls', engine='calamine', skiprows=1)