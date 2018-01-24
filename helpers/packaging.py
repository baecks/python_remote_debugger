'''
Created on 24 Jan 2018

@author: baecks
'''

import os
import zipfile
import sys

def pack(folder, version_label, output_dir="."):
    name = os.path.basename(folder)
    version = version_label.replace(".", "_")
    filename = os.path.join(output_dir, "%s-%s.zip" % (name,version))
    zp = zipfile.ZipFile(filename, mode='w', compression=zipfile.ZIP_DEFLATED)

    for root, dirs, files in os.walk(folder):  # @UnusedVariable
        for f in files:
            extension = os.path.splitext(f)[1]
            if not extension.lower()==".py":
                continue
            flname = os.path.join(root, f)
            packname = flname[len(folder) + 1:]
            print("Adding file %s as <%s>" % (flname, packname))
            zp.write(flname, arcname=packname)

    zp.close()
    print("\nCreated package %s" % filename)
    
if __name__ == '__main__':
    print(sys.argv)
    if len(sys.argv) < 3:
        pack(sys.argv[1], sys.argv[2])
    else:
        pack(sys.argv[1], sys.argv[2], sys.argv[3])
        