# -*- coding:utf-8 -*-
'''
Created on 2014. 11. 16.

@author: biscuit
'''
from eNFA_simul import eNFA
from DFA_simul import DFA_Loader as DL

def load_eNFA():
    numStates = 0
    symbols = []
    numSymbols = 0
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
                numSymbols = len(symbols)
            else : exit("File format error")
            if s_lines[2][0] == 'initialIndex':
                initialIndex = int(s_lines[2][1])
            else : exit("File format error")
            if s_lines[3][0] == 'final':
                final = [int(f) for f in s_lines[4]]
            else : exit("File format error")
            if s_lines[5][0] == 'delta':
                offset = numSymbols+2
                for i in range(numStates):
                    curPivot = 6+i*(offset)
                    trans = []
                    if len(s_lines[curPivot])== 1 and i == int(s_lines[curPivot][0]):
                        for j in range(offset-1):
                            v = [int(d) for d in s_lines[curPivot+1+j]]
                            trans.append(v)
                        iMat.append(trans)
                    else : exit("File format error")
            else : exit("File format error")
        except ValueError: 
            print "numStates or each states must be represented by digits."
            exit("File format error")
    M = eNFA.eNFA(numStates, symbols, initialIndex)
    M.setFinals(final)
    M.setTrans(iMat)
    return M

def simul(N):
    while True:
        print "Input String: (\'q\' to exit)",
        inputStr = raw_input()
        if(inputStr == "q"):
            break
        if(N.isAccept(inputStr)):
            print "네"
        else: 
            print "아니요"
            
def eNFA2DFA_simul():
    print '[CS322] Project 2-1 ==== eNFA to mDFA Converter'
    print '---Loading eNFA'
    N = load_eNFA()
    print '---eNFA Loaded. Converting to DFA..'
    M = N.eNFA2DFA()
    print '---Completely converted to DFA. Minimizing..'
    minM = M.getMinimalDFA()
    print '---Conversion to mDFA Complete.'
    print '---Starting DFA Simulator..'
    DL.simul(minM)
    while True:
        inputPath = raw_input("Saving Location? (\'N\' to quit without saving) ")
        if inputPath != "N":
            try:
                DL.saveDFA(minM, inputPath)
                break
            except IOError:
                continue
        break