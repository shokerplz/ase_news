import urllib.request
from bs4 import BeautifulSoup
from lxml import html
import requests
import os
import sys
import boto3
import codecs
import time
import json
from instagram_private_api import Client, ClientCompatPatch, MediaRatios
from instagram_private_api_extensions import media
from PIL import Image
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
my_custom_device = {
'phone_manufacturer': 'LGE/lge',
'phone_model': 'RS988',
'phone_device': 'h1',
'android_release': '9.0.0',
'android_version': 28,
'phone_dpi': '580dpi',
'phone_resolution': '1440x2392',
'phone_chipset': 'h1'
}
def from_json(json_object):
    if '__class__' in json_object and json_object['__class__'] == 'bytes':
        return codecs.decode(json_object['__value__'].encode(), 'base64')
    return json_object
if (os.path.isfile(new_settings_file)):
    with open(new_settings_file) as file_data:
        cached_auth = json.load(file_data, object_hook=from_json)
        api = Client(username = usr, password = pwd,auto_patch=True, settings=cached_auth, **my_custom_device)
else: api = Client(username = usr, password = pwd,auto_patch=True, **my_custom_device)
def to_json(python_object):
    if isinstance(python_object, bytes):
        return {'__class__': 'bytes',
                '__value__': codecs.encode(python_object, 'base64').decode()}
    raise TypeError(repr(python_object) + ' is not JSON serializable')
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
def make_square(im, min_size=256, fill_color=(0, 0, 0, 0)):
    x, y = im.size
    size = max(min_size, x, y)
    new_im = Image.new('RGB', (size, size), fill_color)
    new_im.paste(im, ((size - x) // 2, (size - y) // 2))
    new_im.save("picture.jpg")
def update():
        global new_settings_file
        global link
        work = open("inst_working.ase", "a+")
        work_file = work.read()
        if (work_file == ""):
            work.write("1")
        work.close()
        cache_settings = api.settings
        if (os.path.isfile(new_settings_file)):
            os.remove(new_settings_file)
            with open(new_settings_file, 'w') as outfile:
                json.dump(cache_settings, outfile, default=to_json)
        link = open("links.txt", "r").read()
        while(len(link) == 0):
            link = open("links.txt", "r").read()
            time.sleep(5)
        soup = BeautifulSoup(urllib.request.urlopen(link), "lxml")
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
                tags += "#"+tag.get("content", None)
            else: tags += tag.get("content", None)
    link_site = "applespbevent.ru"
    caption = BeautifulSoup(urllib.request.urlopen(link)).title.string+"\n"+describtion+"\n"+link_site+"\n"+tags
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
        photo_data, photo_size = media.prepare_image("picture.jpg", aspect_ratios=MediaRatios.standard)
    api.post_photo(photo_data, photo_size, caption=caption)
    tags = ""
    s3.upload_fileobj(open(new_settings_file, "rb"), 'heroku', new_settings_file)
    print("Success")
check_site()
