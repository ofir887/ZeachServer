import pyrebase
from fbprophet import Prophet
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import Constants
from Hours import Hours
from Hours import CurrentHourPrediction
from BeachListener import BeachListener
from Timestamp import Timestamp
import time
from apscheduler.schedulers.blocking import BlockingScheduler

global mFirebaseData
global mBeachId
global mCountry
INTERVAL = 60;


# TODO fix calculations & push new 24 hours values to csv file
def calculateNewEstimation(aBeach, aPrediction, aCurrentDevicesOnBeach):
    newResultValue = 0;
    if (int(aCurrentDevicesOnBeach) > int(aPrediction.getCurrentEstimation())):
        newResultValue = (int(aCurrentDevicesOnBeach)) * 1.05;
    else:
        if (int(aCurrentDevicesOnBeach) < int(aPrediction.getCurrentEstimation())):
            newResultValue = (int(aCurrentDevicesOnBeach)) + int(aPrediction.getCurrentEstimation());
            newResultValue = newResultValue / 2 * 1.5
            resultPath = Constants.Beaches + "/" + Constants.Country + "/" + aBeach.Country + "/" + aBeach.BeachID + "/" + Constants.Result
            mFirebaseData.child(resultPath).set(
                int(round(newResultValue)))
            currentDevicesPath = Constants.Beaches + "/" + Constants.Country + "/" + aBeach.Country + "/" + aBeach.BeachID + "/" + Constants.CurrentDevices
            mFirebaseData.child(currentDevicesPath).set(int(round(aCurrentDevicesOnBeach)))
    return newResultValue;


def BeachListenerHandler(message):
    print(message)  # {'title': 'Pyrebase', "body": "etc..."}
    paths = str(message['path'])
    paths = paths.split('/')
    if (paths.__len__() > 2):
        newDevicesCount = int(message['data'])
        beach = BeachListener(paths[1], newDevicesCount, paths[2])
        beachIdPath = Constants.BeachesListener + "/" + Constants.Country + "/" + beach.Country + "/" + beach.BeachListenerID + "/" + Constants.BeachID
        beachId = mFirebaseData.child(beachIdPath).get().val()
        beach.setBeachID(beachId)
        beach.print()
        onBeachDevicesCountByGps = beach.CurrentDevicesCount;
        CurrentHour = datetime.datetime.now().hour;
        hourPath = Constants.Beaches + "/" + Constants.Country + "/" + beach.Country + "/" + beach.BeachID + "/" + Constants.Hours + "/" + CurrentHour.__str__()
        prediction = CurrentHourPrediction(mFirebaseData, hourPath)
        prediction.print();
        calculateNewEstimation(beach, prediction, onBeachDevicesCountByGps)


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
    update24HoursInDataBase(minHourValue, maxHourValue, predictedHourValue)


def update24HoursInDataBase(minHourValue, maxHourValue, predictedHourValue):
    len = predictedHourValue.__len__()
    hours = Hours();
    minEstimationValue = []
    maxEstimationValue = []
    currentEstimationValue = []
    for i in range(len - (24), len):
        minEstimationValue.append(minHourValue['yhat_lower'][i])
        maxEstimationValue.append(maxHourValue['yhat_upper'][i])
        currentEstimationValue.append(predictedHourValue['yhat'][i])
    # TODO delete one hour from initial excel
    for i in range(0, 24):
        mFirebaseData.child(Constants.Beaches).child(Constants.Country).child(mCountry).child(mBeachId).child(
            Constants.Hours).child(i).child(Constants.MinEstimation).set(minEstimationValue[i])
        mFirebaseData.child(Constants.Beaches).child(Constants.Country).child(mCountry).child(mBeachId).child(
            Constants.Hours).child(i).child(Constants.CurrentEstimation).set(currentEstimationValue[i])
        mFirebaseData.child(Constants.Beaches).child(Constants.Country).child(mCountry).child(mBeachId).child(
            Constants.Hours).child(i).child(Constants.MaxEstimation).set(maxEstimationValue[i])
    print("update 24 hours in cloud !")


