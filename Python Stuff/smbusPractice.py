from smbus import SMBus
import datetime
from threading import Thread
import time

class Sensor(object):
    b = SMBus(1)
    dataArray = []
    timeCodeArray = []

    #collection rate is in seconds
    def __init__(self, collectionRate, address, reg):
        self.address=address
        self.reg = reg
        self.collectionRate = collectionRate
        self.dataThread = Thread(target = self.updateArrays, args =[])
        self.running = False
        self.b.write_byte_data(self.address, 0x2D, 0x08)
    
    def turnOn(self):
        if(self.running == False):
            self.running = True
            self.dataThread.start()
    
    def turnOff(self):
        if(self.running == True):
            self.running = False
       
    def getDeviceData(self):
        return 0
    
    def updateArrays(self):
        while self.running:
            if(len(self.dataArray)==0):
                self.dataArray = [self.getDeviceData()]
            else:
                self.dataArray.append(self.getDeviceData())
            self.timeCodeArray.append(datetime.datetime.now())
            time.sleep(self.collectionRate)
            
class Accelerometer(Sensor):
    def getDeviceData(self):
        try:
            raw = self.b.read_i2c_block_data(self.address, self.reg, 6)
        except:
            raise Exception("device not properly connected, or address is wrong")
        XYZ = []
        for i in range(0, 6, 2):
            g = raw[i] | (raw[i+1] << 8)
            if g > 32767:
                g -= 65535
            g = g*9.8/246
            XYZ.append(g)
        return XYZ
'''def main():
    a = Accelerometer(1, 0x53, 0x32)
    a.turnOn()
    time.sleep(2)
    try:
       while True:
           print(a.dataArray[-1])
           time.sleep(0.5)
    except KeyboardInterrupt:
        a.turnOff()
        sys.exit()

main()'''