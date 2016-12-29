'''
Created on 2014. 11. 9.

@author: user
'''
import random
import math


def generate_prime(bound):
    pList = [2,3,5,7,11,13]
    for i in range(pList[-1]+2, bound+1, 2):
        for j in pList:
            if (j*j > i):
                pList.append(i)
                break
            if (i%j == 0):
                break
    for i in range(len(pList)):
        pList[i] = str(pList[i])
    with open(r"C:\prime_under_"+str(bound)+".txt", "w") as f:
        for i in range(0,len(pList),50):
            f.write(" ".join(pList[i:i+50])+"\n")
'''
def exp_mod(a, exp, mod):
    if exp == 1:
        return a % mod
    if exp == 2:
        return a*a % mod
    if exp%2 == 0:
        print exp
        return (exp_mod(a, exp/2, mod)*exp_mod(a, exp/2, mod)) % mod
    else:
        print exp
        return (exp_mod(a, exp/2, mod)*exp_mod(a, exp/2, mod)*a) % mod
'''
                
def isPrimitive(a, mod, fList):
    if pow(a, mod-1, mod) != 1:
        return False
    for p in fList:
        if pow(a, (mod-1)/p, mod) == 1:
            return False
    return True

def existPrimitive(p, fList, count = 1):
    if count > p/2:
        print "fail to find a primitive root."
        return False
    r = random.randint(2, p-1)
    print "(trial "+str(count)+"): "+ str(r)
    if not isPrimitive(r, p, fList):
        return existPrimitive(p, fList, count+1)
    print str(r)+" is a primitive root."
    return True

def getPrimeFactors(a, pList):
    print "--Get prime factors of "+str(a)+";"
    fList = []
    temp = a
    for p in pList:   
        exp = 0
        while(temp%p == 0):
            exp += 1
            temp /= p
        if exp != 0:
            fList.append(p)
        if temp == 1:
            print "result: ",
            print fList
            print "prime factors of "+str(a)+":",
            print fList
            return fList
    print "result: ",
    print fList,
    print ", unknown: "+str(temp)
    
    if isPrime(temp, pList):
        fList.append(temp)
    else:
        exit()
    print "prime factors of "+str(a),
    print fList
    return fList

def isNthRootInteger(a, n):
    if n == 0:
        return False
    x = int(a**(1.0/n))
    while True:
        if x**n == a:
            return True, x
        if x**n > a:
            return False, x-1
        x += 1

def isPrime(p, pList):
    print "Primality Test: "+str(p)
    print "[CLAIM] "+str(p)+ " is a prime."
    if p == 2:
        print "2 is a prime."
        return True
    print "-Finding primitive root of "+str(p)+";"
    if not existPrimitive(p, getPrimeFactors(p-1, pList)):
        print "[FAIL] Can't find a primitive root."
        return False
    n = 2
    while True:
        isInt, k = isNthRootInteger(p, n)
        print "Is "+str(n)+"th root of "+str(p)+" an integer? " + ("No "+"("+str(k)+".xx...)","Yes")[isInt]
        if isInt:
            print "[FAIL] "+str(p)+" is of the form p^"+str(n)+"."
            return False
        if k < 2:
            print str(p)+" is a prime."
            return True
        n += 1

with open(r"C:\prime_under_16000000.txt", "r") as g:
    pBase = []
    for line in g:
        pBase.extend(line.split())
    for i in range(len(pBase)):
        pBase[i]= int(pBase[i])
              
print isPrime(35742549198872617291353508656626642567, pBase)