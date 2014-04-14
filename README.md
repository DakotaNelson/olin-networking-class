This is a team project repository for the Computer Networks class at the [Olin College of Engineering](http://www.olin.edu/), Spring 2014, taught by [Alex Morrow](http://www.olin.edu/faculty/profile/alexander-morrow/).


######Team members:
* [Dakota Nelson](http://www.dakotanelson.com/)
* Ezra Varady
* Kyle Mayer
* Benny Tang
 
######Sections:

    `./morse_code`
Making RasPi boards blink morse code to one another using direct GPIO connections (with LEDs across them for das blinkenlights purposes, of course).

    `./applications/chatroom`
A socket-based chatroom application built to run on top of the morse_code network (slowly).

    `./applications/netcam'
A program to take a picture using the Raspberry Pi's camera, convert it to a 64x64 greyscale image, and send it across the network to a listening instance of the program.


All of this is written for Python 3.
