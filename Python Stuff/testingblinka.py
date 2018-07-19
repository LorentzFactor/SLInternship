import time
from DHT11Sensor import DHT11
from MotionDetector import MotionDetector
from smbusPractice import Accelerometer

def main():
    dht11 = DHT11(18, 3)
    motion = MotionDetector(17, 3)
    accel = Accelerometer(3, 0x53, 0x32)
    dht11.turnOn()
    accel.turnOn()
    motion.turnOn()
    try:
        time.sleep(1)
        while True:
            time.sleep(30)
            print("")
            print("Time: " + str(dht11.timeCodeArray[-1]))
            print("Humidity(%) Temperature(C): " + str(dht11.dataArray[-1]))
            print("Motion?: " + str(motion.dataArray[-1]))
            print("X, Y, Z Acceleration(m/s^2): " + str(accel.dataArray[-1]))
    except KeyboardInterrupt:
        dht11.turnOff()
        motion.turnOff()
        accel.turnOff()
    
main()
