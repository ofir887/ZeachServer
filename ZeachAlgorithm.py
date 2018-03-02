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
from apscheduler.schedulers.blocking import BlockingScheduler

INTERVAL = 60;
COUNT_FIX = 1.1

global mFirebaseData
mAccurateFeedbackCount = 0
mEasyToUseFeebackCount = 0
mRating = 0
mNumberOfFeedBacks = 0
mNumberOfTests = 0;
mSuccessTest = 0;
mFailedTests = 0;


def updateNumberOfTests():
    global mNumberOfTests;
    mNumberOfTests = mNumberOfTests + 1
    successPrecentage = (mSuccessTest / mNumberOfTests) * 100
    failurePrecentage = (mFailedTests / mNumberOfTests) * 100
    print("% of success:", successPrecentage)
    print("% of failure:", failurePrecentage)


def updateSuccessTests():
    global mSuccessTest
    mSuccessTest = mSuccessTest + 1;


def updateFailedTests():
    global mFailedTests
    mFailedTests = mFailedTests + 1;


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
    mRating = mRating + (rating * 20)
    print("rating: ", mRating)


def setNumberOfFeedBacks(aCount):
    global mNumberOfFeedBacks;
    mNumberOfFeedBacks = aCount
    print("Number of feedbacks: " + str(mNumberOfFeedBacks))


class Info(object):
    mBeachId = ""
    mCountry = ""

    def __init__(self, beachId, country):
        self.mBeachId = beachId
        self.mCountry = country


def setTrafficFlag(aBeachCapacity, aResult):
    percentage = (aResult / aBeachCapacity) * 100;
    if (percentage >= 80):
        return Constants.HighTraffic
    if (percentage >= 40 and percentage < 80):
        return Constants.MediumTraffic
    else:
        return Constants.LowTraffic

def checkForDeviation(aCurrentDevices, aResult):
    deviation = aResult / aCurrentDevices;
    deviation = abs(1 - deviation)
    print("Deviation: ", deviation)
    if (deviation >= 0 and deviation <= 0.2):
        print("Success !")
        updateSuccessTests()
    else:
        print("Failure")
        updateFailedTests()
    updateNumberOfTests()


def updateHourPrediction(aCurrentEstimation, aMinEstimation, aMaxEstimation, aHourPath):
    print("Updating hour chart...")
    mFirebaseData.child(aHourPath).child(Constants.MinEstimation).set(aMinEstimation)
    mFirebaseData.child(aHourPath).child(Constants.CurrentEstimation).set(aCurrentEstimation)
    mFirebaseData.child(aHourPath).child(Constants.MaxEstimation).set(aMaxEstimation)


def calculateNewEstimation(aBeach, aPrediction, aCurrentDevicesOnBeach, aBeachCapacity, aHourPath):
    fixedValue = (int(aCurrentDevicesOnBeach)) * COUNT_FIX;
    currentEstimation = (int(aPrediction.CurrentEstimation))
    maxEstimation = (int(aPrediction.MaxEstimation))
    minEstimation = (int(aPrediction.MinEstimation))
    print("Current people after fix: ", fixedValue)
    # case 1: in range between current and max
    if (fixedValue >= currentEstimation and fixedValue <= maxEstimation):
        print("fixing according to case 1")
        result = (fixedValue + currentEstimation) / 2
        currentEstimation = result
    # case 2: in range between current and min
    if (fixedValue < currentEstimation and fixedValue >= minEstimation):
        print("fixing according to case 2")
        result = (fixedValue + currentEstimation) / 2
        currentEstimation = result
    # case 3: higher than max estimation - Do average and set as current & update max estimation
    if (fixedValue > maxEstimation):
        print("fixing according to case 3")
        result = (fixedValue + maxEstimation) / 2
        currentEstimation = result
        maxEstimation = fixedValue
    # case 4: lowwer than min estimation - Do average and set as current & update min estimation
    if (fixedValue < minEstimation):
        print("fixing according to case 4")
        result = (fixedValue + minEstimation) / 2
        currentEstimation = result
        minEstimation = fixedValue
    updateHourPrediction(currentEstimation, minEstimation, maxEstimation, aHourPath)
    # set traffic flag
    resultPath = Constants.Beaches + "/" + aBeach.BeachID + "/" + Constants.Result
    mFirebaseData.child(resultPath).set(
        int(round(result)))
    trafficFlag = setTrafficFlag(aBeachCapacity, result)
    mFirebaseData.child(
        Constants.Beaches + "/" + aBeach.BeachID + "/" + Constants.Traffic).set(trafficFlag)
    checkForDeviation(aCurrentDevicesOnBeach, result)
    return result;


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
        currentDevicesPath = Constants.Beaches + "/" + beach.BeachID + "/" + Constants.CurrentDevices
        mFirebaseData.child(currentDevicesPath).set(int(round(onBeachDevicesCountByGps)))
        CurrentHour = datetime.datetime.now().hour;
        hourPath = Constants.Beaches + "/" + beach.BeachID + "/" + Constants.Hours + "/" + CurrentHour.__str__()
        prediction = CurrentHourPrediction(mFirebaseData, hourPath)
        prediction.print();
        calculateNewEstimation(beach, prediction, onBeachDevicesCountByGps, beachCapacity, hourPath)


