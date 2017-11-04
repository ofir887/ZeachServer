class BeachListener(object):
    Country = ""
    CurrentDevicesCount = 0
    BeachID = ""
    BeachListenerID = ""

    def __init__(self, country, count, beachListenerId):
        self.Country = country
        self.CurrentDevicesCount = count
        self.BeachListenerID = beachListenerId

    def setBeachID(self, id):
        self.BeachID = id

    def print(self):
        print(self.BeachID + " " + self.Country + " " + str(self.CurrentDevicesCount) + " " + self.BeachListenerID)
