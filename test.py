import pyrebase
from fbprophet import Prophet
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import _thread as thread
import threading
import datetime


def stream_handler(message):
    print(message) # {'title': 'Pyrebase', "body": "etc..."}
    print(message["path"])
    str = message["path"]
    newBeachCountValueByGps = message["data"];
    CurrentHour = datetime.datetime.now().hour;
    strMixed = "Beaches/Country/Israel/Tzok/Hours/"+CurrentHour.__str__()+"/"
    predictedHourValue = data.child(strMixed).get()
    print(predictedHourValue.val())
    if (str !='111'):
        newValue=0;
        if (int(newBeachCountValueByGps) > int(predictedHourValue.val())):
            newValue = (int(newBeachCountValueByGps))*1.05;
        else:
            if (int(newBeachCountValueByGps) < int(predictedHourValue.val())):
                newValue = (int(newBeachCountValueByGps))+int(predictedHourValue.val())/2*1.05;

        str = "Beaches/"+str
        data.child("Beaches/Country/Israel/Tzok/Result").set(newValue)
        data.child("Beaches/Country/Israel/Tzok/Current People").set(int(newBeachCountValueByGps))

config = {
  "apiKey": "apiKey",
  "authDomain": "https://zeach-ab079.firebaseio.com/",
  "databaseURL": "https://zeach-ab079.firebaseio.com/",
  "storageBucket": "gs://zeach-ab079.appspot.com/"
}

firebase = pyrebase.initialize_app(config)
data = firebase.database()
mystream = data.child("BeachesListener/Country/Israel/Tzok/Current People").stream(stream_handler, stream_id="beach count")








