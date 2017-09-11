#!/usr/bin/python
import requests
from bs4 import BeautifulSoup
from PIL import Image
import sqlite3
import subprocess
import os
import random

HOST = "https://www.space.com"
PATH = os.path.dirname(os.path.realpath(__file__))


def dominant_color(file_url):
    im = Image.open(file_url)
    im = im.resize((1, 1))
    ar = im.getcolors()[0][1]
    color = '#%02x%02x%02x' % ar
    return color

def set_image(file_url):
    cmd = [
        'gsettings', 
		'set', 
		'org.gnome.desktop.background', 
		'picture-uri', 
        'file://{0}'.format(file_url)
    ]
    subprocess.call(cmd)
    d_color = dominant_color(file_url)

    cmd = [
        'gsettings', 
		'set', 
		'org.gnome.desktop.background', 
		'primary-color', 
        d_color
    ]
    subprocess.call(cmd)

def random_image():
    URL = HOST + "/images/" + str(random.randint(1, 10))

    response = requests.get(URL)
    body = BeautifulSoup(response.text, "lxml")

    ul = body.find("ul", {'class': 'mod'})

    list_items = ul.find_all("li", {'class': 'search-item'})

    item = list_items[random.randint(0, len(list_items) - 1)]
    link = item.find("a")
    link = HOST + link.get('href')
    print(link)
    header = item.find("h2").text.strip()
    print(header)
    date_posted = item.find("div", {'class': 'date-posted'}).text.strip()
    print(date_posted)
    text = [i for i in item.find("p", {'class': 'mod-copy'}).strings][0].strip()
    print(text)
    image = item.find("img")
    image_url = image.get('src')

    split_image_url = image_url.split('/')
    split_image_url[4] = "x".join([str(4*int(x)) for x in split_image_url[4].split('x')])

    new_url = "/".join(split_image_url)

    image_response = requests.get(new_url)
    dest_url = '{0}/{1}.jpg'.format(PATH, header)
    output = open(dest_url, 'wb')
    output.write(image_response.content)
    output.close()
    set_image(dest_url)
    with sqlite3.connect('{0}/images.db'.format(PATH)) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS images
                    (
                        date text,
                        header text,
                        body text,
                        link text
                    )''')
        c.execute('''INSERT INTO images(date, header, body, link) 
                        VALUES(?,?,?,?)''', (date_posted, header, text, link))
        conn.commit()

if __name__ == '__main__':
    random_image()
