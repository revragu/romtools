#!/usr/bin/env python3
# quick thing i threw together to chart roll probabilities in wiz i-ii-iii

import sys
import matplotlib.pyplot as plt

def main(argv):
    valcount={}
    lines=[]
    with open('wizoutput.txt','r') as f:
        lines=f.readlines()
    
    lines=[int(line.replace("\n",'')) for line in lines]
    total=len(lines)

    uniq_vals=set(lines)

    for val in uniq_vals:
        curr_count=len([roll for roll in lines if roll == val])
        valcount[str(val)]=(curr_count / total) * 100



    fig, ax = plt.subplots()
    ax.barh([str(k) for k in valcount.keys()],[valcount[str(k)] for k in valcount.keys()])
    plt.show()

    print(valcount)


if __name__ == "__main__":
   main(sys.argv[1:])