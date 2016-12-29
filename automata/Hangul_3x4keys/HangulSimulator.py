# -*- coding:utf-8 -*-
'''
Created on 2014. 11. 5.

@author: biscuit
'''

from Mealy import MealyMachine as MM
from Hangul_3x4keys import Loader
from Hangul_3x4keys import outFunctionSet as oF
import pyHook, pythoncom
import codecs


han_dict = {
            "q":u"ㄱ","w":u"ㄴ","e":u"ㄷ",
            "a":u"ㅂ","s":u"ㅅ","d":u"ㅈ",
            "z":u'♥','x':u"ㅇ","c":'N',
            "b":u"ㅣ","n":u"ㆍ","m":u"ㅡ"
            }
key_dict = {
            "q":u"ㄱㅋㄲ","w":u"ㄴㄹ","e":u"ㄷㅌㄸ",
            "a":u"ㅂㅍㅃ","s":u"ㅅㅎㅆ","d":u"ㅈㅊㅉ",
            "z":u'♥','x':u"ㅇㅁ","c":'N',
            "b":u"ㅣ","n":u"ㆍ","m":u"ㅡ"
            }
inp_dict = {
            "q":"g","w":"n","e":"d",
            "a":"b","s":"s","d":"j",
            "z":'Q','x':"o","c":'x',
            "b":"I","n":"C","m":"Z"
            }
buf = []
M = Loader.loadMealy()
f = codecs.open('log.txt', encoding='utf-8', mode="a")

def printCurrent(inp):
    print ""
    if inp in 'qweasdzxcbnm':
        print "input: ", "".join(key_dict[inp])
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
    if inpChr in 'qweasdzxcbnm':
        oF.funcMap[M.doTransChar(inp_dict[inpChr])](han_dict[inpChr], buf)
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
        if len(buf)!=0: buf.pop()
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



print u"[CS322] Project-1 한글 모아쓰기 오토마타 (3x4-keys)"
print "Press any Hangul.."

# create a hook manager
hookManager = pyHook.HookManager()
hookManager.KeyDown = hangulSimulHandle
hookManager.HookKeyboard()
# wait forever
pythoncom.PumpMessages()


