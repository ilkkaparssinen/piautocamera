# Start camera bot
#
#
sudo killall python
# EOS 600 seems to need this
gphoto2 --set-config "capturetarget=Memory card"
sudo python main.py

