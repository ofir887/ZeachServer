import pyrebase
from fbprophet import Prophet
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import Constants
from Hours import Hours
from BeachListener import BeachListener
from apscheduler.schedulers.blocking import BlockingScheduler

global mFirebaseData
global mBeachId
global mCountry


def BeachListenerHandler(message):
    print(message)  # {'title': 'Pyrebase', "body": "etc..."}
    paths = str(message['path'])
    paths = paths.split('/')
    if (paths.__len__() > 2):
        newCount = int(message['data'])
        beach = BeachListener(paths[1], newCount, paths[2])
        beachId = mFirebaseData.child(
            Constants.BeachesListener + "/" + Constants.Country + "/" + beach.Country + "/" + beach.BeachListenerID + "/" + Constants.BeachID).get().val()
        beach.setBeachID(beachId)
        beach.print()
        newBeachCountValueByGps = beach.CurrentCount;
        CurrentHour = datetime.datetime.now().hour;
        strMixed = Constants.Beaches + "/" + Constants.Country + "/" + beach.Country + "/" + beach.BeachID + "/" + Constants.Hours + "/" + CurrentHour.__str__() + "/"+Constants.CurrentEstimation
        predictedHourValue = mFirebaseData.child(strMixed).get()
        print(strMixed)
        print(predictedHourValue.val())
        newValue = 0;
        if (int(newBeachCountValueByGps) > int(predictedHourValue.val())):
            newValue = (int(newBeachCountValueByGps)) * 1.05;
        else:
            if (int(newBeachCountValueByGps) < int(predictedHourValue.val())):
                newValue = (int(newBeachCountValueByGps)) + int(predictedHourValue.val());
                newValue = newValue / 2 * 1.5
                mFirebaseData.child(
                    Constants.Beaches + "/" + Constants.Country + "/" + beach.Country + "/" + beach.BeachID + "/" + Constants.Result).set(
                    int(round(newValue)))
                mFirebaseData.child(
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
    update24InDataBase(minHourValue, maxHourValue, predictedHourValue)


def update24InDataBase(minHourValue, maxHourValue, predictedHourValue):
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


def TimeSeriesAlogrithm(aBeachFile, aBeachName, aBeachId, aCountry):
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
mFirebaseData = firebase.database()
BeachListenerStream = mFirebaseData.child(Constants.BeachesListener + "/" + Constants.Country).stream(
    BeachListenerHandler,
    stream_id="beach count")

schech = BlockingScheduler();

beachesFiles = mFirebaseData.child(Constants.Files + Constants.BeachesFiles).get();


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
#     if (beachName != "Ofir"):
#         beachFile = storage.child(filePath + "/" + beachName + Constants.csvFormat).download(
#             Constants.DownloadFilesPath + beachName + Constants.csvFormat);
#         TimeSeriesAlogrithm(beachFile, beachName, mFirebaseData, mBeachId, mCountry)
#         #  update24InDataBase(data, mBeachId, mCountry)
#         uploadBeachFileToCloud(storage, filePath, beachName)


@schech.scheduled_job('cron', day_of_week='mon-sat', hour=2)
def scheduled_job(mFirebaseData=mFirebaseData):
    # print('This job is run every weekday at 5pm.')
    beachesFiles = mFirebaseData.child(Constants.Files + Constants.BeachesFiles).get();
    for beach in beachesFiles.each():
        beachName = beach.key();
        # print(beach.val())
        filePath = mFirebaseData.child(Constants.Files + Constants.BeachesFiles).child(beach.key()).child(
            'filePath').get()
        filePath = filePath.val()
        print(filePath)
        mBeachId = mFirebaseData.child(Constants.Files + Constants.BeachesFiles).child(beach.key()).child(
            Constants.BeachID).get()
        mBeachId = mBeachId.val();
        print(mBeachId)
        mCountry = mFirebaseData.child(Constants.Files + Constants.BeachesFiles).child(beach.key()).child(
            Constants.Country).get()
        mCountry = mCountry.val();
        print(mCountry)
        storage = firebase.storage();
        if (beachName != "Ofir"):
            beachFile = storage.child(filePath + "/" + beachName + Constants.csvFormat).download(
                Constants.DownloadFilesPath + beachName + Constants.csvFormat);
            mFirebaseData = mFirebaseData
            TimeSeriesAlogrithm(beachFile, beachName, mBeachId, mCountry)
            #  update24InDataBase(data, mBeachId, mCountry)
            uploadBeachFileToCloud(storage, filePath, beachName)


schech.start()
###
