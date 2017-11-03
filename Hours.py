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
