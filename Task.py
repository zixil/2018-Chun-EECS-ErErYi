import copy
from collections import Counter
from functools import reduce
from queue import PriorityQueue
from random import random, seed

import time

from SqMat import SqMat

import Grids


class Task(object):
    grids = None

    def __init__(self, task, start, end, ifWeighed):
        if self.grids is None:
            return
        self.task = task

        self.weighed = ifWeighed
        self.reallyWeighed = True
        self.get_path_length = self.__get_path_length
        self.optimize_branch = self.__optimize_branch
        if ifWeighed or self.reallyWeighed:
            for i in task:
                if self.grids.get_w(i) is None:
                    self.weighed = False
                    self.reallyWeighed = False
                    break
        if self.weighed:
            self.get_path_length = self.get_path_effort
            self.optimize_branch = self.__weighed_optimize_branch

        self.start = tuple(map(lambda x: x * 2 + 1, start))
        self.end = tuple(map(lambda x: x * 2 + 1, end))

        def get_location(id):
            # print(id)
            index = self.grids.ids.index(id)
            return self.grids.xs[index], self.grids.ys[index]

        self.location = [start] + list(map(get_location, task)) + [end]
        if self.weighed or self.reallyWeighed:
            self.weight = [0] + list(map(self.grids.get_w, task)) + [0]

        self.size = len(task) + 2
        self.distance = [-1] * (self.size * self.size)
        for i in range(self.size):
            for j in range(self.size):
                '''
                iLoc = self.location[i]
                jLoc = self.location[j]
                ll = self.grids.distance_between((iLoc[0] - 1, iLoc[1]), (jLoc[0] - 1, iLoc[1]))
                lr = self.grids.distance_between((iLoc[0] - 1, iLoc[1]), (jLoc[0] + 1, iLoc[1]))
                rr = self.grids.distance_between((iLoc[0] + 1, iLoc[1]), (jLoc[0] + 1, iLoc[1]))
                rl = self.grids.distance_between((iLoc[0] + 1, iLoc[1]), (jLoc[0] - 1, iLoc[1]))
                self.distance[i * self.size + j] = min(ll, lr, rr, rl)
                '''
                self.distance[i * self.size + j] = self.grids.distance_between(self.location[i], self.location[j])

        tmp = list(range(self.size - 2))
        for i in range(1, self.size - 1):
            for j in range(i, self.size - 1):
                if self.location[i] == self.location[j]:
                    tmp[j - 1] = tmp[i - 1]
        tmpSet = set(tmp)
        self.shelf = [[] for i in range(self.size)]
        self.shelf[0] = [0]
        self.shelf[-1] = [self.size - 1]
        for i in tmpSet:
            for j in range(self.size - 2):
                if tmp[j] == i:
                    self.shelf[i + 1].append(j + 1)
        self.shelf = list(filter(lambda x: x, self.shelf))
        self.shelfSize = len(self.shelf)
        self.shelfDistance = [-1] * (self.shelfSize * self.shelfSize)
        self.shelfW = [0] * self.shelfSize
        for i in range(self.shelfSize):
            if self.weighed or self.reallyWeighed:
                for j in self.shelf[i]:
                    self.shelfW[i] += self.weight[j]
            for j in range(self.shelfSize):
                I = self.shelf[i][0] * self.size + self.shelf[j][0]
                self.shelfDistance[i * self.shelfSize + j] = self.distance[I]

        self.original = list(range(1, len(task) + 1))
        self.original_len = self.get_path_length(self.original)
        if len(self.original) == 1:
            self.upper = self.optimal = self.original
            self.upper_len = self.lower_len = self.optimal_len = self.original_len
        else:
            self.upper = list(range(1, len(task) + 1))
            self.upper_len = self.get_path_length(self.upper)
            self.__calc_upper()
            self.lower = []
            self.lower_len = 0
            self.__calc_lower()
            # if lower bound is a solution
            if self.lower:
                self.optimal = self.lower
                self.optimal_len = self.lower_len
            else:
                self.optimal = [i for i in self.upper]
                self.optimal_len = self.get_path_length(self.optimal)

    def __calc_upper(self):
        min_path = self.upper
        min_len = self.get_path_length(self.upper)
        for i in range(0, self.size - 2):
            cur = i
            rest_ver = list(range(self.size - 2))
            rest_ver.remove(i)
            cur_path = [i + 1]
            while True:
                '''
                if (rest_ver == 0):
                    print(str(list(map(lambda x: self.task[x - 1], self.original))))
                '''
                next = rest_ver[0]
                for j in rest_ver:
                    if self.distance[(cur + 1) * self.size + j + 1] < self.distance[(cur + 1) * self.size + next + 1]:
                        next = j
                cur = next
                cur_path.append(next + 1)
                rest_ver.remove(next)
                if len(rest_ver) == 0:
                    break
            cur_len = self.get_path_length(cur_path)
            # print(self.get_path_string(cur_path))
            if cur_len < min_len:
                min_path = cur_path
                min_len = cur_len
        self.upper = min_path
        self.upper_len = min_len
        # print()

    def __calc_lower(self):
        # spanning tree lower bound
        selected = [0]
        rest_ver = list(range(1, self.size - 2))
        lower_len = 0
        # connection[0][1] means edge [1][2] is in the lower bound graph
        connection = [[] for i in range(self.size - 2)]

        while len(rest_ver) != 0:
            (min_i, min_j) = (selected[0], rest_ver[0])
            for i in selected:
                for j in rest_ver:
                    if self.distance[(i + 1) * self.size + j + 1] < self.distance[(min_i + 1) * self.size + min_j + 1]:
                        (min_i, min_j) = (i, j)
            selected.append(min_j)
            rest_ver.remove(min_j)
            lower_len += self.distance[min_i * self.size + min_j]
            connection[min_i].append(min_j)
            connection[min_j].append(min_i)

        # from the starting point and to the ending point
        start_ver = 0
        start_len = self.distance[start_ver + 1]
        end_ver = 0
        end_len = self.distance[(self.size - 1) * self.size + end_ver + 1]
        for i in range(0, self.size - 2):
            if self.distance[1 + i] < start_len:
                start_ver = i
                start_len = self.distance[start_ver + 1]
            if self.distance[(self.size - 1) * self.size + 1 + i] < end_len:
                end_ver = i
                end_len = self.distance[(self.size - 1) * self.size + end_ver + 1]
        connection[start_ver].append(-1)
        connection[end_ver].append(-1)

        self.lower_len = start_len + end_len

        # Another lower bound
        base = 0
        for i in range(1, self.size - 1):
            min_j = 0
            min2j = 0
            if i == 0:
                a = 1
                b = 2
            elif i == 1:
                a = 0
                b = 3
            else:
                a = 0
                b = 1
            if self.distance[i * self.size + a] < self.distance[i * self.size + b]:
                min_j = a
                min2j = b
            else:
                min_j = b
                min2j = a
            for j in range(0, self.size):
                if i != j:
                    x = self.distance[i * self.size + j]
                    mj = self.distance[i * self.size + min_j]
                    m2j = self.distance[i * self.size + min2j]
                    if x < mj:
                        min2j = min_j
                        min_j = j
                    elif x <= m2j:
                        min2j = j
            base += self.distance[i * self.size + min2j] + min(self.distance[i * self.size:i * self.size + self.size])
        base = int((base + start_len + end_len + 1) / 2)
        if base > self.lower_len:
            self.lower_len = base
            return

        # if the spanning tree lower bound graph is a solution
        if reduce(lambda x, y: x and len(y) == 2, connection):
            pre = -1
            cur = start_ver
            while True:
                self.lower.append(cur)
                for i in connection[cur]:
                    if i != pre:
                        pre = cur
                        cur = i
                        break

    def optimize(self):
        seed(time.clock())
        startt = time.clock()
        equal_times = 0
        all = set(self.optimal)
        pre = self.optimal
        # pre_len = self.distance
        pop_size = 200
        prt = 0.8
        t = 0.9
        cur = [[] for i in range(pop_size)]
        intcur = [[] for i in range(pop_size)]
        for i in range(pop_size):
            for j in range(self.size - 2):
                rand = random()
                # print(rand)
                cur[i].append(rand * (self.size - 2) + 1)
                # print(self.size - 2)
            # print(len(intcur[i]),len(cur[i]))
            intcur[i] = list(map(lambda x: int(x), cur[i]))
            while True:
                count = Counter(intcur[i])
                perm = [k for k in all if k not in intcur[i]]
                # print(all)
                if len(perm) == 0:
                    break
                for j in range(self.size - 2):
                    if len(perm) == 0:
                        break
                    if count[intcur[i][j]] > 1:
                        rand = int(random() * len(perm))
                        # print(rand)
                        cur[i][j] = float(perm[rand])
                        perm.remove(perm[rand])
                        count[intcur[i][j]] -= 1
                intcur[i] = list(map(lambda x: int(x), cur[i]))
        cur.append(list(map(lambda x: float(x), pre)))
        intcur.append(pre)
        pop_size += 1
        distance = list(map(self.get_path_length, intcur))
        self.optimal = intcur[distance.index(min(distance))]
        self.optimal_len = distance[distance.index(min(distance))]
        while True:
            # pre = self.optimal
            pre_len = self.optimal_len
            for i in range(pop_size):
                for j in range(self.size - 2):
                    Prt = int(random() * prt * 2)
                    cur[i][j] = cur[i][j] + (self.optimal[j] - cur[i][j]) * Prt * t
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
            distance = list(map(self.get_path_length, intcur))
            self.optimal = intcur[distance.index(min(distance))]
            self.optimal_len = min(distance)
            if self.optimal_len - pre_len < 0.01:
                equal_times += 1
                timectrl = 10
                curt = time.clock() - startt
                if self.optimal_len < 1.05 * self.lower_len or equal_times > 1 or curt > timectrl:
                    self.optimal_len = self.optimal_len
                    if curt > timectrl:
                        print(curt)
                    break
            else:
                equal_times = 0

    def __weighed_optimize_branch(self):
        original_matrix = SqMat(self.shelfDistance, self.shelfSize)
        totalW = 0
        # print(original_matrix.toString())
        original_matrix.set_col_none(0)
        original_matrix.set_row_none(self.shelfSize - 1)
        for i in range(self.shelfSize):
            original_matrix.set_none(i, i)
        matrix = copy.copy(original_matrix)
        path = [0]
        realPath = []
        for i in path:
            for j in self.shelf[i]:
                realPath.append(j)
        maxLen = 1
        cost = matrix.reduce() * totalW
        queue = PriorityQueue()

        class Unit(tuple):
            def __init__(self, unit):
                tuple.__init__(unit)

            def __cmp__(self, other):
                if self[0] < other[0]:
                    return -1
                if self[0] > other[0]:
                    return 1
                if len(self[1]) < len(other[1]):
                    return -1
                if len(self[1]) > len(other[1]):
                    return 1
                return 0

        all_ver_no_end = range(self.shelfSize - 1)
        queue.put(Unit((cost, path, matrix, 0, totalW)))
        (cost, path, matrix, rest_next, totalW) = queue.get()
        while True:
            newMatrix = copy.copy(matrix)
            newPath = copy.copy(path)

            rest_ver = [i for i in all_ver_no_end if i not in path]
            pathLen = len(path)
            if self.shelfSize - pathLen == 1:
                rest_ver = [self.shelfSize - 1]
            elif self.shelfSize - pathLen == 0:
                break
            next_ver = rest_ver[rest_next]
            last_ver = path[-1]

            newPath.append(next_ver)
            newTotalW = totalW + self.shelfW[next_ver]
            costPlus = newMatrix[last_ver * self.shelfSize + next_ver] * totalW
            newMatrix.set_row_none(last_ver)
            newMatrix.set_col_none(next_ver)
            costPlus += newMatrix.reduce() * newTotalW
            newCost = cost + costPlus
            queue.put(Unit((newCost, newPath, newMatrix, 0, newTotalW)))
            realPath = []
            for i in newPath:
                for j in self.shelf[i]:
                    realPath.append(j)

            if rest_next < len(rest_ver) - 1:
                rest_next += 1
            else:
                (cost, path, matrix, rest_next, totalW) = queue.get()

        realPath = []
        for i in path:
            for j in self.shelf[i]:
                realPath.append(j)

        self.optimal = realPath[1:-1]
        self.optimal_len = self.get_path_length(self.optimal)

    def __optimize_branch(self):
        threshold = 9
        startTime = time.time()
        original_matrix = SqMat(self.shelfDistance, self.shelfSize)
        original_matrix.set_col_none(0)
        original_matrix.set_row_none(self.shelfSize - 1)
        for i in range(self.shelfSize):
            original_matrix.set_none(i, i)
        matrix = copy.copy(original_matrix)
        path = [0]
        realPath = []
        for i in path:
            for j in self.shelf[i]:
                realPath.append(j)
        maxLen = 1
        cost = matrix.reduce()
        queue = PriorityQueue()

        class Unit(tuple):
            def __init__(self, unit):
                tuple.__init__(unit)

            def __cmp__(self, other):
                if self[0] < other[0]:
                    return -1
                if self[0] > other[0]:
                    return 1
                if len(self[1]) < len(other[1]):
                    return -1
                if len(self[1]) > len(other[1]):
                    return 1
                return 0

        all_ver_no_end = range(self.shelfSize - 1)
        queue.put(Unit((cost, path, matrix, 0, 1)))
        (cost, path, matrix, rest_next, realLen) = queue.get()
        while True:
            maxLen = max(realLen, maxLen)
            newRealLen = realLen + 1
            newMatrix = copy.copy(matrix)
            newPath = copy.copy(path)

            rest_ver = [i for i in all_ver_no_end if i not in path]
            pathLen = len(path)
            if self.shelfSize - pathLen == 1:
                rest_ver = [self.shelfSize - 1]
            elif self.shelfSize - pathLen == 0:
                break
            if time.time() - startTime > 25:
                threshold = 2
            if maxLen - realLen > threshold:
                (cost, path, matrix, rest_next, realLen) = queue.get()
                continue

            next_ver = rest_ver[rest_next]
            last_ver = path[-1]

            newPath.append(next_ver)
            costPlus = newMatrix[last_ver * self.shelfSize + next_ver]
            newMatrix.set_row_none(last_ver)
            newMatrix.set_col_none(next_ver)
            costPlus += newMatrix.reduce()
            newCost = cost + costPlus
            # newRealLen += 1
            queue.put(Unit((newCost, newPath, newMatrix, 0, newRealLen)))
            realPath = []
            for i in newPath:
                for j in self.shelf[i]:
                    realPath.append(j)

            if rest_next < len(rest_ver) - 1:
                rest_next += 1
            else:
                (cost, path, matrix, rest_next, realLen) = queue.get()

        realPath = []
        for i in path:
            for j in self.shelf[i]:
                realPath.append(j)

        self.optimal = realPath[1:-1]
        self.optimal_len = self.get_path_length(self.optimal)
        # print(matrix.toString())

    def csv(self):
        Str = lambda x: str((x- 1) / 2)
        s = [Str(self.start[0]) + "," + Str(self.start[1]) + "," + Str(self.end[0]) + "," + Str(
            self.end[1]) + "," + self.get_optimal_len() + "," + self.get_optimal_effort() + "\n"]
        for i in map(lambda x: self.task[x - 1], self.optimal):
            s += [str(i)] + [","]
        s[-1] = "\n"
        s = "".join(s)
        return s

    def output(self):
        Str = lambda x: str(((x[0] - 1) / 2, (x[1] - 1) / 2))
        s = ""
        if not self.reallyWeighed:
            s += "NO WEIGHT DATUM.\n"
        s += "##Worker Start Location##\n" + Str(list(self.start))
        s += "\n## Worker End Location##\n" + Str(list(self.end))
        s += "\n##Original Parts Order##\n" + str(list(map(lambda x: self.task[x - 1], self.original)))
        s += "\n##Upper-Bound Order##\n" + str(list(map(lambda x: self.task[x - 1], self.upper)))
        s += "\n##Optimized Parts Order##\n" + str(list(map(lambda x: self.task[x - 1], self.optimal)))
        s += "\n##Original Parts Total Distance##\n" + str(float(self.original_len) / 2)
        s += "\n##Upper-Bound Distance##\n" + str(float(self.upper_len) / 2)
        s += "\n##Lower-Bound Distance##\n" + str(float(self.lower_len) / 2)
        s += "\n##Optimized Parts Total Distance##\n" + str(float(self.optimal_len) / 2)
        if self.weighed:
            self.optimize_branch = self.__optimize_branch
            self.optimize_branch()
            s += "\n##Optimized without Weight##\n" + str(list(map(lambda x: self.task[x - 1], self.optimal)))
            s += "\n##Total Distance##" + str(float(self.optimal_len) / 2)
        if self.reallyWeighed:
            s += "\n##Total Effort##" + str(float(self.get_path_effort(self.optimal)) / 2)
        s += "  \n\n"
        return s

    def __get_path_length(self, path):
        total = self.distance[path[0]] + \
                self.distance[path[self.size - 3] * self.size + self.size - 1]
        for i in range(self.size - 3):
            total += self.distance[path[i] * self.size +
                                   path[i + 1]]
        return total

    def get_path_effort(self, path):
        totalW = 0
        total = 0.0
        for i in range(self.size - 3):
            totalW += self.weight[path[i]]
            total += totalW * self.distance[path[i] * self.size + path[i + 1]]
        totalW += self.weight[path[-1]]
        total += totalW * self.distance[path[-1] * self.size + self.size - 1]
        return total

    def get_path_string(self, path):
        tmp = str(list(map(lambda x: self.task[x - 1], path)))
        return tmp

    def get_path_detail(self, path):
        def get_left(coord):
            return coord[0] - 1, coord[1]

        def get_right(coord):
            return coord[0] + 1, coord[1]

        path = list(map(lambda x: self.location[x], path))
        tmpPath = [self.start] + path + [self.end]
        tmpLiftPoints = [None] * len(tmpPath)
        tmpLiftPoints[0] = self.start
        tmpLiftPoints[len(tmpPath) - 1] = self.end
        for i in range(1, len(tmpPath) - 1):
            pre = tmpLiftPoints[i - 1]
            l = get_left(tmpPath[i])
            r = get_right(tmpPath[i])
            if self.grids.distance_between(pre, l) < self.grids.distance_between(pre, r):
                tmpLiftPoints[i] = l
            else:
                tmpLiftPoints[i] = r
        tmp = [self.grids.getI(self.start)]
        for i in range(len(tmpPath) - 1):
            tmp += self.grids.pathBetween(tmpLiftPoints[i], tmpLiftPoints[i + 1])
        return map(self.grids.getI, tmpPath), tmp, map(self.grids.getI, tmpLiftPoints)

    @classmethod
    def get_real_path_detail(cls, start, end, path):
        def get_location(id):
            index = cls.grids.ids.index(id)
            return cls.grids.xs[index], cls.grids.ys[index]

        def get_left(coord):
            return coord[0] - 1, coord[1]

        def get_right(coord):
            return coord[0] + 1, coord[1]

        path = list(map(lambda x: get_location(x), path))
        tmpPath = [start] + path + [end]
        tmpLiftPoints = [None] * len(tmpPath)
        tmpLiftPoints[0] = start
        tmpLiftPoints[len(tmpPath) - 1] = end
        for i in range(1, len(tmpPath) - 1):
            pre = tmpLiftPoints[i - 1]
            l = get_left(tmpPath[i])
            r = get_right(tmpPath[i])
            if cls.grids.distance_between(pre, l) < cls.grids.distance_between(pre, r):
                tmpLiftPoints[i] = l
            else:
                tmpLiftPoints[i] = r
        tmp = [cls.grids.getI(start)]
        for i in range(len(tmpPath) - 1):
            tmp += cls.grids.pathBetween(tmpLiftPoints[i], tmpLiftPoints[i + 1])
        return map(cls.grids.getI, tmpPath), tmp, map(cls.grids.getI, tmpLiftPoints)
        pass

    def get_optimal_detail(self):
        return self.get_path_detail(self.optimal)

    def get_optimal_effort(self):
        effort = "None"
        if self.reallyWeighed:
            effort = str(self.get_path_effort(self.optimal))
        return effort

    def get_optimal_len(self):
        return str(float(self.optimal_len) / 2)
