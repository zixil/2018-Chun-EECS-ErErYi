import csv
import sys

from Grids import Grids
from Task import Task

if len(sys.argv) >= 2:
    accuracy = int(sys.argv[1])
else:
    accuracy = 50

while True:
    start_x = int(input("Hello User, where is your worker?\nx:"))
    start_y = int(input("y:"))
    start = (start_x, start_y)
    end_x = int(input("What is your worker's end location?\nx:"))
    end_y = int(input("y:"))
    end = (end_x, end_y)

    if Task.grids is None:
        Task.grids = Grids('warehouse-grid.csv', max(start_x, end_x), max(start_y, end_y))
    alter = input("File input or manual input? (f/m): ").lower()
    if alter == "m":
        task = Task((input("Hello User, what items would you like to pick? (split with spaces)\n")).split(), start, end)
        task.optimize()
        print(task.output())

    if alter == "f":
        i_file = input("Please list file of orders to be processed: ")
        o_file = input("Please list output file: ")
        f=open(i_file)
        tasks = map(lambda x: Task(x, start, end), csv.reader(f))
        f.close()
        s = ""
        for i in tasks:
            i.optimize()
            s += i.output() + "\n"
        f = open(o_file, "w")
        f.write(s)
        f.close()

    foo = input("Continue? (Y/N): ").lower()
    if (foo == "n"):
        break
