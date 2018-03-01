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

import threading

global mFirebaseData
mAccurateFeedbackCount = 0
mEasyToUseFeebackCount = 0
mRating = 0
mNumberOfFeedBacks = 0


def increaseAccurateFeedback():
    global mAccurateFeedbackCount
    mAccurateFeedbackCount = mAccurateFeedbackCount + 1
    print("accurate: ", mAccurateFeedbackCount)

def increaseEasyToUseFeedback():
    global mEasyToUseFeebackCount
    mEasyToUseFeebackCount = mEasyToUseFeebackCount + 1
    print("easy to use: ", mEasyToUseFeebackCount)


def increaseRatingFeedback(rating):
    global mRating
    mRating = mRating + rating
    print("rating: ", mRating)


def setNumberOfFeedBacks(aCount):
    mNumberOfFeedBacks = aCount


class Info(object):
    mBeachId = ""
    mCountry = ""

    def __init__(self, beachId, country):
        self.mBeachId = beachId
        self.mCountry = country


INTERVAL = 60;


def setTrafficFlag(aBeachCapacity, aResult):
    percentage = (aResult / aBeachCapacity) * 100;
    if (percentage >= 80):
        return Constants.HighTraffic
    if (percentage >= 40 and percentage < 80):
        return Constants.MediumTraffic
    else:
        return Constants.LowTraffic


# TODO fix calculations & push new 24 hours values to csv file
def calculateNewEstimation(aBeach, aPrediction, aCurrentDevicesOnBeach, aBeachCapacity):
    newResultValue = 0;
    if (int(aCurrentDevicesOnBeach) > int(aPrediction.getCurrentEstimation())):
        newResultValue = (int(aCurrentDevicesOnBeach)) * 1.05;
    else:
        if (int(aCurrentDevicesOnBeach) < int(aPrediction.getCurrentEstimation())):
            newResultValue = (int(aCurrentDevicesOnBeach)) + int(aPrediction.getCurrentEstimation());
            newResultValue = newResultValue / 2 * 1.5
            # resultPath = Constants.Beaches + "/" + aBeach.BeachID + "/" + Constants.Result
            # mFirebaseData.child(resultPath).set(
            #     int(round(newResultValue)))
            currentDevicesPath = Constants.Beaches + "/" + aBeach.BeachID + "/" + Constants.CurrentDevices
            mFirebaseData.child(currentDevicesPath).set(int(round(aCurrentDevicesOnBeach)))
    # set traffic flag
    resultPath = Constants.Beaches + "/" + aBeach.BeachID + "/" + Constants.Result
    mFirebaseData.child(resultPath).set(
        int(round(newResultValue)))
    trafficFlag = setTrafficFlag(aBeachCapacity, newResultValue)
    mFirebaseData.child(
        Constants.Beaches + "/" + aBeach.BeachID + "/" + Constants.Traffic).set(trafficFlag)
    return newResultValue;


def BeachListenerHandler(message):
    print(message)  # {'title': 'Pyrebase', "body": "etc..."}
    paths = str(message['path'])
    paths = paths.split('/')
    if (paths.__len__() > 2):
        newDevicesCount = int(message['data'])
        beach = BeachListener(paths[0], newDevicesCount, paths[1])
        beachIdPath = Constants.BeachesListener + "/" + beach.BeachListenerID + "/" + Constants.BeachID
        beachId = mFirebaseData.child(beachIdPath).get().val()
        beachCapacity = mFirebaseData.child(Constants.Beaches).child(beachId).child(Constants.Capacity).get().val()
        beach.setBeachID(beachId)
        beach.print()
        onBeachDevicesCountByGps = beach.CurrentDevicesCount;
        CurrentHour = datetime.datetime.now().hour;
        hourPath = Constants.Beaches + "/" + beach.BeachID + "/" + Constants.Hours + "/" + CurrentHour.__str__()
        prediction = CurrentHourPrediction(mFirebaseData, hourPath)
        prediction.print();
        calculateNewEstimation(beach, prediction, onBeachDevicesCountByGps, beachCapacity)


