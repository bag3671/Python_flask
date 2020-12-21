import numpy as np 
import pandas as pd 
import matplotlib as mpl 
import matplotlib.pyplot as plt 
from wordcloud import WordCloud, STOPWORDS
from PIL import Image
import nltk, re
from konlpy.tag import Okt
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time

def engCloud(text, stop_words, mask_file, img_file, max_words=1000):
    stopwords = set(STOPWORDS)
    for sw in stop_words:
        stopwords.add(sw)

    if mask_file == None:
        wc = WordCloud(background_color='black', width=800, height=800, max_words=max_words, stopwords=stopwords)
    else:
        mask = np.array(Image.open(mask_file))
        wc = WordCloud(background_color='white', width=800, height=800, max_words=max_words, mask=mask, stopwords=stopwords)
    wc = wc.generate(text)
    plt.figure(figsize=(8,8), dpi=100)
    ax = plt.axes([0,0,1,1])
    #plt.imshow(wc, interpolation='bilinear')
    plt.imshow(wc, interpolation='nearest', aspect='equal')
    plt.axis('off')
    plt.savefig(img_file)

def hanCloud(text, stop_words, mask_file, img_file, max_words=1000):
    mpl.rc('font', family='Malgun Gothic')
    mpl.rc('axes', unicode_minus=False)
    okt = Okt()
    tokens = okt.nouns(text)
    new_text = []
    for token in tokens:
        text = re.sub('[a-zA-Z0-9]', '', token)
        new_text.append(text)
    new_text = [word for word in new_text if word not in stop_words]
    han_text = nltk.Text(new_text, name='한글 텍스트')
    data = han_text.vocab().most_common(300)
    if mask_file == None:
        wc = WordCloud(font_path='c:/Windows/Fonts/malgun.ttf',
                        width=800, height=800,
                        relative_scaling = 0.2, background_color='black',
                        ).generate_from_frequencies(dict(data))
    else:
        mask = np.array(Image.open(mask_file))
        wc = WordCloud(font_path='c:/Windows/Fonts/malgun.ttf',
                        width=800, height=800,
                        relative_scaling = 0.2, mask=mask,
                        background_color='white',
                        ).generate_from_frequencies(dict(data))

    plt.figure(figsize=(8,8), dpi=100)
    ax = plt.axes([0,0,1,1])
    #plt.imshow(wc, interpolation='bilinear')
    plt.imshow(wc, interpolation='nearest', aspect='equal')
    plt.axis('off')
    plt.savefig(img_file)

def sports_wordCloud():
    driver = webdriver.Chrome('D:/workspace/data-home/05.Crawling/chromedriver.exe')
    text = ''
    events = ['kbaseball','wbaseball','kfootball','wfootball','basketball','volleyball','golf']
    for event in events:
        url = f'https://sports.news.naver.com/{event}/news/index.nhn?page=1&isphoto=N'
        driver.get(url)
        while True:
            paginate = driver.find_element_by_css_selector('.paginate')
            pagelist = paginate.find_elements_by_css_selector('a')
            if driver.find_elements_by_css_selector('.content_area > #_pageList > a')[-1].text != '다음':
                pagelist[-1].click()
                break
            pagelist[-1].click()
            time.sleep(1)
        time.sleep(1)
        endpage = driver.find_element_by_css_selector('#_pageList > strong').text
        print(endpage)
        for page in range(1,int(endpage)+1):
            url = f'https://sports.news.naver.com/{event}/news/index.nhn?page={page}&isphoto=N'
            driver.get(url)
            titles = driver.find_elements_by_css_selector('.text > .title')
            for title in titles:
                if title.text != '': 
                    text += '\n' + title.text
    with open('static/data/sports.txt','w' ,encoding='utf-8')  as file:
        file.write(text)
    return text
