'''
Created on 2014. 8. 1.

@author: biscuit

bob_114
'''

class simulator():
   
    reg = {"%eax":0,
          "%ebx":0, 
          "%ecx":0, 
          "%edx":0, 
          "%esi":0, 
          "%edi":0, 
          "%esp":0, 
          "%ebp":0 
          } 
    stack = []

    def __init__(self):
        self.file = []
        self.inst = []
        self.cur_inst = None
        self.cur_line = 0
        
    def load(self,path):
        with open(path,"r") as f:
            self.file = f.readlines()
        self.inst = self.split_all()
    
    def print_instructions(self):
        print self.file
        
    def split_all(self):
        ins_h = []
        for line in self.file:
            ins_l = []
            for i in line.split("\t"):
                for j in i.split(","):
                    for k in j.split("\n"):
                        for l in k.split():
                            ins_l.append(l)
            ins_h.append(ins_l)
        return ins_h
    
    def process(self):
        if len(self.inst) > self.cur_line :
            self.cur_inst = self.inst[self.cur_line]
            print str(self.cur_line+1)+": ",
            print self.file[self.cur_line],
            self.operation(self.cur_inst)
            print self.reg
            print ""
            self.cur_line += 1
            return True
        else :
            return False
    
    def operation(self,ins):
        if ins[0] == "mov":
            self.mov(ins[1], ins[2])
        elif ins[0] == "push":
            self.push(ins[1])
        elif ins[0] == "pop":
            self.pop(ins[1])
        elif ins[0] == "xor":
            self.xor(ins[1], ins[2])
        elif ins[0] == "sub":
            self.sub(ins[1], ins[2])
        elif ins[0] == "add":
            self.add(ins[1], ins[2])
        elif ins[0] == "nop":
            self.nop()
        else :
            return False
    
    def mov(self, source, dest):
        if source[0] == "$":
            self.reg[dest] = int(source[1:],0)
        elif source[0] == "%":
            self.reg[dest] = self.reg[source]
        else : return False
        
    def push(self,element):
        if element[0] == "$":
            self.stack.append(int(element[1:],0))
        elif element[0] == "%":
            self.stack.append(self.reg[element])
        else : return False
        self.reg["%esp"] -= 4
         
    def pop(self,dest):
        self.reg[dest] = self.stack.pop()
        self.reg["%esp"] += 4
    
    def xor(self, source, dest):
        if source[0] == "$":
            self.reg[dest] ^= int(source[1:],0)
        elif source[0] == "%":
            self.reg[dest] ^= self.reg[source]
        else : return False
        
    def sub(self, source, dest):
        if source[0] == "$":
            self.reg[dest] -= int(source[1:],0)
        elif source[0] == "%":
            self.reg[dest] -= self.reg[source]
        else : return False
    
    def add(self, source, dest):
        if source[0] == "$":
            self.reg[dest] += int(source[1:],0)
        elif source[0] == "%":
            self.reg[dest] += self.reg[source]
        else : return False
        
    def nop(self):
        pass
    
    def ret(self):
        pass
    
'''    
class STACK():
    def __init__(self):
        self.stack_list = []
        
    def push(self, elem):
        self.stack_list.append(elem)
        self.reg.esp -= 4

    def pop(self, dest):
        self.reg[dest] = self.stack_list.pop()
        self.reg.esp += 4
            
class REGISTERS():
    
    select = {"%eax":0,
              "%ebx":0, 
              "%ecx":0, 
              "%edx":0, 
              "%esi":0, 
              "%edi":0, 
              "%esp":0, 
              "%ebp":0 
              }
    
    def __init__(self):
        pass
        
    def __str__(self):
        return self.select.__str__()
'''
