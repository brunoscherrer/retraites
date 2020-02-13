# -*- coding: utf-8 -*-
"""
Find Ipython Notebook files in the directory, and subdirectories.
"""

import os

def findIpythonNotebookfiles(dirname, maximumNumberOfFiles = 100):
    '''
    Cherche la liste des fichiers .ipynb dans le répertoire courant. 
    '''
    print("+ Searching in ", dirname, "...")
    nbfiles=0
    for dirpath,dirnames,filenames in os.walk(dirname):
        for shortfilename in filenames:
            filename, fileExtension = os.path.splitext(shortfilename)
            if ((fileExtension==".ipynb") and \
              (not ".ipynb_checkpoints" in dirpath)):
                fullfile = os.path.join(dirpath, shortfilename)
                print("(%d) %-40s" % (nbfiles, fullfile))
                nbfiles = nbfiles + 1
                executeIpythonNotebook(fullfile)
                if (nbfiles > maximumNumberOfFiles):
                    break
    print("Number of empty files:", nbfiles)
    return None

def executeIpythonNotebook(ipythonNBFile):
    """
    Execute the given notebook file. 
    This function fails if the execution fails.
    Generates a temporary script which is deleted afterwards. 
    """
    print("+ Testing ", ipythonNBFile)
    dirname = os.path.dirname(ipythonNBFile)
    # 1. Got into the directory
    cwd = os.getcwd()
    os.chdir(dirname)
    basename = os.path.basename(ipythonNBFile)
    # 2. Execute the notebook
    command = "jupyter nbconvert --to notebook --execute "
    command += basename
    print(command)
    returncode = os.system(command)
    if (returncode != 0):
        raise ValueError('Wrong return code = %s' % (returncode))
    print("OK")
    # 3. Delete the temporary generated NB file
    filename, fileExtension = os.path.splitext(basename)
    convertNBFile = filename + ".nbconvert" + fileExtension
    print("Delete ", convertNBFile)
    os.remove(convertNBFile)
    # 4. Go back where we come from
    os.chdir(cwd)
    return None

if (__name__=="__main__"):
    dirname = "."
    print("CWD = ", os.getcwd())
    os.chdir(dirname)
    findIpythonNotebookfiles(dirname)
