'''
Created on 2014. 10. 14.

@author: biscuit
'''


class Mealy:
    '''
    Implemented class of Mealy-Machine with partial function.
    States and inputs are must be clarified first.
    '''
    numStates = 0
    inputs = []
    numInputs = 0
    outputs = []
    numOutputs = 0
    initial = None
    
    trans = []
    out_function = []
    
    current = None
    
    def __init__(self, numStates, inputList, outputList, initialIndex):
        '''
        Constructor
        '''
        self.states = range(numStates)
        self.numStates = numStates
        self.inputs = list(inputList)
        self.numInputs = len(inputList)
        self.outputs = list(outputList)
        self.numOutputs = len(outputList)
        self.initial = initialIndex
        self.current = self.initial
        
    def setInputs(self, inputList):
        '''
        Set Inputs by given lists of inputs
        ''' 
        self.inputs = inputList
        self.numInputs = len(inputList)
        
    def setEmptyTrans(self):
        '''
        Generate empty transform-function, as (states)*(inputs) matrix.
        Every entries are set to None.
        ''' 
        temp = {}
        self.trans = []
        for i in self.states:
            self.trans.append(temp.fromkeys(self.inputs))

    def setEmptyOutFunction(self):
        '''
        Generate empty output-function, as (states)*(inputs) matrix.
        Every entries are set to None.
        ''' 
        temp = {}
        self.out_function = []
        for i in self.states:
            self.out_function.append(temp.fromkeys(self.inputs))
            
    def setTrans(self, incidentMat):
        '''
        Clarify the transform function, with given information incidentMat.
        incidentMat is of the form (states)*(inputs) matrix (entices are elements in states) 
        ''' 
        self.setEmptyTrans()
        str_states = []
        for i in self.states:
            str_states.append(str(i))
        for i in self.states:
            for j in range(self.numInputs):
                if incidentMat[i][j] in str_states:
                    self.trans[i][self.inputs[j]] = int(incidentMat[i][j])
                    
    def setOutFunc(self, funcMat):
        '''
        Clarify the output function, with given information funcMat.
        funcMat is of the form (states)*(inputs) matrix (entices are elements in outputs) 
        ''' 
        self.setEmptyOutFunction()
        for i in self.states:
            for j in range(self.numInputs):
                if funcMat[i][j] in self.outputs:
                    self.out_function[i][self.inputs[j]] = funcMat[i][j]
                    
                    
    def addTransRule(self, startState, symbol, destState):
        if (symbol not in self.inputs):
            print symbol + "is not in input symbols."
            return 
        if startState not in self.states:
            print startState + "is not in states."
            return
        if destState not in self.states:
            print destState + "is not in states."   
            return 
        self.trans[startState][symbol] = destState
    
    def addOutFuncRule(self, startState, symbol, output):
        if (symbol not in self.inputs):
            print symbol + "is not in input symbols."
            return 
        if startState not in self.states:
            print startState + "is not in states."
            return
        if output not in self.outputs:
            print output + "is not in outputs."   
            return 
        self.out_function[startState][symbol] = output
        
    def getOutput(self, inputStr):
        strList = list(inputStr)
        curState = self.initial
        outputStr = ''
        for s in strList:
            if s not in self.inputs:
                return outputStr
            if curState == None :
                return outputStr
            if self.trans[curState][s] != None :
                if self.out_function[curState][s] != None:     
                    outputStr += self.out_function[curState][s]
                curState = self.trans[curState][s]
        return outputStr
     
    def setCurrent(self, destStateNum):
        if destStateNum not in range(self.numStates):
            print "There's no such state."
            return False
        self.current = destStateNum
        return True
    
    def doTransChar(self, inputSym):
        result = None
        if inputSym not in self.inputs:
            print "The input can't be accepted."
        elif self.current == None :
            print "Current state is None."
        else:        
            result = self.out_function[self.current][inputSym]
            self.current = self.trans[self.current][inputSym]
        return result
    
    def doTransStr(self, inputStr):
        result = ''
        for s in inputStr:
            temp = self.doTransChar(s)
            if temp == None:
                return result
            result += temp
        return result
    
            

    