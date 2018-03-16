import Constants


class Hours(object):
    MinEstimation = [0] * 24;
    CurrentEstimation = [0] * 24;
    MaxEstimation = [0] * 24;

    def __init__(self):
        self.Current = [0] * 24;
        self.MinEstimation = [0] * 24;
        self.MaxEstimation = [0] * 24;

    def setHourPeople(self, index, num):
        self.Current[index] = num;

    def dump(self):
        i = 0;
        lst2 = [];
        while (i < len(self.Current)):
            lst2.append({Constants.MinEstimation: self.MinEstimation[i], Constants.CurrentEstimation: self.Current[i],
                         Constants.MaxEstimation: self.MaxEstimation[i]})
            i = i + 1
        return lst2;


class CurrentHourPrediction(object):
    MinEstimation = 0.0;
    CurrentEstimation = 0.0;
    MaxEstimation = 0.0;

    def __init__(self, aFirebaseData, aPath):
        self.MinEstimation = aFirebaseData.child(aPath).child(Constants.MinEstimation).get();
        self.MinEstimation = self.MinEstimation.val();
        self.MaxEstimation = aFirebaseData.child(aPath).child(Constants.MaxEstimation).get();
        self.MaxEstimation = self.MaxEstimation.val();
        self.CurrentEstimation = aFirebaseData.child(aPath).child(Constants.CurrentEstimation).get();
        self.CurrentEstimation = self.CurrentEstimation.val();

    def getMinEstimation(self):
        return self.MinEstimation;

    def getMaxEstimation(self):
        return self.MaxEstimation

    def getCurrentEstimation(self):
        return self.CurrentEstimation;

    def print(self):
        print("minEstimation: " + str(self.MinEstimation));
        print("CurrentEstimation: " + str(self.CurrentEstimation));
        print("maxEstimation: " + str(self.MaxEstimation));
