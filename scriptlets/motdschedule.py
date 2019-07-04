import os, json
# this script is ran every hour by cron. check with "crontab -e"

with open("/home/pi/code/apptests/secondserver/trackfiles/singleton.txt") as f:
    tmpolddict = str(f.read())
    olddict = json.loads(tmpolddict)

olddict["motd"] = "empty"
olddict["notification"] = ["greylynx", "practice!", "time to code!"] #{\"notification\":\[\"greylynx/alerts\", \"practice\", \"time to code~!\"]}

with open("/home/pi/code/apptests/secondserver/trackfiles/singleton.txt", "w") as f:
    f.write(json.dumps(olddict))
