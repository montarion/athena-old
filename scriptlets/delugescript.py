import os, json, datetime, sys
from time import sleep

#os.system("touch /home/pi/code/apptests/secondserver/scriptlets/torrentfile.txt")

with open("/home/pi/code/apptests/secondserver/scriptlets/torrentfile.txt", "w") as f:
    f.write(sys.argv[1])


