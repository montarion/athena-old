Welcome to athena v3.0

The goal of this project is to create a personal assistant running on a raspberry pi.

for now features include:

*monitor anime

*monitor series to see when downloaded

*keep track of a downloaded-but-not-yet-watched list

*communicate with webfront

*communicate with app

*have centralised settings, configurable through that webfront

*be encrypted

*integrate with google calender(to see when user is free to work on their not-yet-watched list)

CHANGELOG

02-11-19: Release Alpha 0.1

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

   xMotd(generates message of the day)

   xAnime(watch for new anime)

   xGoogle(get the calendar)

   xSettings(get and set the settings)

   xWebsite(host and communicate with the website)
    
The different classes communicate through redis

The above must work reliably, in real world environments, before moving on to adding new functions.