def FeedbackListenerHandler(message):
    print(message)
    paths = str(message['path'])
    paths = paths.split('/')
    print(paths)
    if (paths.__len__() > 2):
        if (paths[2] == Constants.FeedBack_Accurate):
            accurate = message['data']
            if (accurate == True):
                increaseAccurateFeedback()
        if (paths[2] == Constants.FeedBack_Easy_To_Use):
            easyToUse = message['data']
            if (easyToUse == True):
                increaseEasyToUseFeedback()
        if (paths[2] == Constants.FeedBack_Rating):
            rating = message['data']
            increaseRatingFeedback(rating)
    numberOfFeedbacks = mFirebaseData.child(Constants.FeedBack).get().val()
    if (numberOfFeedbacks != None):
        setNumberOfFeedBacks(len(numberOfFeedbacks))
        calculateAppFeedbackResults()
        showTotalFeedbackScore()


def calculateAppFeedbackResults():
    if (mNumberOfFeedBacks > 0):
        if (mAccurateFeedbackCount != 0):
            print("Accurate: ", ((mAccurateFeedbackCount / mNumberOfFeedBacks) * 100), "%")
        if (mEasyToUseFeebackCount != 0):
            print("Easy To Use: ", ((mEasyToUseFeebackCount / mNumberOfFeedBacks) * 100), "%")
        if (mRating != 0):
            print("Rating: ", (mRating / mNumberOfFeedBacks), "%")
        showTotalFeedbackScore()


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


def ReadFeedbacks():
    feedbacks = mFirebaseData.child(Constants.FeedBack).get();
    if (feedbacks.val() is not None):
        print("Reading feedbacks...")
        for feedback in feedbacks.each():
            userId = feedback.key();
            details = mFirebaseData.child(Constants.FeedBack).child(userId).get()
            details = details.val()
            details = dict(details)
            print(details)
            if (details.get(Constants.FeedBack_Accurate) == True):
                increaseAccurateFeedback()
            if (details.get(Constants.FeedBack_Easy_To_Use) == True):
                increaseEasyToUseFeedback()
            increaseRatingFeedback(details.get(Constants.FeedBack_Rating))
        length = len(feedbacks.val())
        setNumberOfFeedBacks(length)
        showTotalFeedbackScore()


def showTotalFeedbackScore():
    totalAstimation = ((mAccurateFeedbackCount + mEasyToUseFeebackCount + (mRating / 100)) / 3) * 100
    print("Updated feedbacks score: ", totalAstimation, "%")


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
            Constants.FilePath).get()
        filePath = filePath.val()
        print(filePath)
        print(mBeachId)
        mCountry = mFirebaseData.child(Constants.Files + Constants.BeachesFiles).child(mBeachId).child(
            Constants.Country).get()
        mCountry = mCountry.val();
        beachInfo = Info(mBeachId, mCountry);
        print(mCountry)
        storage = firebase.storage();
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
FeedbackListener = mFirebaseData.child(Constants.FeedBack). \
    stream(FeedbackListenerHandler, stream_id="feedback_listener")
# readBeachesFromFirebase(mFirebaseData)
ReadFeedbacks()
schech = BlockingScheduler();


@schech.scheduled_job('interval', minutes=10)
def DeleteTimeStamps():
    print("Checking timestamps..")
    ReadTimestamps()


@schech.scheduled_job('cron', day_of_week='mon-sun', hour=22, minute=6)
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
