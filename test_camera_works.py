#!/usr/bin/env python3
# Test the Pi camera is working OK, and has the correct orientation

from picamera import PiCamera
from time import sleep

camera = PiCamera()

# Show a live video on-screen for 5 seconds
camera.start_preview()
sleep(5)
camera.stop_preview()
