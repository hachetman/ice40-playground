#!/usr/bin/env python3

from PIL import Image, ImageDraw, ImageFont
from datetime import datetime


class updater():
    def __init__(self):
        self.im = Image.new('RGBA', (64, 32), (0,0,0,0))
        self.fnt = ImageFont.load("./fonts/7x13.pil")
        self.draw = ImageDraw.Draw(self.im)

    def update(self):
        now = datetime.now()
        self.draw.rectangle((0, 0, 64, 32), fill=(0, 0, 0, 0))
        self.draw.text((3, -1), now.strftime("%H %M %S"),
                       font=self.fnt, fill=(32, 32, 32, 0))
        return self.im
