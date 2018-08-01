import csv
import sys

import time
from functools import reduce
from tkinter import *
from tkinter.scrolledtext import ScrolledText

from Grids import Grids
from Task import Task

if len(sys.argv) >= 2:
    accuracy = int(sys.argv[1])
else:
    accuracy = 50

window = Tk()
window.title("221AZIXIL")
if Task.grids is None:
    Task.grids = Grids(0, 0)
maxx = Task.grids.maxx
maxy = Task.grids.maxy

gridShow = []
gridFrame = Frame()
gridFrame.grid(row=0, column=0)
for i in range(0, maxx):
    for j in range(0, maxy):
        label = Label(gridFrame, text="", bg="black", width=4, height=2, font=("Arial", 6), wraplength=15)
        label.grid(row=j, column=i)
        gridShow.append(label)

for i in range(0, maxx, 2):
    for j in range(0, maxy, 2):
        gridShow[i * maxy + j]['bg'] = "yellow"


def resetShow():
    for i in gridShow:
        i["bg"] = "black"
        i["text"] = ""
    for i in range(0, maxx, 2):
        for j in range(0, maxy, 2):
            gridShow[i * maxy + j]['bg'] = "yellow"


startEndFrame = Frame()
startEndFrame.grid(row=1, column=0)
startXLabel = Label(startEndFrame, text="start x: ")
startXLabel.grid(row=0, column=0)
startXEntry = Entry(startEndFrame, width=4)
startXEntry.insert(0, 1)
startXEntry.grid(row=0, column=1)
startYLabel = Label(startEndFrame, text=" start y: ")
startYLabel.grid(row=0, column=2)
startYEntry = Entry(startEndFrame, width=4)
startYEntry.insert(0, 1)
startYEntry.grid(row=0, column=3)
endXLabel = Label(startEndFrame, text=" end x: ")
endXLabel.grid(row=0, column=4)
endXEntry = Entry(startEndFrame, width=4)
endXEntry.insert(0, 1)
endXEntry.grid(row=0, column=5)
endYLabel = Label(startEndFrame, text=" end y: ")
endYLabel.grid(row=0, column=6)
endYEntry = Entry(startEndFrame, width=4)
endYEntry.insert(0, 1)
endYEntry.grid(row=0, column=7)
startEndButton = Button(startEndFrame, text="Reset")
startEndButton.grid(row=0, column=8)

alterAlgFrame = Frame()
alterAlgFrame.grid(row=2, column=0)
alterAlg = IntVar()
alterAlg.set(2)
NNRadio = Radiobutton(alterAlgFrame, variable=alterAlg, text="Nearest Neighbot", value=0)
NNRadio.grid(row=0, column=0)
SOMARadio = Radiobutton(alterAlgFrame, variable=alterAlg, text="SOMA", value=1)
SOMARadio.grid(row=0, column=1)
BBRadio = Radiobutton(alterAlgFrame, variable=alterAlg, text="Branch & Bound", value=2)
BBRadio.grid(row=0, column=2)

alterWeiFrame = Frame()
alterWeiFrame.grid(row=3)
alterWei = BooleanVar()
alterWei.set(True)
UWRadio = Radiobutton(alterWeiFrame, variable=alterWei, text="Unweighted", value=False)
UWRadio.grid(row=0, column=0)
WRadio = Radiobutton(alterWeiFrame, variable=alterWei, text="Weighted", value=True)
WRadio.grid(row=0, column=1)


def showPath(pathDetail):
    resetShow()
    (path, detail, lift) = pathDetail
    k = 0
    for i in detail:
        gridShow[i]["bg"] = "Cyan"
        if gridShow[i]["text"] != "":
            gridShow[i]["text"] += ","
        gridShow[i]["text"] += str(k)
        k += 1
    k = 0
    for i in path:
        gridShow[i]["bg"] = "Green"
        gridShow[i]["text"] = k
        k += 1
    for i in lift:
        gridShow[i]["bg"] = "pink"


def orderOptimize():
    start = (int(startXEntry.get()), int(startYEntry.get()))
    end = (int(endXEntry.get()), int(endYEntry.get()))
    task = Task(orderEntry.get().split(), start, end, alterWei.get())
    if alterAlg.get() == 1:
        task.optimize()
    elif alterAlg.get() == 2:
        task.optimize_branch()
    resultText.delete("0.0", END)
    resultText.insert(INSERT, task.csv())
    distanceValue["text"] = task.get_optimal_len()
    effortValue["text"] = task.get_optimal_effort()
    showPath(task.get_optimal_detail())
    pass


orderFrame = Frame()
orderFrame.grid(row=5)
orderLabel = Label(orderFrame, text="Input a single order: ")
orderLabel.grid(row=0, column=0)
orderEntry = Entry(orderFrame, width=50)
orderEntry.grid(row=0, column=1)
orderButton = Button(orderFrame, text="Optimize", command=orderOptimize)
orderButton.grid(row=0, column=2)


