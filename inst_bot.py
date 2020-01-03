import urllib.request
from bs4 import BeautifulSoup
import subprocess
from PIL import Image
import os
from instagram_private_api_extensions import media
from instagram_private_api import MediaRatios
import sys
import boto3
import time
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
class AppURLopener(urllib.request.FancyURLopener):
    version = "Mozilla/5.0"
opener = AppURLopener()
def make_square(im, min_size=256, fill_color=(0, 0, 0, 0)):	
    x, y = im.size	
    size = max(min_size, x, y)
    if size > 1080: size = 1070	
    new_im = Image.new('RGB', (size, size), fill_color)	
    new_im.paste(im, ((size - x) // 2, (size - y) // 2))	
    new_im.save("picture.jpg")
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
                soup = BeautifulSoup(opener.open(link))
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
    coup = BeautifulSoup(opener.open(link))
    for tag in coup.find_all("meta"):
        if tag.get("property", None) == "og:description":
            describtion = tag.get("content", None)
    for tag in coup.find_all("meta"):
        if tag.get("property", None) == "article:tag":
            if(tag.get("content", None).find("#") == -1):
                tags += "#"+(tag.get("content", None)).replace(" ", "_")+" "
            else: tags += (tag.get("content", None)).replace(" ", "_")+" "
    link_site = "aSPBe.ru"
    caption = BeautifulSoup(opener.open(link)).title.string+"\n"+describtion+"\n"+link_site+"\n"+tags
    print(final_link)
    if (final_link.find("jpeg") != -1):
        urllib.request.urlretrieve(final_link, "picture."+"jpg")
    else: urllib.request.urlretrieve(final_link, "picture."+final_link[-3:])
    if (final_link[-3:] == "png"):
        im = Image.open("picture.png")
        rgb_im = im.convert('RGB')
        rgb_im.save('picture.jpg')
    photo_data, photo_size = media.prepare_image("picture.jpg", aspect_ratios=MediaRatios.standard)
    if(photo_size[0]>photo_size[1] or photo_size[1]>photo_size[0]):
        work_image = Image.open("picture.jpg")
        make_square(work_image) 
    subprocess.call(["php", "inst_post.php", usr, pwd, "picture.jpg", caption])
    tags = ""
    s3.upload_fileobj(open('instagram.sqlite', "rb"), 'heroku', 'instagram.sqlite')
    s3.upload_fileobj(open('inst_link.txt', "rb"), 'heroku', 'inst_link.txt')
    print("Success")
check_site()
