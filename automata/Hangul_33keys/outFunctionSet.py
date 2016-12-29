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

def pC(c, buf):
    buf.append(c)
    return
def pV(v, buf):
    buf.append(v)
    return
def pAddv(inpV, buf):
    cho_i = cho_index[buf[-1]]
    buf[-1] = unichr((cho_i*21 + jung_index[inpV])*28 + 0xAC00)
    return
def pAddc(inpC, buf):
    buf[-1] = unichr(ord(buf[-1])+jong_index[inpC])
    return
def transV(inpV, buf):
    lastJung = ((ord(buf[-1])-0xAC00)/28)%21
    if inpV in [u"ㅏ", u"ㅐ"]:
        buf[-1] = unichr(ord(buf[-1])+28*(jung_index[inpV]+1))
    elif inpV in [u"ㅓ", u"ㅔ"]:
        buf[-1] = unichr(ord(buf[-1])+28*(jung_index[inpV]-3))
    elif lastJung == 18:
        buf[-1] = unichr(ord(buf[-1])+28)
    else:
        buf[-1] = unichr(ord(buf[-1])+28*3)
    return
def tCs_jong(inp, buf):
    r = ord(buf[-1])%28%3
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
def VInverse(inpV, buf):
    lastJong = (ord(buf[-1])-0xAC00)%28
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
def mergeC(inpC, buf):
    r = (ord(buf[-2])-0xAC00)%28
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

funcMap = {'c': pC, 'v': pV, 'a': pAddv, 'A': pAddc, 'T': transV, 's': tCs_jong, 'n': tCn_jong, 'r': tCr_jong, 'i': VInverse, 'b': mergeC} #, 'S': tCs_cho, 'N': tCn_cho, 'R': tCr_cho}