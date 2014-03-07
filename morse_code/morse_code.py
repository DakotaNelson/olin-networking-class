import Queue
from threading import Thread
import RPi.GPIO as GPIO
from time import sleep, time
class morseNet:
    edgeList = []
    in_pin = 11
    out_pin = 7
    pin_high = False

    transmit_speed = 100 # speed of one clock cycle, in ms

    morseQueue = Queue.Queue()
    transmitQueue = Queue.Queue()
    msgBuffer = []
    ourMac = ''

    def changeBase(self,x,base):
        y = ''
        lessThanBase = x < base
        while x/base != 0 or lessThanBase:
          if(x%base!=0):
              y= chr(getChar(x/base))+chr(getChar(x%base))+y
          else:
              y=chr(getChar(x/base))+'0'+y
          x/=base
          lessThanBase = False
        return y

    def getChar(self,x):
      if x < 10: return x+48
      else: return x+55

    def on(self): GPIO.output(self.out_pin,True)

    def off(self): GPIO.output(self.out_pin,False)

    def blink(self,n=5,t=1000):
        for i in range(n):
            on()
            sleep(t/1000.)
            off()
            sleep(t/1000.)

    def dot(self,t):
        on()
        sleep(t/1000.) # locking this thread probably won't hurt anything (I think)
        off()
        sleep(t/1000.)

    def dash(self,t):
        on()
        sleep((t*3)/1000.)
        off()
        sleep(t/1000.)

    def risingCallback(self,channel):
        global self.pin_high
        self.pin_high = True
        if not GPIO.input(channel): print('wat')
        self.edgeList.append([time(),0])

    def fallingCallback(self, channel):
        global self.pin_high
        self.pin_high = False
        global self.edgeList
        if len(self.edgeList) == 0:
            return # there's no matching rise for this fall
        if self.edgeList[-1][1] != 0: print('wat')
        self.edgeList[-1][1] = time()-edgeList[-1][0]
        self.morseQueue.put_nowait(self.edgeList[-1])
        self.edgeList = []

    def waveCallback(self,channel):
        sleep(.02) # debounce a little
        if GPIO.input(channel):
            #channel is high
            risingCallback(channel)
        else:
            #channel is low
            fallingCallback(channel)

    def findWords(self):
        startWait = time()
        while True:
            while self.pin_high:
                startWait = time()
            while not self.pin_high:
                if (time()-startWait >= ((3.*self.transmit_speed)/1000)-.1) and not self.morseQueue.empty(): translate()

    def translate(self):
        letter_to_morse = {"+":".-.-.","A":".-","B":"-...","C":"-.-.","D":"-..","E":".","F":"..-.","G":"--.","H":"....","I":"..","J":".---","K":"-.-","L":".-..","M":"--","N":"-.","O":"---","P":".--.","Q":"--.-","R":".-.","S":"...","T":"-","U":"..-","V":"...-","W":".--","X":"-..-","Y":"-.--","Z":"--..","1":".----","2":"..---","3":"...--","4":"....-","5":".....","6":"-....","7":"--...","8":"---..","9":"----.","0":"-----"}
        morse_to_letter = {v:k for (k,v) in letter_to_morse.items()}
        queueSize = 0
        edges = []
        global self.msgBuffer
        while not self.morseQueue.empty():
            edges.append(self.morseQueue.get())
        if len(edges) == 0:
            return # no waveforms to translate
        tolerance = (.3*self.transmit_speed)/1000
        char = ''

        for edge in edges:
            result = dotOrDash(edge)
            if result is not None:
                char += result

        char = morse_to_letter[char]
        print(char)
        self.msgBuffer.append(char)
        if char == '+': # and (self.msgBuffer[0] + msgBuffer[1]) == self.ourMac:
            #print(self.msgBuffer)
            printMsg(self.msgBuffer)
            self.msgBuffer = []
            return
        firstTransmit = True
        if len(self.msgBuffer) < 4:
            pass
        elif len(self.msgBuffer) >=4 and (msgBuffer[2] + msgBuffer[3]) == self.ourMac:
            #print("to us!")
            pass
        elif self.msgBuffer[0]=='0' or msgBuffer[1]=='0':
            pass
        else:
            if firstTransmit:
                ghostInt = int(self.msgBuffer[0])-1
                ghostInt2 = int(self.msgBuffer[1])-1
                if ghostInt != ghostInt2:
                    ghostInt=ghostInt2=min([ghostInt,ghostInt2])
                self.msgBuffer[0]=msgBuffer[1]=ghostInt
                self.transmitQueue.put_nowait(self.msgBuffer[0])
                self.transmitQueue.put_nowait(self.msgBuffer[1])
                self.transmitQueue.put_nowait(self.msgBuffer[2])
                firstTransmit=False
            self.transmitQueue.put_nowait(char)

    def printMsg(self,packet):
        nice = self.msgBuffer[2] + msgBuffer[3] + '|' # TO:
        nice += self.msgBuffer[4] + msgBuffer[5] + '|' # FROM:
        nice += self.msgBuffer[5] + msgBuffer[6] + '|' # LENGTH
        #length = int(self.msgBuffer[4] + msgBuffer[5]) # Length of message
        #for i in range(6,length):
        #    nice += self.msgBuffer[i]
        nice += ''.join(self.msgBuffer[6:-3]) + '|'
        if changeBase(checksum(self.msgBuffer[2:-3]),36) == msgBuffer[-3]+msgBuffer[-2]:
            nice += 'GOOD'
        else:
            nice += 'BAD'
        print(nice)
        return

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

    letter_to_morse = {"+":".-.-.","A":".-","B":"-...","C":"-.-.","D":"-..","E":".","F":"..-.","G":"--.","H":"....","I":"..","J":".---","K":"-.-","L":".-..","M":"--","N":"-.","O":"---","P":".--.","Q":"--.-","R":".-.","S":"...","T":"-","U":"..-","V":"...-","W":".--","X":"-..-","Y":"-.--","Z":"--..","1":".----","2":"..---","3":"...--","4":"....-","5":".....","6":"-....","7":"--...","8":"---..","9":"----.","0":"-----"}
