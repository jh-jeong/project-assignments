'''
Created on 2014. 10. 13.

@author: biscuit
'''

import AES

key = [0]*16

w = AES.KeyExpansion(key)
input = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

Nb = 4
Nr = len(w)/Nb - 1

state = [ [0] * Nb, [0] * Nb, [0] * Nb, [0] * Nb ]
for i in range(0, 4*Nb): state[i%4][i//4] = input[i]

state = AES.AddRoundKey(state, w, 0, Nb)

print "round 0; ",
print state 

for round in range(1, Nr):
    state = AES.SubBytes(state, Nb)
    state = AES.ShiftRows(state, Nb)
    state = AES.MixColumns(state, Nb)
    state = AES.AddRoundKey(state, w, round, Nb)
    print "round "+str(round)+"; ",
    print state
    
state = AES.SubBytes(state, Nb)
state = AES.ShiftRows(state, Nb)
state = AES.AddRoundKey(state, w, Nr, Nb)
print "round 10; ",
print state

print "output; ",
print state
