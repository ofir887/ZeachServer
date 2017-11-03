# from firebase import firebase
import pyrebase
import Constants


class Hours(object):
    Hour = [0] * 24;

    def __init__(self):
        self.Hour = [0] * 24;

    def setHourPeople(self, index, sum):
        self.Hour[index] = sum;

    def dump(self):
        i = 0;
        lst2 = [];
        while (i < len(self.Hour)):
            lst2.append(self.Hour[i])
            i = i + 1
        return lst2;


class Coords(object):
    lat = 0.0
    lng = 0.0

    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng

    def dump(self):
        return {'lat': self.lat, "lng": self.lng}

    def print(self):
        print('lat:', self.lat, ' lng:', self.lng)


class Beach(object):
    Country = ""
    name = ""
    Currentcount = 500
    Result = 0;
    PreviousHourCount = 0;
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
        return {'BeachName': self.name, 'Coords': self.coords, 'CurrentPeople': self.Currentcount,
                'PreviousHourPeople': self.PreviousHourCount, 'Peoplelist': self.Users, 'Result': self.Result,
                'Hours': self.hours.dump()}

    def getCountry(self):
        return self.Country

    def beachListenerDump(self, beachID):
        return {'BeachName': self.name, 'CurrentPeople': self.Currentcount, "BeachID": beachID}


# Set coords to fit data structure
def setCoordsAsDictionary(coords):
    newCoords = dict()
    i = 0;
    while (i < len(coords)):
        string = 'latlng' + str(i + 1)
        newCoords.update({string: coords[i].dump()})
        i = i + 1
    return newCoords


config = {
    "apiKey": "apiKey",
    "authDomain": "https://zeach-ab079.firebaseio.com/",
    "databaseURL": "https://zeach-ab079.firebaseio.com/",
    "storageBucket": "zeach-ab079.appspot.com"
}

firebase = pyrebase.initialize_app(config)
data = firebase.database()

beachCoords = []
beachCoords.append(Coords(32.146056, 34.791982))
beachCoords.append(Coords(32.146065, 34.971623))
beachCoords.append(Coords(32.143527, 37.971358))
beachCoords.append(Coords(32.143518, 34.790861))

beachCoords2 = []
beachCoords2.append(Coords(32.320852, 35.130682))
beachCoords2.append(Coords(32.318412, 34.475076))
beachCoords2.append(Coords(31.897635, 34.469299))
beachCoords2.append(Coords(31.912346, 35.012269))
beachFormattedCoords2 = setCoordsAsDictionary(beachCoords2)

beachFormattedCoords = setCoordsAsDictionary(beachCoords)
print(beachFormattedCoords)

#
storage = firebase.storage()
Country = "Israel";
City = "Tel Aviv";
BeachName = "Tzok";
csvFileName = BeachName + ".csv";
xlsxFileName = BeachName + ".xlsx";
#

BeachCoords = Beach(BeachName, beachFormattedCoords, 'Israel');

# BeachCoords.printBeach(BeachCoords)
hours = Hours()
BeachCoords.hours.setHourPeople(4, 500)
BeachID = data.child("Beaches/Country/" + BeachCoords.getCountry()).push(BeachCoords.dump())
BeachListenerID = data.child("BeachesListener/Country/" + BeachCoords.getCountry()).push(
    BeachCoords.beachListenerDump(BeachID['name']))
data.child("Beaches/Country/" + BeachCoords.getCountry() + "/" + BeachID['name']).child("BeachListenerID").set(
    BeachListenerID['name'])
data.child("Beaches/Country/" + BeachCoords.getCountry() + "/" + BeachID['name']).child("BeachID").set(BeachID['name'])

#Add to storage
storage.child(Constants.Beaches).child(Country).child(City).child(BeachName).child(csvFileName).put(
    "/Users/ofirmonis/PycharmProjects/firebaseStream/Ofir11.csv")
storage.child(Constants.Beaches).child(Country).child(City).child(BeachName).child(xlsxFileName).put(
    "/Users/ofirmonis/PycharmProjects/firebaseStream/Ofir11.xlsx")
data.child(Constants.Files).child(Constants.BeachesFiles).child(BeachName).child("filePath").set(
    Constants.Beaches + "/" + Country + "/" + City + "/" + BeachName);
data.child(Constants.Files).child(Constants.BeachesFiles).child(BeachName).child(Constants.BeachID).set(
    BeachID['name']);
data.child(Constants.Files).child(Constants.BeachesFiles).child(BeachName).child(Constants.Country).set(
    Country);
#
print(BeachCoords.hours.dump())
