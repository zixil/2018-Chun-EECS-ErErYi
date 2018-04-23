from collections import Counter
from random import random

import Grids


class Task(object):
    grids = None

    def __init__(self, task, start, end):
        if self.grids is None:
            return
        # print(task)
        self.task = task
        self.start = map(lambda x: x * 2 + 1, start)
        self.end = map(lambda x: x * 2 + 1, end)

        def get_location(id):
            index = self.grids.ids.index(id)
            return self.grids.xs[index], self.grids.ys[index]

        self.location = [start] + list(map(get_location, task)) + [end]

        self.original = range(1, len(task) + 1)
        self.optimal = range(1, len(task) + 1)

        self.size = len(task) + 2
        self.distance = [-1] * (self.size * self.size)
        for i in range(self.size):
            for j in range(self.size):
                # print(self.location[i], self.location[j], "in __get_distance")
                self.distance[i * self.size + j] = self.grids.distance_between(self.location[i], self.location[j])

        self.original_len = float(self.__get_path_length(self.original)) / 2
        self.optimal_len = float(self.__get_path_length(self.optimal)) / 2

    def optimize(self):
        equal_times=0;
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
            if self.optimal_len - pre_len < 1 / (20):
                equal_times+=1
                if equal_times>10:
                    self.optimal_len = float(self.optimal_len) / 2
                    break
            else:
                equal_times=0

    def output(self):
        Str = lambda x: str(((x[0]-1) / 2, (x[1]-1) / 2))
        s = "##Worker Start Location##\n" + Str(list(self.start))
        s += "\n## Worker End Location##\n" + Str(list(self.end))
        s += "\n##Original Parts Order##\n" + str(list(map(lambda x: self.task[x - 1], self.original)))
        s += "\n##Optimized Parts Order##\n" + str(list(map(lambda x: self.task[x - 1], self.optimal)))
        s += "\n##Original Parts Total Distance##\n" + str(self.original_len)
        s += "\n##Optimized Parts Total Distance##\n" + str(self.optimal_len)
        return s

    def __get_path_length(self, path):
        total = self.distance[1] + self.distance[path[self.size - 3] * self.size + self.size - 1]
        for i in range(self.size - 3):
            total += self.distance[path[i] * self.size +
                                   path[i + 1]]
        return total
