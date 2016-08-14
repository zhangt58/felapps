#!/bin/bash

#
# update launchers
# 
# Created: 2015-10-08
# Author : Tong Zhang
#
# deprecated: use update-felapps-menu instead

for launcher in *.desktop
do
    cp -arv $launcher /usr/share/applications/
done
