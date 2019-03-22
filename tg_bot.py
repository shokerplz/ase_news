#! /usr/bin/env python
# -*- coding: utf-8 -*-
import telebot
import sys
import urllib.request
from bs4 import BeautifulSoup
from lxml import html
import boto3
import time
import feedparser
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
    f = open("links.txt", "r")
    past_link = f.read()
    print(past_link)
    check_site(past_link)
def check_site(past_link):
        global links
        global work
        f = open("links.txt", "a+")
        data = f.read()
        while True:
            work = open("working.ase", "a+")	
            work_file = work.read()	
            if (work_file == ""):	
                work.write("1")	
                work.close()	
            sys.stdout.flush()
            if (data != past_link):
                open("links.txt", "w").close()
                f.write(past_link)
                f.close()
                s3.upload_fileobj(open("links.txt", "rb"), 'heroku', 'links.txt')
                data = past_link
                f = open("links.txt", "a+")
            while True:
                try:
                    feed = feedparser.parse("https://applespbevent.ru/feed")
                    link_feed = feed.entries[0]['link']
                except:
                    print("Error appeared. Try again")
                    time.sleep(30)
                    continue
                break
            #soup = BeautifulSoup(urllib.request.urlopen("https://applespbevent.ru/"), features="lxml")
            #soup = soup.find("div", {"class": "post-inner post-hover"})
            #for link in soup.find_all('a', href=True):
                #links.append(link.get('href'))
            if (past_link != link_feed):
                past_link = link_feed
                bot_send(link_feed)
            time.sleep(30)
def bot_send(message):
    while True:
        try:
            soup1 = BeautifulSoup(urllib.request.urlopen(message))
            pc_link = "<a href='"+message+"'>"+"Прямая ссылка на новость"+"</a>"
            message = message[8:]
            for tag in soup1.find_all("meta"):
                if tag.get("property", None) == "og:description":
                    describtion = tag.get("content", None)
            message = "https://t.me/iv?url=https%3A%2F%2F"+message+"%2F&rhash=588c4d85708c86"
            print(message)
            if (" | Apple SPb Event" in soup1.title.string):
                name = soup1.title.string[:-18]
            else: name = soup1.title.string
            url_html = "<a href='"+message+"'>"+name+"</a> "+"\n"+pc_link
            bot.send_message(sys.argv[2], url_html, parse_mode = 'HTML')
        except: 
            print("Error appeared. Try again")
            time.sleep(30)
            continue
        break
check_file()
