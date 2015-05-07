#!/usr/bin/env python
# -*- coding:utf-8 -*-

import epics
import numpy as np
import matplotlib.pyplot as plt

wfarrname = 'DCLS:ARR:PROF19'

wfarrpv = epics.PV(wfarrname)

#arrdata = np.loadtxt('wfdata', dtype=np.int8)
#wfarrpv.put(arrdata)

a = wfarrpv.get().reshape((494, 659))
im = plt.imshow(a, cmap = 'jet', origin = 'lower left', 
        interpolation = 'bicubic')
plt.show()
