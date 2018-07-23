import time
from DHT11Sensor import DHT11
from MotionDetector import MotionDetector
from smbusPractice import Accelerometer
import datatools

def main():
    #dht11 = DHT11(18, 3)
    motion = MotionDetector(17, 3)
    accel = Accelerometer(3, 0x53, 0x32)
    RTTool = datatools.DataTools(url = 'http://sl-iot-server-9.slsandbox.com/raspberry_pi_rtvpost')
    RTTool.verbose = True
    RTTool.validateTargetUrl()
    RTTool.datatable_begin('testData', 'this is a table I guess')
    RTTool.datacache_create('testCache', 'Motion')
    #dht11.turnOn()
    accel.turnOn()
    motion.turnOn()
    try:
        time.sleep(1)
        while True:
            time.sleep(4)
            print("")
            print("Time: " + str(accel.timeCodeArray[-1]))
            #print("Humidity(%) Temperature(C): " + str(dht11.dataArray[-1]))
            print("Motion?: " + str(motion.dataArray[-1]))
            print("X, Y, Z Acceleration(m/s^2): " + str(accel.dataArray[-1]))
            RTTool.datatable_addrow('testData', [motion.dataArray[-1]])
            RTTool.send_to_rtview('testData', 'testCache')
    except KeyboardInterrupt:
        #dht11.turnOff()
        motion.turnOff()
        accel.turnOff()
main()
