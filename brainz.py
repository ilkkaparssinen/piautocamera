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
import picamera

class Brainz:
    STATE_DETECTION = 1
    STATE_MANUAL = 2
    MOTION_UPPER_LIMIT = 40
    STATUS_REPORT_TICKS = 50
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
        # Have one camera and share it between motiondetector and video comp
        # Errors - if both try to create camera
        self.camera = picamera.PiCamera()

    def __print(self, str):
        if self.verbose:
            print (str)


    def start(self):
        # If you dont want/have some module - just remove start method

        self.web_connection.start()
        self.external_camera.start()
	self.motion_detector.start()
        # self.video.start()
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
        print("STATE CHANGED")
        self.camera_mode = new_state
        if new_state == self.STATE_DETECTION:
            print ("Stop video")
            self.video.stop()
            time.sleep(1)
            print ("Start detector")
            self.motion_detector.start()
            print ("Ok")
            time.sleep(1)
        else:
            print ("Stop detector")
            self.motion_detector.stop()
            time.sleep(1)
            print ("Start video")
            self.video.start()
            print ("ok")
            time.sleep(1)

    def tick(self):
        try:
            interval = self.TICK_INTERVAL
            self.external_camera.tick(interval)
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