#This is currently only global for toMorse and toMessage

    morse_to_letter = {v:k for (k,v) in letter_to_morse.items()}


    def toMorse(self,message):
        morse = [letter_to_morse[c] for c in message]
        return morse

    def toMessage(self,morse):
        message = [morse_to_letter[c] for c in morse]
        return message

    def blinkMessage(self,message):
        morse = toMorse(message)
        for c in morse:
            for i in range(len(c)):
                if c[i] == ".":
                    dot(self.transmit_speed)
                else:
                    dash(self.transmit_speed)
                if i == len(c)-1:
                    sleep((2.*self.transmit_speed)/1000) # gap between characters
        #sleep((4.*self.transmit_speed)/1000) # plus 3 above = 7 -> between words

    def blinkWorker(self):
        while True:
            message = self.transmitQueue.get()
            if not message is None:
                blinkMessage(message)
                self.transmitQueue.task_done()

    def sendMassage(self,macto,message):
        packet = packetize(macto, message)
        #print packet
        for char in packet:
            self.transmitQueue.put_nowait(char)
        print("Sending message!")

    def packetize(self,macto,msg):
        packet = macto+self.ourMac+changeBase(len(msg),36)+msg
        return '99'+packet+changeBase(checksum(packet),36)+'+'

    def checksum(self,msg):
        msg = ''.join(msg)
        cksm=0
        for char in msg:
            cksm^=ord(char)
        return cksm

    def __init__(self,inpin=11,outpin=7):
        try:
            self.in_pin=inpin
            self.out_pin=outpin
            GPIO.setmode(GPIO.BOARD)

            GPIO.setup(self.out_pin,GPIO.OUT)
            GPIO.setup(self.in_pin,GPIO.IN)

            GPIO.add_event_detect(self.in_pin, GPIO.BOTH, callback=waveCallback)

            recieveThread = Thread(target=findWords)
            recieveThread.daemon = True
            recieveThread.start()

            transmitThread = Thread(target=blinkWorker)
            transmitThread.daemon = True
            transmitThread.start()
            self.ourMac = 'AA'#changeBase(input('Enter unique MAC address between 0 and 1296: '))
            #we should probably do a GPIO.cleanup() in here somewhere.
        finally:
            GPIO.cleanup()
