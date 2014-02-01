import Queue
import threading
import send_recieve

letter_to_morse =
{"A":".-","B":"-...","C":"-.-.","D":"-..","E":".","F":"..-.","G":"--.","H":"....","I":"..","J":".---","K":"-.-","L":".-..","M":"--","N":"-.","O":"---","P":".--.","Q":"--.-","R":".-.","S":"...","T":"-","U":"..-","V":"...-","W":".--","X":"-..-","Y":"-.--","Z":"--..","1":".----","2":"..---","3":"...--","4":"....-","5":".....","6":"-....","7":"--...","8":"---..","9":"----.","0":"-----"}

morse_to_letter = {v:k for (k,v) in letter_to_morse.items()}

def toMorse(message):
    morse = [letter_to_morse[c] for c in message]
    #print(morse)
    return message

def toMessage(morse):
    message = [morse_to_letter[c] for c in morse]
    #print(message)
    return message

def blinkMessage(message):
    morse = toMorse(message)
    for c in morse:
        for i in c:
            if i == ".":
                blink(1)
            else:
                blink(3)
            sleep(1)
            if c.index(i) == len(c)-1:
                sleep(2) # plus 1 above = 3 -> between letters
    sleep(3) # plus 3 above = 6 -> between words

def retransmitMode():
    stack = Queue.Queue
    while(True):
        #recieve message
        if(end_of_word):
            stack.put_nowait(word)

def blinkWorker():
    while True:
        word = stack.get()
        if not word is None:
            blinkMessage(word)
            q.task_done()

t = Thread(target=blinkWorker)
t.daemon = True
t.start()


