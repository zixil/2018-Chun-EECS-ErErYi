import sys
import csv
from itertools import product
from functools import reduce
from random import random
from collections import Counter


class Node(object):

    def __init__(self, x, y):
        self.__x = x
        self.__y = y
        self.__items = []
        self.__accessible_items = []
        self.__distance = []
        self.__path = []

    def add_item(self, item_id):
        self.__items.append(item_id)

    def get_items(self):
        return self.__items

    def is_occupied(self):
        return len(self.__items) != 0

    def add_accessible_items(self, ids):
        self.__accessible_items += ids

    def get_accessible_items(self):
        return self.__accessible_items

    def set_shortest_paths(self, distance, path):
        self.__distance = distance
        self.__path = path

    def has_distance(self):
        return self.__distance

    def get_distance(self, x, y):
        # print(x, y)
        return self.__distance[x][y]

    def has_path(self):
        return self.__path

    def get_path(self, x, y):
        if self.__path[x][y] == (-1, -1):
            return []
        cur = (x, y)
        Str = lambda x: str((float(x[0]) / accuracy, float(x[1]) / accuracy))
        cur_path = Str(self.__path[x][y])
        while cur != (self.__x, self.__y):
            cur = self.__path[cur[0]][cur[1]]
            cur_path = Str(cur) + cur_path
        return cur_path


class Grid(object):

    def __init__(self, csv_file_name, accuracy, xLen="0", yLen="0"):
        self.__accuracy = accuracy
        # read csv file
        (self.__ids, self.__xs, self.__ys) = self.__read_csv(csv_file_name)
        self.__xLen = max(max(self.__xs), self.f2i(xLen)) + 1
        self.__yLen = max(max(self.__ys), self.f2i(yLen)) + 1
        self.__nodes = [[Node(i, j) for j in range(self.__yLen)] for i in range(self.__xLen)]
        # initiate
        self.__initiate()
        self.__start_x = 0
        self.__start_y = 0
        self.__end_x = 0
        self.__end_y = 0

    # convert float string to int
    def f2i(self, s):
        return int(round(float(s) * self.__accuracy))

    def set_start(self, x, y):
        (self.__start_x, self.__start_y) = (x, y)

    def get_start(self):
        return self.__start_x, self.__start_y

    def set_end(self, x, y):
        (self.__end_x, self.__end_y) = (x, y)

    def get_end(self):
        return self.__end_x, self.__end_y

    def get_location(self, id):
        index = self.__ids.index(id)
        return self.__xs[index], self.__ys[index]

    def find_item(self, id):
        return self.find_item_from(id, self.__start_x, self.__start_y)

    def find_item_from(self, id, from_x, from_y):
        if not self.__nodes[from_x][from_y].has_path():
            self.__find_path(from_x, from_y)
        if not self.__nodes[from_x][from_y].has_path():
            return "Non accessible."
        index = self.__ids.index(id)
        neighbor_x = [self.__xs[index] - 1, self.__xs[index] + 1]
        distances = list(map(lambda x: self.__nodes[from_x][from_y].get_distance(x, self.__ys[index]), neighbor_x))
        index = distances.index(min(distances))
        return self.__nodes[from_x][from_y].get_path(neighbor_x[index], self.__ys[index])

    def path_between(self, from_x, from_y, to_x, to_y):
        if not self.__nodes[from_x][from_y].has_path():
            self.__find_path(from_x, from_y)
        if not self.__nodes[from_x][from_y].has_path():
            return "Non accessible."
        return self.__nodes[from_x][from_y].get_path(to_x, to_y)

    def distance_between(self, from_coord, to_coord):
        (from_x, from_y) = from_coord
        (to_x, to_y) = to_coord
        if not self.__nodes[from_x][from_y].has_distance():
            self.__find_path(from_x, from_y)
        if not self.__nodes[from_x][from_y].has_distance():
            return "Non accessible."
        # print(from_coord, " in distance_between")
        return self.__nodes[from_x][from_y].get_distance(to_x, to_y)

    def is_occupied(self, x, y):
        return self.__nodes[x][y].is_occupied();

    def __read_csv(self, csv_file_name):
        item_table = zip(*csv.reader(open(csv_file_name)))
        return map(lambda x, y: list(map(y, x)), item_table, [lambda x: x, self.f2i, self.f2i])

    def __initiate(self):
        self.__locate_items()
        self.__find_item_access()

    def __locate_items(self):
        items = zip(*(self.__ids, self.__xs, self.__ys))
        for i in items:
            self.__nodes[i[1]][i[2]].add_item(i[0])

    def __find_item_access(self):
        for i in range(self.__xLen):
            for j in range(self.__yLen):
                accessible_neighbor = self.__get_accessible_neighbor(i, j)
                accessible_items = map(lambda x: self.__nodes[x[0]][x[1]].get_items(), accessible_neighbor)
                self.__nodes[i][j].add_accessible_items(reduce(lambda x, y: x + y, accessible_items))

    def __get_neighbor(self, x, y):
        neighbor = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        return filter(lambda x: self.__is_inside_grid(x[0], x[1]), neighbor)

    def __get_accessible_neighbor(self, x, y):
        neighbor = [(x - 1, y), (x + 1, y)]
        return filter(lambda x: self.__is_inside_grid(x[0], x[1]), neighbor)

    def __is_inside_grid(self, x, y):
        return 0 <= x < self.__xLen and 0 <= y < self.__yLen

    def __find_path(self, x, y):
        if self.__nodes[x][y].is_occupied():
            return None
        distance = [[-1 for j in range(self.__yLen)] for i in range(self.__xLen)]
        path = [[(-1, -1) for j in range(self.__yLen)] for i in range(self.__xLen)]
        distance[x][y] = 0
        changed = 1
        i_range = max(map(lambda k: k[0] + k[1], product([x, self.__xLen - x], [y, self.__yLen - y])))

        # calculate the distance from the starting point to the four accessible neighbors of (_x,_y)
        def neighbor_distance(x, y):
            # unoccupied and inside the map
            if not self.__is_inside_grid(x, y) or self.__nodes[x][y].is_occupied() or distance[x][y] < 0:
                return 0

            _changed = 0
            # four neighbor squares of (_x,_y)
            neighbors = self.__get_neighbor(x, y)
            # neighbors unoccupied and inside the grid
            valid = lambda x, y: self.__is_inside_grid(x, y) and not self.__nodes[x][y].is_occupied()
            neighbors = filter(lambda k: valid(k[0], k[1]), neighbors)
            # calculating distance
            for neighbor in neighbors:
                if distance[x][y] + 1 < distance[neighbor[0]][neighbor[1]] or distance[neighbor[0]][neighbor[1]] < 0:
                    _changed = 1
                    distance[neighbor[0]][neighbor[1]] = distance[x][y] + 1
                    path[neighbor[0]][neighbor[1]] = (x, y)
            return _changed

        while changed != 0:
            changed = 0
            for i in range(i_range):
                for j in range(max(i - self.__xLen, 0), min(i + 1, self.__yLen)):
                    cur = product([x + (i - j), x - (i - j)], [y + j, y - j])
                    changed += sum(map(lambda k: neighbor_distance(k[0], k[1]), cur))
        self.__nodes[x][y].set_shortest_paths(distance, path)


