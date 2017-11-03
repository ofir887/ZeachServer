class Coords(object):
    lat = 0.0
    lng = 0.0

    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng

    def dump(self):
        return {'lat': self.lat, "lng": self.lng}

    def print(self):
        print('lat:', self.lat, ' lng:', self.lng)
