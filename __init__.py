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

ADDON_FOLDER = "python_remote_debugger"

import bpy.app
import bpy.utils
import os.path
from bpy.types import AddonPreferences
from bpy.props import StringProperty
import socket
import importlib
import sys
from subprocess import call
from os.path import expanduser
import shutil

def install_pip():
    python_path = bpy.app.binary_path_python
    get_pip_script = os.path.join(bpy.utils.user_resource('SCRIPTS', "addons"), ADDON_FOLDER, 'get-pip', 'get-pip.py')
    retval = call([python_path, get_pip_script], stdout=sys.stdout, stderr=sys.stderr)
    return retval==0

def generate_stubs(addon_object, path):
    print ("Generating the stubs for IDE auto-completion")
    blender_path = bpy.app.binary_path
    script_path = os.path.join(bpy.utils.user_resource('SCRIPTS', "addons"), ADDON_FOLDER, 'pypredef_gen')
    script = os.path.join(script_path,'pypredef_gen.py')
    call([blender_path, "-b", "-P", script, path])
    
    addon_object.report({'INFO'}, "IDE auto-completion files generated in %s" % (os.path.join(script_path, 'pypredef_gen')))

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

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'stub_folder')
        
class PRD_GenerateStubs(bpy.types.Operator):
    bl_idname = 'debug.generate_stubs'
    bl_label = 'Generate auto-completion stubs'
    bl_description = 'Generate auto-completion stubs for use in an IDE'

    def execute(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences

        stub_folder = os.path.abspath(addon_prefs.stub_folder)
        stub_folder = os.path.join(stub_folder, "python_stubs_blender_%s" % bpy.app.version_string.split(" ")[0])
        print (stub_folder)

        if os.path.exists(stub_folder):
            shutil.rmtree(stub_folder)
        os.makedirs(stub_folder)

        generate_stubs(self, stub_folder)

        return {'FINISHED'}     
       
def register():
    print('REGISTERING ...')
    bpy.utils.register_class(PRD_AddonPreferences)
    bpy.utils.register_class(PRD_GenerateStubs)
    #bpy.types.TEXT_MT_toolbox.append(addon_button)
    

def unregister():
    bpy.utils.unregister_class(PRD_AddonPreferences)
    bpy.utils.unregister_class(PRD_GenerateStubs)
    #bpy.types.TEXT_MT_toolbox.remove(addon_button)

if __name__ == '__main__':
    register()


