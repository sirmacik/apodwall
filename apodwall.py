#!/usr/bin/env python
# -*- coding: utf-8 -*-

# apodwall
# Copyright (C) 2015  Marcin Karpezo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

#import sys
import os
import time
from pattern.web import download, plaintext
from bs4 import BeautifulSoup
import Tkinter as tk
from PIL import Image, ImageFont, ImageDraw, ImageFile
import textwrap
import subprocess

# Get user home directory and set path for download
home = os.path.expanduser("~")
directory = home+"/.apod"

# If working directory doesn't exist create one
if not os.path.exists(directory):
    os.makedirs(directory)

# Go to working directory
os.chdir(directory)

# Make it work in some cases
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Get information about the main screen
def get_screensizecmd():
    command = ["xrandr", "--current", "--screen", "0"]
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    return iter(p.stdout.readline, b'')

def get_screensize():
    i = 0    
    for line in get_screensizecmd():
        if i == 0:
            i += 1
        elif i == 1:
            str(line)
            # possible output:
            #     LVDS1 connected primary 1366x768+0+0 (normal left inverted right x axis y axis) 256mm x 144mm
            # so we need to parse it
            line = line.split()

            # get the part with just the screen resolution
            line = line[3]

            # convert it to a list
            line = line.split("x")

            # we have screen width
            screenw = int(line[0])

            # screen height still needs some work since it loos like '768+0+0'
            screenh = line[1]
            screenh = screenh.split("+")
            screenh = int(screenh[0])

            i += 1
        else:
            break
    return (screenw, screenh)

screen_width, screen_height = get_screensize()

# Set timestamp format
timestamp = time.strftime('%Y%m%d')

# set url for download and download current website, no cache
website = "http://apod.nasa.gov/apod/"
html = download(website+"astropix.html", cached=False, unicode=True)

soup = BeautifulSoup(html, "html.parser")

def get_explanation(soup):
    explanation = soup.find("b", string=" Explanation: ")
    explanation = str(explanation.parent)
    
    explanation2 = BeautifulSoup(explanation, "html.parser")
    explanation2 = explanation2.p.center
    explanation2 = str(explanation2)
    
    text = explanation.replace(explanation2, "")
    text = plaintext(text, linebreaks=2, indentation=True)
    text = str(text).replace("\n", "")
    text = textwrap.wrap(text, width=140)
    return text
    
def get_image():
    img = soup.img.parent.get('href')

    w = screen_width
    h = screen_height

    img = website+img                           
    imgdw = download(img, cached=False, unicode=False)
    imgname = timestamp+"_apod.jpg"
    imgfile = open(imgname, "wb")
    imgfile.write(imgdw)
    imgfile.close

    wall = Image.open(imgname)
    draw = ImageDraw.Draw(wall)
    FOREGROUND = (255, 255, 255)
    #font = ImageFont.truetype("sans-serif.ttf", 16)
    font_path = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
    font = ImageFont.truetype(font_path, 20, encoding='unic')
    y_text = 0
    for line in text:
        width, height = font.getsize(line)
        y_text += height

    y_text = screen_height - y_text
    for line in text:
        draw.text(((w - width) / 2, y_text), line, font=font, fill=FOREGROUND)
        y_text += height

        #draw.text((0, 0),text,(255,255,255))
    wall.save(imgname)
    
    imgpath = directory + "/" + imgname
    uri = "'file://%s'" % imgpath
    return uri

def set_wall(uri):
    args = ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", uri]
    opts = ["gsettings", "set", "org.gnome.desktop.background", "picture-options", "stretched"]
    
    subprocess.Popen(opts)
    subprocess.Popen(args)


text = get_explanation(soup)
uri = get_image()
set_wall(uri)

#print img
