from picamera import PiCamera
from gpiozero import LED, DistanceSensor
import time
from multiprocessing import Process, Manager, Value
from ctypes import c_wchar_p
import sys
from rpi_lcd import LCD

light = LED(18)
lcd = LCD()
lcd.text("TollLater", 1)
lcd.text("Ready...", 2)

time.sleep(2)   
        
def PenaltyCheck(card):
    sensor = DistanceSensor(echo=24, trigger=23)
    while True:
        distance = sensor.distance * 100
        print(distance)
        if(distance < 5):
            if card.value == '':
                print(distance)
                print('no card')
                CaptureImage()
            else:
                print('Card detected: ',card.value)
                card.value = ''
                light.off()
        time.sleep(.5)
    
def SetCard(card, num):
    card.value = num
    print('card: ', card.value)
    
def CaptureImage():
    camera = PiCamera()
    camera.resolution = (640,480)
    camera.capture('images/test.jpg')
    camera.close()
        
if __name__ == '__main__':
    manager = Manager()
    card = manager.Value(c_wchar_p, "")
    
    process1 = Process(target = PenaltyCheck, args=(card,))
    process1.start()
    
    while True:
        num = input()
        SetCard(card, num)
        light.on()
        time.sleep(2)
