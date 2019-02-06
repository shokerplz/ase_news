#! /usr/bin/env python
# -*- coding: utf-8 -*-
import telebot
import sys
import urllib.request
from bs4 import BeautifulSoup
from lxml import html
import boto3
import time
url_html = ""
links = []
past_link = ""
bot = telebot.TeleBot("787378414:AAGuzZDHyCEJY7ssd0LP_76HaDZ-oRekF2k")
session = boto3.session.Session()
s3 = session.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net'
)
def check_file():
    global past_link
    f = open("links.txt", "a+")
    past_link = f.read()
    print(past_link)
    check_site(past_link)
def check_site(past_link):
        global links
        global work
        f = open("links.txt", "a+")
        data = f.read()
        while True:
            if (data != past_link):
                open("links.txt", "w").close()
                f.write(past_link)
                f.close()
                s3.upload_fileobj(open("links.txt", "rb"), 'heroku', 'links.txt')
                data = past_link
                f = open("links.txt", "a+")
            soup = BeautifulSoup(urllib.request.urlopen("https://applespbevent.ru/"), features="lxml")
            soup = soup.find("div", {"class": "post-inner post-hover"})
            for link in soup.find_all('a', href=True):
                links.append(link.get('href'))
            if (past_link != links[0]):
                past_link = links[0]
            time.sleep(30)
            del links[:]
def bot_send(message):
        soup1 = BeautifulSoup(urllib.request.urlopen(message))
        pc_link = "<a href='"+message+"'>"+"Прямая ссылка"+"</a>"
        message = message[8:]
        message = "https://t.me/iv?url=https%3A%2F%2F"+message+"%2F&rhash=588c4d85708c86"
        print(message)
        url_html = "<a href='"+message+"'>"+soup1.title.string+"</a> "+ pc_link
        bot.send_message(sys.argv[2], url_html, parse_mode = 'HTML')
check_file()
