'''
Created on 2014. 10. 4.

@author: biscuit
'''

class DFA:
    '''
    Implemented class of DFA_simul with partial function.
    States and inputs are must be clarified first.
    '''
    numStates = 0
    inputs = []
    numInputs = 0
    finals = set([])
    numFinals = 0
    initial = None
    
    trans = []
    
    def __init__(self, numStates, inputList, initialIndex):
        '''
        Constructor
        '''
        self.states = range(numStates)
        self.numStates = numStates
        self.inputs = list(inputList)
        self.numInputs = len(inputList)
        self.initial = initialIndex
        self.setEmptyTrans()
        
    def setInputs(self, inputList):
        '''
        Set Inputs by given lists of inputs
        ''' 
        self.inputs = inputList
        self.numInputs = len(inputList)
        
    def setFinals(self, finalList):
        self.finals = set([f for f in finalList if f in self.states])
        self.numFinals = len(self.finals)
        
    def setEmptyTrans(self):
        '''
        Generate empty transform-function, as (states)*(inputs) matrix.
        Every entries are set to None.
        ''' 
        emp_dict = {}.fromkeys(self.inputs)
        self.trans = []
        for i in self.states:  # @UnusedVariable
            self.trans.append(emp_dict.copy())
    
    def setTrans(self, incidentMat):
        '''
        Clarify the transform function, with given information incidentMat.
        incidentMat is of the form (states)*(inputs) matrix (entices are elements in states) 
        ''' 
        for i in self.states:
            for j in range(self.numInputs):
                if incidentMat[i][j] in self.states:
                    self.trans[i][self.inputs[j]] = incidentMat[i][j]
                    
    def addTransRule(self, startState, symbol, destState):
        if symbol not in self.inputs:
            print symbol + "is not in input symbols."
            return 
        if startState not in self.states:
            print startState + "is not in states."
            return
        if destState not in self.states:
            print destState + "is not in states."   
            return 
        self.trans[startState][symbol] = destState
    
    def isAccept(self, inputStr):
        '''
        Check whether the input string is accepted in the DFA_simul. 
        ''' 
        curState = self.initial
        for s in inputStr:
            if s not in self.inputs:
                return False
            if curState == None :
                return False
            curState = self.trans[curState][s]
        if curState in self.finals:
            return True
        return False
    
    def getMinimalDFA(self):
        
        mStates = self.getEquipartition()
        p2m = {}
        s2p = {}
        for i in range(len(mStates)):
            p2m[mStates[i]]=i
        for m in mStates:
            for i in m:
                s2p[i] = m
        
        minit = p2m[s2p[self.initial]]
        mfinal = set([p2m[s2p[f]] for f in self.finals])
        
        mDFA = DFA(len(mStates), self.inputs, minit)
        mDFA.setFinals(mfinal)
        for m in mStates:
            t = m[0]
            for i in self.inputs:
                mDFA.addTransRule(p2m[m], i, p2m[s2p[self.trans[t][i]]])
        return mDFA
    
    def tableEliminate(self, tableList):            
        delTemp = []
        temp = tableList[:]
        for t in temp:
            T = list(t)
            for s in self.inputs:
                sT = set([self.trans[T[0]][s],self.trans[T[1]][s]])
                if len(sT) == 2 and sT not in temp:
                    delTemp.append(t)
                    break
        for d in delTemp:
            temp.remove(d)
        return temp    
    
    def getEquipartition(self):
        tableList = []
        for i in self.states:
            for j in self.states:
                if i == j:
                    break
                tableList.append(set([i,j]))
        for f in self.finals :
            for s in self.states:
                if s not in self.finals:
                    tableList.remove(set([f,s]))           
        
        while self.tableEliminate(tableList) != tableList:
            tableList = self.tableEliminate(tableList)
        
        singList = self.states[:]
        multList = []
        partition = []
        for t in tableList:
            isSet = False
            for s in t:
                try:
                    singList.remove(s)
                except ValueError:
                    isSet = True
            if isSet:
                for m in multList:
                    if m & t != set([]):
                        m |= t
                        break
            else:
                multList.append(t)
        for i in singList:
            partition.append((i,))
        for i in multList:
            partition.append(tuple(i))
        return partition