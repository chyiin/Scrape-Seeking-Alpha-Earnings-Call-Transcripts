import time
import bs4 as bs
import datetime
import pandas as pd
import numpy as np
from splinter import Browser
from bs4 import BeautifulSoup as bs
from urllib.request import FancyURLopener  
from random import choice 
from selenium import webdriver
from selenium.webdriver import ChromeOptions

# user_agents = ['Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)']

class MyOpener(FancyURLopener, object):
    version = choice('Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)')

def init_browser():
    chrome_options = webdriver.ChromeOptions(); 
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser("chrome", **executable_path, headless=False, options=chrome_options) # , desired_capabilities=caps)

def getTranscriptInfo(ticker, browser_):   
    url = 'https://seekingalpha.com/symbol/' + ticker + '/transcripts' # 'https://www.cmoney.tw/forum/popular/buzz' # 
    browser = browser_
    browser.visit(url)
    for x in range(1, 10):
        browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(3)
    html = browser.html
    soup = bs(html, "html.parser")
    search_results = []
    results = soup.find_all("article")
    for result in results:
        try:
            title = result.find('h3').text
            url = result.find('a')['href']
            date = result.find('span').text
            date = pd.to_datetime(date,infer_datetime_format=True)
            if (date < datetime.datetime(2018, 1, 1)) and ('- Earnings Call Transcript' in title):
                # print(title)
                # print(url)
                # print(date)
                # print('----------------------------------------')
                results_dict = {
                    "title": title,
                    "url": url,
                    "date": date,
                    "ticker": ticker,
                }
                search_results.append(results_dict)
                print(len(search_results))
        except:
            continue
    return search_results 

def getTextFromArticle(url, browser_):

    url_begin = 'https://seekingalpha.com/'
    url_end = url
    browser = browser_
    browser.visit(url_begin+url_end)
    time.sleep(10)
    button = browser.find_by_xpath('//*[@id="root"]/div/div[1]/header/nav/div[1]/div/div[2]/button')
    button.click()
    browser.fill('email', '###')
    browser.fill('password', '###')
    button = browser.find_by_xpath('//*[@id="root"]/div/div[2]/div/div[2]/div/form/button')
    button.click()
    html = browser.html
    soup = bs(html, "html.parser")
    texts = soup.find_all('p')
    total_doc = ''
    for text in texts:
        total_doc += text.text + '\n'
    return total_doc

if __name__ == '__main__':

    company_id = ['MU', 'TSM', 'ASML', 'TSLA', 'INTC', 'META', 'TXN', 'MSFT', 'GOOGL', 'AMD', 'TER', 'AMZN', 'AAPL', 'NXPI', 'QRVO', 'LITE', 'QCOM', 'SWKS', 'IIVI', 'NVDA', 'AMAT', 'ADI', 'MRVL', 'AVGO']

    # myopener = MyOpener()
    browser = init_browser()
    # for id in company_id:
    id = 'MU'
    transcript_list = getTranscriptInfo(id, browser)
    output_df = pd.DataFrame(transcript_list)
    output_df.to_csv(f'transcripts_url/{id}_url.csv', index=False)
    output_df['text'] = np.nan
    for index, row in output_df.iterrows():
        try:
            text = getTextFromArticle(row['url'], browser)
            row['text'] = text
        except:
            continue
    # comb_transcript.extend(transcript_list)
    output_df.to_csv(f'transcripts/{id}_transcripts.csv', index=False)
