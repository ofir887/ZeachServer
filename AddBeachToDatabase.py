# from firebase import firebase
import pyrebase
import Constants
from Hours import Hours
from Coords import Coords
from Beach import Beach


# Set coords to fit data structure
def setCoordsAsDictionary(coords):
    newCoords = dict()
    i = 0;
    while (i < len(coords)):
        string = Constants.LatLng + str(i + 1)
        newCoords.update({string: coords[i].dump()})
        i = i + 1
    return newCoords


config = {
    "apiKey": "apiKey",
    "authDomain": Constants.FireBaseUrl,
    "databaseURL": Constants.FireBaseUrl,
    "storageBucket": Constants.FirebaseStorage
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

beachFormattedCoords = setCoordsAsDictionary(beachCoords2)
print(beachFormattedCoords)

#
storage = firebase.storage()
Country = "Israel";
City = "Tel Aviv";
BeachName = "Norni";
csvFileName = BeachName + ".csv";
xlsxFileName = BeachName + ".xlsx";
#

BeachCoords = Beach(BeachName, beachFormattedCoords, 'Israel', 1000);

# BeachCoords.printBeach(BeachCoords)
hours = Hours()
# BeachCoords.hours.setHourPeople(4, 500)
BeachID = data.child("Beaches").push(BeachCoords.dump())
BeachListenerID = data.child("BeachesListener").push(
    BeachCoords.beachListenerDump(BeachID['name']))
data.child("Beaches" + "/" + BeachID['name']).child("BeachListenerID").set(
    BeachListenerID['name'])
data.child("Beaches" + "/" + BeachID['name']).child("BeachID").set(BeachID['name'])

# Add to storage
storage.child(Constants.Beaches).child(Country).child(City).child(BeachName).child(csvFileName).put(
    "/Users/ofirmonis/PycharmProjects/firebaseStream/Ofir11.csv")
storage.child(Constants.Beaches).child(Country).child(City).child(BeachName).child(xlsxFileName).put(
    "/Users/ofirmonis/PycharmProjects/firebaseStream/Ofir11.xlsx")
data.child(Constants.Files).child(Constants.BeachesFiles).child(BeachID['name']).child("filePath").set(
    Constants.Beaches + "/" + Country + "/" + City + "/" + BeachName);
data.child(Constants.Files).child(Constants.BeachesFiles).child(BeachID['name']).child(Constants.BeachID).set(
    BeachID['name']);
data.child(Constants.Files).child(Constants.BeachesFiles).child(BeachID['name']).child(Constants.Country).set(
    Country);
data.child(Constants.Files).child(Constants.BeachesFiles).child(BeachID['name']).child(Constants.BeachName).set(
    BeachCoords.name);
#
print(BeachCoords.hours.dump())
