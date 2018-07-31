import time
import rtView
import datatools
from smbusPractice import Accelerometer
from DHT11Sensor import DHT11
from MotionDetector import MotionDetector

url = 'http://sl-iot-server-9.slsandbox.com/raspberry_pi_rtvpost/'
CacheName = 'newPiTest'
verbose = True
thermo = DHT11(18, 3)
accel = Accelerometer(3, 0x53, 0x32)
motion = MotionDetector(17, 3)

currentID = "RaspberryPi-0801"
thermo.verbose = verbose
accel.verbose = verbose
motion.verbose = verbose

thermo.turnOn()
accel.turnOn()
motion.turnOn()

'''tool = datatools.DataTools(url="http://sl-iot-server-9.slsandbox.com/raspberry_pi_rtvpost/")
tool.initialize()

metadata = {"indexColumnNames":"ID" ,"historyColumnNames":"Temperature;Humidity;Motion;X_accel;Y_accel;Z_accel"}
columndata  =[
                {"name":"Temperature", "type":"double"},
                {"name":"Humidity", "type":"double"},
                {"name":"Motion", "type":"boolean"},
                {"name":"X_accel", "type": "double"},
                {"name":"Y_accel", "type": "double"},
                {"name":"Z_accel", "type": "double"},
                {"name":"ID", "type":"string"}
                ]
tool.datacache_create("PiCache", metadata)
tool.datatable_begin("PiTable", columndata)'''
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
        time.sleep(4)
        '''data = {"Temperature":thermo.dataArray[-1][1], "Humidity":thermo.dataArray[-1][0], "Motion":motion.dataArray[-1], "X_accel":accel.dataArray[-1][0], "Y_accel":accel.dataArray[-1][1],
                "Z_accel":accel.dataArray[-1][2]}
        tool.datatable_addrow("PiTable", data)
        test = tool.datatable_send("PiTable", "PiCache")
        print(test)'''
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