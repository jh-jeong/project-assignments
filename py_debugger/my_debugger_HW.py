'''
Created on 2014. 7. 30.

@author: biscuit
'''

from ctypes import *
from my_debugger_defines import *

kernel32=windll.kernel32

class debugger():
    def __init__(self):  #initial constructor
        self.h_process = None # Process Handler
        self.pid = None # PID
        self.debugger_active = False #is_active
        self.h_thread = None
        self.context = None
        self.breakpoints = {}
        self.first_breakpoint = True
        self.hardware_breakpoints = True
        self.exception = None
        self.exception_address = None

        
    def load(self,path_to_exe):
        
        #dwCreationFlags setting
        creation_flags = DEBUG_PROCESS
        
        startupinfo = STARTUPINFO()
        process_information = PROCESS_INFORMATION()
        
        startupinfo.dwflags = 0x1
        startupinfo.wShowWindow = 0x0
        startupinfo.cb = sizeof(startupinfo)
        
        # Create Process & Error Handling
        if kernel32.CreateProcessA(path_to_exe,
                                   None,
                                   None,
                                   None,
                                   None,
                                   creation_flags,
                                   None,
                                   None,
                                   byref(startupinfo),
                                   byref(process_information)):
            print "[*] We have successfully launched the process!"
            print "[*] PID: %d" % process_information.dwProcessId
            
            #====================================================
            # get process handler (for temporal)
            self.h_process = self.open_process(process_information.dwProcessId)
            
            
        else:
            print "[*] Error 0x%08x." % kernel32.GetLastError()
            
            
    def open_process(self, pid):
        self.h_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
        return self.h_process
    
    def open_thread (self, thread_id):
        h_thread = kernel32.OpenThread(THREAD_ALL_ACCESS, None, thread_id)
        
        if h_thread is not None:
            return h_thread
        else:
            print "[*] Could not obtain a valid thread handle."
            return False
    
    def enumerate_threads(self): #extract threads in current PID...
        thread_entry = THREADENTRY32() #create new thread entry
        thread_list = []
        snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, self.pid)
        
        if snapshot is not None:
            thread_entry.dwSize= sizeof(thread_entry)
            success = kernel32.Thread32First(snapshot, byref(thread_entry))
            # Take first element of Thread-list
            
            while success: #generates threads which are included is process PID
                if thread_entry.th32OwnerProcessID == self.pid:
                    thread_list.append(thread_entry.th32ThreadID)
                success = kernel32.Thread32Next(snapshot,byref(thread_entry))
                   
            kernel32.CloseHandle(snapshot)
            return thread_list
        else:
            return False
    
    def get_thread_context(self, thread_id=None, h_thread=None):
        context = CONTEXT();
        context.ContextFlags = CONTEXT_FULL | CONTEXT_DEBUG_REGISTERS 
        #Setting the Flag
        
        if not h_thread:
            h_thread = self.open_thread(thread_id)  
        #identify thread first, get a handle of the thread
        
        if kernel32.GetThreadContext(h_thread, byref(context)):
            kernel32.CloseHandle(h_thread)
            return context
        else:
            return False  
    
    def attach(self,pid):
        self.h_process = self.open_process(pid)
        
        # Try to attach
        if kernel32.DebugActiveProcess(pid):
            self.debugger_active = True
            self.pid = int(pid)
        else:
            print "[*] Unable to attach to the process."
            print "[*] Error 0x%08x." % kernel32.GetLastError()
        
    def detach(self):
        if kernel32.DebugActiveProcessStop(self.pid):
            print "[*] Finished debugging. Exiting..."
            return True
        else:
            print "There was an error"
            print "[*] Error 0x%08x." % kernel32.GetLastError()
            return False  
        
    def run(self):
        while self.debugger_active == True:
            self.get_debug_event()
        
    def get_debug_event(self):
        
        if self.exception == EXCEPTION_ACCESS_VIOLATION:
            print "Access Violation Detected."
        elif self.exception == EXCEPTION_BREAKPOINT:
            continue_status = self.exception_handler_breakpoint()
        elif self.exception == EXCEPTION_GUARD_PAGE:
            print "Guard Page Access Detected."
        elif self.exception == EXCEPTION_SINGLE_STEP:
            self.exception_handler_single_step()
    
        debug_event = DEBUG_EVENT()  # Make a new DEBUG_EVENT structure
        continue_status = DBG_CONTINUE
        
        if kernel32.WaitForDebugEvent(byref(debug_event),INFINITE):
            # Let's obtain the thread 
            self.h_thread = self.open_thread(debug_event.dwThreadId)
          
            self.context = self.get_thread_context(self.h_thread)
           
            print "Event Code: %d Thread ID: %d" %(debug_event.dwDebugEventCode, debug_event.dwThreadId)
        
            # If the event code is an exception, we want to
            # examine it further.
            if debug_event.dwDebugEventCode == EXCEPTION_DEBUG_EVENT:
                
                # Obtain the exception code
                exception = debug_event.u.Exception.ExceptionRecord.ExceptionCode
                self.exception_address = debug_event.u.Exception.ExceptionRecord.ExceptionAddress
                
                if exception == EXCEPTION_ACCESS_VIOLATION:
                    print "Access Violation Detected"
                    
                    # If a breakpoint is detected, we call an internal
                    # handler
                elif exception == EXCEPTION_BREAKPOINT:
                    continue_status = self.exception_handler_breakpoint()
                    
                elif exception == EXCEPTION_GUARD_PAGE:
                    print "Guard Page Access Detected."
                    
                elif exception == EXCEPTION_SINGLE_STEP:
                    print "Single Stepping."
                
            kernel32.ContinueDebugEvent( debug_event.dwProcessId, debug_event.dwThreadId, continue_status)
            
            ## HANDLER is needed
            #raw_input("Press a key to continue...")
            #self.debugger_active = False
            
            print "Event Code: %d Thread ID: %d" %(debug_event.dwDebugEventCode, debug_event.dwThreadId)
            
            kernel32.ContinueDebugEvent( \
                                         debug_event.dwProcessId, \
                                         debug_event.dwThreadId, \
                                         continue_status)
            
    def exception_handler_breakpoint(self):
        
        print "[*] Inside the breakpoint handler."
        print "Exception Address: 0x%08x" % self.exception_address 

        return DBG_CONTINUE
    
    def bp_set_hw(self, address, length, condition):
        
        # Check for a valid length value
        if length not in (1, 2, 4):
            return False
        else:
            length -= 1
            
        # Check for a valid condition
        if condition not in (HW_ACCESS, HW_EXECUTE, HW_WRITE):
            return False
        
        # Check for available slots
        if not self.hardware_breakpoints.has_key(0):
            available = 0
        elif not self.hardware_breakpoints.has_key(1):
            available = 1
        elif not self.hardware_breakpoints.has_key(2):
            available = 2
        elif not self.hardware_breakpoints.has_key(3):
            available = 3
        else:
            return False

        # We want to set the debug register in every thread
        for thread_id in self.enumerate_threads():
            context = self.get_thread_context(thread_id=thread_id)

            # Enable the appropriate flag in the DR7
            # register to set the breakpoint
            context.Dr7 |= 1 << (available * 2)

            # Save the address of the breakpoint in the
            # free register that we found
            if   available == 0: context.Dr0 = address
            elif available == 1: context.Dr1 = address
            elif available == 2: context.Dr2 = address
            elif available == 3: context.Dr3 = address

            # Set the breakpoint condition
            context.Dr7 |= condition << ((available * 4) + 16)

            # Set the length
            context.Dr7 |= length << ((available * 4) + 18)

            # Set this threads context with the debug registers
            # set
            h_thread = self.open_thread(thread_id)
            kernel32.SetThreadContext(h_thread,byref(context))

        # update the internal hardware breakpoint array at the used slot index.
        self.hardware_breakpoints[available] = (address,length,condition)

        return True


    def exception_handler_single_step(self):
        print "[*] Exception address: 0x%08x" % self.exception_address
        # Comment from PyDbg:
        # determine if this single step event occured in reaction to a hardware breakpoint and grab the hit breakpoint.
        # according to the Intel docs, we should be able to check for the BS flag in Dr6. but it appears that windows
        # isn't properly propogating that flag down to us.
        if self.context.Dr6 & 0x1 and self.hardware_breakpoints.has_key(0):
            slot = 0

        elif self.context.Dr6 & 0x2 and self.hardware_breakpoints.has_key(1):
            slot = 0
        elif self.context.Dr6 & 0x4 and self.hardware_breakpoints.has_key(2):
            slot = 0
        elif self.context.Dr6 & 0x8 and self.hardware_breakpoints.has_key(3):
            slot = 0
        else:
            # This wasn't an INT1 generated by a hw breakpoint
            continue_status = DBG_EXCEPTION_NOT_HANDLED

        # Now let's remove the breakpoint from the list
        if self.bp_del_hw(slot):
            continue_status = DBG_CONTINUE

        print "[*] Hardware breakpoint removed."
        return continue_status


    def bp_del_hw(self,slot):
        
        # Disable the breakpoint for all active threads
        for thread_id in self.enumerate_threads():

            context = self.get_thread_context(thread_id=thread_id)
            
            # Reset the flags to remove the breakpoint
            context.Dr7 &= ~(1 << (slot * 2))

            # Zero out the address
            if   slot == 0: 
                context.Dr0 = 0x00000000
            elif slot == 1: 
                context.Dr1 = 0x00000000
            elif slot == 2: 
                context.Dr2 = 0x00000000
            elif slot == 3: 
                context.Dr3 = 0x00000000

            # Remove the condition flag
            context.Dr7 &= ~(3 << ((slot * 4) + 16))

            # Remove the length flag
            context.Dr7 &= ~(3 << ((slot * 4) + 18))

            # Reset the thread's context with the breakpoint removed
            h_thread = self.open_thread(thread_id)
            kernel32.SetThreadContext(h_thread,byref(context))
            
        # remove the breakpoint from the internal list.
        del self.hardware_breakpoints[slot]

        return True