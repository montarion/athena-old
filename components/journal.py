
class journal:
    def __init__(self):
        pass

    def setentry(self, message):
        time = message["time"]
        location = message["location"]
        message = message["message"]

        entry = "{}, {} - {}".format(time, location, message)
        return entry
    def getentry(self, number=10):
        pass
