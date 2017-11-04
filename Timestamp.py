class Timestamp(object):
    BeachID = ''
    BeachListenerID = ''
    BeachName = ''
    Timestamp = ''
    UserID = ''
    Country = ''

    def __init__(self):
        self.BeachID;
        self.BeachListenerID
        self.Timestamp
        self.UserID
        self.Country

    # def __init__(self, aBeachID, aBeachListenerID, aTimestamp, aUserID):
    #     self.BeachID = aBeachID
    #     self.BeachListenerID = aBeachListenerID
    #     self.Timestamp = aTimestamp
    #     self.UserID = aUserID

    def setBeachId(self, aBeachId):
        self.BeachID = aBeachId;

    def setUserId(self, aUserId):
        self.UserID = aUserId;

    def setTimestamp(self, aTimestamp):
        self.Timestamp = aTimestamp;

    def setBeachName(self, aBeachName):
        self.BeachName = aBeachName;

    def setBeachListenerId(self, aBeachListenerID):
        self.BeachListenerID = aBeachListenerID;

    def setBeachCountry(self, aCountry):
        self.Country = aCountry

    def print(self):
        print(self.BeachName)
        print(self.BeachID)
        print(self.BeachListenerID)
        print(self.UserID)
        print(self.Timestamp)
        print(self.Country)
