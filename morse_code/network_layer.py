import queue
from threading import Thread
import RPi.GPIO as GPIO
from time import sleep, time
from random import randint
class morseNet:


    def changeBase(self,x,base):
        y = ''
        lessThanBase = x < base
        while x//base !=0 or lessThanBase:
            if(x%base != 0):
                y=chr(self.getChar(x//base))+chr(self.getChar(x%base))+y
            else:
                y=chr(self.getChar(x//base))+'0'+y
            x//=base
            lessThanBase = False
        if len(y) == 1:
            return '0'+y
        return y

    def reverseBase(self,x,base):
        powers = range(len(x))[::-1]
        val = 0
        for i in range(len(x)):
            val += self.getCharReverse(x[i])*base**powers[i]
        return val

    def getCharReverse(self,x):
        if ord(x)< 58: return ord(x)-48
        else: return ord(x)-55

    def getChar(self,x):
        if x< 10: return x+48
        else: return x+55

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

    def risingCallback(self,channel):
        self.pin_high = True
        if not GPIO.input(channel): print('wat')
        self.edgeList.append([time(),0])
        self.lastTransmit = time()

    def fallingCallback(self, channel):
        self.pin_high = False
        if len(self.edgeList) == 0:
            return # there's no matching rise for this fall
        if self.edgeList[-1][1] != 0: print('wat')
        self.edgeList[-1][1] = time()-self.edgeList[-1][0]
        #print(self.edgeList)
        self.morseQueue.put_nowait(self.edgeList[-1])
        self.edgeList = []

    def waveCallback(self,channel):
        sleep(.02) # debounce a little
        if GPIO.input(channel):
            #channel is high
            self.risingCallback(channel)
        else:
            #channel is low
            self.fallingCallback(channel)

    def findWords(self):
        startWait = time()
        while True:
            while self.pin_high:
                startWait = time()
            while not self.pin_high:
                #print(self.transmit_speed)
                if (time()-startWait >= ((3.*self.transmit_speed)/1000)-.1) and not self.morseQueue.empty():
                    self.translate()
                elif self.morseQueue.empty() and time() - startWait > 5:
                    self.msgBuffer = []
                    self.recvLen = 0

    def translate(self):
        edges = []
        while not self.morseQueue.empty():
            edges.append(self.morseQueue.get())
        if len(edges) == 0:
            return # no waveforms to translate
        tolerance = (.3*self.transmit_speed)/1000
        char = ''
        #print(edges)
        fail = False
        for edge in edges:
            result = self.dotOrDash(edge)
            if result is not None:
                char += result
            else:
                fail = True
                print('ERROR: Waveform was not able to be identified.')
        try:
            if not fail:
                char = self.morse_to_letter[char]
            else: char = '+'
        except KeyError:
            print('ERROR: KeyError thrown in translation of waveforms')
            return

        if self.verbose: print(char)
        self.msgBuffer.append(char)
        if len(self.msgBuffer)==8: # we've recieved up to the length field
            self.recvLen = self.reverseBase(self.msgBuffer[6]+self.msgBuffer[7],36)
        if len(self.msgBuffer)==self.recvLen+10: # we've recieved the whole message
            if self.verbose: self.printMsg(self.msgBuffer)
            if self.router: # if the program on top of this is a router
                if str(self.msgBuffer[2]) != self.ourMac[0]: # and if the destination groupcode is different than ours
                    self.passUpQueue.put_nowait(self.msgBuffer)
                    ackval = self.ack()
                    return
            if len(self.msgBuffer) == 11 and self.msgBuffer[8]=='E': # we got an ack
                if (str(self.msgBuffer[2]) + str(self.msgBuffer[3])) == self.ourMac: # and it's to us!
                    self.sent = []
                    pass
            else:
                ackval = self.ack()
                if (str(self.msgBuffer[2])+str(self.msgBuffer[3])) == self.ourMac:
                    self.passUpQueue.put_nowait(self.msgBuffer)
            self.msgBuffer = []
            self.recvLen = 0
            return
        firstTransmit = True
        if len(self.msgBuffer) < 4:
            pass
        elif len(self.msgBuffer) >=4 and (self.msgBuffer[2] + self.msgBuffer[3]) == self.ourMac:
            #print("to us!")
            pass
        elif self.msgBuffer[0]=='0' or self.msgBuffer[1]=='0':
            pass
        else:
            if firstTransmit:
                try:
                    ghostInt = int(self.msgBuffer[0])-1
                    ghostInt2 = int(self.msgBuffer[1])-1
                except:
                    ghostInt=ghostInt2=1
                if ghostInt != ghostInt2:
                    ghostInt=ghostInt2=min([ghostInt,ghostInt2])
                #self.msgBuffer[0]=self.msgBuffer[1]=ghostInt
                #self.transmitQueue.put_nowait((1,self.msgBuffer[0]))
                #self.transmitQueue.put_nowait((1,self.msgBuffer[1]))
                #self.transmitQueue.put_nowait((1,self.msgBuffer[2]))
                firstTransmit=False
            #self.transmitQueue.put_nowait((1,char))

    def printMsg(self,packet):
        nice = self.msgBuffer[2] + self.msgBuffer[3] + '|' # TO:
        nice += self.msgBuffer[4] + self.msgBuffer[5] + '|' # FROM:
        nice += self.msgBuffer[6] + self.msgBuffer[7] + '|' # LENGTH
        #length = int(self.msgBuffer[4] + self.msgBuffer[5]) # Length of message
        #for i in range(6,length):
        #    nice += self.msgBuffer[i]
        nice += ''.join(self.msgBuffer[8:-2]) + '|'
        if self.changeBase(self.checksum(self.msgBuffer[2:-2]),36) == self.msgBuffer[-2]+self.msgBuffer[-1]:
            nice += 'GOOD'
        else:
            nice += 'BAD'
        print(nice)

    def ack(self):
        if self.verbose: print('ack')
        if self.changeBase(self.checksum(self.msgBuffer[2:-2]),36) == self.msgBuffer[-2]+self.msgBuffer[-1]:
            if self.ourMac == self.msgBuffer[2] + self.msgBuffer[3]:
                if len(self.msgBuffer)==12 and self.msgBuffer[8]=='E':
                    self.sent = []
                    if self.verbose: print("clearing self.sent")
                    return 'ackrecv'
                else:
                    #self.sendMassage(self.msgBuffer[4] + self.msgBuffer[5],'E')
                    packet = self.packetize(self.msgBuffer[4]+self.msgBuffer[5],'E')
                    self.transmitQueue.put_nowait((0,packet))
                    if self.verbose: print("sent an ack")
                    return 'acksend'
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
        morse = [self.letter_to_morse[c] for c in message.upper()]
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
            try:
                message = self.transmitQueue.get_nowait()
                message = message[1] # drop the part setting the message's priority
            except:
                message = None
            if not message is None:
                self.blinkMessage(message)
                self.transmitQueue.task_done()

    def sendMassage(self,macto,message):
        self.sent = [macto,message,randint(20,90)]
        packet = self.packetize(macto, message)
        #print packet
        #for char in packet:
        #    self.transmitQueue.put_nowait(char)
        self.transmitQueue.put_nowait((1,packet))
        if self.verbose: print("Sending message!")
        if self.verbose: print(packet)
        self.retr()

    def retr(self):
        while len(self.sent)!=0:
            while len(self.sent) != 0 and not self.sent[-1] == 'sent':
                sleep(1) # sleep a second
                pass # block until message is sent
            if self.verbose: print("finished sending")
            senttime = time() # take note of when the message finished transmitting
            if len(self.sent) != 0:
                waittime = int(self.sent[2]) # how long to back off for
                break
            while True:
                # if we get an ack, break and return
                if not self.sent:
                    if self.verbose: print("ack recieved!")
                    return
                elif time()-senttime > waittime:
                    break
            # else retry with the message
            self.sendMassage(self.sent[0],self.sent[1])
            return

    def packetize(self,macto,msg):
        packet = str(macto)+str(self.ourMac)+self.changeBase(int(len(msg)),36)+msg
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
                if self.verbose: print("Breakout:")
                if self.verbose: print(breakout)
                ipfrom = ''.join(breakout[4:6])
                if self.verbose: print("Ipfrom:")
                if self.verbose: print(ipfrom)
                msg = ''.join(breakout[8:-2])
                if self.verbose: print("Message:")
                if self.verbose: print(msg)
                return [ipfrom, msg]
            except:
                return None, None
        else:
            try:
                breakout = self.passUpQueue.get_nowait()
                if self.verbose: print("Breakout:")
                if self.verbose: print(breakout)
                ipfrom = ''.join(breakout[4:6])
                if self.verbose: print("Ipfrom:")
                if self.verbose: print(ipfrom)
                msg = ''.join(breakout[8:-2])
                if self.verbose: print("Message:")
                if self.verbose: print(msg)
                return [ipfrom, msg]
            except:
                return None, None

    def setAddress(self, address):
        # address is a tuple (host,port)
        self.ourMac = address[0]
        print("This device's MAC/IP has been changed to:" + str(self.ourMac))
        #self.ourPort (or something) = address[1]
        return

    def __init__(self,inpin=11,outpin=7,address="EE"):
        try:
            self.letter_to_morse = {"\\":"----..","+":".-.-.","A":".-","B":"-...","C":"-.-.","D":"-..","E":".","F":"..-.","G":"--.","H":"....","I":"..","J":".---","K":"-.-","L":".-..","M":"--","N":"-.","O":"---","P":".--.","Q":"--.-","R":".-.","S":"...","T":"-","U":"..-","V":"...-","W":".--","X":"-..-","Y":"-.--","Z":"--..","1":".----","2":"..---","3":"...--","4":"....-","5":".....","6":"-....","7":"--...","8":"---..","9":"----.","0":"-----"}

            self.morse_to_letter = {v:k for (k,v) in self.letter_to_morse.items()}

            self.verbose = False

            self.in_pin=inpin
            self.out_pin=outpin
            self.edgeList = []
            self.pin_high = False
            self.transmit_speed = 150 # speed of one clock cycle, in ms
            self.recvLen = 0
            self.msgBuffer = []
            self.sent = []
            self.lastTransmit = time()

            self.morseQueue = queue.Queue()
            self.transmitQueue = queue.PriorityQueue()
            self.passUpQueue = queue.Queue()

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
            self.router = False
            # is this interface for a router
            # routers must recieve and ack any message to any group code other
            # than that of its mac address

        except Exception as e:
            print(e)
            print("Something went horribly awry when starting morse_code.py")

