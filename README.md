./morse_code -> Making RasPi boards blink morse code to one another using
an LED and photoresistor.

##TODO

|Item|Assigned To|
|---|:---:|
|Chatroom user list| Dakota
|Get client and server to return data| Dakota
|Chatroom user list updates| Kyle
|Chatroom message echo| Ben
|Eliminate ghost packets| Ezra
|MSG| Dakota
|Users| Dakota


####Chatroom User List
Maintain the current users of the chatroom in memory, with the addition of rooms. Users will be stored in a dict of lists as follows:  `{name_of_room:[[user1_name,ip,port],[user2_name,ip,port],[user3_name,ip,port]],name_of_other_room:[[user4_name,ip,port],[user5_name,ip,port],[user6_name,ip,port]]}`. Note that `[user_name,ip,port]` is not a dictionary because users can change their names on the fly.

####Get Client and Server to Return Data
Currently, the client and server objects simply print out any packets recieved. Instead, they need to actually return data any time some is recieved, so that data can be used by the program that instantiated them.

####Chatroom User List Updates
Be able to update the user list whenever a user joins or leaves a room, so the server knows who to echo messages to. Users will join or leave the room using [these commands](http://www.ircbeginner.com/ircinfo/ircc-commands.html).

####Chatroom Message Echo
Whenever the server recieves a message for a certain room, forward that message on to be displayed by every user in that room. When a user sends a message, it is sent to everyone in every room that user is in.

####MSG
Implement private messaging.

####Users
Allows users to query who is currently in a room.
