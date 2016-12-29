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
        self.hardware_breakpoints = {}
        self.guarded_page = []
        self.memory_breakpoint = {}
        self.exception = None
        self.exception_address = None
        
        system_info = SYSTEM_INFO()
        kernel32.GetSystemInfo(byref(system_info))
        self.page_size = system_info.dwPageSize
        
    def bp_set_mem(self, address, size):
        mbi = MEMORY_BASIC_INFORMATION()
        
        
        if kernel32.VirturalQueryEx(self.h_process, address, byref(mbi) < sizeof(mbi)):
            return False
        current_page = mbi.BaseAddress
      
        while current_page <= address + size:
            
           
            self.guarded_pages.append(current_page)
            
            old_protection = c_ulong(0)
            if not kernel32.VirtualProtectEx(self.h_process, current_page, size, mbi.Protect | PAGE_GUARD, byref(old_protection)):
                return False
          
            current_page += self.page_size
            
            self.memory_breakpoints[address] = (address, size, mbi)
            
            return True
        
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