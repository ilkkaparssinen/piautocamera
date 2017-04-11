from __future__ import division

import time
import os
import subprocess
import datetime

import picamera
import picamera.array
import numpy as np


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
            self.brainz.external_camera.take_photo()
            self.brainz.external_camera.take_photo()
            self.brainz.external_camera.take_photo()
            self.detected = True

    def tick(self):
        pass

    def get_motion_avg(self):
        if self.motion_count == 0:
            return 0
        avg = self.motion_sum / self.motion_count
        # Zero variables
        self.motion_sum = 0
        self.motion_count = 0
        self.motion_max = 0
        return avg


    def start(self):
        self.started = True
        self.camera = picamera.PiCamera()
        self.camera.resolution = (1280, 960)
        self.camera.framerate = 10

        self.__print('Waiting 2 seconds for the camera to warm up')
        time.sleep(2)

        self.__print('Start recording')
        self.camera.start_recording(
                    '/dev/null', format='h264',
                    motion_output=MyMotionDetector(self.camera, self)
                )
    def stop(self):
        if not self.started:
            return
        self.camera.stop_recording()
        self.started = False


class MyMotionDetector(picamera.array.PiMotionAnalysis):
    def __init__(self, camera, handler):
        super(MyMotionDetector, self).__init__(camera)
        self.handler = handler
        self.first = True

    def analyse(self, a):
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
        if self.last_motion > self.handler.brainz.motion_limit:
            # Ignore the first detection
            if self.first:
                self.first = False
                return
            self.handler.motion_detected()


