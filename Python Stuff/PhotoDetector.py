import smbusPractice
from smbus import SMBus
import time
import numpy as np

class PhotoDetector(smbusPractice.Sensor):
    def __init__(self, collectionRate, address, verbose=False):
        super().__init__(collectionRate, verbose)
        self.address = address
        self.reg = int('00100001', 2)
        self.b.write_byte(self.address, 0x01) #Power on
    
    def getDeviceData(self):

        self.b.write_byte(self.address, 0x01) #Power on
        self.b.write_byte(self.address, self.reg)
        raw = self.b.read_i2c_block_data(self.address, self.reg)
        #except:
            #raise Exception("device not properly connected, or address is wrong")
            
        value = (raw[0]* 2**7 + raw[1]/2)/1.2
        return value
        
        