def FeedbackListenerHandler(message):
    print(message)
    paths = str(message['path'])
    paths = paths.split('/')
    print(paths)
    if (paths.__len__() > 2):
        if (paths[2] == 'Accurate'):
            accurate = message['data']
            if (accurate == True):
                increaseAccurateFeedback()
        if (paths[2] == 'EasyToUse'):
            easyToUse = message['data']
            if (easyToUse == True):
                increaseEasyToUseFeedback()
        if (paths[2] == 'Rating'):
            rating = message['data']
            increaseRatingFeedback(rating)
    numberOfFeedbacks = mFirebaseData.child('Feedback').get().val()
    if (numberOfFeedbacks != None):
        setNumberOfFeedBacks(len(numberOfFeedbacks))
        calculateAppFeedbackResults()


def calculateAppFeedbackResults():
    if (mNumberOfFeedBacks > 0):
        if (mAccurateFeedbackCount != 0):
            print("Accurate: ", mAccurateFeedbackCount / mNumberOfFeedBacks)
        if (mEasyToUseFeebackCount != 0):
            print("Easy To Use: ", mEasyToUseFeebackCount / mNumberOfFeedBacks)
        if (mRating != 0):
            print("Rating: ", mRating / mNumberOfFeedBacks)


def uploadBeachFileToCloud(aFirebaseStorage, aFilePath, aBeachName):
    aFirebaseStorage.child(aFilePath + "/" + aBeachName + Constants.csvFormat).put(
        Constants.DownloadFilesPath + aBeachName + Constants.csvFormat);
    aFirebaseStorage.child(aFilePath + "/" + aBeachName + Constants.xlsxFormat).put(
        Constants.DownloadFilesPath + aBeachName + Constants.xlsxFormat);
    print("Updated Files !")


def savePredictionToFile(aForecast, aBeachName, beachInfo):
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
    update24HoursInDataBase(minHourValue, maxHourValue, predictedHourValue, beachInfo)


def update24HoursInDataBase(minHourValue, maxHourValue, predictedHourValue, beachInfo):
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
        mFirebaseData.child(Constants.Beaches).child(
            beachInfo.mBeachId).child(
            Constants.Hours).child(i).child(Constants.MinEstimation).set(minEstimationValue[i])
        mFirebaseData.child(Constants.Beaches).child(
            beachInfo.mBeachId).child(
            Constants.Hours).child(i).child(Constants.CurrentEstimation).set(currentEstimationValue[i])
        mFirebaseData.child(Constants.Beaches).child(
            beachInfo.mBeachId).child(
            Constants.Hours).child(i).child(Constants.MaxEstimation).set(maxEstimationValue[i])
    print("update 24 hours in cloud !")


def TimeSeriesAlogrithm(aBeachName, beachInfo):
    dayResults = getBeachHoursFinalResults(mFirebaseData, beachInfo)
    print(dayResults);
    BeachData = pd.read_csv(Constants.DownloadFilesPath + aBeachName + Constants.csvFormat)
    # Set last day results
    len = BeachData.__len__()
    for i in range(0, dayResults.__len__()):
        if (dayResults[i] > 0):
            print(BeachData['y'][len - 24 + i])
            BeachData['y'][len - 24 + i] = dayResults[i]
            print(BeachData['y'][len - 24 + i])
    #
    BeachData['y'] = np.log(BeachData['y'])
    ProphetAlgorithm = Prophet(daily_seasonality=True, yearly_seasonality=False, weekly_seasonality=False);
    ProphetAlgorithm.fit(BeachData)
    Predict = ProphetAlgorithm.make_future_dataframe(periods=24 * 1, freq='H')
    Forecast = ProphetAlgorithm.predict(Predict)
    print("Forecasting algorithm finished !")
    savePredictionToFile(Forecast, aBeachName, beachInfo)