class Task(object):
    grid = None

    def __init__(self, task):
        # print(task)
        self.task = task
        self.original = range(1, len(task) + 1)
        self.optimal = range(1, len(task) + 1)

        def get_side_location(i):
            loc = self.grid.get_location(i)
            new_loc = (loc[0] - 1, loc[1])
            if self.grid.is_occupied(new_loc[0], new_loc[1]):
                return (loc[0] + 1, loc[1])
            return new_loc

        self.location = [self.grid.get_start()] + list(map(get_side_location, task)) + [self.grid.get_end()]
        self.size = len(task) + 2
        self.distance = [[-1 for i in range(self.size)] for j in range(self.size)]
        self.__get_distance()
        self.original_len = float(self.__get_path_length(self.original)) / accuracy
        self.optimal_len = float(self.__get_path_length(self.optimal)) / accuracy

    def optimize(self):
        all = set(self.optimal)
        pre = self.optimal
        pre_len = self.distance
        pop_size = 50
        prt = 0.8
        t = 0.9
        cur = [[] for i in range(pop_size)]
        intcur = [[] for i in range(pop_size)]
        for i in range(pop_size):
            for j in range(self.size - 2):
                # print(i,"curlen",len(cur))
                cur[i].append(random() * (self.size - 2) + 1)
            # print(len(intcur[i]),len(cur[i]))
            intcur[i] = list(map(lambda x: int(x), cur[i]))
            count = Counter(intcur[i])
            perm = [k for k in all if k not in intcur[i]]
            for j in range(self.size - 2):
                if len(perm) == 0:
                    break
                if count[intcur[i][j]] > 1:
                    rand = int(random() * len(perm))
                    cur[i][j] = float(perm[rand])
                    perm.remove(perm[rand])
                    count[intcur[i][j]] -= 1
            intcur[i] = list(map(lambda x: int(x), cur[i]))
        cur.append(list(map(lambda x: float(x), pre)))
        intcur.append(pre)
        pop_size += 1
        distance = list(map(self.__get_path_length, intcur))
        self.optimal = intcur[distance.index(min(distance))]
        self.optimal_len = distance[distance.index(min(distance))]
        while True:
            pre = self.optimal
            pre_len = self.optimal_len
            for i in range(pop_size):
                for j in range(self.size - 2):
                    # print(i, j, len(cur), len(self.optimal))
                    Prt = int(random() * prt * 2)
                    cur[i][j] = cur[i][j] + (self.optimal[j] - cur[i][j]) * Prt * t
                # print(len(intcur[i]),len(cur[i]))
                intcur[i] = list(map(lambda x: int(x), cur[i]))
                count = Counter(intcur[i])
                perm = [k for k in all if k not in intcur[i]]
                for j in range(self.size - 2):
                    if len(perm) == 0:
                        break
                    if count[intcur[i][j]] > 1:
                        rand = int(random() * len(perm))
                        cur[i][j] = perm[rand]
                        perm.remove(perm[rand])
                        count[intcur[i][j]] -= 1
                intcur[i] = list(map(lambda x: int(x), cur[i]))
            distance = list(map(self.__get_path_length, intcur))
            self.optimal = intcur[distance.index(min(distance))]
            self.optimal_len = distance[distance.index(min(distance))]
            if self.optimal_len - pre_len < 1 / (10 * accuracy):
                self.optimal_len = float(self.optimal_len) / accuracy
                break

    def output(self):
        Str = lambda x: str((float(x[0]) / accuracy, float(x[1]) / accuracy))
        s = "##Worker Start Location##\n" + Str(self.grid.get_start())
        s += "\n## Worker End Location##\n" + Str(self.grid.get_end())
        s += "\n##Original Parts Order##\n" + str(list(map(lambda x: self.task[x - 1], self.original)))
        s += "\n##Optimized Parts Order##\n" + str(list(map(lambda x: self.task[x - 1], self.optimal)))
        s += "\n##Original Parts Total Distance##\n" + str(self.original_len)
        s += "\n##Optimized Parts Total Distance##\n" + str(self.optimal_len)
        return s

    def __get_distance(self):
        for i in range(self.size):
            for j in range(self.size):
                # print(self.location[i], self.location[j], "in __get_distance")
                self.distance[i][j] = self.grid.distance_between(self.location[i], self.location[j])

    def __get_path_length(self, path):
        total = 0
        tmp = [0] + list(path) + [self.size - 1]
        for i in range(self.size - 1):
            total += self.distance[tmp[i]][tmp[i + 1]]
        return total


