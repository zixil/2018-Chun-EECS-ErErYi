import csv

from memory_profiler import profile


class Grids:

    def __init__(self, maxx=0, maxy=0):
        f = open('warehouse-grid.csv', "r")
        (self.ids, self.xs, self.ys) = zip(*csv.reader(f))
        f.close()
        self.xs = list(map(lambda x: int(float(x)) * 2, self.xs))
        self.ys = list(map(lambda x: int(float(x)) * 2, self.ys))
        # weight
        self.ws = [None] * len(self.xs)
        self.maxx = max(max(self.xs) + 2, maxx * 2 + 1)
        self.maxy = max(max(self.ys) + 1, maxy * 2 + 1)
        self.map = [[] for i in range(self.maxx * self.maxy)]
        for i in range(len(self.xs)):
            self.map[self.xs[i] * self.maxy + self.ys[i]].append(self.ids[i])
        self.distances = [[] for i in range(self.maxx * self.maxy)]
        self.path = [[] for i in range(self.maxx * self.maxy)]

        f = open('item-dimensions-tabbed.csv', "r")
        wInfo = csv.reader(f)
        tmp_start = 0
        next(wInfo)
        for i in wInfo:
            try:
                tmp_start = self.ids.index(i[0])
            except ValueError:
                continue
            self.ws[tmp_start] = float(i[4])
        f.close()

    def getI(self, coord):
        return coord[0] * self.maxy + coord[1]

    def distance_between(self, coord1, coord2):

        I1 = self.getI(coord1)
        I2 = self.getI(coord2)
        (x, y) = coord1
        (x2, y2) = coord2
        if self.distances[I1] and self.distances[I1][I2] != -1:
            return self.distances[I1][I2]
        '''
        if len(self.map[I1]) != 0:
            print(I1)
            return None
        '''
        distance = [-1] * self.maxy * self.maxx
        path = [-1] * self.maxy * self.maxx
        distance[I1] = 0
        changed = 1
        i_range = max(x + y, x + self.maxy - y, self.maxx - x + y, self.maxx - x + self.maxy - y)

        # calculate the distance from the starting point to the four accessible neighbors of (_x,_y)
        def neighbor_distance(coord):
            (x, y) = coord
            I = self.getI(coord)
            # unoccupied and inside the map
            if not self.__is_inside_grid(coord) or (self.map[I] and coord != coord1) or distance[I] < 0:
                return 0

            _changed = 0
            # four neighbor squares of (_x,_y)
            neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            # neighbors and inside the grid
            ''' and not self.map[self.getI(x)]'''
            neighbors = filter(lambda x: self.__is_inside_grid(x), neighbors)
            # calculating distance
            for neighbor in neighbors:
                i_neighbor = self.getI(neighbor)
                if distance[I] + 1 < distance[i_neighbor] or distance[i_neighbor] < 0:
                    _changed = 1
                    distance[i_neighbor] = distance[I] + 1
                    path[i_neighbor] = I
            return _changed

        while changed != 0:
            changed = 0
            for i in range(i_range):
                for j in range(max(i - self.maxx, 0), min(i + 1, self.maxy)):
                    cur = [(x + (i - j), y + j), (x + (i - j), y - j), (x - (i - j), y + j), (x - (i - j), y - j)]
                    changed += sum(map(neighbor_distance, cur))
        self.distances[I1] = distance
        self.path[I1] = path
        return self.distances[I1][I2]

    def __is_inside_grid(self, coord):
        return 0 <= coord[0] < self.maxx and 0 <= coord[1] < self.maxy

    def get_w(self, _id):
        return self.ws[self.ids.index(_id)]

    def pathBetween(self, coord1, coord2):

        distance = self.distance_between(coord1, coord2)
        path = self.path[self.getI(coord1)]
        if distance == 0:
            return []
        tmp = [-1] * distance
        tmp[distance - 1] = self.getI(coord2)
        for i in range(distance - 2, -1, -1):
            tmp[i] = path[tmp[i + 1]]
        return tmp
