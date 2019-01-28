#! /usr/bin/env python
# -*- coding: utf-8 -*-
import telebot
import sys
import urllib2
from bs4 import BeautifulSoup
from lxml import html
import os
import time
import subprocess
import signal
import boto3
reload(sys)
sys.setdefaultencoding('utf-8')
session = boto3.session.Session()
s3 = session.client(
    service_name='s3'
)
bot = telebot.TeleBot("787378414:AAGuzZDHyCEJY7ssd0LP_76HaDZ-oRekF2k")
inst_usr = os.environ['INST_USER']
inst_pwd = os.environ['INST_PASSWORD']
link = ""
link1 = ""
admin_id = os.environ['ADMIN_TG_ID']
tg_channel = os.environ['TG_CHANNEL']
try:
    for key in s3.list_objects(Bucket='cloud-cube-eu')['Contents']:
        s3.download_file('cloud-cube-eu', key['Key'], key['Key'])
except: print("Error appeared")
@bot.message_handler(func=lambda message: True)
def message_receive(message):
    f = open("links.txt", "a+")
    link = f.read()
    if (message.text == "/tg_status"): send_status(message)
    elif (message.text == "/inst_status"): send_inst_status(message)
    elif ((message.text == "/start") and (len(link) != 0)): welcome_message(message)
    elif (len(link) == 0):
        if (message.text.find("applespbevent.ru")==-1): 
            bot.send_message(admin_id, "Отправьте ссылку на последнюю опубликованную новость")
        if (message.text.find("applespbevent.ru")!=-1): 
            link = message.text
            f.write(link)
            f.close()
            bot.reply_to(message, "Спасибо, ваша ссылка принята")
            print(link)
    else: bot.send_message(message.chat.id, "Допустимые комманды /tg_status, /inst_status, /start")
def welcome_message(message):
    bot.send_message(message.chat.id, "Этот бот публикует новости с сайта AppleSPBevent.ru в телеграм канал в виде IV")
def send_status(message):
    file = open("links.txt", "r")
    link1 = file.read()
    if (len(link1) != 0):
        soup = BeautifulSoup(urllib2.urlopen(link1), features="lxml")
        link1 = soup.title.string
        if (os.path.isfile("working.ase")):
            work = open("working.ase", "r")
            check = work.read()
        else: check = "0"
        print (check)
        if (check == "1"):
            bot.send_message(message.chat.id, "Бот работает \nПоследняя отправленная новость: "+link1)
            time.sleep(60)
            open("working.ase", "w").close()
        else: bot.reply_to(message, "Бот не работает")
    else: bot.send_message(message.chat.id, "Бот не получил ссылку")
def send_inst_status(message):
    file = open("links.txt", "r")
    link1 = file.read()
    if (len(link1) != 0):
        soup = BeautifulSoup(urllib2.urlopen(link1), features="lxml")
        link1 = soup.title.string
        if (os.path.isfile("inst_working.ase")):
            work = open("inst_working.ase", "r")
            check = work.read()
        else: check = "0"
        print (check)
        if (check == "1"):
            bot.send_message(message.chat.id, "Бот работает \nПоследняя опубликованная новость: "+link1)
            time.sleep(60)
            open("inst_working.ase", "w").close()
        else: bot.reply_to(message, "Бот не работает")
    else: bot.send_message(message.chat.id, "Бот не получил ссылку")
if (os.path.isfile("working.ase")): 
    os.remove("working.ase")
    print("file removed")
#tg_bot = subprocess.Popen("python tg_bot.py "+admin_id+" "+tg_channel, shell=True, preexec_fn=os.setsid)
inst_bot = subprocess.Popen("python inst_bot.py "+inst_usr+" "+inst_pwd, shell=True, preexec_fn=os.setsid)
bot.infinity_polling(True)
