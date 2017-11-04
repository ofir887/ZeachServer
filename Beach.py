from Hours import Hours
import Constants


class Beach(object):
    Country = ""
    name = ""
    CurrentDevices = 500
    Result = 0;
    coords = []
    Users = []
    hours = Hours

    def __init__(self, name, coords, country):
        self.name = name
        self.coords = coords
        self.Country = country
        self.Users = ""
        self.hours = Hours()

    def make_Beach(name, coords):
        beach = Beach(name, coords)
        return beach

    def printBeach(self, beach):
        print(beach.name, beach.coords)

    def dump(self):
        return {Constants.BeachName: self.name, Constants.Coords: self.coords,
                Constants.CurrentDevices: self.CurrentDevices,
                Constants.Peoplelist: self.Users, Constants.Result: self.Result,
                'Hours': self.hours.dump()}

    def getCountry(self):
        return self.Country

    def beachListenerDump(self, beachID):
        return {Constants.BeachName: self.name, Constants.CurrentDevices: self.CurrentDevices, Constants.BeachID: beachID}
