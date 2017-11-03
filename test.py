import pyrebase
from fbprophet import Prophet
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler


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


def stream_handler(message):
    print(message)  # {'title': 'Pyrebase', "body": "etc..."}
    paths = str(message['path'])
    paths = paths.split('/')
    if (paths.__len__() > 2):
        newCount = int(message['data'])
        #  beachId = data.child("BeachesListener/Country/" + paths[1] + "/" + paths[2] + "/BeachID").get().val()
        beach = BeachListener(paths[1], newCount, paths[2])
        beachId = data.child(
            "BeachesListener/Country/" + beach.Country + "/" + beach.BeachListenerID + "/BeachID").get().val()
        beach.setBeachID(beachId)
        # beachId = data.child("BeachesListener/Country/" + beach.Country + "/" + beach.BeachID + "/BeachID").get().val()
        beach.print()
        newBeachCountValueByGps = beach.CurrentCount;
        CurrentHour = datetime.datetime.now().hour;
        strMixed = "Beaches/Country/" + beach.Country + "/" + beach.BeachID + "/Hours/" + CurrentHour.__str__() + "/"
        predictedHourValue = data.child(strMixed).get()
        print(strMixed)
        print(predictedHourValue.val())
        newValue = 0;
        if (int(newBeachCountValueByGps) > int(predictedHourValue.val())):
            newValue = (int(newBeachCountValueByGps)) * 1.05;
        else:
            if (int(newBeachCountValueByGps) < int(predictedHourValue.val())):
                newValue = (int(newBeachCountValueByGps)) + int(predictedHourValue.val());
                newValue = newValue / 2 * 1.5
        data.child("Beaches/Country/" + beach.Country + "/" + beach.BeachID + "/Result").set(int(round(newValue)))
        data.child("Beaches/Country/" + beach.Country + "/" + beach.BeachID + "/CurrentPeople").set(
            int(round(newBeachCountValueByGps)))


def TimeSeriesAlogrithm():
    storage = firebase.storage()
    print("test");


config = {
    "apiKey": "apiKey",
    "authDomain": "https://zeach-ab079.firebaseio.com/",
    "databaseURL": "https://zeach-ab079.firebaseio.com/",
    "storageBucket": "zeach-ab079.appspot.com"
}

firebase = pyrebase.initialize_app(config)
data = firebase.database()
mystream = data.child("BeachesListener/Country").stream(stream_handler, stream_id="beach count")
# storage = firebase.storage()
# storage.child("Users/ofir.pdf").put("/Users/ofirmonis/Desktop/Flight confirmation.pdf",token=None)
schech = BlockingScheduler();


@schech.scheduled_job('cron', day_of_week='mon-sat', hour=15)
def scheduled_job():
    # print('This job is run every weekday at 5pm.')
    TimeSeriesAlogrithm()


schech.start()
###
