# -*- coding:utf-8 -*-
'''
Created on 2014. 10. 14.

@author: biscuit
'''

cho_index = { u"ㄱ":0, u"ㄲ":1, u"ㄴ":2, u"ㄷ":3, u"ㄸ":4, u"ㄹ":5, u"ㅁ":6, u"ㅂ":7, u"ㅃ":8, u"ㅅ":9, u"ㅆ":10, u"ㅇ":11, 
             u"ㅈ":12, u"ㅉ":13, u"ㅊ":14, u"ㅋ":15, u"ㅌ":16, u"ㅍ":17, u"ㅎ":18 }
jung_index = { u"ㅏ":0, u"ㅐ":1, u"ㅑ":2, u"ㅒ":3, u"ㅓ":4, u"ㅔ":5, u"ㅕ":6, u"ㅖ":7, u"ㅗ":8, u"ㅘ":9, u"ㅙ":10, u"ㅚ":11, 
              u"ㅛ":12, u"ㅜ":13, u"ㅝ":14, u"ㅞ":15, u"ㅟ":16, u"ㅠ":17, u"ㅡ":18, u"ㅢ":19, u"ㅣ":20 }
jong_index = { u"":0, u"ㄱ":1, u"ㄲ":2, u"ㄳ":3, u"ㄴ":4, u"ㄵ":5, u"ㄶ":6, u"ㄷ":7, u"ㄹ":8, u"ㄺ":9, u"ㄻ":10, u"ㄼ":11, 
              u"ㄽ":12, u"ㄾ":13, u"ㄿ":14, u"ㅀ":15, u"ㅁ":16, u"ㅂ":17, u"ㅄ":18, u"ㅅ":19, u"ㅆ":20, u"ㅇ":21, u"ㅈ":22, 
              u"ㅊ":23, u"ㅋ":24, u"ㅌ":25, u"ㅍ":26, u"ㅎ":27 }
jong_cho_imbedding = {1:0, 2:1, 4:2, 7:3, 8:5, 16:6, 17:7, 19:9, 20:10, 21:11, 22:12, 23:14, 24:15, 25:16, 26:17, 27:18 }


def extractV(inp):
    o = ord(inp)
    if 0x314F <= o <= 0x318E:
        return jung_index(unichr(o))
    return ((o-0xAC00)/28)%21
def extractJ(inp):
    o = ord(inp)
    return (o-0xAC00)%28

def pC(c, buf):
    buf.append(c)
    return
def pV(v, buf):
    buf.append(v)
    return
def stop(inp, buf):
    buf.append(inp)
    return
def none(inp, buf):
    return

def loneV_normal(inp, buf):
    Cmap = {18:13, 20:0, 11:9}
    prev = buf[-1]
    if inp == u"ㆍ":
        t = jung_index[buf[-1]]
        buf[-1] = unichr(Cmap[t]+0x314F)
    elif prev in [u"ㅏ",u"ㅓ",u"ㅑ", u"ㅡ",u"ㅕ",u"ㅘ",u"ㅝ"]:
        buf[-1] = unichr(ord(buf[-1])+1)
    elif prev in [u"ㅗ",u"ㅜ"]:
        buf[-1] = unichr(ord(buf[-1])+3)
    else:
        buf[-1] = unichr(([u"ㅣ",u"ㅡ"].index(inp)+1)*(4+2*[u"ㆍ",":"].index(buf[-1]))+0x314F)
    return
def loneV_rot(inp, buf):
    rotList = [u"ㆍ",":",u"ㅏ",u"ㅑ",u"ㅜ",u"ㅠ"]
    i = rotList.index(buf[-1])
    buf[-1] = rotList[i+(-1)**i]
    return
def V_wa(inp, buf):
    if(buf[-1]==u"ㆍ"):
        buf.pop()
    else:
        buf.append(u"ㆍ")
    return

def V_withC(inp, buf):
    o = unichr(([u"ㅣ",u"ㅡ"].index(inp)+1)*(4+2*[u"ㆍ",":"].index(buf[-1]))+0x314F)
    buf.pop()
    if 0x3131 <= ord(buf[-1]) <= 0x314E:
        addV(o, buf)
    else:
        carry_withV(o, buf)
    return

