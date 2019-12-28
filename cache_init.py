#!/usr/bin/env python3

import requests
import zipfile
import os
import re
import sys

aws_master_zip = 'https://github.com/terraform-providers/terraform-provider-aws/archive/master.zip'
local_cache_path = sys.argv[1]

def download_file(url, path):
    '''download a filen chunked out for large capability'''
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                if chunk:
                    f.write(chunk)

def unzip_file(zipfile_path, destination):
    '''extract only the markdown files'''
    with zipfile.ZipFile(zipfile_path, 'r') as files:
        for file in files.namelist():
            if file.endswith('.html.markdown'):
                files.extract(file, destination)

def fix_hcl_blocks(file_path):
    '''remove the information table as well as fix hcl code blocks'''
    md = open(file_path, 'r')
    contents = md.read()
    contents = contents.replace('```hcl', '```')
    md.close()
    # why the heck doesn't r+ work above?
    md = open(file_path, 'w')
    md.write(contents)
    md.close()
    
def prep_files(directory):
    '''walk the directory and run a function on each file'''
    for root, _, files in os.walk(directory):
        for file in files:
            fix_hcl_blocks(os.path.join(root, file))

def cleanup_file(filename):
    '''simply delete a file'''
    os.remove(filename)

def main():
    zip_path = local_cache_path + '/awsprovider.zip'
    download_file(aws_master_zip, zip_path)
    unzip_file(zip_path, local_cache_path)
    prep_files(local_cache_path + '/terraform-provider-aws-master')
    cleanup_file(zip_path)

main()