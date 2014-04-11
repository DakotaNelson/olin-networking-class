import Queue
from threading import Thread
import RPi.GPIO as GPIO
from time import sleep, time
from random import randint
class morseNet:

    def changeBase(self,x,base):
        y = ''
        lessThanBase = x < base
        while x/base != 0 or lessThanBase:
          if(x%base!=0):
              y= chr(self.getChar(x/base))+chr(self.getChar(x%base))+y
          else:
              y=chr(self.getChar(x/base))+'0'+y
          x/=base
          lessThanBase = False
        return y

    def getChar(self,x):
      if x < 10: return x+48
      else: return x+55

    def reverseBase(self,x,base):
        powers = range(len(x))[::-1]
        val = 0
        for i in range(len(x)):
            val += self.getCharReverse(x[i])*base**powers[i]
        return val

    def getCharReverse(self,x):
        if ord(x)< 58: return ord(x)-48
        else: return ord(x)-55

    def on(self):
        GPIO.setup(self.out_pin, GPIO.OUT)
        GPIO.output(self.out_pin,True)

    def off(self):
        GPIO.output(self.out_pin,False)
        GPIO.setup(self.out_pin,GPIO.IN)
    def blink(self,n=5,t=1000):
        for i in range(n):
            self.on()
            sleep(t/1000.)
            self.off()
            sleep(t/1000.)

    def dot(self,t):
        self.on()
        sleep(t/1000.) # locking this thread probably won't hurt anything (I think)
        self.off()
        sleep(t/1000.)

    def dash(self,t):
        self.on()
        sleep((t*3)/1000.)
        self.off()
        sleep(t/1000.)

def dot(t):
    on()
    sleep(t/1000.) # locking this thread probably won't hurt anything (I think)
    off()
    sleep(t/1000.)

def dash(t):
    on()
    sleep((t*3)/1000.)
    off()
    sleep(t/1000.)

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
    sleep(.02) # debounce a little
    if GPIO.input(channel):
        #channel is high
        risingCallback(channel)
    else:
        #channel is low
        fallingCallback(channel)

def findWords():
    startWait = time()
    while True:
        while pin_high:
            startWait = time()
        while not pin_high:
            if (time()-startWait >= ((3.*transmit_speed)/1000)-.1) and not morseQueue.empty(): translate()

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
    tolerance = (.3*transmit_speed)/1000
    char = ''

    for edge in edges:
        result = dotOrDash(edge)
        if result is not None:
            char += result

    char = morse_to_letter[char]
    print(char)
    msgBuffer.append(char)
    if char == '+': # and (msgBuffer[0] + msgBuffer[1]) == ourMac:
        #print(msgBuffer)
        printMsg(msgBuffer)
        msgBuffer = []
        return
    firstTransmit = True
    if len(msgBuffer) < 4:
        pass
    elif len(msgBuffer) >=4 and (msgBuffer[2] + msgBuffer[3]) == ourMac:
        #print("to us!")
        pass
    elif msgBuffer[0]=='0' or msgBuffer[1]=='0':
        pass
    else:
        if firstTransmit:
            ghostInt = int(msgBuffer[0])-1
            ghostInt2 = int(msgBuffer[1])-1
            if ghostInt != ghostInt2:
                ghostInt=ghostInt2=min([ghostInt,ghostInt2])
            msgBuffer[0]=msgBuffer[1]=ghostInt
            transmitQueue.put_nowait(msgBuffer[0])
            transmitQueue.put_nowait(msgBuffer[1])
            transmitQueue.put_nowait(msgBuffer[2])
            firstTransmit=False
        transmitQueue.put_nowait(char)

def printMsg(packet):
    nice = msgBuffer[2] + msgBuffer[3] + '|' # TO:
    nice += msgBuffer[4] + msgBuffer[5] + '|' # FROM:
    nice += msgBuffer[5] + msgBuffer[6] + '|' # LENGTH
    #length = int(msgBuffer[4] + msgBuffer[5]) # Length of message
    #for i in range(6,length):
    #    nice += msgBuffer[i]
    nice += ''.join(msgBuffer[6:-3]) + '|'
    if changeBase(checksum(msgBuffer[2:-3]),36) == msgBuffer[-3]+msgBuffer[-2]:
        nice += 'GOOD'
    else:
        nice += 'BAD'
    print(nice)
    return

def dotOrDash(edge):
    tolerance = (.3*transmit_speed)/1000
    tDot = (transmit_speed)/1000.
    tDash = (3.*transmit_speed)/1000
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

