'''
Created on 23 Jan 2018

@author: baecks
'''

ADDON_FOLDER = ''
import os
import bpy.utils
import bpy.app

def get_addon_folder_path():
    script_file = os.path.realpath(__file__)
    addon_folder = os.path.abspath(bpy.utils.user_resource("SCRIPTS", "addons"))
    
    if script_file.find(addon_folder) != 0:
        return None # Strange, should not happen
    
    i = script_file.find(os.sep, len(addon_folder)+1)
    
    return script_file[:i]

def get_addon_folder_name():
    path = get_addon_folder_path()
    print ("get_addon_folder_name returned %s" % path)
    return path.split(os.sep)[-1]

def get_blender_path():
    return bpy.app.binary_path