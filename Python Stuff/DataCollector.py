import Accelerometer
import numpy as np

def getTheta(XYZ):
    return np.arcsin(XYZ[2]/np.sqrt(np.power(XYZ[0],2)+np.power(XYZ[1],2)+np.power(XYZ[2],2)))
                   
def getPhi(XYZ):
    return(np.arctan2(XYZ[0], XYZ[1]))

def getR(XYZ):
    return np.sqrt(np.power(XYZ[0],2)+np.power(XYZ[1],2)+np.power(XYZ[2],2))

def main():
    XYZ = [1.0, 1.0, 1.0]
    print(getTheta(XYZ))
    print(getPhi(XYZ))


if __name__ == '__main__':
          main()