def ReadTimestamps():
    mTimestamp = Timestamp()
    UsersTimestamps = mFirebaseData.child(Constants.Timestamps).get();
    print("Deleting relevant timestamps..")
    if (UsersTimestamps is not None):
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
                if ((checkInHour + Constants.Timestamp_Max_Hour) < currentHour):
                    mFirebaseData.child(Constants.Timestamps).child(mTimestamp.UserID).remove()
                    mFirebaseData.child(Constants.Beaches).child(
                        mTimestamp.BeachID).child(Constants.Peoplelist).child(mTimestamp.UserID).remove();
                    mFirebaseData.child(Constants.Users).child(mTimestamp.UserID).child(Constants.CurrentBeach).remove()
                    CurrentDevices = mFirebaseData.child(Constants.BeachesListener).child(
                        mTimestamp.BeachListenerID).child(
                        Constants.CurrentDevices).get()
                    CurrentDevices = int(CurrentDevices.val());
                    CurrentDevices = CurrentDevices - 1;
                    mFirebaseData.child(Constants.BeachesListener).child(
                        mTimestamp.BeachListenerID).child(Constants.CurrentDevices).set(CurrentDevices)
                else:
                    print("Not deleteing from timestamps")


def readBeachesFromFirebase(mFirebaseData):
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
        beachInfo = Info(mBeachId, mCountry);
        print(mCountry)
        storage = firebase.storage();
        #   if (beachName != "Ofir"):
        beachFile = storage.child(filePath + "/" + beachName + Constants.csvFormat).download(
            Constants.DownloadFilesPath + beachName + Constants.csvFormat);
        mFirebaseData = mFirebaseData
        TimeSeriesAlogrithm(beachName, beachInfo)
        uploadBeachFileToCloud(storage, filePath, beachName)


def getBeachHoursFinalResults(mFirebaseData, beachInfo):
    i = 0;
    dayResults = [0] * 24
    for i in range(0, 24):
        dayResults[i] = mFirebaseData.child(Constants.Beaches).child(beachInfo.mBeachId).child(Constants.Hours).child(
            i).child(Constants.CurrentEstimation).get()
        dayResults[i] = round(dayResults[i].val(), 0);
        print(dayResults[i])
    return dayResults;


config = {
    "apiKey": "apiKey",
    "authDomain": Constants.FireBaseUrl,
    "databaseURL": Constants.FireBaseUrl,
    "storageBucket": Constants.FirebaseStorage
}

firebase = pyrebase.initialize_app(config)
mFirebaseData = firebase.database()
BeachListenerStream = mFirebaseData.child(Constants.BeachesListener).stream(
    BeachListenerHandler,
    stream_id="beach count")
FeedbackListener = mFirebaseData.child("Feedback").\
    stream(FeedbackListenerHandler, stream_id="feedback_listener")
# readBeachesFromFirebase(mFirebaseData)
schech = BlockingScheduler();


@schech.scheduled_job('interval', minutes=10)
def DeleteTimeStamps():
    print("Checking timestamps..")
    ReadTimestamps()


@schech.scheduled_job('cron', day_of_week='mon-sun', hour=21, minute=50)
def scheduled_job(mFirebaseData=mFirebaseData):
    readBeachesFromFirebase(mFirebaseData)


@schech.scheduled_job('interval', hours=1)
def UpdateHourChart(mFirebaseData=mFirebaseData):
    print("updating current estimation")
    currentHour = datetime.datetime.utcnow().hour;
    beaches = mFirebaseData.child(Constants.Beaches).get();
    for beach in beaches.each():
        beachId = beach.key();
        result = mFirebaseData.child(Constants.Beaches).child(beachId).child(Constants.Result).get();
        result = result.val()
        print(result)
        mFirebaseData.child(Constants.Beaches).child(beachId).child(Constants.Hours).child(currentHour - 1).child(
            Constants.CurrentEstimation).set(result)


schech.start()
###