def TimeSeriesAlogrithm(aBeachName):
    BeachData = pd.read_csv(Constants.DownloadFilesPath + aBeachName + Constants.csvFormat)
    BeachData['y'] = np.log(BeachData['y'])
    ProphetAlgorithm = Prophet(daily_seasonality=True, yearly_seasonality=False, weekly_seasonality=False);
    ProphetAlgorithm.fit(BeachData)
    Predict = ProphetAlgorithm.make_future_dataframe(periods=24 * 1, freq='H')
    Forecast = ProphetAlgorithm.predict(Predict)
    print("Forecasting algorithm finished !")
    savePredictionToFile(Forecast, aBeachName)


def ReadTimestamps():
    mTimestamp = Timestamp()
    UsersTimestamps = mFirebaseData.child(Constants.Timestamps).get();
    print("running")
    if (UsersTimestamps.each() is not None):
        for timestamp in UsersTimestamps.each():
            userId = timestamp.key();
            mTimestamp.setUserId(userId)
            print(userId);
            details = mFirebaseData.child(Constants.Timestamps).child(userId).get()
            details = timestamp.val();
            details = dict(details)
            mTimestamp.setTimestamp(details.get(Constants.Timestamp_Timestamp))
            mTimestamp.setBeachName(details.get(Constants.Timestamp_BeachName))
            mTimestamp.setBeachId(details.get(Constants.Timestamp_BeachID))
            mTimestamp.setBeachListenerId(details.get(Constants.Timestamp_BeachListenerId))
            mTimestamp.setBeachCountry(details.get(Constants.Timestamp_Country))
            mTimestamp.print()
            checkInHour = datetime.datetime.utcfromtimestamp(int(mTimestamp.Timestamp)).hour
            checkInMinutes = int(datetime.datetime.fromtimestamp(int(mTimestamp.Timestamp)).minute)
            print(checkInMinutes)
            print(checkInHour)
            currentHour = datetime.datetime.utcnow().hour;
            currentMinute = datetime.datetime.utcnow().minute;
            print(currentHour)
            print(currentMinute)
            if ((checkInHour + Constants.Timestamp_Max_Hour) > currentHour):
                mFirebaseData.child(Constants.Timestamps).child(mTimestamp.UserID).remove()
                mFirebaseData.child(Constants.Beaches).child(Constants.Country).child(mTimestamp.Country).child(
                    mTimestamp.BeachID).child(Constants.Peoplelist).child(mTimestamp.UserID).remove();
                mFirebaseData.child(Constants.Users).child(mTimestamp.UserID).child(Constants.CurrentBeach).remove()
                CurrentDevices = mFirebaseData.child(Constants.BeachesListener).child(Constants.Country).child(
                    mTimestamp.Country).child(mTimestamp.BeachListenerID).child(Constants.CurrentDevices).get()
                CurrentDevices = int(CurrentDevices.val());
                CurrentDevices = CurrentDevices - 1;
                mFirebaseData.child(Constants.BeachesListener).child(Constants.Country).child(mTimestamp.Country).child(
                    mTimestamp.BeachListenerID).child(Constants.CurrentDevices).set(CurrentDevices)


config = {
    "apiKey": "apiKey",
    "authDomain": Constants.FireBaseUrl,
    "databaseURL": Constants.FireBaseUrl,
    "storageBucket": Constants.FirebaseStorage
}

firebase = pyrebase.initialize_app(config)
mFirebaseData = firebase.database()
BeachListenerStream = mFirebaseData.child(Constants.BeachesListener + "/" + Constants.Country).stream(
    BeachListenerHandler,
    stream_id="beach count")

schech = BlockingScheduler();
# while (True):

while (True):
    ReadTimestamps()
    time.sleep(INTERVAL)

