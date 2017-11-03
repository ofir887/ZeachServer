import pyrebase
import Constants
import json

config = {
    "apiKey": "apiKey",
    "authDomain": Constants.FireBaseUrl,
    "databaseURL": Constants.FireBaseUrl,
    "storageBucket": Constants.FirebaseStorage
}

firebase = pyrebase.initialize_app(config)
data = firebase.database()
storage = firebase.storage()
Country = "Israel";
City = "Tel Aviv";
BeachName = "Ofir";
csvFileName = "Ofir.csv";
xlsxFileName = "Ofir.xlsx";
storage.child(Constants.Beaches).child(Country).child(City).child(BeachName).child(csvFileName).put(
    "/Users/ofirmonis/PycharmProjects/firebaseStream/Ofir11.csv")
storage.child(Constants.Beaches).child(Country).child(City).child(BeachName).child(xlsxFileName).put(
    "/Users/ofirmonis/PycharmProjects/firebaseStream/Ofir11.xlsx")
data.child(Constants.Files).child(Constants.BeachesFiles).child(BeachName).child("filePath").set(
    Constants.Beaches + "/" + Country + "/" + City + "/" + BeachName);

print("Updated !")

