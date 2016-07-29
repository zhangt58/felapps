#!/bin/bash

# update: 2016-07-28 14:23:44 PM CST

#category="short"
category="long"

[ -e ${category} ] || mkdir ${category}

px="16 20 22 24 32 40 48 72 96 128 192 256 512 1024"
for ipx in ${px}
do
    [ -e ${category}/${ipx} ] || mkdir ${category}/${ipx}
    #for appname in {"imageviewer","cornalyzer","felformula","dataworkshop","matchwizard","appdrawer","latticeviewer","wxmpv"}
    for appname in {"imageviewer","cornalyzer","felformula","dataworkshop","appdrawer","latticeviewer","wxmpv"}
    do
        convert -resize ${ipx}x${ipx} ./original/${category}/${appname}.png .tmp.png
        mv .tmp.png ${category}/${ipx}/${appname}.png
        echo "Generate icon with ${ipx}x${ipx} for ${appname}"
    done
done
    
