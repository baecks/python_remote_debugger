"""
Python remote debugging support.

"""

bl_info = {
    'name': 'Python Remote Debugger',
    'author': 'Sven Baeck',
    'version': (0, 1),
    'blender': (2, 78, 0),
    'location': 'Press [Space], search for "debugger"',
    'category': 'Development',
}

import os
import sys

folder = os.path.dirname(__file__)
if not folder in sys.path:
    sys.path.append(folder)
for i in sys.path:
    print(i)
    
import bpy.app
import bpy.utils
import os.path
from bpy.types import AddonPreferences
from bpy.props import StringProperty, IntProperty
import socket
import importlib
from subprocess import call
from os.path import expanduser
import shutil
from remote_debugger.debugger import RemoteDebugger
from helpers.reporting import ReportingOperator
from helpers.filesystem import get_addon_folder_name, get_blender_path, get_addon_folder_path

def report(addon_object, tp, msg):
    addon_object.report(tp, msg)
    print (msg)

class PRD_AddonPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__
    home = expanduser("~")

    stub_folder = StringProperty(
        name='Path for the auto-completion stubs',
        description='Folder where the subs will be saved',
        subtype='FILE_PATH',
        default=os.path.abspath(home)
    )
    
    debugger_port = IntProperty(
        name="Remote debugger port number",
        description="TCP port to which the addon will try connecting for remote debugging",
        default=5678, #default value for pydev (eclipse)
        soft_min=1,
        soft_max=65535
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'stub_folder')
        layout.prop(self, 'debugger_port')
        
class PRD_GenerateStubs(ReportingOperator):
    bl_idname = 'debug.generate_stubs'
    bl_label = 'Generate auto-completion stubs'
    bl_description = 'Generate auto-completion stubs for use in an IDE'
        
    def generate_stubs(self, path):
        self.info("Generating the stubs for IDE auto-completion")
        
        blender_path = get_blender_path()
        script_path = os.path.join(get_addon_folder_path(), 'pypredef_gen', 'pypredef_gen.py')      
        
        try:
            call([blender_path, "-b", "-P", script_path, path])
        except Exception as e:
            self.error("Failed to generate IDE auto-completion files to %s (%s)" % (path, str(e)))
            return
        
        self.info("IDE auto-completion files generated in %s" % path)


    def execute(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences

        stub_folder = os.path.abspath(addon_prefs.stub_folder)
        stub_folder = os.path.join(stub_folder, "python_stubs_blender_%s" % bpy.app.version_string.split(" ")[0])
        print (stub_folder)

        if os.path.exists(stub_folder):
            shutil.rmtree(stub_folder)
        os.makedirs(stub_folder)

        self.generate_stubs(stub_folder)

        return {'FINISHED'}     
       
class PRD_Connect_Pydevd(ReportingOperator):
    bl_idname = 'debug.connect_pydevd'
    bl_label = 'Connect to a remote PYDEVD-based debugger'
    bl_description = 'Install the PYDEVD module from PyPI if needed and connect to a remote PYDEVD-based debugger'

    def execute(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences

        port = addon_prefs.debugger_port
        debugger = RemoteDebugger(self, port=port)
        debugger.connect()
        #RemoteDebugger.install_pydevd(self)

        return {'FINISHED'}          
       
def register():
    print('REGISTERING ...')
    bpy.utils.register_class(PRD_AddonPreferences)
    bpy.utils.register_class(PRD_GenerateStubs)
    bpy.utils.register_class(PRD_Connect_Pydevd)
    #bpy.types.TEXT_MT_toolbox.append(addon_button)
    

def unregister():
    bpy.utils.unregister_class(PRD_AddonPreferences)
    bpy.utils.unregister_class(PRD_GenerateStubs)
    bpy.utils.unregister_class(PRD_Connect_Pydevd)
    #bpy.types.TEXT_MT_toolbox.remove(addon_button)

if __name__ == '__main__':
    register()


