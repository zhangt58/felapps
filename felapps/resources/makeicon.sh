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

# make image resources for appdrawer app
img2py -a -n iicon ../../launchers/icons/128/imageviewer.png  ${respyname}
img2py -a -n cicon ../../launchers/icons/128/cornalyzer.png   ${respyname}
img2py -a -n ficon ../../launchers/icons/128/felformula.png   ${respyname}
img2py -a -n dicon ../../launchers/icons/128/dataworkshop.png ${respyname}
img2py -a -n micon ../../launchers/icons/128/matchwizard.png  ${respyname}

mv ${respyname} ../utils