# beachesFiles = mFirebaseData.child(Constants.Files + Constants.BeachesFiles).get();
#
# for beach in beachesFiles.each():
#     beachName = beach.key();
#     # print(beach.val())
#     filePath = mFirebaseData.child(Constants.Files + Constants.BeachesFiles).child(beach.key()).child('filePath').get()
#     filePath = filePath.val()
#     print(filePath)
#     mBeachId = mFirebaseData.child(Constants.Files + Constants.BeachesFiles).child(beach.key()).child(
#         Constants.BeachID).get()
#     mBeachId = mBeachId.val();
#     print(mBeachId)
#     mCountry = mFirebaseData.child(Constants.Files + Constants.BeachesFiles).child(beach.key()).child(
#         Constants.Country).get()
#     mCountry = mCountry.val();
#     print(mCountry)
#     storage = firebase.storage();
#     if (beachName == 'Nir'):
#         beachFile = storage.child(filePath + "/" + beachName + Constants.csvFormat).download(
#             Constants.DownloadFilesPath + beachName + Constants.csvFormat);
#         TimeSeriesAlogrithm(beachName)
#         uploadBeachFileToCloud(storage, filePath, beachName)

beachesFiles = mFirebaseData.child(Constants.Files + Constants.BeachesFiles).get();
for beach in beachesFiles.each():
    mBeachId = beach.key();
    print(mBeachId)
    beachName = mFirebaseData.child(Constants.Files + Constants.BeachesFiles).child(mBeachId).child(
        Constants.BeachName).get()
    beachName = beachName.val();
    filePath = mFirebaseData.child(Constants.Files + Constants.BeachesFiles).child(mBeachId).child(
        'filePath').get()
    filePath = filePath.val()
    print(filePath)
    print(mBeachId)
    mCountry = mFirebaseData.child(Constants.Files + Constants.BeachesFiles).child(mBeachId).child(
        Constants.Country).get()
    mCountry = mCountry.val();
    print(mCountry)
    storage = firebase.storage();
    if (beachName != "Ofir"):
        beachFile = storage.child(filePath + "/" + beachName + Constants.csvFormat).download(
            Constants.DownloadFilesPath + beachName + Constants.csvFormat);
        mFirebaseData = mFirebaseData
        TimeSeriesAlogrithm(beachName)
        uploadBeachFileToCloud(storage, filePath, beachName)


@schech.scheduled_job('cron', day_of_week='mon-sat', hour=2)
def scheduled_job(mFirebaseData=mFirebaseData):
    # print('This job is run every weekday at 5pm.')
    beachesFiles = mFirebaseData.child(Constants.Files + Constants.BeachesFiles).get();
    for beach in beachesFiles.each():
        mBeachId = beach.key();
        # print(beach.val())
        beachName = mFirebaseData.child(Constants.Files + Constants.BeachesFiles).child(mBeachId).child(
            Constants.BeachName).get()
        beachName = beachName.val();
        filePath = mFirebaseData.child(Constants.Files + Constants.BeachesFiles).child(mBeachId).child(
            'filePath').get()
        filePath = filePath.val()
        print(filePath)
        # mBeachId = mFirebaseData.child(Constants.Files + Constants.BeachesFiles).child(beach.key()).child(
        #     Constants.BeachID).get()
        # mBeachId = mBeachId.val();
        print(mBeachId)
        mCountry = mFirebaseData.child(Constants.Files + Constants.BeachesFiles).child(mBeachId).child(
            Constants.Country).get()
        mCountry = mCountry.val();
        print(mCountry)
        storage = firebase.storage();
        if (beachName != "Ofir"):
            beachFile = storage.child(filePath + "/" + beachName + Constants.csvFormat).download(
                Constants.DownloadFilesPath + beachName + Constants.csvFormat);
            mFirebaseData = mFirebaseData
            TimeSeriesAlogrithm(beachFile, beachName, mBeachId, mCountry)
            uploadBeachFileToCloud(storage, filePath, beachName)


schech.start()
###
