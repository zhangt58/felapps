#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# This script is used to update the app version numbers when commit to git
# usage:
#  1 modify the version numer in file: versionlist
#  2 run this script by 'python updateVersion.py'
#  3 if given other versionlist file, please tell the script the filename
#    as the external parameter by 'python updateVersion.py versionfilename'
#
# Tong Zhang
# 2015-05-28
#

import sys
import subprocess

try:
    filename = sys.argv[1]
except:
    filename = 'versionlist'

versiondict = {}
with open(filename) as f:
    for line in f:
        k, v = line.strip().split()
        versiondict[k] = v

for k in versiondict.keys():
    cmd1 = 'sed -i ' + '"' + 's/\(' + "'" + k + "'" + ' *\:\)\(.*\)/\\1' + " '" + versiondict[k] + "\'," + '/"' + ' felapps/utils/miscutils.py'
    subprocess.call(cmd1, shell=True)
