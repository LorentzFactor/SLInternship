import time
import rtView
from smbusPractice import Accelerometer
from DHT11Sensor import DHT11
from MotionDetector import MotionDetector

url = 'http://sl-iot-server-9.slsandbox.com/raspberry_pi_rtvpost'
CacheName = 'PiData'
thermo = DHT11(18, 3)
accel = Accelerometer(3, 0x53, 0x32)
motion = MotionDetector(17, 3)

thermo.turnOn()
accel.turnOn()
motion.turnOn()

currentID = "RaspberryPi-0801"
rt_ID = rtView.rtVar("ID", "string", "index")
rt_humidity = rtView.rtVar("humidity", "double", "history")
rt_temp = rtView.rtVar("temp", "double", "history")
rt_motion = rtView.rtVar("motion", "boolean", "history")
rt_x_accel = rtView.rtVar("x_accel", "double", "history")
rt_y_accel = rtView.rtVar("y_accel", "double", "history")
rt_z_accel = rtView.rtVar("z_accel", "double", "history")
piCache = rtView.Cache(url, CacheName, [rt_ID, rt_humidity, rt_temp, rt_motion, rt_x_accel, rt_y_accel, rt_z_accel])


try:
    while True:
        time.sleep(30)
        rt_ID.updateValue(currentID)
        rt_humidity.updateValue(thermo.dataArray[-1][0])
        rt_temp.updateValue(thermo.dataArray[-1][1])
        rt_motion.updateValue(motion.dataArray[-1])
        rt_x_accel.updateValue(accel.dataArray[-1][0])
        rt_y_accel.updateValue(accel.dataArray[-1][1])
        rt_z_accel.updateValue(accel.dataArray[-1][2])
        
        piCache.send_data_row()
         
except KeyboardInterrupt:
        thermo.turnOff()
        motion.turnOff()
        accel.turnOff()