#!/bin/bash

px="16 20 22 24 32 40 48 72 96 128 192 256 512"
for ipx in ${px}
do
    [ -e ${ipx} ] || mkdir ${ipx}
    for appname in {"imageviewer","cornalyzer","felformula","dataworkshop","matchwizard","appdrawer"}
    do
        convert -resize ${ipx}x${ipx} ./original/${appname}.png .tmp.png
        mv .tmp.png ${ipx}/${appname}.png
        echo "Generate icon with ${ipx}x${ipx} for ${appname}"
    done
done
    
