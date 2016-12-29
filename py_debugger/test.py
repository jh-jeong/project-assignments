'''
Created on 2014. 7. 30.

@author: biscuit
'''

import my_debugger_HW

dbg = my_debugger_HW.debugger()

pid = raw_input("Enter the PID of the process to attach to: ")
dbg.attach(int(pid))
dbg.run()
dbg.detach()


t_list = dbg.enumerate_threads()

for thread in t_list:
    thread_context = dbg.get_thread_context(thread)
    
    print "[*] Dumping Registers for Thread ID: 0x%08x" % thread
    print "[**] EIP: 0x%08x" % thread_context.Eip
    print "[**] ESP: 0x%08x" % thread_context.Esp
    print "[**] EBP: 0x%08x" % thread_context.Ebp
    print "[**] EAX: 0x%08x" % thread_context.Eax
    print "[**] EBX: 0x%08x" % thread_context.Ebx
    print "[**] ECX: 0x%08x" % thread_context.Ecx
    print "[**] EDX: 0x%08x" % thread_context.Edx
    print "[*] END DUMP"

dbg.detach()
