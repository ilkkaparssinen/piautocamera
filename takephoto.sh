#!/bin/sh
echo "Start" >>test.log
gphoto2 --set-config "capturetarget=Memory card"
gphoto2 --get-config capturetarget >>test.log
gphoto2 --capture-image -I 1 -F $1
