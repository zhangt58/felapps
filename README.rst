FEL Apps (felapps) Python project
=================================

High-level application suite for free-electron laser, developed by Python

Author: Tong Zhang (zhangtong AT sinap dot ac dot cn)

first uploaded to github on Apr. 23, 2015

USAGE example:

create python script file (test.py) like:

#!/usr/bin/env python

import sys

sys.path.append('./felapps-1.0.1-py2.7.egg')

#sys.path.append('./felapps-1.0.1-py2.py3-none-any.whl')

import felapps

felapps.imageviewer.run(maximize = True,logon = False)

#felapps.formula.run()

or install by pip install felapps

then import felapps

and run test.py by python test.py.

