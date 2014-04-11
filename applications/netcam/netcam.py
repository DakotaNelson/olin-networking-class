import picamera
import time
import numpy as np

# Basically: take a picture with the raspberry pi camera and send it across the
# morse_code network. Now with only two days of latency!

# Learning objectives: encoding, compression, use of hilariously slow networks.

with picamera.PiCamera() as camera:
    size = 64 # get a 64x64 image
    camera.resolution = (size,size)
    camera.color_effects = (128,128) # make the camera capture in black and white

    camera.start_preview()
    time.sleep(5)
    camera.capture('test.data', 'yuv')
    camera.stop_preview()

    img = open("test.jpg","rb")
    Y = np.fromfile(img, dtype=np.uint8, count=size*size)\
            .reshape((size,size)).astype(np.float)

    print(Y)

    #data = img.read(16)
    #while True:
        #data = img.read(16)
        #if not data:
            #break
        #print(repr(data))
