# This will contain the hardware-level code: blink(), on(), off(), recieve(),
# etc.
import Queue
import RPi.GPIO as GPIO
from time import sleep, time
edgeList = []
in_pin = 0
out_pin = 0
pin_high = False

q = None
morseQueue = Queue.Queue()

def init_board(ip,op,wordQueue):
    GPIO.setmode(GPIO.BOARD)
    in_pin = ip
    out_pin = op
    q = wordQueue

    GPIO.setup(out_pin,GPIO.OUT)
    GPIO.setup(in_pin,GPIO.IN)

    GPIO.add_event_detect(in_pin, GPIO.RISING, callback=risingCallback)
    GPIO.add_event_detect(in_pin, GPIO.FALLING, callback=fallingCallback)
    t = Thread(target=findWords)
    t.daemon = True
    t.start()

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
    pin_high = True
    if not GPIO.input(in_pin): print('wat')
    edgeList.append((time(),0))

def fallingCallback():
    pin_high = False
    if (edgeList[-1])[1] != 0: print('wat')
    (edgeList[-1])[1] = time()-(edgeList[-1])[0]
    morseQueue.put_nowait(edgeList[-1])

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
    for i in words:
        char += morse_to_letter[i]
    q.put_nowait(char)

def recieve():
    pass
