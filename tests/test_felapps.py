#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# test script for felapps package
# Tong Zhang, 2015-10-03
#

import felapps
import sys

def testApp(appname=None):
    if appname == 'imageviewer':
        felapps.imageviewer.run(maximize=True, logon=False, debug=True)
    elif appname == 'felformula':
        felapps.felformula.run(maximize=True, logon=True, debug=False)
    elif appname == 'cornalyzer':
        felapps.cornalyzer.run(maximize=True, logon=False, debug=True)
    elif appname == 'dataworkshop':
        felapps.dataworkshop.run(maximize=True, logon=True, debug=True)
    elif appname == 'matchwizard':
        felapps.matchwizard.run(maximize=True, logon=False, debug=True)
    elif appname == 'wxmpv':
        felapps.wxmpv.run(debug=True)
    else: # if app name was not given, show the main launcher panel
        felapps.appdrawer.run(maximize=True, logon=False, 
                debug=False, icon_set='short')

def test_argv():
    appname = sys.argv[1:]
    if appname == []:
        testApp()
    else:
        for app in appname:
            testApp(app)

def test(app):
    testApp(app)

if __name__ == '__main__':
    test_argv()
    #app = 'imageviewer'
    #test(app)

