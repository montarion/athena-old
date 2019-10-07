import os

import socketio, json, redis, threading
from time import sleep

from components.motd import motd
from components.anime import anime


# run your general modules here
class Modules:
    def __init__(self):
        pass

    def standard(self):
        while True:
            anime().search()

            sleep(120)
