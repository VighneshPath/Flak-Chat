# Flak-Chat

A proprietary freeware instant messaging Web Application that allows a user to chat with other users, in the form of direct messages or separate server messages.

This Application tries to replicate Whatsapp's User Interface for Direct Messages and Discord's User Interface for Server Messages, though the similar name to Slack, it does not try to replicate any features from it.

#### This Web Application was made for the completion of the CS50 Course, and fulfills the following requirements: 

https://docs.cs50.net/ocw/web/projects/2/project2.html

#### Some Additional Features:

    The Application Uses A database, as opposed to using global variables as mentioned in the Project Requirements.



### Link to demonstration: 

[![Watch the video](https://cdn.discordapp.com/attachments/703184836097081406/731153153650720798/tn.png)](https://youtu.be/mf0qoZe-Pl4)

### Usage: 

    1) Visit: https://flak-chat.herokuapp.com/
    
    2) Create an account by clicking the sign up button, and entering a Username, Email and Password. The Password is stored using a hash function securely in a database.
    
    3) Each User is identified by a unique User ID located in the Profile tab, and has the option to Add a friend, Create a Server and Join a Server
    
    4) A User ID is used to Add friends temporarily, and like whatsapp, the friends are permanently registered to the database once a Message is sent by the user.
    
    5) A User can Create a server having a Unique Server ID, or can Join a Server. 
    
    6) Each Server is initiated with a default General Channel. The User who created the server has the option to Add a Channel, Delete a Channel, or Delete the Server.
    

## Features to be added in the near future or are "buggy"

    - An option to leave the Server, once joined.
    
    - A better way to represent a Unique Identity, rahter than using incremental integers.
    
    - Fix Mobile View
    
    
