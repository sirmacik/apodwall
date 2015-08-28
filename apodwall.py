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

import sys
import os
import time
from pattern.web import download, plaintext
from bs4 import BeautifulSoup
import Tkinter as tk
from PIL import Image, ImageFont, ImageDraw, ImageFile
import textwrap
import subprocess

home = os.path.expanduser("~")
directory = home+"/.apod"

print directory
if not os.path.exists(directory):
    os.makedirs(directory)

os.chdir(directory)

ImageFile.LOAD_TRUNCATED_IMAGES = True
root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = 766

# print screen_width 
timestamp = time.strftime('%Y%m%d')
website = "http://apod.nasa.gov/apod/"
html = download(website+"astropix.html", cached=False, unicode=True)

soup = BeautifulSoup(html, "html.parser")
img = soup.img.parent.get('href')

explanation = soup.find("b", string=" Explanation: ")
explanation = str(explanation.parent)

explanation2 = BeautifulSoup(explanation, "html.parser")
explanation2 = explanation2.p.center
explanation2 = str(explanation2)

text = explanation.replace(explanation2, "")
text = plaintext(text, linebreaks=2, indentation=True)
text = str(text).replace("\n", "")
text = textwrap.wrap(text, width=140)
w = screen_width
y_text = screen_height

img = website+img                           
imgdw = download(img, unicode=False)
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

for line in text:
    width, height = font.getsize(line)
    draw.text(((w - width) / 2, y_text), line, font=font, fill=FOREGROUND)
    y_text += height

#draw.text((0, 0),text,(255,255,255))
wall.save(imgname)

imgpath = directory + "/" + imgname
uri = "'file://%s'" % imgpath

args = ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", uri]
opts = ["gsettings", "set", "org.gnome.desktop.background", "picture-options", "zoom"]


subprocess.Popen(opts)
subprocess.Popen(args)

    
#print img