def V_normal(inp, buf):
    Cmap = {18:13, 20:0, 11:9}
    v = ((ord(buf[-1])-0xAC00)/28)%21
    if inp == u"ㆍ":
        buf[-1] = unichr(ord(buf[-1])+(Cmap[v]-v)*28)
    elif v in [0,5,2,18,6,9,14]:
        buf[-1] = unichr(ord(buf[-1])+28)
    else:
        buf[-1] = unichr(ord(buf[-1])+3*28)
    return

def V_rot(inp, buf):
    dList = [u"ㆍ",":"]
    vMap = {0:2, 2:0, 13:17, 17:13}
    if buf[-1] in dList:
        buf[-1] = dList[buf[-1]!=":"]
    else:
        o = extractV(buf[-1])
        O = vMap[o]
        buf[-1] = unichr(ord(buf[-1])+(O-o)*28)
    
    
def addV(inpV, buf):
    cho_i = cho_index[buf[-1]]
    buf[-1] = unichr((cho_i*21 + jung_index[inpV])*28 + 0xAC00)
    return

def addJ(inpC, buf):
    buf[-1] = unichr(ord(buf[-1])+jong_index[inpC])
    return
def c_rot(inp, buf):
    twoList = [u"ㄴ",u"ㄹ",u"ㅇ",u"ㅁ"]
    threeList = [u"ㄱ",u"ㅋ",u"ㄲ",u"ㄷ",u"ㅌ",u"ㄸ",u"ㅂ",u"ㅍ",u"ㅃ",u"ㅈ",u"ㅊ",u"ㅉ",u"ㅅ",u"ㅎ",u"ㅆ"]
    if inp in twoList:
        i = twoList.index(buf[-1])
        buf[-1] = twoList[i+(-1)**i]
        return
    i = threeList.index(buf[-1])
    k = i/3; r= (i+1)%3
    buf[-1] = threeList[3*k+r]

def mergeJ(inp, buf):
    if extractJ(buf[-1])==8:
        tCr_jong(inp,buf)
        return 
    elif inp == u"ㅅ" :
        tCs_jong(inp, buf)
        return
    else:
        tCn_jong(inp,buf)
        return
     
def tCs_jong(inp, buf):
    r = extractJ(buf[-1])%3
    buf[-1] = unichr(ord(buf[-1])+(3-r))
    return
def tCn_jong(inpC,buf):
    r = jong_index[inpC]%3
    buf[-1] = unichr(ord(buf[-1])+(2-r))
    return 
def tCr_jong(inpC,buf):
    r = jong_index[inpC]%7
    if r<4:
        buf[-1] = unichr(ord(buf[-1])+r)
    elif r!=5:
        buf[-1] = unichr(ord(buf[-1])+(r+1))
    else:
        r = jong_index[inpC]%3
        buf[-1] = unichr(ord(buf[-1])+(2+2*r))
    return


def carry_withV(inpV, buf):
    lastJong = extractJ(buf[-1])
    if lastJong in jong_cho_imbedding.keys():
        buf[-1] = unichr(ord(buf[-1])-lastJong)
        buf.append(unichr((jong_cho_imbedding[lastJong]*21+jung_index[inpV])*28+0xAC00))
        return
    if lastJong in [3, 18]:
        buf[-1] = unichr(ord(buf[-1])-1)
        buf.append(unichr((9*21+jung_index[inpV])*28+0xAC00))
        return 
    if lastJong in [5, 6]:
        s=lastJong-4
        buf[-1] = unichr(ord(buf[-1])-s)
        buf.append(unichr(([12,18][s-1]*21+jung_index[inpV])*28+0xAC00))
        return
    else:
        s=lastJong-8
        buf[-1] = unichr(ord(buf[-1])-s)
        buf.append(unichr(([0,6,7,9,16,17,18][s-1]*21+jung_index[inpV])*28+0xAC00))
        return
    return

def insMerge(inp,buf):
    l=buf.pop()
    if l in [u"ㄷ",u"ㅅ",u"ㅇ"]:
        i = [u"ㄷ",u"ㅅ",u"ㅇ"].index(l)
        J = [13,6,10][i]
        buf[-1]= unichr(ord(buf[-1])-extractJ(buf[-1])+J)
    else: addJ(inp, buf)
    return

