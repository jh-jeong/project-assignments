# -*- coding:utf-8 -*-
'''
Created on 2014. 11. 25.

@author: user
'''
import regLY
from ply import lex, yacc
from eNFA_simul import eNFA as en
from DFA_simul import DFA_Loader as DL

lexer = lex.lex(module=regLY)
parser = yacc.yacc(module=regLY)


def sym(inp1):
    symbol = inp1
    if inp1 == "_e":
        symbol = ""
    N = en.eNFA(2, symbol, 0)
    N.setFinals([1])
    N.addTransRule(0, inp1, [1])
    return N

def empty(inp1):
    N = en.eNFA(2, "", 0)
    N.setFinals([1])
    return N

def paren(inp1):
    if type(inp1) == tuple:
        inp1 = fMap[inp1[0]](*inp1[1:])
    return inp1

def conc(inp1, inp2):
    if type(inp1) == tuple:
        inp1 = fMap[inp1[0]](*inp1[1:])
    if type(inp2) == tuple:
        inp2 = fMap[inp2[0]](*inp2[1:])
    n1 = inp1.numStates; n2 = inp2.numStates
    nStates = n1 + n2
    Inputs = list(set(inp1.inputs) | set(inp2.inputs))
    N = en.eNFA(nStates, Inputs, 0)
    N.setFinals([N.states[-1]])
    Trans = inp1.trans
    for vec in inp2.trans:
        tvec = {k: set(map(lambda x:x+n1, v)) for k, v in vec.iteritems()}
        Trans.append(tvec)
    for i in N.states:
        N.trans[i].update(Trans[i])
        
    N.addTransRule(n1-1, "_e", [n1])
    return N

def plus(inp1, inp2):
    if type(inp1) == tuple:
        inp1 = fMap[inp1[0]](*inp1[1:])
    if type(inp2) == tuple:
        inp2 = fMap[inp2[0]](*inp2[1:])
    n1 = inp1.numStates; n2 = inp2.numStates
    nStates = n1 + n2 + 2
    Inputs = list(set(inp1.inputs) | set(inp2.inputs))
    N = en.eNFA(nStates, Inputs, 0)
    N.setFinals([N.states[-1]])
    N.addTransRule(0, "_e", [1])
    N.addTransRule(0, "_e", [n1+1])
    
    Trans = [N.trans[0]]
    for vec in inp1.trans:
        tvec = {k: set(map(lambda x:x+1, v)) for k, v in vec.iteritems()}
        Trans.append(tvec)
    for vec in inp2.trans:
        tvec = {k: set(map(lambda x:x+n1+1, v)) for k, v in vec.iteritems()}
        Trans.append(tvec)
    Trans.append(N.trans[-1])
    for i in N.states:
        N.trans[i].update(Trans[i])
        
    N.addTransRule(n1, "_e", [n1+n2+1])
    N.addTransRule(n1+n2, "_e", [n1+n2+1])
    return N

def star(inp1):
    if type(inp1) == tuple:
        inp1 = fMap[inp1[0]](*inp1[1:])
    n1 = inp1.numStates
    nStates = n1 + 2
    Inputs = inp1.inputs
    N = en.eNFA(nStates, Inputs, 0)
    N.setFinals([N.states[-1]])
    N.addTransRule(0, "_e", [1])
    N.addTransRule(0, "_e", [n1+1])
    
    Trans = [N.trans[0]]
    for vec in inp1.trans:
        tvec = {k: set(map(lambda x:x+1, v)) for k, v in vec.iteritems()}
        Trans.append(tvec)
    Trans.append(N.trans[-1])
    for i in N.states:
        N.trans[i].update(Trans[i])
        
    N.addTransRule(n1, "_e", [1])
    N.addTransRule(n1, "_e", [n1+1])
    return N

fMap = {'symbols': sym, 'concat': conc, 'paren': paren, 'star': star, "plus": plus, "empty": empty }    

def get_eNFA(regStr):
    reg_AST = parser.parse(regStr)
    print reg_AST
    return fMap[reg_AST[0]](*reg_AST[1:])

def main():
    print '[CS322] Project 2 ====  RE to mDFA Converter'
    while True:
        try:
            inpStr = raw_input('Input your valid RE > ')
        except EOFError:
            break
        if not inpStr: continue
        reg_eNFA = get_eNFA(inpStr)
        print '---An eNFA generated from RE'
        reg_DFA = reg_eNFA.eNFA2DFA()
        print '---Completely converted to DFA. Minimizing..'
        minDFA = reg_DFA.getMinimalDFA()
        print '---Conversion to mDFA Complete.'
        print '---Starting DFA Simulator..'
        DL.simul(minDFA)
        while True:
            inputPath = raw_input("Saving Location? (\'N\' to quit without saving) ")
            if inputPath != "N":
                try:
                    DL.saveDFA(minDFA, inputPath)
                    break
                except IOError:
                    continue
            break
        break
    
if __name__ == '__main__':
    main()