from smbus import SMBus
from smbusPractice import Sensor

class LSM6DS33(Sensor):
    def __init__(self, CollectionRate, address=int('1101011',2), verbose = False):
        self.address = address
        super().__init__(CollectionRate, verbose)
        self.b.write_byte(self.address, 0x10, int('10100001',2)) #Turn on accelerometer, 1010 sets it to 6.66 kHz, 00 sets it to +/- 2g, 01 sets anti-aliasing to 200 Hz
        self.b.write_byte(self.address, 0x11, int('10000000',2)) #Turn on gyroscope
        self.b.write_byte(self.address, 0x0A, 0) #Disables FIFO
        
    def getDeviceData(self):
        Gyro = self.getXYZ(0x22)
        Accel = self.getXYZ(0x28)
        self.dataArray.append([Gyro, Accel])
    
    def getXYZ(self, xReg): #takes advantage of the fact that measurement registers for each direction are sequential so if xReg's are 5 and 6 yReg's are 7 and 8 etc.
        XYZ = []
        for i in range(3):
            LS = self.b.read_byte(self.address, xReg + 2*i)
            MS = self.b.read_byte(self.address, xReg + 2*i + 1)
            value = MS * 2**8 + LS #Combines the less significant and more significant values into one number
            if(value >= 2**15): #if value is >=2^15 it's actually a negative number, so makes it negative of two's complement
                value = value - 2**16
            XYZ.append(value)
        return XYZ