from components.networking import Networking
from components.anime import anime
from components.site import Site
import threading
from time import sleep

t1 = threading.Thread(target=Networking().runsite)
t2 = threading.Thread(target=anime().search)
t3 = threading.Thread(target=Site().runsite)
#t2.start()
t1.start()
#t3.start()
