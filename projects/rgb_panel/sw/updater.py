#!/usr/bin/env python3

from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import threading
import time
import requests
import json


class updater(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.data_lock = threading.Lock()
        self.im = Image.new('RGBA', (64, 32), (0,0,0,0))
        self.time_font = ImageFont.load("./fonts/9x15.pil")
        self.status_font = ImageFont.load("./fonts/6x9.pil")
        self.time_color = (255, 255, 255, 0)
        self.status_color = (255, 255, 255, 0)
        self.co2_color = (255, 255, 255, 0)
        self.draw = ImageDraw.Draw(self.im)
        self.timer = time.time()
        self.base_url="https://dynamic.grumbein.de/api/states/"
        self.headers = {
                'Authorization': 'Bearer <enter bearer>',
                'content-type': 'application/json',
            }
        self.temperature = 0
        self.co2 = 0
        self.humidity = 0
        self.rain = 0.0
        self.timer = time.time()
        self.ping = "100"
        self.sun = "above_horizon"
        self.seconds = 0

    def get_draw_buffer(self):
        self.data_lock.acquire()
        if self.sun == "above_horizon":
            self.time_color = (255, 255, 255, 0)
            self.status_color = (255, 255, 255, 0)
            self.co2_color = (0, 255, 0, 0)
            if self.co2 > 700:
                self.co2_color = (255, 255, 0, 0)
            if self.co2 > 900:
                self.co2_color = (255, 165, 0, 0)
            if self.co2 > 1000:
                self.co2_color = (255, 0, 0, 0)
        else:
            self.time_color = (32, 32, 32, 0)
            self.status_color = (32, 32, 32, 0)
            self.co2_color = (0, 32, 0, 0)
            if self.co2 > 700:
                self.co2_color = (32, 32, 0, 0)
            if self.co2 > 900:
                self.co2_color = (32, 20, 0, 0)
            if self.co2 > 1000:
                self.co2_color = (32, 0, 0, 0)

        now = datetime.now()
        self.draw.rectangle((0, 0, 64, 32), fill=(0, 0, 0, 0))
        self.draw.text((0, -2), now.strftime("%H"),
                       font=self.time_font,
                       fill=self.time_color)
        self.draw.text((24, -2), now.strftime("%M"),
                       font=self.time_font,
                       fill=self.time_color)
        self.draw.text((46, -2), now.strftime("%S"),
                       font=self.time_font,
                       fill=self.time_color)
        self.draw.text((0, 10), "T:" + str(self.temperature),
                       font=self.status_font,
                       fill=self.status_color)
        self.draw.text((23, 9), "°",
                       font=self.status_font,
                       fill=self.status_color)
        self.draw.text((0, 17), "P:" + str(self.ping),
                       font=self.status_font,
                       fill=self.status_color)
        self.draw.text((35, 10), "H:" + str(self.humidity) + "%",
                       font=self.status_font,
                       fill=self.status_color)
        self.draw.text((35, 17), "R:" + str(self.rain),
                       font=self.status_font,
                       fill=self.status_color)
        self.draw.text((7, 25), "CO2:" + str(self.co2),
                       font=self.status_font,
                       fill=self.co2_color)
        self.data_lock.release()
        return self.im

    def request_wrapper(self, url, headers):
        try:
            response = requests.get(url, headers=headers)
        except Exception as e:
            print(time.strftime("%d:%m %H:%M") + " Request exception Homeassistant")
            print(e)
        return response

    def update(self):
        print("updating")
        self.data_lock.acquire()
        try:
            print(time.strftime("%d:%m %H:%M") + " Updating")
            response = self.request_wrapper(self.base_url + "sun.sun",
                                             self.headers)
            response_json = json.loads(response.text)

            self.sun = response_json['state']

            response = self.request_wrapper(self.base_url + "sensor.co2",
                                            self.headers)
            response_json = json.loads(response.text)
            self.co2 = int(response_json['state'])

            response = self.request_wrapper(self.base_url + "binary_sensor.ping_heise_de", self.headers)
            response_json = json.loads(response.text)
            self.ping = int(float(response_json['attributes']['round_trip_time_avg']))

            response = self.request_wrapper(self.base_url + "weather.home",
                                             self.headers)
            response_json = json.loads(response.text)
            print(response_json['attributes']['forecast'][0]['precipitation'])                                    
            self.humidity = int(response_json['attributes']['humidity'])
            self.temperature = int(response_json['attributes']['temperature'])
            self.rain = int(response_json['attributes']['forecast'][0]['precipitation'])                        
        except Exception as e:
                print(e)
        self.data_lock.release()

    def run(self):
        self.update()
        while True:
            time.sleep(10)
            if (time.time() - self.timer > 60):
                self.update()
                self.timer = time.time()
