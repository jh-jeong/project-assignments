# -*- coding:utf-8 -*-
'''
Created on 2014. 10. 14.

@author: biscuit
'''

from Mealy import MealyMachine
from Mealy import outFunctionSet

numStates = 0
inputs = []
outputs = []
initialIndex = 0
iMat = []
oMat = []

 
def loadMealy():
    print "[LOAD] File path: ",
    temp = raw_input()
    with open(temp, "r") as f:
        lines = f.readlines()
        s_lines = []
        for line in lines:
            s_lines.append(line.split())
        if s_lines[0][0] == 'numStates':
            if s_lines[0][1].isdigit():
                numStates = int(s_lines[0][1])
            else: 
                print "numStates must be a digit."
                return 
        else : exit("error")
        if s_lines[1][0] == 'inputs':
            inputs = list(s_lines[1][1])
        else : exit("error")
        if s_lines[2][0] == 'outputs':
            outputs = list(s_lines[2][1])
        else : exit("error")
        if s_lines[3][0] == 'initialIndex':
            if s_lines[3][1].isdigit():
                initialIndex = int(s_lines[3][1])
            else: 
                print "initialIndex must be a digit."
                return 
        else : exit("error")
        if s_lines[4][0] == 'delta':
            iMat = s_lines[5:5+numStates]
        if s_lines[5+numStates][0] == "lambda":
            oMat = s_lines[6+numStates:6+numStates*2]
    M = MealyMachine.Mealy(numStates, inputs, outputs, initialIndex)
    M.setTrans(iMat)
    M.setOutFunc(oMat)
    if not (set(outputs) <= set(outFunctionSet.funcMap.keys())):
        print "Wrong Output setting"
        return False
    return M

def exeString(funcString):
    f_list = list(funcString)
    for s in f_list:
        outFunctionSet.funcMap[s]();
        
def simul(Mealy):
    while True:
        print "Input String: ",
        inputStr = raw_input()
        outputStr = Mealy.getOutput(inputStr)
        if outputStr == False:
            print "Wrong input"
            continue
        print "Output String: ",
        print outputStr
        print "-------------execution"
        exeString(outputStr)
        print "-------------terminated"