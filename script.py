from picamera import PiCamera
from gpiozero import LED, DistanceSensor
import time
from multiprocessing import Process, Manager, Value
from ctypes import c_wchar_p
import sys
from rpi_lcd import LCD
import requests

url = 'http://192.168.0.145:8000/api'
        
def PenaltyCheck(card, toll_station_id, toll_type):
    sensor = DistanceSensor(echo=24, trigger=23)
    while True:
        distance = sensor.distance * 100
        print(distance)
        if(distance < 7):
            if card.value == '':
                light.off()
                print(distance)
                print('no card')
                CaptureImage()
                time.sleep(1)
                light.on()
                LCDtext()
            else:
                print('Card detected: ',card.value)
                card.value = ''
                time.sleep(1)
                light.on()
                LCDtext()
        time.sleep(.5)
    
def SetCard(card, num):
    card.value = num
    print('card: ', card.value)
    
def LCDtext(text="TollLater", text2="Ready..."):
    lcd.text(text, 1)
    lcd.text(text2, 2)

def CaptureImage():
    try:
        camera = PiCamera()
        camera.resolution = (600,400)
        camera.rotation = 90
        camera.capture('images/test.jpg')
        print('Image captured.')
        camera.close()
        
        files = {'file':open('images/test.jpg', 'rb')}
        request = requests.post('http://192.168.0.145:5000', files = files)
        if request.ok:
            response = request.json()
            car_plate_number = response[0]['car_plate_number']
            print('car plate number: ' + car_plate_number)
            data = {'car_plate_number': car_plate_number, 'toll_station_id':toll_station_id}
            request = requests.post(url+'/penalize', json = data)
            if request.ok:
                response = request.json()
                lcd.text(response['data']['keyword'], 1)
                lcd.text(response['data']['amount'], 2)
                print(response['message'])
        else:
            print('Cannot recognize the car plate number.')
    except:
        print('Camera stucked.')
    
def ReadRFID(card, toll_station_id, toll_type):
    while True:
        try:
            num = input()
            light.off()
            data = {'card_serial_no':num, 'toll_station_id':toll_station_id, 'type':toll_type}
            request = requests.post(url+'/toll', json = data)
            if request.ok:
                SetCard(card, num)
                response = request.json()
                lcd.text(response['data']['keyword'], 1)
                lcd.text(response['data']['amount'], 2)
                print(response['message'])
        except:
            print('Error: Unable to connect to the server.')
        
if __name__ == '__main__':
    light = LED(18)
    light.on()
    lcd = LCD()
    LCDtext()

    manager = Manager()
    card = manager.Value(c_wchar_p, "")
    
    toll_station_id = input('Enter Toll Station ID: ')
    toll_type = input('Enter Toll Type:')
    
    process1 = Process(target = PenaltyCheck, args=(card, toll_station_id, toll_type,))
    process1.start()

    ReadRFID(card, toll_station_id, toll_type)
