'''
Created on 2014. 11. 26.

@author: user
'''
from __future__ import division
import math

def Binomial(n, k):
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    c = 1
    for i in range(k):
        c = c * (n - i) // (i + 1)
    return c

for t in [10, 20, 30]:
    B = 10**t
    pi_B = B // int(math.log(B))
    u = 300//t
    print "-----CASE B = 10^%d" % t
    print Binomial(pi_B+u, u) / (10**300)
    
for u in [30, 15, 10]:
    k = (math.e)/(u*math.log(u))
    print k**u