from __future__ import division

import time
import os
import subprocess
import datetime

import picamera
import picamera.array
import threading
import numpy as np
import logging
logging.basicConfig()

class MyMotionDetector(picamera.array.PiMotionAnalysis):
    def __init__(self, camera, handler):
        super(MyMotionDetector, self).__init__(camera)
        self.handler = handler
        self.first = True

    def analyse(self, a):
        if not self.handler.started:
            return
        a = np.sqrt(
            np.square(a['x'].astype(np.float)) +
            np.square(a['y'].astype(np.float))
        ).clip(0, 255).astype(np.uint8)
        self.handler.last_motion = (a > 60).sum()
        # Just keep statistics
        self.handler.motion_sum = self.handler.motion_sum + self.handler.last_motion
        self.handler.motion_count = self.handler.motion_count + 1
        self.handler.motion_max = max(self.handler.motion_max, self.handler.last_motion)
        # Trigger motion detecttion if over the limit
        if self.handler.last_motion > self.handler.brainz.motion_limit:
            # Ignore the first detection
            if self.first:
                self.first = False
                return
            print("movement")
            self.handler.motion_detected()

class MotionDetector:
    def __init__(self, brainz=None, verbose=False):
        self.brainz = brainz
        self.verbose = verbose
        self.camera = None
        self.detected = False
        self.started = False
        self.take_photo = False
        self.last_motion = 0
        self.motion_sum = 0
        self.motion_count = 0
        self.motion_max = 0

    def __print(self, str):
        if self.verbose:
            print (str)

    def motion_detected(self):
        if self.started:
            # Movement - take 3 photos as fast that camera can
            # 
            print("Request 3 photos")
            self.brainz.external_camera.take_photos = 3
            self.detected = True

    def tick(self):
        pass

    def get_motion_avg(self):
        print ("Get motion average")
        if self.motion_count == 0:
            return 0
        avg = self.motion_sum / self.motion_count
        # Zero variables
        self.motion_sum = 0
        self.motion_count = 0
        self.motion_max = 0
        return avg


    def start(self):
        print("START MOTION DETECTOR")
        self.started = True
        self.camera = self.brainz.camera
        self.camera.resolution = (1280, 960)
        self.camera.framerate = 10

        self.__print('Waiting 2 seconds for the camera to warm up')
        time.sleep(2)

        with MyMotionDetector(self.camera, self) as output:
            self.__print('Start recording')
            self.camera.start_recording(
                    '/dev/null', format='h264', motion_output=output)
        print("MOTION DETECTOR STARTED")

    def stop(self):
        if not self.started:
            return
        self.started = False
        print("STOP MOTION DETECTOR")
        time.sleep(0.1)
        try:
            self.camera.stop_recording()
        except:
            pass

        time.sleep(0.1)
        print("MOTION DETECTOR STOPPED")


