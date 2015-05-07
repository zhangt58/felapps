#!/usr/bin/env python2

#
# test image reading
# Tong Zhang
# 2015-02-09
#

import epics
import time
import numpy as np

pvname = 'DCLS:ARR:PROF19'
#pvname = 'DCLS:INT:PROF19'
mypv=epics.PV(pvname, auto_monitor = True)
time.sleep(1)

# within pv callback, cannot do other caget or caput action!
def onChanges(pvname = None, value = None, **kws):
    print "Intensity on %s is %.3f" % (pvname, np.sum(mypv.get()))

mypv.add_callback(onChanges)
while True:
    time.sleep(1)
