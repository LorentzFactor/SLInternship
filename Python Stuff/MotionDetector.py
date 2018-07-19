import smbusPractice
import RPi.GPIO as GPIO
from threading import Thread
import time

class MotionDetector(smbusPractice.Sensor):
    def __init__(self, pin, collectionRate):
        self.dataThread = Thread(target = self.updateArrays, args =[])
        self.running = False
        self.collectionRate = collectionRate
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    def getDeviceData(self):
            while(self.running):
                if(GPIO.input(self.pin) == GPIO.LOW):
                    return True
                else:
                    return False
''' main():
    try:
        print("does print even work")
        thermometer = MotionDetector(17, 0.5)
        thermometer.turnOn()
        time.sleep(1)

        while True:
            try:
                print(thermometer.dataArray)
            except IndexError:
                pass
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("we were here")
        thermometer.turnOff()
        sys.exit(1)
main()'''