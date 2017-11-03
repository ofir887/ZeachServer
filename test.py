import pyrebase
from fbprophet import Prophet
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import Constants
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


def BeachListenerHandler(message):
    print(message)  # {'title': 'Pyrebase', "body": "etc..."}
    paths = str(message['path'])
    paths = paths.split('/')
    if (paths.__len__() > 2):
        newCount = int(message['data'])
        beach = BeachListener(paths[1], newCount, paths[2])
        beachId = data.child(
            Constants.BeachesListener + "/" + Constants.Country + "/" + beach.Country + "/" + beach.BeachListenerID + "/" + Constants.BeachID).get().val()
        beach.setBeachID(beachId)
        beach.print()
        newBeachCountValueByGps = beach.CurrentCount;
        CurrentHour = datetime.datetime.now().hour;
        strMixed = Constants.Beaches + "/" + Constants.Country + "/" + beach.Country + "/" + beach.BeachID + "/" + Constants.Hours + "/" + CurrentHour.__str__() + "/"
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
        data.child(
            Constants.Beaches + "/" + Constants.Country + "/" + beach.Country + "/" + beach.BeachID + "/" + Constants.Result).set(
            int(round(newValue)))
        data.child(
            Constants.Beaches + "/" + Constants.Country + "/" + beach.Country + "/" + beach.BeachID + "/" + Constants.CurrentPeople).set(
            int(round(newBeachCountValueByGps)))


def uploadBeachFileToCloud(aFirebaseStorage, aFilePath, aBeachName):
    aFirebaseStorage.child(aFilePath).put(
        Constants.DownloadFilesPath + aBeachName + Constants.csvFormat);
    aFirebaseStorage.child(aFilePath).put(
        Constants.DownloadFilesPath + aBeachName + Constants.xlsxFormat);
    print("Updated Files !")


def savePredictionToFile(aForecast, aBeachName):
    Date = aForecast['ds'];
    minHourValue = np.exp(aForecast[['yhat_lower']]);
    maxHourValue = np.exp(aForecast[['yhat_upper']]);
    predictedHourValue = np.exp(aForecast[['yhat']]);
    # TODO
    minDailyValue = np.exp(aForecast[['daily_lower']]);
    maxDailyValue = np.exp(aForecast[['daily_upper']]);
    predictedDailyValue = np.exp(aForecast[['daily']]);
    Excel = pd.DataFrame({'ds': Date, 'y': predictedHourValue['yhat'], 'yhat_lower': minHourValue['yhat_lower'],
                          'yhat_upper': maxHourValue['yhat_upper'],
                          'daily_lower': minDailyValue['daily_lower'], 'daily_upper': maxDailyValue['daily_upper'],
                          'daily': predictedDailyValue['daily']});
    Excel.to_csv(aBeachName + Constants.csvFormat);
    Excel.to_excel(aBeachName + Constants.xlsxFormat, sheet_name='sheet1', index=False);
    print("Files Saved !")

def update24InDataBase(afireaseData):
    #TODO
    s = afireaseData.get()

def TimeSeriesAlogrithm(aBeachFile, aBeachName):
    # storage = firebase.storage()
    BeachData = pd.read_csv(Constants.DownloadFilesPath + aBeachName + Constants.csvFormat)
    BeachData['y'] = np.log(BeachData['y'])
    ProphetAlgorithm = Prophet(daily_seasonality=True, yearly_seasonality=False, weekly_seasonality=False);
    ProphetAlgorithm.fit(BeachData)
    Predict = ProphetAlgorithm.make_future_dataframe(periods=24 * 1, freq='H')
    Forecast = ProphetAlgorithm.predict(Predict)
    print("Forecasting algorithm finished !")
    savePredictionToFile(Forecast, aBeachName)


config = {
    "apiKey": "apiKey",
    "authDomain": Constants.FireBaseUrl,
    "databaseURL": Constants.FireBaseUrl,
    "storageBucket": Constants.FirebaseStorage
}

firebase = pyrebase.initialize_app(config)
data = firebase.database()
BeachListenerStream = data.child(Constants.BeachesListener + "/" + Constants.Country).stream(BeachListenerHandler,
                                                                                             stream_id="beach count")
# storage = firebase.storage()
# storage.child("Users/ofir.pdf").put("/Users/ofirmonis/Desktop/Flight confirmation.pdf",token=None)
schech = BlockingScheduler();

beachesFiles = data.child(Constants.Files + Constants.BeachesFiles).get();
for beach in beachesFiles.each():
    beachName = beach.key();
    # print(beach.val())
    filePath = data.child(Constants.Files + Constants.BeachesFiles).child(beach.key()).child('filePath').get()
    filePath = filePath.val()
    print(filePath)
    storage = firebase.storage();
    beachFile = storage.child(filePath + "/" + beachName + Constants.csvFormat).download(
        Constants.DownloadFilesPath + beachName + Constants.csvFormat);
    TimeSeriesAlogrithm(beachFile, beachName)
    update24InDataBase(data)
    uploadBeachFileToCloud(storage, filePath, beachName)


@schech.scheduled_job('cron', day_of_week='mon-sat', hour=15)
def scheduled_job():
    # print('This job is run every weekday at 5pm.')
    beachesFiles = data.child(Constants.Files + Constants.BeachesFiles).get();
    for beach in beachesFiles.each():
        beachName = beach.key();
        # print(beach.val())
        filePath = data.child(Constants.Files + Constants.BeachesFiles).child(beach.key()).child('filePath').get()
        filePath = filePath.val()
        print(filePath)
        storage = firebase.storage();
        beachFile = storage.child(filePath).download(Constants.DownloadFilesPath + beachName);
        TimeSeriesAlogrithm(beachFile, beachName)
        uploadBeachFileToCloud(storage, filePath, beachName)


schech.start()
###
