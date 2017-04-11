#
# Brainz for camera control
#
# Either send video or analyze motion with video - cant do both in same time

from webconnection import WebConnection
from video import Video
from externalcamera import ExternalCamera
from motiondetector import MotionDetector

import time
import os
import datetime
import sys
class Brainz:
    STATE_DETECTION = 1
    STATE_MANUAL = 2
    MOTION_UPPER_LIMIT = 50
    STATUS_REPORT_TICKS = 5
    TICK_INTERVAL = 0.1

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.camera_mode   = self.STATE_DETECTION
        self.web_connection = WebConnection(self,verbose)
        self.video = Video(self,verbose)
        self.external_camera = ExternalCamera(self,verbose)
        self.motion_detector = MotionDetector(self,verbose)
        self.send_video = False
        self.status_counter = 0
        self.motion_limit = self.MOTION_UPPER_LIMIT

    def __print(self, str):
        if self.verbose:
            print (str)


    def start(self):
        # If you dont want/have some module - just remove start method

        self.web_connection.start(self)
        self.external_camera.start(self)
        self.motion_detector.start(self)
        self.__print('Brainz warming up')

        time.sleep(1)
        self.web_connection.send_message("Camera bot started")

        try:
            while True:
                self.tick()
        finally:
            self.web_connection.stop()
            self.video.stop()
            self.external_camera.stop()
            self.motion_detector.stop()
            self.__print('Brainz died')

    def camera_mode_changed(self,new_state):
        if new_state == self.STATE_DETECTION:
            self.video.stop()
            self.motion_detector.start()
        else:
            self.motion_detector.stop()
            self.video.start()
        self_camera_mode = new_state

    def tick(self):
        try:
            interval = self.TICK_INTERVAL
            self.video.tick(interval)
            self.web_connection.tick(interval)
            self.status_counter += 1
        # Send status report to websocket server
            if self.status_counter > self.STATUS_REPORT_TICKS:
                self.web_connection.send_status()
                self.status_counter = 0
            time.sleep(self.TICK_INTERVAL)
        except:
            self.__print("Unexpected error 1:")
            self.__print( sys.exc_info()[0])
            raise
