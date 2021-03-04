#!/usr/bin/python

import zipfile
import os
from os.path import join

class pushd:
    def __init__(self, new_cwd):
        self.saved_cwd = os.getcwd()
        self.new_cwd = new_cwd

    def __enter__(self):
        os.chdir(self.new_cwd)
    
    def __exit__(self, e, value, traceback):
        os.chdir(self.saved_cwd)

# Creates an archive which contains directory 'directory_path'
def zip_directory(directory_path, zip_path):
    if os.path.exists(zip_path):
        os.remove(zip_path)
    zip_path_abs = os.path.abspath(zip_path)

    parent_path, dir_name = os.path.split(directory_path)
    with pushd(parent_path):
        with zipfile.ZipFile(zip_path_abs, 'x', zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(dir_name):
                for file in files:
                    zip_file.write(os.path.join(root, file))
