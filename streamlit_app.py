import streamlit as st
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import numpy as np
import pandas as pd
#import yfinance as yf
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
        driver = get_driver()
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

        driver.quit()

        return SET50
    

    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    driver = get_driver()
    TRI = check_TRI_price()
    SET50 = check_SET50_price()
    check_TRI_date = datetime.strptime(TRI['update'], '%d %b %Y')

    #st.write(SET50)
    df_tri = pd.DataFrame({'SET50':[SET50['index']], 'SET50_TRI':[TRI['index']]}, index = [check_TRI_date.strftime("%d/%m/%Y")])
    #df_tri = pd.DataFrame({'SET50_TRI':[TRI['index']]}, index = [check_TRI_date.strftime("%d/%m/%Y")])
    st.dataframe(df_tri)
    #st.code(driver.page_source)
