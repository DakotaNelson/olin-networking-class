import picamera
import time

# Basically: take a picture with the raspberry pi camera and send it across the
# morse_code network. Now with only two days of latency!

# Learning objectives: encoding, compression, use of hilariously slow networks.

with picamera.PiCamera() as camera:
    camera.resolution = (64,64)

    camera.start_preview()
    time.sleep(5)
    camera.capture('test.jpg')
    camera.stop_preview()
