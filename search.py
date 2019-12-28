#!/usr/bin/env python3

import os
from markdown_code_blocks import highlight
from subprocess import Popen, DEVNULL
from rofi import Rofi
import sys

r = Rofi()

browser = 'firefox'
tmpfolder = '/tmp'

docs_dir     = tmpfolder + '/terraform-provider-aws-master/website/docs'
data_dir     = docs_dir + '/d'
resource_dir = docs_dir + '/r'

def verify_cache(docdir, tmpfolder):
    '''test to see that the cache exists or not, create cache if needed'''
    if os.path.isdir(docdir):
        return
    else:
        firstrun(tmpfolder)

def firstrun(tmpdir):
    '''run if cache is found not to exist, but be kinda careful of external script run'''
    try:
        print('download, caching, processing markdown')
        retcode = os.system("./cache_init.py " + tmpdir)
        if retcode < 0:
            print("Child was terminated by signal", -retcode, file=sys.stderr)
        else:
            print("Child returned", retcode, file=sys.stderr)
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)

def process_file(path):
    '''pull out some pertinent data from the OG markdown file and stow them'''
    file_obj = {}
    file = open(path)
    file_obj['contents'] = file.readlines()
    file_obj['page_title'] = file_obj['contents'][3].split('AWS: ')[1][0:-2].replace('aws_','')
    file_obj['page_desc'] = file_obj['contents'][5].lstrip()
    return file_obj

def dump_contents(path):
    '''simply grab the contents of a file as a string and return them'''
    file = open(path)
    return file.read()

def sweep_directory(scan_path):
    '''generate the rofi list by scanning for all markdown files and sending them through processing'''
    rofi_table = []
    for filename in os.listdir(scan_path):
        if '.html.markdown' in filename:
            process_results = process_file(scan_path + '/' + filename)
            rofi_table.append({'title': process_results['page_title'], 'description': process_results['page_desc'], 'raw': dump_contents(scan_path + '/' + filename)})    
    return(rofi_table)

def generate_rofi_menu(list_of_dicts):
    '''generate the strings by sticking title and description together'''
    rofi_list = []
    for entry in list_of_dicts:
        rofi_list.append(entry['title'] + ' - ' + entry['description'])
    index, _ = r.select('Terraform search?', rofi_list, rofi_args=['-matching regex'])
    return index

def add_style(css_path, body):
    '''inject the css into the resultant html file'''
    style_file = open('./dark.css')
    style_css = '<style>' + style_file.read() + '</style>'
    return style_css + html_body


verify_cache(docs_dir, tmpfolder)
aws_data_table = sweep_directory(data_dir)
aws_resource_table = sweep_directory(resource_dir)
combined_list = aws_resource_table + aws_data_table
selected_index = generate_rofi_menu(combined_list)
html_body = highlight(combined_list[selected_index]['raw'])
html_complete = add_style('./dark.css', html_body)

f = open(tmpfolder + "/tfap.html", "w")
f.write(html_complete)
f.close()
Popen(['nohup', browser, tmpfolder + '/tfap.html'], stdout=DEVNULL, stderr=DEVNULL)
