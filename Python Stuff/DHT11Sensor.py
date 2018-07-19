import Adafruit_DHT
import smbusPractice
import time
from threading import Thread
import sys

class DHT11(smbusPractice.Sensor):
    sensor = Adafruit_DHT.DHT11
    def __init__(self, pin, collectionRate):
        if(collectionRate < 1.7):
                Error("collection rate too fast")
        self.collectionRate = collectionRate
        self.pin = pin
        self.sensor = Adafruit_DHT.DHT11
        self.dataThread = Thread(target = self.updateArrays, args =[])
        self.running = False

    def getDeviceData(self):
        HT = []
        humidity, temperature = Adafruit_DHT.read_retry(self.sensor, self.pin)
        HT.append(humidity)
        HT.append(temperature)
        return HT
        
'''def main():
    try:
        print("does print even work")
        thermometer = DHT11(18, 2)
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