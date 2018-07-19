import RPi.GPIO as GPIO
import time
LEDPin = 17

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LEDPin, GPIO.OUT, initial=GPIO.HIGH)
    
def main():
        while True:
                print('...LED ON')
                GPIO.output(LEDPin, GPIO.LOW)
                time.sleep(.5)
                print('...LED OFF')
                GPIO.output(LEDPin, GPIO.HIGH)
                time.sleep(.5)
def destroy():
    GPIO.output(LEDPin, GPIO.HIGH)
    GPIO.cleanup()

                
if __name__ == '__main__':
    setup()
    try:
        main()
    except KeyboardInterrupt:
        destroy()
