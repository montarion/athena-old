import threading
from time import sleep
from components.server import server, modules
from components.site import site
from components.gatekeeper import gatekeeper

#t0 = threading.Thread(target=server().listen).start()
#t1 = threading.Thread(target=modules().standard).start()
#t2 = threading.Thread(target=site().runsite).start()
#t3 = threading.Thread(target=gatekeeper().watch).start()
#t4 = threading.Thread(target=modules().filereader).start()

t0 = threading.Thread(target=gatekeeper().watch).start()
#sleep(3)
t1 = threading.Thread(target=site().runsite).start()
sleep(1)
t2 = threading.Thread(target=server().listen).start()
sleep(3)
t3 = threading.Thread(target=modules().standard).start()
print("started main")
sleep(2)
t4 = threading.Thread(target=modules().filereader).start()

#t3.start()
#sleep(5)

#t0.start()
#t1.start()
#t2.start()
#sleep(3)
#t4.start()
