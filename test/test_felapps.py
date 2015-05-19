#!/usr/bin/env python

import sys
#sys.path.append('../dist/felapps-1.0.0-py2.7.egg')
sys.path.append('../dist/felapps-1.2.0-py2.py3-none-any.whl')

import felapps
felapps.imageviewer.run(maximize = True,logon = False)
#felapps.formula.run()
