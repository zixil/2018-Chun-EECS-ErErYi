class SqMat(list):
    def __init__(self, array, x):
        if len(array) == x * x:
            list.__init__([])
            self.extend(array)
            self.x = x
            self.size = x * x
        else:
            print("wrong size")

    def reduce(self):
        cost = 0
        for i in range(self.x):
            start = i * self.x
            minVal = self[start]
            for j in range(start, start + self.x):

                if not (self[j] is None) and (minVal is None or self[j] < minVal):
                    minVal = self[j]
            if minVal:
                cost += self.row_minus(i, minVal)
        for i in range(self.x):
            minVal = self[i]
            for j in range(i, self.size, self.x):
                if not (self[j] is None) and (minVal is None or self[j] < minVal):
                    minVal = self[j]
            if minVal:
                cost += self.col_minus(i, minVal)
        return cost

    def get_row_min(self, i):
        start = i * self.x
        minVal = self[start]
        for j in range(start, start + self.x):
            if self[j] and (minVal is None or self[j] < minVal):
                minVal = self[j]
        return minVal

    def get_col_min(self, i):
        minVal = self[i]
        for j in range(i, self.size, self.x):
            if self[j] and (minVal is None or self[j] < minVal):
                minVal = self[j]
        return minVal

    def row_minus(self, i, n):
        if n:
            start = i * self.x
            for j in range(start, start + self.x):
                if self[j]:
                    self[j] -= n
        return n

    def col_minus(self, i, n):
        if n:
            for j in range(i, self.size, self.x):
                if self[j]:
                    self[j] -= n
        return n

    def set_col_none(self, i):
        for j in range(i, self.size, self.x):
            self[j] = None

    def set_row_none(self, i):
        start = i * self.x
        for j in range(start, start + self.x):
            self[j] = None

    def set_none(self, i, j):
        self[i * self.x + j] = None

    def copy_column(self, m):
        for j in range(i, self.size, self.x):
            self[j] = m[j]

    def toString(self):
        tmp = ""
        for i in range(self.x):
            for j in range(self.x):
                tmp += str(self[i * self.x + j])+" "
            tmp += "\n"
        return tmp
