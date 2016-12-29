'''
Created on 2014. 12. 3.

@author: biscuit
'''
from decimal import *

getcontext().prec = 500

def getContiFrac(p, cList):
    cList.append(int(p))
    p = p-int(p)
    if p == 0:
        return cList
    if Decimal(1)/p > 500000:
        return cList
    return getContiFrac(Decimal(1)/p, cList)

def evalContiFrac(cList):
    p = Decimal(0)
    for i in range(1,len(cList)):
        p += cList[-i]
        p = Decimal(1)/p
    return p+cList[0]

def getFrac(cList):
    pList = [1,cList[0]]
    qList = [0,1]
    for i in range(2, len(cList)+1):
        pList.append(cList[i-1]*pList[i-1]+pList[i-2])
        qList.append(cList[i-1]*qList[i-1]+qList[i-2])
    return pList[-1], qList[-1]


C = []
p = Decimal(0.432797610581709571895889631631346892333949651543165979234817237946238088465367657516711705305077513867159721234532783387853790356990470772294126013369364244062011093727776987626226710283032285592376617835300810695491395249608874982221590100981368226425828473901294268240648556393116199687099985777272080785094581140662779121035414592518845114492959749679988621817664628075664912530223296828331674015076091594367799743990)
print "p = ",
print p
print "Continued fraction of p : "
print getContiFrac(p, C)

print "Original Sequence: ",
a = '432797610581709571895889631631346892333949651543165979234817237946238088465367657516711705305077513867159721234532783387853790356990470772294126013369364244062011093727776987626226710283032285592376617835300810695491395249608874982221590100981368226425828473901294268240648556393116199687099985777272080785094581140662779121035414592518845114492959749679988621817664628075664912530223296828331674015076091594367799743990'
print a
print "Computed Sequence: ",
b = str(evalContiFrac(C))
print b

print "Original in Computed : ",
print a in b

print "p = %d/%d" % getFrac(C)

        