def rotJ(inp,buf):
    o = extractJ(buf[-1])
    rotDict = {1:24,24:2,2:1,4:8,8:4,7:25,21:16,16:21,17:26,19:27,27:20,20:19,22:23,12:15,11:14}
    O = rotDict[o]
    buf[-1]=unichr(ord(buf[-1])+(O-o))
    
def carryJ(inp,buf):
    if inp in [u"ㅇ",u"ㄷ",u"ㅂ",u"ㄱ"]:
        i = [u"ㅇ",u"ㄷ",u"ㅂ",u"ㄱ"].index(inp)
        buf[-1]=unichr(ord(buf[-1])-extractJ(buf[-1])+8)
        buf.append([u"ㅇ",u"ㄸ",u"ㅃ",u"ㅋ"][i])
    elif inp == u"ㅈ":
        buf[-1]=unichr(ord(buf[-1])-extractJ(buf[-1])+4)
        buf.append(u"ㅊ")
    else:
        t = extractJ(buf[-1])/3
        if t == 1:
            buf[-1]=unichr(ord(buf[-1])-extractJ(buf[-1])+1)
            buf.append(u"ㅎ")
        elif t == 2:
            buf[-1]=unichr(ord(buf[-1])-extractJ(buf[-1])+4)
            buf.append(u"ㅆ")
        else:
            buf[-1]=unichr(ord(buf[-1])-extractJ(buf[-1])+8)
            buf.append(u"ㅆ")
    return

def moveJ(inp,buf):
    cMap = {u"ㅍ":u"ㅃ", u"ㅊ":u"ㅉ",u"ㅌ":u"ㄸ" }
    o = extractJ(buf[-1])
    O = jong_cho_imbedding[o]
    buf[-1] = unichr(ord(buf[-1])-o)
    c = cho_index.keys()[cho_index.values().index(O)]
    buf.append(cMap[c])
    return

def insertJ(inp,buf):
    buf.pop()
    addJ(inp, buf)
    return

def mergeC(inpC, buf):
    r = extractJ(buf[-2])
    s = jong_index[buf[-1]]
    if r in [1,17]:
        buf[-2] = unichr(ord(buf[-2])+(3-(r%3)))
    elif r == 4:
        buf[-2] = unichr(ord(buf[-2])+(2-s%3))
    elif r == 8:
        t = s%7
        if t<4:
            buf[-2] = unichr(ord(buf[-2])+t)
        elif t!=5:
            buf[-2] = unichr(ord(buf[-2])+(t+1))
        else:
            t = s%3
            buf[-2] = unichr(ord(buf[-2])+(2+2*t))
    else:
        buf[-2] = unichr(ord(buf[-2])+s)
        
    buf[-1] = inpC
    return

def pushC(inp, buf):
    buf[-2] = unichr(ord(buf[-2])+jong_index[buf[-1]])
    buf[-1] = inp
    
def k_next(inp, buf):
    r = extractJ(buf[-2])
    s = jong_index[buf[-1]]
    if r in [1,17]:
        buf[-2] = unichr(ord(buf[-2])+(3-(r%3)))
    elif r == 4:
        buf[-2] = unichr(ord(buf[-2])+(2-s%3))
    elif r == 8:
        t = s%7
        if t<4:
            buf[-2] = unichr(ord(buf[-2])+t)
        elif t!=5:
            buf[-2] = unichr(ord(buf[-2])+(t+1))
        else:
            t = s%3
            buf[-2] = unichr(ord(buf[-2])+(2+2*t))
    else:
        buf[-2] = unichr(ord(buf[-2])+s)
    buf.pop()
    return
    

funcMap = {'c': pC, 'v': pV, 's': stop, 'N':none,
        "n":loneV_normal, "r":loneV_rot, 'w':V_wa,
        "C":V_withC, "m":V_normal, "R":V_rot,
        "V":addV, "o":c_rot, 
        "j":addJ, "z":mergeJ, "J":rotJ, "x":carryJ, "e":moveJ, "i":insertJ,
        "I":insMerge, "E":carry_withV,
        "P":pushC, "M":mergeC, "k":k_next }