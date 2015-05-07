#!/bin/bash
respyname="resutils.py"
img2py    -n dclslayouticon   DCLSlayout.png ${respyname}
img2py -a -n matchlayouticon matchlayout.png ${respyname}
img2py -a -n moddslayouticon moddslayout.png ${respyname}
img2py -a -n radislayouticon radislayout.png ${respyname}
img2py -a -n moddsicon     modulationBox.png ${respyname}
img2py -a -n radisicon      radiationBox.png ${respyname}
img2py -a -n matchicon       matchingBox.png ${respyname}
img2py -a -n mainlogoicon           logo.jpg ${respyname}
img2py -a -n moddslogoicon     moddslogo.png ${respyname}
img2py -a -n matchlogoicon     matchlogo.png ${respyname}
img2py -a -n radislogoicon     radislogo.png ${respyname}
img2py -a -n addicon                 add.png ${respyname}
img2py -a -n delicon              remove.png ${respyname}
mv ${respyname} ../utils
