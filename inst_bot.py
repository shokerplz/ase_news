import urllib.request
from bs4 import BeautifulSoup
from lxml import html
import requests
import subprocess
import shutil
import os
import sys
import boto3
import codecs
import time
import json
usr = sys.argv[1]
pwd  = sys.argv[2]
tag = []
tags = ""
images = []
link = ""
past_link = ""
new_settings_file = "cookies.json"
session = boto3.session.Session()
s3 = session.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net'
)
def check_site():
    global tag
    global past_link
    global link
    if (not os.path.isfile("inst_link.txt")):
        open("inst_link.txt", "w").close()
    final_link=update()
    while True:
        final_link = update()
        if (open("inst_link.txt", "r").read()!=final_link):
            open("inst_link.txt", "w").close()
            open("inst_link.txt", "w").write(final_link)
            s3.upload_fileobj(open("inst_link.txt", "rb"), 'heroku', 'inst_link.txt')
            if (os.path.isfile("picture.jpg")):
                os.remove("picture.jpg")
            if (os.path.isfile("picture.png")):
                os.remove("picture.png")
            send_picture(final_link, link)
        time.sleep(30)
def update():
        global new_settings_file
        global link
        work = open("inst_working.ase", "a+")
        work_file = work.read()
        if (work_file == ""):
            work.write("1")
        work.close()
        link = open("links.txt", "r").read()
        while(len(link) == 0):
            link = open("links.txt", "r").read()
            time.sleep(5)
        while True:
            try:
                soup = BeautifulSoup(urllib.request.urlopen(link), "lxml")
            except:
                print("Error appeared. Try again")
                time.sleep(30)
                continue
            break
        for tag in soup.find_all("meta"):
            if tag.get("property", None) == "og:image":
                image_link = tag.get("content", None)
        return(image_link.split("?", 1)[0])
def send_picture(final_link, link):
    global tags
    global new_settings_file
    coup = BeautifulSoup(urllib.request.urlopen(link), "lxml")
    for tag in coup.find_all("meta"):
        if tag.get("property", None) == "og:description":
            describtion = tag.get("content", None)
    for tag in coup.find_all("meta"):
        if tag.get("property", None) == "article:tag":
            if(tag.get("content", None).find("#") == -1):
                tags += "#"+(tag.get("content", None)).replace(" ", "_")+" "
            else: tags += (tag.get("content", None)).replace(" ", "_")+" "
    link_site = "aSPBe.ru"
    caption = BeautifulSoup(urllib.request.urlopen(link)).title.string+"\n"+describtion+"\n"+link_site+"\n"+tags
    print(final_link)
    if (final_link.find("jpeg") != -1):
        urllib.request.urlretrieve(final_link, "picture."+"jpg")
        photo_phile = "picture.jpg"
    else: 
        urllib.request.urlretrieve(final_link, "picture."+final_link[-3:])
        photo_phile = "picture."+final_link[-3:]
    subprocess.call(["php", "PHPPostInst/inst_post.php", usr, pwd, photo_phile, caption])
    tags = ""
    s3.upload_fileobj(open(new_settings_file, "rb"), 'heroku', new_settings_file)
    print("Success")
check_site()
