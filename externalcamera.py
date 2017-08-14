
#
# Usb camera for taking high resolution photos
#
import time
import os
import subprocess
# Not used for now import gphoto2 as gp

class ExternalCamera:
    def __init__(self, brainz=None, verbose=False):
        self.brainz = brainz
        self.verbose = verbose
        self.started = False
        self.wait_for_next = 0

    def __print(self, str):
        if self.verbose:
            print(str)

    def start(self):
        self.started = True
        self.take_photos = 0
# gphoto2lib didnt work with my camera - use gphoto2 from command line
#        self.context = gp.gp_context_new()
#        self.camera = gp.check_result(gp.gp_camera_new())
        print("Camera CREATED")
        pass

    def tick(self,interval):
        self.wait_for_next = max(0,self.wait_for_next - interval)
        if self.take_photos == 0 or self.wait_for_next > 0:
            self.take_photos = 0
            return
        self.capture(self.take_photos)
        self.take_photos = 0
        # Wait for next photo set at least two seconds
        self.wait_for_next = 2
        pass

    def stop(self):
        pass

    def capture(self,count):
        print("Take photo with external camera")
        
        try:
            # Use command line - slower than 
            # subprocess.call(["gphoto2","--capture-image"])
            for i in range (0,count):
                subprocess.call(["gphoto2","--capture-image"])
                # This wait depends of the camera speed
                time.sleep(0.4)
            
            # Direct library calls - worked unreliably
            # file_path = gp.check_result(gp.gp_camera_capture( self.camera, gp.GP_CAPTURE_IMAGE, self.context))
            # print('Camera file path: {0}/{1}'.format(file_path.folder, file_path.name))
        except:
            print("Camera failed")

