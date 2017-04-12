#
# WebConnection via web sockets
#
import time
import os
import subprocess
import datetime
import pickle
import websocket
import os.path
import json
import base64
import threading
from threading import Timer


class WebConnection:
    def __init__(self, brainz=None, verbose=False):
        self.brainz = brainz
        self.verbose = verbose
        self.ticks = 0
        self.started = False
        self.connected = False
        self.ws = None
        self.wst = None
        self.topic = os.getenv('BOAT', 'TEST')
        self.lock = threading.Lock()

    def __print(self, str):
        if self.verbose:
            print (str)

    def on_message(self, ws, message):
        self.__print("Message received")
        imess = json.loads(message)
        self.__print(imess)
        if imess["action"] == "PING":
            self.__print("ping")
        elif imess["action"] == "SETTINGS":
            self.set_settings(imess)
        elif imess["action"] == "EXTERNALPHOTO":
            self.take_photo()
        else:
            self.__print("Unknown message")

    def on_error(self, ws, error):
        self.__print(error)

    def on_close(self, ws):
        self.connected = False
        self.__print("Websocket closed, Trying to reconnect")
        self.reconnect()

    def on_open(self, ws):
        self.connected = True
        self.subscribe()
        self.send_settings()
        self.__print("Websocket opened")
        self.send_message("Ahoy! Automatic camera is ready!")

    def start(self):
        self.reconnect()
        self.started = True

    def connect(self):
        self.ws = websocket.WebSocketApp("ws://52.49.204.204:8080",
                                on_message = self.on_message,
                                on_error = self.on_error,
                                on_close = self.on_close)
        self.ws.on_open = self.on_open
        self.__print("Websocket started")
        self.wst = threading.Thread(target=self.ws.run_forever)
        self.wst.daemon = True
        self.wst.start()

    def reconnect(self):
        self.__print("Websocket  reconnect")
        if self.connected:
            return
        self.connect()

    # Just to test connection
    def tick(self,tick_time):
        if not self.started:
            return
        self.ticks = self.ticks + 1
        if self.ticks > 1000:
            self.reconnect()
            self.ticks = 0

    def stop(self):
        if not self.started:
            return

    def ping(self):
        self.__print("Ping")
        mess = {}
        mess["action"] = "ping"
        self.ws.send(json.dump(mess))

    def subscribe(self):
        if not self.connected:
            return

        self.__print("Send subscribe")
        mess = {}
        mess["action"]             = "SUBSCRIBE"
        mess["topic"]              = self.topic
        mess["type"]              = "PI"
        self.lock.acquire()
        self.ws.send(json.dumps(mess))
        self.lock.release()

    def send_message(self,message):
        if not self.connected:
            return
        self.__print("Send chat")
        mess = {}
        mess["action"]             = "MESSAGE"
        mess["topic"]              = self.topic
        mess["who"]                = "PI"
        mess["message"]            = message
        self.lock.acquire()
        self.ws.send(json.dumps(mess))
        self.lock.release()


    def set_settings(self,mess):
        self.__print("Set settings!!")

        if mess["camera_mode"] != self.brainz.camera_mode:
            self.brainz.camera_mode_changed(mess["camera_mode"])

    def take_photo(self):
        self.__print("Take photo command from client")
        self.brainz.external_camera.take_photos = 1

    def send_settings(self):
        if not self.started:
            return
        mess = {}
        mess["action"]             = "SETTINGS"
        mess["topic"]              = self.topic
        mess["motion_limit"]       = self.brainz.motion_limit
        mess["camera_mode"]         = self.brainz.camera_mode

        # Properties to commander - knows what to display
        mess["has_video"]  = True
        mess["has_external_camera"]  = True
        mess["has_motion_detector"]  = True

        self.lock.acquire()
        xx = json.dumps(mess)
        self.ws.send(json.dumps(mess))
        self.lock.release()

    def send_image(self,image):
        self.send_image_type("IMAGE",image)

    def send_photo(self,image):
        self.__print('Sending a real photo')
        self.send_image_type("PHOTO",image)

    def send_image_type(self,type,image):
        if not self.connected:
            return
        mess = {}
        mess["action"]             = type
        mess["topic"]              = self.topic
        mess["image"]              = base64.b64encode(image)
        self.lock.acquire()
        self.ws.send(json.dumps(mess))
        self.lock.release()

    def send_status(self):
        self.__print("Send status")
        if not self.connected:
            return
        mess = {}
        mess["action"] = "STATUS"
        mess["topic"]  = self.topic
        mess["motion"] = self.brainz.motion_detector.last_motion
        mess["motion_max"] = self.brainz.motion_detector.motion_max
        mess["motion_avg"] = self.brainz.motion_detector.get_motion_avg()


        self.lock.acquire()
        self.ws.send(json.dumps(mess))
        self.lock.release()
        self.__print("sended status")
