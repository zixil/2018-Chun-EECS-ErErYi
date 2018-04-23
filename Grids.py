import csv


class Grids:

    def __init__(self, filename, maxx=0, maxy=0):
        f=open(filename, "r")
        (self.ids, self.xs, self.ys) = zip(*csv.reader(f))
        f.close()
        self.xs = list(map(lambda x: int(float(x)) * 2, self.xs))
        self.ys = list(map(lambda x: int(float(x)) * 2, self.ys))
        self.maxx = max(max(self.xs) + 1, maxx * 2)
        self.maxy = max(max(self.ys) + 1, maxy * 2)
        self.map = [[] for i in range(self.maxx * self.maxy)]
        for i in range(len(self.xs)):
            self.map[self.xs[i] * self.maxy + self.ys[i]].append(self.ids[i])

    def distance_between(self, coord1, coord2):
        return sum(map(lambda x, y: abs(x - y), coord1, coord2))
