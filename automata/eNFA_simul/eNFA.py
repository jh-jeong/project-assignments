'''
Created on 2014. 11. 15.

@author: user
'''
from DFA_simul import DFA as d

class eNFA:
    '''
    Implemented class of e-NFA.
    States and inputs are must be clarified first.
    '''
    numStates = 0
    states = []
    inputs = []
    numInputs = 0
    finals = set([])
    numFinals = 0
    initial = None
    trans = []
    
    curStates = set([])
    
    def __init__(self, numStates, inputList, initialIndex):
        '''
        Constructor
        '''
        self.states = range(numStates)
        self.numStates = numStates
        self.inputs = list(inputList)
        self.numInputs = len(inputList)
        if not self.setInitial(initialIndex):
            return None
        self.setEmptyTrans()
    
    def setInitial(self, initialIndex):
        if initialIndex not in self.states:
            print "Initial is not in states"
            return False
        self.initial = initialIndex
        self.curStates = set([self.initial])
        return True
    
    def setFinals(self, finalList):
        self.finals = set(finalList) & set(self.states)
        self.numFinals = len(self.finals)

    def setEmptyTrans(self):
        '''
        Generate empty transform-function, as (states)*(inputs) matrix.
        Every entries are set to empty-set (built-in data type).
        ''' 
        emp_dict = {}.fromkeys(self.inputs, set([]))
        emp_dict["_e"] = set([])
        self.trans = []
        for i in self.states:  # @UnusedVariable
            self.trans.append(emp_dict.copy())
    
    def setTrans(self, incidentMat):
        '''
        Clarify the transform function, with given information incidentMat.
        incidentMat is of the form (states)*(inputs+1)(;including '_e') matrix (entices are set-data; subset of states)
        '''
        self.inputs.insert(0, "_e")
        for i in self.states:
            for j in range(self.numInputs+1):
                self.trans[i][self.inputs[j]] = set(incidentMat[i][j]) & set(self.states)
        self.inputs.remove("_e")
        
    def addTransRule(self, startState, symbol, destSet):
        if symbol not in self.inputs and symbol != "_e":
            print symbol + "is not in input symbols."
            return 
        if startState not in self.states:
            print startState + "is not in states."
            return
        self.trans[startState][symbol] = (set(destSet) & set(self.states)) | self.trans[startState][symbol]

    def isAccept(self, inputStr):
        '''
        Check whether the input string is accepted in the DFA_simul. 
        ''' 
        cur = self.get_eClosure_state(self.initial)
        cur = self.getTransStr(cur, inputStr)
        if cur & self.finals != set([]):
            return True
        return False
    
    def getTransChar(self, curSet, inputSym):
        result = set([])
        curSet = self.get_eClosure_set(curSet)
        try:
            for c in curSet:
                result |= self.trans[c][inputSym]
        except KeyError:
            print "The input symbol %s can't accept." % inputSym
        return self.get_eClosure_set(result)
    
    def getTransStr(self, curSet, inputStr):
        if inputStr == "" or curSet == set([]):
            return curSet
        curSet = self.getTransChar(curSet, inputStr[0])
        return self.getTransStr(curSet, inputStr[1:])
    
    def doTrans(self, inputStr):
        self.curStates = self.getTransStr(self.curStates, inputStr)
    
    def get_eClosure_state(self, state):
        if state not in self.states:
            return set([])
        task = set([state])
        visited = set([])
        while task != set([]):
            pElem = task.pop()
            task |= self.trans[pElem]["_e"]
            visited.add(pElem)
            task -= visited
        return visited
    
    def get_eClosure_set(self, stateSet):
        closure = set([])
        temp = set(stateSet)
        while temp != set([]):
            state = temp.pop()
            closure |= self.get_eClosure_state(state)
            temp -= closure
        return closure

    def eNFA2DFA(self):
        task = set([frozenset(self.get_eClosure_state(self.initial))])
        stateList = []
        s2i = {}
        inputs = "".join(self.inputs)
        while task != set([]):
            pElem = task.pop()
            for i in self.inputs:
                task.add(frozenset(self.getTransChar(pElem,i)))
            stateList.append(pElem)
            task -= set(stateList)
        numStates = len(stateList)
        for i in range(numStates):
            s2i[stateList[i]]=i
        finals = [s2i[f] for f in stateList if f & self.finals != set([])]
        M = d.DFA(numStates, inputs, 0)
        M.setFinals(finals)
        for s in stateList:
            for i in inputs:
                dest = self.getTransChar(s,i)
                M.addTransRule(s2i[frozenset(s)], i, s2i[frozenset(dest)])
        return M
    
