from components.networking import Networking
from components.modules import Modules
from components.website import Website
import threading
from time import sleep

t1 = threading.Thread(target=Networking().runserver)
t2 = threading.Thread(target=Modules().standard)
t3 = threading.Thread(target=Website().runsite)

t1.start()
t2.start()
t3.start()
