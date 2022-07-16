import re
import time
import requests
import colorama
import traceback
import requests_html
from time import sleep
from lxml import etree
from colorama import Fore
from tqdm.auto import tqdm
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ChromeOptions

def preproc(text):
    text = re.sub(r"'|\\u003+[a-z]{1,}|/+[a-z]{1,}|\\+[a-z]", '', text).replace("'", '').replace('"', "").replace(':', ': ').replace('.', '. ').replace("  ", " ")
    return text

def get_doctor_answer():
    soup = BeautifulSoup(driver.page_source, "lxml")
    result = str(soup.find_all('doctor-topic')[0]).split(" ")

    left, right = None, None

    for i, j in enumerate(result):
        if re.match("doctor-topic-content=", j):
            left = i
        if re.match("post-date=", j):
            right = i

    result = " ".join(result[left+1:right])
    return preproc(result)

def get_patient_question():
    soup = BeautifulSoup(driver.page_source, "lxml")
    result = str(soup.find_all('detail-topic')[0]).split(" ")

    left, right = None, None
    for i, j in enumerate(result):
        if re.match("member-topic-content=", j):
            left = i
        if re.match("member-topic-title=", j):
            right = i

    result = " ".join(result[left+1:right])
    return preproc(result)

def get_href(url):
    global is_answered
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "lxml")
    result = soup.find_all("card-topic")
    results = []

    for i in range(len(result)):
        is_answered = res.html.find('#topic-list > card-topic:nth-child({})'.format(i+1), first=True)
        is_answered = res.html.xpath('//*[@id="topic-list"]/card-topic[{}]'.format(i+1), first=True)
        if int(is_answered.attrs['counter-reply']) > 0:
            result = str(soup.find_all("card-topic")[i]).split(" ")
            left, right = None, None
            for i, j in enumerate(result):
                if re.match("href=", j):
                    left = i
                if re.match("image-url=", j):
                    right = i
            result = " ".join(result[left:right])
            result = re.sub('href=|"', "", result)
            result = "https://www.alodokter.com" + result
            results.append(result)
    return results

option = webdriver.ChromeOptions()
option.add_argument("headless")

answers = []
questions = []

p = 1
pages = 100
pbar = tqdm(total=pages)
while p < pages: # 21977 is max pagination so far
    if p == 1:
        url = "https://www.alodokter.com/komunitas/diskusi/penyakit"
    url = "https://www.alodokter.com/komunitas/diskusi/penyakit/page/{}".format(p)

    ChromeOptions.binary_location = "C:/Program Files/Google/Chrome Beta/Application/chrome.exe"
    driver = webdriver.Chrome("./chromedriver.exe", options=option)
    driver.get(url)

    ses = requests_html.HTMLSession()
    res = ses.get(url)
    html = res.html

    URL = get_href(url)
    for card_url in URL:
        try:
            ChromeOptions.binary_location = "C:/Program Files/Google/Chrome Beta/Application/chrome.exe"
            driver = webdriver.Chrome("./chromedriver.exe")
            driver.get(card_url)
            sleep(1)
            patient_question = get_patient_question()
            doctor_answer = get_doctor_answer()
            questions.append(patient_question)
            answers.append(doctor_answer)
            driver. close()
            print(card_url + Fore.LIGHTGREEN_EX + " ==SUCCEED==")
        except Exception as e:
            print(card_url + Fore.LIGHTRED_EX + " ==FAILED==")
            print(e)
    p+=1
    pbar.update(1)
pbar.close()
