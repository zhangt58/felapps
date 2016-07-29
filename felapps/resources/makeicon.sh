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
img2py -a -n popicon               popup.png ${respyname}
img2py -a -n incrfsicon  increase_font16.png ${respyname}
img2py -a -n decrfsicon  decrease_font16.png ${respyname}

# make image resources for appdrawer app
#img2py -a -n micon_s ../../launchers/icons/short/128/matchwizard.png   ${respyname}
img2py -a -n iicon_s ../../launchers/icons/short/128/imageviewer.png   ${respyname}
img2py -a -n cicon_s ../../launchers/icons/short/128/cornalyzer.png    ${respyname}
img2py -a -n ficon_s ../../launchers/icons/short/128/felformula.png    ${respyname}
img2py -a -n dicon_s ../../launchers/icons/short/128/dataworkshop.png  ${respyname}
img2py -a -n licon_s ../../launchers/icons/short/128/latticeviewer.png ${respyname}
img2py -a -n wicon_s ../../launchers/icons/short/128/wxmpv.png         ${respyname}

#img2py -a -n micon_l ../../launchers/icons/long/512/matchwizard.png   ${respyname}
img2py -a -n iicon_l ../../launchers/icons/long/512/imageviewer.png   ${respyname}
img2py -a -n cicon_l ../../launchers/icons/long/512/cornalyzer.png    ${respyname}
img2py -a -n ficon_l ../../launchers/icons/long/512/felformula.png    ${respyname}
img2py -a -n dicon_l ../../launchers/icons/long/512/dataworkshop.png  ${respyname}
img2py -a -n licon_l ../../launchers/icons/long/512/latticeviewer.png ${respyname}
img2py -a -n wicon_l ../../launchers/icons/long/512/wxmpv.png         ${respyname}

mv ${respyname} ../utils
