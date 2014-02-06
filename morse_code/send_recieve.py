# This will contain the hardware-level code: blink(), on(), off(), recieve(),
# etc.

import RPi.GPIO as GPIO
from time import sleep, time

def init_board(in_pin,out_pin):
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(out_pin,GPIO.OUT)
    GPIO.setup(in_pin,GPIO.IN)

    GPIO.add_event_detect(in_pin, GPIO.RISING, callback=risingCallback)
    GPIO.add_event_detect(in_pin, GPIO.FALLING, callback=fallingCallback)

def on(): GPIO.output(out_pin,True)

def off(): GPIO.output(out_pin,False)

def blink(n=5,t=1000):
    for i in range(n):
        on()
        sleep(t/1000)
        off()
        sleep(t/1000)

def dot(t):
    on()
    sleep(t/1000) # locking this thread probably won't hurt anything (I think)
    off()
    sleep(t/1000)

def dash(t):
    on()
    sleep((t*3)/1000)
    off()
    sleep(t/1000)

def risingCallback():
    if not GPIO.input(in_pin): print('wat')
    edgeList.append((time(),0))

def fallingCallback():
    if (edgeList[-1])[1] != 0: print('wat')
    (edgeList[-1])[1] = time()-(edgeList[-1])[0]

def sleepms(t): # lets you specify sleep in ms and also doesn't lock up
    ##TODO: actually use this function
    start = time()
    while time() - start < (t/1000):
        pass
    return

def recieve():
    pass
