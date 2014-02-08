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
    print('Rising!')
    global pin_high
    pin_high = True
    if not GPIO.input(channel): print('wat')
    edgeList.append([time(),0])

def fallingCallback(channel):
    print('Falling!')
    global pin_high
    pin_high = False
    global edgeList
    if len(edgeList) == 0:
        return # there's no matching rise for this fall
    if edgeList[-1][1] != 0: print('wat')
    edgeList[-1][1] = time()-edgeList[-1][0]
    print(edgeList)
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
        #might need to check value of queue length
        while not pin_high:
            if (time()-startWait > ((7*transmit_speed)/1000)) and not morseQueue.empty(): translate()

def translate():
    letter_to_morse = {"A":".-","B":"-...","C":"-.-.","D":"-..","E":".","F":"..-.","G":"--.","H":"....","I":"..","J":".---","K":"-.-","L":".-..","M":"--","N":"-.","O":"---","P":".--.","Q":"--.-","R":".-.","S":"...","T":"-","U":"..-","V":"...-","W":".--","X":"-..-","Y":"-.--","Z":"--..","1":".----","2":"..---","3":"...--","4":"....-","5":".....","6":"-....","7":"--...","8":"---..","9":"----.","0":"-----"}
    morse_to_letter = {v:k for (k,v) in letter_to_morse.items()}
    queueSize = 0
    edges = []
    while not morseQueue.empty():
        edges.append(morseQueue.get())
    if len(edges) == 0:
        return # no waveforms to translate
    print(edges)
    tolerance = .3
    char = ''
    words = []
    tDot = (transmit_speed)/1000
    tDash = (3*transmit_speed)/1000

    for i in range(1,len(edges)-1):
        tStart = edges[i][0]
        tDuration = edges[i][1]
        tPrevStart = edges[i-1][0]
        tPrevDuration = edges[i-1][1]
        tPrevEnd = (tPrevStart + tPrevDuration) # when the last wave ended
        tLow = tStart - tPrevEnd # the amount of time the line was low before this
        if abs(tLow - tDot) < tolerance: # if there was only one space...
            if abs(tPrevDuration-tDot) < tolerance:
                char += '.'
            elif abs(tPrevDuration-tDash) < tolerance:
                char += '-'
        else: # there were three spaces...
            words.append(char) #make a new morse character
            char = ''
            if abs(tPrevDuration - tDot) < tolerance:
                char += '.'
            elif abs(tPrevDuration - tDash) < tolerance:
                char += '-'
    message = []
    print(words)
    for letter in words:
        message.append(morse_to_letter[letter])
    print('----------------')
    print(message)
    print('----------------')
    #transmitQueue.put_nowait(char)

def recieve():
    pass

letter_to_morse = {"A":".-","B":"-...","C":"-.-.","D":"-..","E":".","F":"..-.","G":"--.","H":"....","I":"..","J":".---","K":"-.-","L":".-..","M":"--","N":"-.","O":"---","P":".--.","Q":"--.-","R":".-.","S":"...","T":"-","U":"..-","V":"...-","W":".--","X":"-..-","Y":"-.--","Z":"--..","1":".----","2":"..---","3":"...--","4":"....-","5":".....","6":"-....","7":"--...","8":"---..","9":"----.","0":"-----"}
#This is currently only global for toMorse and toMessage

morse_to_letter = {v:k for (k,v) in letter_to_morse.items()}


def toMorse(message):
    morse = [letter_to_morse[c] for c in message]
    #print(morse)
    return morse

def toMessage(morse):
    message = [morse_to_letter[c] for c in morse]
    #print(message)
    return message

def blinkMessage(message):
    morse = toMorse(message)
    for c in morse:
        for i in c:
            if i == ".":
                dot(transmit_speed)
            else:
                dash(transmit_speed)
            if c.index(i) == len(c)-1:
                sleep((2*transmit_speed)/1000) # gap between characters
    sleep((4*transmit_speed)/1000) # plus 3 above = 7 -> between words

#def retransmitMode():
#    while(True):
#        #recieve message
#        end_of_word = False ##TODO make this work for reals
#        if(end_of_word):
#            transmitQueue.put_nowait(word)

def blinkWorker():
    while True:
        word = transmitQueue.get()
        if not word is None:
            blinkMessage(word)
            transmitQueue.task_done()

if __name__ == '__main__':
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(out_pin,GPIO.OUT)
    GPIO.setup(in_pin,GPIO.IN)

    GPIO.add_event_detect(in_pin, GPIO.BOTH, callback=waveCallback)
    #GPIO.add_event_detect(in_pin, GPIO.FALLING, callback=fallingCallback)

    recieveThread = Thread(target=findWords)
    recieveThread.daemon = True
    recieveThread.start()

    transmitThread = Thread(target=blinkWorker)
    transmitThread.daemon = True
    transmitThread.start()

    #we should probably do a GPIO.cleanup() in here somewhere.
