./morse_code -> Making RasPi boards blink morse code to one another using
an LED and photoresistor.

##TODO

|Item|Assigned To|
|---|:---:|
|Chatroom user list| Dakota
|Chatroom user list updates| Kyle
|Chatroom message echo| Ben
|Eliminate ghost packets| Ezra
|Other IRC commands| Dakota, Others


####Chatroom User List
Maintain the current users of the chatroom in memory, with the addition of rooms. Users will be stored in a dict of lists as follows:  `{name_of_room:[user1,user2,user3],name_of_other_room:[user4,user5,user6]}`

####Chatroom User List Updates
Be able to update the user list whenever a user joins or leaves a room, so the server knows who to echo messages to. Users will join or leave the room using [these commands](http://www.ircbeginner.com/ircinfo/ircc-commands.html).

####Chatroom Message Echo
Whenever the server recieves a message for a certain room, forward that message on to be displayed by every user in that room. When a user sends a message, it is sent to everyone in every room that user is in.

####Other IRC Commands
Implement some of the other IRC commands found [here](http://www.ircbeginner.com/ircinfo/ircc-commands.html). Private messaging is priority one, followed by whatever else looks good.