def fileOptimize():
    start = (int(startXEntry.get()), int(startYEntry.get()))
    end = (int(endXEntry.get()), int(endYEntry.get()))
    i_file = fileEntry.get()
    o_file = resultEntry.get()
    f1 = open(i_file)
    c = list(csv.reader(f1))
    task = list(map(lambda x: Task(x, start, end, False), c))
    '''
    if alterWei.get():
        task = list(filter(lambda x: x.weighed, task))
    else:
        task = list(task)
    '''
    if alterAlg.get() == 1:
        for i in task:
            i.optimize()
    elif alterAlg.get() == 2:
        for i in task:
            i.optimize_branch()
    s = ""
    s += reduce(lambda x, y: x + y, map(lambda x: x.csv(), task))

    f2 = open(o_file, "w")
    f2.write(s)
    resultText.delete("0.0", END)
    resultText.insert("0.0", s)

    f2.close()
    f1.close()


fileFrame = Frame()
fileFrame.grid(row=6)
fileLabel = Label(fileFrame, text="Batch File: ")
fileLabel.grid(row=0, column=0)
fileEntry = Entry(fileFrame, width=50)
fileEntry.insert(0, "warehouse-orders-v03.csv")
fileEntry.grid(row=0, column=1)
fileButton = Button(fileFrame, text="Optimize", command=fileOptimize)
fileButton.grid(row=0, column=2)


def showResult():
    i_file = resultEntry.get()
    f1 = open(i_file)
    rs = list(csv.reader(f1))
    orderNo = int(resultNoEntry.get())
    if orderNo > len(rs) * 2:
        print("No out of range.")
        return
    info = rs[orderNo * 2]
    path = rs[orderNo * 2 + 1]
    convert = lambda x: int(float(x) * 2 + 1)
    start = (convert(info[0]), convert(info[1]))
    end = (convert(info[2]), convert(info[3]))
    showPath(Task.get_real_path_detail(start, end, path))
    s = ""
    for i in info:
        s += i + ","
    s = s[0:-1]
    s += "\n"
    for i in path:
        s += i + ","
    s = s[0:-1]
    s += "\n"
    resultText.delete("0.0", END)
    resultText.insert("0.0", s)
    distanceValue["text"] = info[4]
    effortValue["text"] = info[5]
    pass


resultFileFrame = Frame()
resultFileFrame.grid(row=7)
resultLabel = Label(resultFileFrame, text="Result File: ")
resultLabel.grid(row=0, column=0)
resultEntry = Entry(resultFileFrame, width=50)
resultEntry.insert(0, "out")
resultEntry.grid(row=0, column=1)
resultNoLabel = Label(resultFileFrame, text="No.")
resultNoLabel.grid(row=0, column=2)
resultNoEntry = Entry(resultFileFrame, width=4)
resultNoEntry.insert(0, 0)
resultNoEntry.grid(row=0, column=3)
resultButton = Button(resultFileFrame, text="Show", command=showResult)
resultButton.grid(row=0, column=4)

resultFrame = Frame()
resultFrame.grid(row=0, column=1, rowspan=6)
resultText = ScrolledText(resultFrame, width=50, height=50)
resultText.grid()

distanceFrame = Frame()
distanceFrame.grid(row=6, column=1)
distanceLabel = Label(distanceFrame, text="Distance:")
distanceLabel.grid(row=0, column=0)
distanceValue = Label(distanceFrame)
distanceValue.grid(row=0, column=1)
effortLabel = Label(distanceFrame, text="Effort:")
effortLabel.grid(row=0, column=2)
effortValue = Label(distanceFrame)
effortValue.grid(row=0, column=3)

window.mainloop()

'''
while True:
    start_x = 0
    start_y = 0
    end_x = 0
    end_y = 0
    start = (start_x, start_y)
    end = (end_x, end_y)
    if Task.grids is None:
        Task.grids = Grids(max(start_x, end_x), max(start_y, end_y))
    alter = input("File input or manual input? (f/m): ").lower()
    if alter == "m":
        param = (input("Hello User, what items would you like to pick? (split with spaces)\n")).split()
        task = Task(param, start, end)
        alter = input(
            "Which algorithm do you want to use? \na: Nearest Neighbor\nb: SOMA\nc: Branch & Bound\n").lower()
        if alter == "b":
            task.optimize()
        elif alter == "c":
            task.optimize_branch
        print(task.output())

    if alter == "f":
        i_file = "warehouse-orders-v01.csv"
        o_file = "out"
        startt = time.clock()
        f1 = open(i_file)
        c = list(csv.reader(f1))
        task = map(lambda x: Task(x, start, end), c)
        task = list(filter(lambda x: x.weighed, task))
        alter = input(
            "Which algorithm do you want to use? \na: Nearest Neighbor\nb: SOMA\nc: Branch & Bound\n").lower()
        if alter == "b":
            for i in task:
                i.optimize()
        elif alter == "c":
            for i in task:
                i.optimize_branch()
        s = ""
        s += reduce(lambda x, y: x + y, map(lambda x: x.output(), task))

        f2 = open(o_file, "w")
        f2.write(s)

        endt = time.clock()
        print(endt - startt)

        f2.close()
        f1.close()

    foo = input("Continue? (Y/N): ").lower()
    if foo == "n":
        break
'''
