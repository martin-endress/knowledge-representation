#!/usr/bin/python

import random
import sys

baserels = ["b", "bi", "m", "mi", "o", "oi", "eq", "f", "fi", "s", "si", "d", "di"]

# A(n, d, l)
# n - size of network (# of var's)
# d - average degree (avg. # of non-universal constraint relations)
# l - average label size

def randomLabel(l):
    tmp = [x for x in baserels if random.uniform(0.0,1.0) < (float(l) / float(len(baserels))) ]
    if (len(tmp) == 0):
        tmp = [baserels[random.randint(0,len(baserels)-1)]]
    return tmp

def generateNetwork(n, d, l):
    print(n, "#", d, l)
    for i in range(0,n+1):
        for j in range (0,n+1):
            if ((i != j) and random.uniform(0.0,1.0) < (float(d) / float(n-1))):
                print(i, j, "(", " ".join(randomLabel(l)), ")")
    print(".")

def main():
    for instances in range(0, int(sys.argv[1])):
        generateNetwork(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))

main()
