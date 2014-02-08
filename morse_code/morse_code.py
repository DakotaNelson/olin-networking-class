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
    pin_high = True
    if not GPIO.input(channel): print('wat')
    edgeList.append((time(),0))

def fallingCallback(channel):
    print('Falling!')
    pin_high = False
    if (edgeList[-1])[1] != 0: print('wat')
    (edgeList[-1])[1] = time()-(edgeList[-1])[0]
    print(edgeList)
    morseQueue.put_nowait(edgeList[-1])

def waveCallback(channel):
    if GPIO.input(channel):
        #channel is high
        risingCallback(channel)
    else:
        #channel is low
        fallingCallback(channel)

def sleepms(t): # lets you specify sleep in ms and also doesn't lock up
    ##TODO: actually use this function
    start = time()
    while time() - start < (t/1000):
        pass
    return

def findWords():
    while True:
        startWait = time()
        #might need to check value of queue length
        while not pin_high:
            if time()-startWait>=7: translate()

def translate():
    letter_to_morse = {"A":".-","B":"-...","C":"-.-.","D":"-..","E":".","F":"..-.","G":"--.","H":"....","I":"..","J":".---","K":"-.-","L":".-..","M":"--","N":"-.","O":"---","P":".--.","Q":"--.-","R":".-.","S":"...","T":"-","U":"..-","V":"...-","W":".--","X":"-..-","Y":"-.--","Z":"--..","1":".----","2":"..---","3":"...--","4":"....-","5":".....","6":"-....","7":"--...","8":"---..","9":"----.","0":"-----"}
    morse_to_letter = {v:k for (k,v) in letter_to_morse.items()}
    edges = [item for item in morseQueue.queue]
    tolerance = .3
    char = ''
    words = []
    for i in range(len(1,edges)):
        if abs(edges[i][0]-edges[i-1][0]-edges[i-1][1] - 1) < tolerance:
            if abs((edges[i-1])[1]-1) < tolerance:
                char += '.'
            elif abs((edges[i-1])[1]-3) < tolerance:
                char += '-'
            if i == edges -1:
                if abs((edges[i])[1]-1) < tolerance:
                    char += '.'
                elif abs((edges[i])[1]-3) < tolerance:
                    char += '-'
        else:
            if abs((edges[i-1])[1]-1) < tolerance:
                char += '.'
            elif abs((edges[i-1])[1]-3) < tolerance:
                char += '-'
            if i == edges -1:
                if abs((edges[i])[1]-1) < tolerance:
                    char += '.'
                elif abs((edges[i])[1]-3) < tolerance:
                    char += '-'
            words.append(char)
            char = ''
    char = ''
    for word in words:
        char += morse_to_letter[word]
    print('----------------')
    print(char)
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

    GPIO.add_event_detect(in_pin, GPIO.BOTH, callback=waveCallback, bouncetime=100)
    #GPIO.add_event_detect(in_pin, GPIO.FALLING, callback=fallingCallback)

    recieveThread = Thread(target=findWords)
    recieveThread.daemon = True
    recieveThread.start()

    transmitThread = Thread(target=blinkWorker)
    transmitThread.daemon = True
    transmitThread.start()

    #we should probably do a GPIO.cleanup() in here somewhere.
