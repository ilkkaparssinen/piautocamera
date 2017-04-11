
#
# Usb camera for taking high resolution photos
#
import time
import os
import subprocess
import gphoto2 as gp

class ExternalCamera:
    def __init__(self, brainz=None, verbose=False):
        self.brainz = brainz
        self.verbose = verbose
        self.started = False

    def __print(self, str):
        if self.verbose:
            print(str)

    def start(self):
        self.started = True
        self.context = gp.gp_context_new()
        self.camera = gp.check_result(gp.gp_camera_new())
        pass

    def tick(self):
        pass

    def stop(self):
        pass

    def capture(self):
        print("Take photo with external camera")
        file_path = gp.check_result(gp.gp_camera_capture( self.camera, gp.GP_CAPTURE_IMAGE, self.context))
        print('Camera file path: {0}/{1}'.format(file_path.folder, file_path.name))


