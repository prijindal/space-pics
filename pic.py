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

IMAGE_OF_DAY = True
TOTAL_PAGES = 75

def dominant_color(file_url):
    im = Image.open(file_url)
    width, height = im.size
    print(width, height)
    colors = im.getcolors(width*height)
    max_occurence, most_present = 0, 0
    try:
        for c in colors:
            if c[0] > max_occurence:
                (max_occurence, most_present) = c
        print(most_present)
        return '#%02x%02x%02x' % most_present
    except TypeError:
        raise Exception("Too many colors in the image")
    # im = im.resize((1, 1))
    # ar = im.getcolors()[0][1]
    # color = '#%02x%02x%02x' % ar
    # return color

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
    RAND_LIMIT = TOTAL_PAGES
    if IMAGE_OF_DAY:
        RAND_LIMIT = 1
    URL = HOST + "/images/" + str(random.randint(1, RAND_LIMIT)) + "?type=wallpaper"

    response = requests.get(URL)
    body = BeautifulSoup(response.text, "html.parser")

    ul = body.find("ul", {'class': 'mod'})

    list_items = ul.find_all("li", {'class': 'search-item'})

    if IMAGE_OF_DAY:
        list_items = list_items[0:1]

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
    dest_url = '{0}/{1} | {2}.jpg'.format(PATH, header, date_posted)
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
