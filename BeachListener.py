class BeachListener(object):
    Country = ""
    CurrentCount = 0
    BeachID = ""
    BeachListenerID = ""

    def __init__(self, country, count, beachListenerId):
        self.Country = country
        self.CurrentCount = count
        self.BeachListenerID = beachListenerId

    def setBeachID(self, id):
        self.BeachID = id

    def print(self):
        print(self.BeachID + " " + self.Country + " " + str(self.CurrentCount) + " " + self.BeachListenerID)
