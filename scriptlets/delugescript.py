import os, json, datetime
from time import sleep

os.system("deluge-console \"info --sort time_added\" | tail -n 7 | head -n 1 > trackfiles/torrentdone.txt")

