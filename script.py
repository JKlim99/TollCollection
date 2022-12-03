from picamera import PiCamera
import time

camera = PiCamera()
camera.resolution = (640,480)
time.sleep(2)
camera.capture("images/test1.jpg")
