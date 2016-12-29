'''
Created on 2014. 11. 10.

@author: user
'''
def isRootInteger(a):
    '''
    x = int(a**0.5)
    while True:
        if x*x == a:
            return True, x
        if x*x > a:
            return False, x-1
        x += 1
    '''
    # Using Newton's Method
    x = a
    y = (x + 1) / 2
    while y < x:
        x = y
        y = (x + a / x) / 2
    if x*x == a:
        return True, x
    return False, x

def getContinuedFraction(b, n, cList): 
    # continued fraction of b/n, return on cList
    if n == 1:
        cList.append(b)
        return cList
    cList.append(b/n)
    return getContinuedFraction(n, b%n, cList)

def findRoots(a, b):
    #find two real roots of x^2-ax+b = 0
    t = a*a-4*b
    if t<0:
        return None, False
    isInt, r = isRootInteger(t)  # For precise answer when it has integer roots
    if not isInt:
        r = t**0.5
    return ((a+r)/2, (a-r)/2), isInt

def Wiener(n, e):
    print "--Wiener's Low Decryption Exponent Attack--"
    print "Attack on... \nn = %d\ne = %d" % (n, e)
    cList = getContinuedFraction(e, n, [])
    print "Continued Fraction of e/n = %d/%d" % (e, n)
    print "=>",
    print cList
    pList = [1,cList[0]]
    qList = [0,1]
    for i in range(2, len(cList)+1):
        pList.append(cList[i-1]*pList[i-1]+pList[i-2])
        qList.append(cList[i-1]*qList[i-1]+qList[i-2])
        print "(trial %d) convergent %d/%d" % (i-1, pList[-1], qList[-1])
        print "[CLAIM] phi(n) = (%d*%d-1)/%d" % (qList[-1],e,pList[-1])
        if (qList[-1]*e-1)%pList[-1] != 0:
            print "[FAIL] phi(n) is not an integer."
            continue
        PHIn= (qList[-1]*e-1)/pList[-1]
        print "phi(n) = %d" % PHIn
        print "Solving x^2-%dx+%d = 0" % (n-PHIn+1, n)
        roots, isRootsInt = findRoots(n-PHIn+1, n)
        if isRootsInt:
            if roots[0]<n and roots[1]<n:
                print "[SUCCESS] %d = %d * %d" % ((n,)+roots)
                print "p = %d, q = %d" % roots
                return roots
            print "[FAIL] Can't find p, q"
        print "[FAIL] Can't find p, q"
    print "Attack Failed"


Wiener(448287482824619041153515251555947753732028432352319597882813402923937648539470241704783094371, 29018140892398745811489835593794243807431637474636631331734346949745234011096735)

    