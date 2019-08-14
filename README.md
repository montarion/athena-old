Welcome to athena v3.0

The goal of this project is to create a personal assistant running on a raspberry pi.

for now features include:

monitor anime

monitor series to see when downloaded

keep track of a downloaded-but-not-yet-watched list

communicate with webfront

communicate with app

have centralised settings, configurable through that webfront

be encrypted

generate a message of the day

integrate with google calender(to see when user is free to work on their not-yet-watched list)


Some design principles: the project must be

*modular

*clear(easy to find whatever function)

*secure

*efficient(in code)

*reliable(re-establish lost connections for example)

what does that all look like then?

Every class does one thing, and it does it perfectly. One class per file. Classes will always return something. 
If not an actual result, that a status code. 0 is SUCESS, 1 is generic failure, others will be as necessary and
then documented here. The script starts with a start.py file, that calls threaded functions. They will be(for now):

Networking(listen for and establish connections to any client that wants to join.)

Website(running the website and responding to events that come from it

Modules(monitoring, communication, generating motd)

    Event(responds to and sends out events*, to and from the modules)

    Motd(generates message of the day)

    Anime(watch for new anime)

    Filewatch(watch for filechanges to see if a file was access)

    Google(get the calendar)

    Settings(get and set the settings)

    Website(host and communicate with the website)
    
The different classes communicate through redis

*an Event is defined as a specific thing that happens, which requires or invites the user's attention. Examples include:

    - a new show being watchable

    - someone coming home

    - a new unknown client connecting/disconnecting

    - an upcoming google calendar event


The above must work reliably, in real world environments, before moving on to adding new functions.
