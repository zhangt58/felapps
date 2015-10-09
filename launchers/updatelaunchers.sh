#!/bin/bash

#
# update launchers
# 
# Created: 2015-10-08
# Author : Tong Zhang
#

for launcher in *.desktop
do
    sudo cp -arv $launcher /usr/share/applications/
done
