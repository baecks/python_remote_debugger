'''
Created on 23 Jan 2018

@author: baecks
'''

import socket
import sys
import importlib
import os
from subprocess import call
from helpers.filesystem import get_addon_folder_path, get_blender_path

class RemoteDebugger(object):
    '''
    classdocs
    '''
    DEFAULT_PYDEV_REMOTE_DEBUG_PORT = 5678
    DEFAULT_PYDEV_REMOTE_DEBUG_HOST = 'localhost'
    PYDEV_VERSION = "1.1.1"

    @staticmethod
    def install_pip():
        python_path = get_blender_path()
        get_pip_script = os.path.join(get_addon_folder_path(), 'get-pip', 'get-pip.py')
        retval = call([python_path, get_pip_script], stdout=sys.stdout, stderr=sys.stderr)
        return retval==0

    @staticmethod
    def install_pydevd(addon_object):
        try:
            import pydevd  # @UnresolvedImport @UnusedImport
            addon_object.info("PYDEVD is already installed!")
            return
        except:
            # not installed
            addon_object.info("PYDEVD not installed!")
            pass
        
        # First install PIP if needed
        addon_object.info("Installing PIP")
        if not RemoteDebugger.install_pip():
            addon_object.error("Failed to install PIP!")
            return False
        
        # install PYDEVD through PIP
        import pip
        addon_object.info("Installing PYDEVD version %s" % RemoteDebugger.PYDEV_VERSION)
        try:
            pip.main(["install", "pydevd==%s" % RemoteDebugger.PYDEV_VERSION])
        except:
            addon_object.error("Failed installing PYDEVD!")
            return False
        
        addon_object.info("Successfully installed PYDEVD!")
        return True


    def __init__(self, addon_object, host=DEFAULT_PYDEV_REMOTE_DEBUG_HOST, port=DEFAULT_PYDEV_REMOTE_DEBUG_PORT):
        '''
        Constructor
        '''
        self.addon_object = addon_object
        self.port = port
        self.host = host
        
        
    def _is_remote_debugger_listening(self):
        '''
        This function checks if a TCP server is listening on host:port.
        '''
        s = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
    
        try:
            s.settimeout(0.01)
            s.connect((self.host, self.port))
            s.close()
        except Exception as e:
            self.addon_object.info("No remote debugger listening on %s:%d (%s)" % (self.host, self.port, str(e)) )
            return False
        
        self.addon_object.info("Remote debugger listening on port %s:%d" % (self.host, self.port) )
        return True
    
    def connect(self):
        if not self._is_remote_debugger_listening():
            self.addon_object.error("No remote debugger found on %s:%d" % (self.host, self.port) )
            return
        
        # load/reload the pydevd module
        try:
            mod = sys.modules['pydevd']
            global pydevd  # @UnusedVariable
            pydevd = importlib.reload(mod)  # @UnusedVariable
            self.addon_object.info("Reloaded PYDEVD module")
        except:
            try:
                import pydevd  # @UnresolvedImport @UnusedImport
                self.addon_object.info("Imported PYDEVD module")
            except:
                # If this fails, PYDEVD is not installed
                if RemoteDebugger.install_pydevd(self):
                    self.addon_object.info("Installed PYDEVD module. Importing module ...")
                    import pydevd  # @UnresolvedImport @Reimport
                    self.addon_object.info("Imported PYDEVD module")
                else:
                    self.addon_object.error("Failed installing PYDEVD for remote debugging")
                    return
                
        try:
            self.addon_object.info("PYDEVD Tracing ...")
            pydevd.settrace(self.host, port=self.port, 
                            stdoutToServer=True, stderrToServer=True,
                            suspend=False)
        except Exception as e:
            self.addon_object.error("Failed connecting to the remote debugger on %s:%d (%s)" % (self.host, self.port, str(e)))
            return
        
        self.addon_object.info("Connected to the remote debugger on %s:%d" % (self.host, self.port))
