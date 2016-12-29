# -*- coding:utf-8 -*-
'''
Created on 2014. 11. 5.

@author: biscuit
'''

from Mealy import MealyMachine as MM
from Mealy import Loader
from Hangul_33keys import outFunctionSet as oF
import pyHook, pythoncom
import codecs


han_dict = {"r":u"ㄱ", "s":u"ㄴ", "e":u"ㄷ", "f":u"ㄹ", "a":u"ㅁ", "q":u"ㅂ", "t":u"ㅅ", "d":u"ㅇ", "w":u"ㅈ", "c":u"ㅊ", "z":u"ㅋ", "x":u"ㅌ", "v":u"ㅍ", "g":u"ㅎ", 
            "R":u"ㄲ", "E":u"ㄸ", "Q":u"ㅃ", "T":u"ㅆ", "W":u"ㅉ", 
            "k":u"ㅏ", "i":u"ㅑ", "j":u"ㅓ", "u":u"ㅕ", "h":u"ㅗ", "y":u"ㅛ", "n":u"ㅜ", "b":u"ㅠ", "m":u"ㅡ", "l":u"ㅣ", "o":u"ㅐ", "O":u"ㅒ", "p":u"ㅔ", "P":u"ㅖ" }

buf = []
M = Loader.loadMealy()
f = codecs.open('log.txt', encoding='utf-8', mode="a")

def printCurrent(inp):
    print ""
    if inp.isalpha():
        print "input: ", han_dict[inp]
    else:
        print "input : ", inp
    print ">", ''.join(buf)
    print "-------------------------"
    
def printReturn():
    print ""
    print "input: Return (log updated)"
    print ">", ''.join(buf)
    print "-------------------------"

def printSp(inp):
    print ""
    print "input : ", inp
    print ">", ''.join(buf)
    print "-------------------------" 

def hangulSimulHandle(event):
    inpAscii = event.Ascii
    inpKey = event.Key
    spKeys = ['Tab', 'Space', 'Return', 'Back', 'Escape']
    if inpAscii == 0:
        return True
    inpChr = chr(inpAscii)
    if inpChr.isalpha():
        if inpChr not in 'rsefaqtdwczxvgREQTWkijuhynbmloOpP':
            inpChr=inpChr.lower()
        oF.funcMap[M.doTransChar(inpChr)](han_dict[inpChr], buf)
        printCurrent(inpChr)
    elif inpKey not in spKeys:
        buf.append(inpChr)
        M.setCurrent(0)
        printCurrent(inpChr)
    elif inpKey == 'Return':
        f.write("".join(buf)+"\n")
        del buf[:]
        M.setCurrent(0)
        printReturn()
    elif inpKey == 'Back':
        buf.pop()
        M.setCurrent(0)
        printCurrent(inpChr)
    elif inpKey == 'Escape':
        printSp(inpKey)
        print "Thank you!"
        f.close()
        exit()
    else:
        buf.append(inpChr)
        M.setCurrent(0)
        printSp(inpKey)
    return True



print u"[CS322] Project-1 한글 모아쓰기 오토마타 (33-keys)"
print "Press any Hangul.."

# create a hook manager
hookManager = pyHook.HookManager()
hookManager.KeyDown = hangulSimulHandle
hookManager.HookKeyboard()
# wait forever
pythoncom.PumpMessages()


