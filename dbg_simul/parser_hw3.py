'''
Created on 2014. 8. 2.

@author: biscuit

bob_114
'''

import simulator

simul = simulator.simulator()

path = raw_input("path: ")
simul.load(path)

while simul.process():
    pass



