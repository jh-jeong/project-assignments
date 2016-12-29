# -*- coding:utf-8 -*-
'''
Created on 2014. 10. 5.

@author: biscuit
'''
from DFA_simul import DFA

def loadDFA():
    numStates = 0
    symbols = []
    initialIndex = 0
    final = []
    iMat = []
    temp = raw_input("[LOAD] File path: ")
    with open(temp, "r") as f:
        lines = f.readlines()
        s_lines = []
        for line in lines:
            s_lines.append(line.split())
        try:
            numStates = int(s_lines[0][1])
            if s_lines[0][0] == 'numStates':
                numStates = int(s_lines[0][1])
            else : exit("File format error")
            if s_lines[1][0] == 'symbols':
                symbols = list(s_lines[1][1])
            else : exit("File format error")
            if s_lines[2][0] == 'initialIndex':
                initialIndex = int(s_lines[2][1])
            else : exit("File format error")
            if s_lines[3][0] == 'final':
                final = [int(f) for f in s_lines[4]]
            else : exit("File format error")
            if s_lines[5][0] == 'delta':
                for d in s_lines[6:6+numStates]:
                    iMat.append([int(e) for e in d])
        except ValueError: 
            print "numStates or each states must be represented by digits."
            exit("File format error")
    M = DFA.DFA(numStates, symbols, initialIndex)
    M.setFinals(final)
    M.setTrans(iMat)
    return M
    
def saveDFA(D, path):
    with open(path, "w") as f:
        f.write("numStates\t%d\n" % D.numStates)
        f.write("symbols\t\t%s\n" % "".join(D.inputs))
        f.write("initialIndex\t%d\n" % D.initial)
        f.write("final\n")
        finalStr = [str(i) for i in D.finals]
        f.write(" ".join(finalStr)+"\n")
        f.write("delta\n")
        for s in range(D.numStates):
            tempVec = []
            for i in D.inputs:
                tempVec.append(str(D.trans[s][i]))
            f.write(" ".join(tempVec)+"\n")
    
def simul(D):
    while True:
        print "Input String: (\'q\' to exit) ",
        inputStr = raw_input()
        if inputStr == 'q':
            break
        if(D.isAccept(inputStr)):
            print "네"
        else: 
            print "아니요"