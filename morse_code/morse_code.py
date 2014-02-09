import Queue
from threading import Thread
import RPi.GPIO as GPIO
from time import sleep, time

edgeList = []
in_pin = 11
out_pin = 7
pin_high = False

transmit_speed = 1000 # speed of one clock cycle, in ms

morseQueue = Queue.Queue()
transmitQueue = Queue.Queue()
msgBuffer = []
ourMac = ''

def changeBase(x,base):
    y = ''
    while x/base != 0:
      if(x%base!=0):
          y= chr(getChar(x/base))+chr(getChar(x%base))+y
      else:
          y=chr(getChar(x/base))+'0'+y
          x/=base
    return y

def getChar(x):
  if x < 10: return x+48
  else: return x+55

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

def risingCallback(channel):
    global pin_high
    pin_high = True
    if not GPIO.input(channel): print('wat')
    edgeList.append([time(),0])

def fallingCallback(channel):
    global pin_high
    pin_high = False
    global edgeList
    if len(edgeList) == 0:
        return # there's no matching rise for this fall
    if edgeList[-1][1] != 0: print('wat')
    edgeList[-1][1] = time()-edgeList[-1][0]
    morseQueue.put_nowait(edgeList[-1])
    edgeList = []

def waveCallback(channel):
    sleep(.01) # debounce a little
    if GPIO.input(channel):
        #channel is high
        risingCallback(channel)
    else:
        #channel is low
        fallingCallback(channel)

#def sleepms(t): # lets you specify sleep in ms and also doesn't lock up
#    ##TODO: actually use this function
#    start = time()
#    while time() - start < (t/1000):
#        pass
#    return

def findWords():
    startWait = time()
    while True:
        while pin_high:
            startWait = time()
        while not pin_high:
            if (time()-startWait >= ((3*transmit_speed)/1000)-.1) and not morseQueue.empty(): translate()

def translate():
    letter_to_morse = {"+":".-.-.","A":".-","B":"-...","C":"-.-.","D":"-..","E":".","F":"..-.","G":"--.","H":"....","I":"..","J":".---","K":"-.-","L":".-..","M":"--","N":"-.","O":"---","P":".--.","Q":"--.-","R":".-.","S":"...","T":"-","U":"..-","V":"...-","W":".--","X":"-..-","Y":"-.--","Z":"--..","1":".----","2":"..---","3":"...--","4":"....-","5":".....","6":"-....","7":"--...","8":"---..","9":"----.","0":"-----"}
    morse_to_letter = {v:k for (k,v) in letter_to_morse.items()}
    queueSize = 0
    edges = []
    global msgBuffer
    while not morseQueue.empty():
        edges.append(morseQueue.get())
    if len(edges) == 0:
        return # no waveforms to translate
    tolerance = .3
    char = ''

    for edge in edges:
        result = dotOrDash(edge)
        if result is not None:
            char += result

    char = morse_to_letter[char]
    msgBuffer.append(char)
    if char == '+': # and (msgBuffer[0] + msgBuffer[1]) == ourMac:
        print(msgBuffer)
        msgBuffer = []
    firstTransmit = True
    if len(msgBuffer) < 2:
        pass
    elif len(msgBuffer) >= 2 and (msgBuffer[0] + msgBuffer[1]) == ourMac:
        print("to us!")
    else:
        if firstTransmit:
            transmitQueue.put_nowait(msgBuffer[0])
            firstTransmit=False
        transmitQueue.put_nowait(char)
    print(char)

def dotOrDash(edge):
    tolerance = 0.3
    tDot = (transmit_speed)/1000
    tDash = (3*transmit_speed)/1000
    tStart = edge[0]
    tDuration = edge[1]
    #tPrevStart = edges[i-1][0]
    #tPrevDuration = edges[i-1][1]
    #tPrevEnd = (tPrevStart + tPrevDuration) # when the last wave ended
    #tLow = tStart - tPrevEnd # the amount of time the line was low before this
    if abs(tDuration-tDot) < tolerance:
        return '.'
    elif abs(tDuration-tDash) < tolerance:
        return '-'
    else:
        return None

letter_to_morse = {"+":".-.-.","A":".-","B":"-...","C":"-.-.","D":"-..","E":".","F":"..-.","G":"--.","H":"....","I":"..","J":".---","K":"-.-","L":".-..","M":"--","N":"-.","O":"---","P":".--.","Q":"--.-","R":".-.","S":"...","T":"-","U":"..-","V":"...-","W":".--","X":"-..-","Y":"-.--","Z":"--..","1":".----","2":"..---","3":"...--","4":"....-","5":".....","6":"-....","7":"--...","8":"---..","9":"----.","0":"-----"}
#This is currently only global for toMorse and toMessage

morse_to_letter = {v:k for (k,v) in letter_to_morse.items()}


def toMorse(message):
    morse = [letter_to_morse[c] for c in message]
    return morse

def toMessage(morse):
    message = [morse_to_letter[c] for c in morse]
    return message

def blinkMessage(message):
    morse = toMorse(message)
    for c in morse:
        for i in range(len(c)):
            if c[i] == ".":
                dot(transmit_speed)
            else:
                dash(transmit_speed)
            if i == len(c)-1:
                sleep((2*transmit_speed)/1000) # gap between characters
    sleep((4*transmit_speed)/1000) # plus 3 above = 7 -> between words

def blinkWorker():
    while True:
        message = transmitQueue.get()
        if not message is None:
            blinkMessage(message)
            transmitQueue.task_done()

def packetize(macto,macfrom,msg):
    packet = macto+macfrom+changeBase(len(msg))+msg
    return packet+checksum(packet)

if __name__ == '__main__':
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(out_pin,GPIO.OUT)
    GPIO.setup(in_pin,GPIO.IN)

    GPIO.add_event_detect(in_pin, GPIO.BOTH, callback=waveCallback)

    recieveThread = Thread(target=findWords)
    recieveThread.daemon = True
    recieveThread.start()

    transmitThread = Thread(target=blinkWorker)
    transmitThread.daemon = True
    transmitThread.start()
    ourMac = 'AA'
    #we should probably do a GPIO.cleanup() in here somewhere.