letter_to_morse = {"\":"----..", "+":".-.-.","A":".-","B":"-...","C":"-.-.","D":"-..","E":".","F":"..-.","G":"--.","H":"....","I":"..","J":".---","K":"-.-","L":".-..","M":"--","N":"-.","O":"---","P":".--.","Q":"--.-","R":".-.","S":"...","T":"-","U":"..-","V":"...-","W":".--","X":"-..-","Y":"-.--","Z":"--..","1":".----","2":"..---","3":"...--","4":"....-","5":".....","6":"-....","7":"--...","8":"---..","9":"----.","0":"-----"}
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
                return 'notme'
        else:
            return 'badcksm'

    def dotOrDash(self,edge):
        tolerance = (.3*self.transmit_speed)/1000
        tDot = (self.transmit_speed)/1000.
        tDash = (3.*self.transmit_speed)/1000
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

    def toMorse(self,message):
        morse = [self.letter_to_morse[c] for c in message]
        return morse

    def toMessage(self,morse):
        message = [self.morse_to_letter[c] for c in morse]
        return message

    def blinkMessage(self,message):
        morse = self.toMorse(message)
        for c in morse:
            for i in range(len(c)):
                if c[i] == ".":
                    self.dot(self.transmit_speed)
                else:
                    self.dash(self.transmit_speed)
                if i == len(c)-1:
                    sleep((2.*self.transmit_speed)/1000) # gap between characters
        self.sent.append('sent')
        #sleep((4.*self.transmit_speed)/1000) # plus 3 above = 7 -> between words

    def blinkWorker(self):
        while True:
            while time()-self.lastTransmit < 50.*self.transmit_speed/1000:
                sleep(.1)
                pass
            message = self.transmitQueue.get()
            message = message[1] # drop the part setting the message's priority
            if not message is None:
                self.blinkMessage(message)
                self.transmitQueue.task_done()

    def sendMassage(self,macto,message):
        self.sent = [macto,message,randint(10,90)]
        packet = self.packetize(macto, message)
        #print packet
        #for char in packet:
        #    self.transmitQueue.put_nowait(char)
        self.transmitQueue.put_nowait((1,packet))
        print("Sending message!")
        print(packet)
        self.retr()

    def retr(self):
        while not self.sent[-1] == 'sent':
            sleep(1) # sleep a second
            pass # block until message is sent
        print("finished sending")
        sentTime = time() # take note of when the message finished transmitting
        waitTime = int(self.sent[2]) # how long to back off for
        while True:
            # if we get an ack, break and return
            if not self.sent:
                print("ack recieved!")
                return
            elif time()-sentTime > waitTime:
                break
        # else retry with the message
        self.sendMassage(self.sent[0],self.sent[1])
        return

    def packetize(self,macto,msg):
        packet = str(macto)+str(self.ourMac)+self.changeBase(len(msg),36)+msg
        return '99'+packet+self.changeBase(self.checksum(packet),36)

    def checksum(self,msg):
        msg = ''.join(msg)
        cksm=0
        for char in msg:
            cksm^=ord(char)
        return cksm

    def returnMessage(self,wait=False,timeout=None):
        if wait:
            try:
                breakout = self.passUpQueue.get(True,timeout)
                print(breakout)
                ipfrom = breakout[8:11]
                print(ipfrom)
                msg = ''.join(breakout[8:-2])
                print(msg)
                return [ipfrom, msg]
            except:
                return None, None
        else:
            try:
                breakout = self.passUpQueue.get_nowait()
                print(breakout)
                ipfrom = breakout[8:11]
                print(ipfrom)
                msg = ''.join(breakout[8:-2])
                print(msg)
                return [ipfrom, msg]
            except:
                return None, None

    def setAddress(self, address):
        # address is a tuple (host,port)
        self.ourMac = address[0]
        print("This device's MAC/IP has been changed to:")
        print(self.ourMac)
        #self.ourPort (or something) = address[1]
        return

    def __init__(self,inpin=11,outpin=7,address="EE"):
        try:
            self.letter_to_morse = {"\\":"----..","+":".-.-.","A":".-","B":"-...","C":"-.-.","D":"-..","E":".","F":"..-.","G":"--.","H":"....","I":"..","J":".---","K":"-.-","L":".-..","M":"--","N":"-.","O":"---","P":".--.","Q":"--.-","R":".-.","S":"...","T":"-","U":"..-","V":"...-","W":".--","X":"-..-","Y":"-.--","Z":"--..","1":".----","2":"..---","3":"...--","4":"....-","5":".....","6":"-....","7":"--...","8":"---..","9":"----.","0":"-----"}

            self.morse_to_letter = {v:k for (k,v) in self.letter_to_morse.items()}

            self.in_pin=inpin
            self.out_pin=outpin
            self.edgeList = []
            self.pin_high = False
            self.transmit_speed = 100 # speed of one clock cycle, in ms
            self.recvLen = 0
            self.msgBuffer = []
            self.sent = []
            self.lastTransmit = time()

            self.morseQueue = Queue.Queue()
            self.transmitQueue = Queue.PriorityQueue()
            self.passUpQueue = Queue.Queue()

            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self.out_pin,GPIO.OUT)
            GPIO.setup(self.in_pin,GPIO.IN)

            GPIO.add_event_detect(self.in_pin, GPIO.BOTH, callback=self.waveCallback)

            #self.retransmitThread = Thread(target=self.retr)
            #self.retransmitThread = True
            #seld.retransmitThread.start()

            self.recieveThread = Thread(target=self.findWords)
            self.recieveThread.daemon = True
            self.recieveThread.start()

            self.transmitThread = Thread(target=self.blinkWorker)
            self.transmitThread.daemon = True
            self.transmitThread.start()

            self.ourMac = address
            # in the form "EA" where E is the groupcode
            # and A is the MAC

        except:
            print("Something went horribly awry when starting morse_code.py")