# accuracy of map grid
if len(sys.argv) >= 2:
    accuracy = int(sys.argv[1])
else:
    accuracy = 50

while True:
    start_x = input("Hello User, where is your worker?\nx:")
    start_y = input("y:")
    end_x = input("What is your worker's end location?\nx:")
    end_y = input("y:")

    if Task.grid is None:
        Task.grid = Grid('warehouse-grid.csv', accuracy, max(start_x, end_x), max(start_y, end_y))

    start_x = Task.grid.f2i(start_x)
    start_y = Task.grid.f2i(start_y)
    end_x = Task.grid.f2i(end_x)
    end_y = Task.grid.f2i(end_y)

    Task.grid.set_start(start_x, start_y)
    Task.grid.set_end(end_x, end_y)
    alter = input("File input or manual input? (f/m): ").lower()
    if alter == "m":
        task = Task((input("Hello User, what items would you like to pick? (split with spaces)\n")).split())
        task.optimize()
        print(task.output())

    if alter == "f":
        i_file = input("Please list file of orders to be processed: ")
        o_file = input("Please list output file: ")
        tasks = map(Task, csv.reader(open(i_file)))
        s = ""
        for i in tasks:
            i.optimize()
            s += i.output() + "\n"
        f = open(o_file)
        print(s, f)

    foo = input("Continue? (Y/N): ").lower()
    if (foo=="n"):
        break
