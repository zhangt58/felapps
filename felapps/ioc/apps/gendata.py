#!/usr/bin/env python
# -*- coding:utf-8 -*-

#
# epics and python interface demo
# data manipulation:
# read/write waveform record
#
# Tong Zhang
# 2015-02-05, 21:11
#

import epics
import numpy as np
import matplotlib.pyplot as plt
import time

wfarrname    = 'UN-BI:PROF19:ARR'
wfintname    = 'UN-BI:PROF19:INT'
imgampname   = 'UN-BI:AMP'
laserarrname = 'OPA:PROF:ARR'
laserampname = 'OPA:POWER'
laserw0name  = 'OPA:OMEGA'
ebeamarrname = 'DCLS:EBEAM:PROF:ARR'
ebeamampname = 'DCLS:ENERGY'
ebeamw0name  = 'DCLS:BSIZE'

wfarrpv    = epics.PV(wfarrname)
wfintpv    = epics.PV(wfintname)
imgamppv   = epics.PV(imgampname)
laserarrpv = epics.PV(laserarrname)
laseramppv = epics.PV(laserampname)
laserw0pv  = epics.PV(laserw0name)
ebeamarrpv = epics.PV(ebeamarrname)
ebeamamppv = epics.PV(ebeamampname)
ebeamw0pv  = epics.PV(ebeamw0name)

def gauss2d(x, y, x0, y0, sx, sy):
    return np.exp(-(((x-x0)/float(sx))**2)/2) * np.exp(-(((y-y0)/float(sy))**2)/2)

xx = np.linspace(0, 15, 659)
yy = np.linspace(0, 15, 494)
x, y = np.meshgrid(xx, yy)

xx1 = np.linspace(0, 10, 659) # mm
yy1 = np.linspace(0, 10, 494) # mm
x1, y1 = np.meshgrid(xx1, yy1)

for i in np.arange(100000):
    #### PROF test
    """
    ampArr = np.random.random_integers(2,25,5)
    tmpdata1= ampArr[0]*gauss2d(x, y, 5,  3, 1.0, 2.0) + \
              ampArr[1]*gauss2d(x, y, 9,  6, 1.0, 1.0) + \
              ampArr[2]*gauss2d(x, y, 11, 4, 1.5, 1.5) + \
              ampArr[3]*gauss2d(x, y, 7, 10, 2.0, 2.0) + \
              ampArr[4]*gauss2d(x, y, 6,  7, 0.5, 0.5) + \
              0.5*np.random.random(size = 659*494).reshape(494, 659)
    """
    #ampArr = np.random.random_integers(50,100,1)
    ampArr = imgamppv.get()
    rx, ry = np.random.random()*0.5+0.5, np.random.random()*0.5+0.3
    px, py = np.random.random()*3+1, np.random.random()*2+1
    tmpdata1= ampArr*gauss2d(x, y, px, py, rx, ry) + \
              0.0*np.random.random(size = 659*494).reshape(494, 659)

    arrdata1 = np.array(tmpdata1, dtype = np.int8)
    inputArr1 = arrdata1.flatten()
    wfarrpv.put(inputArr1)
    #wfintpv.put(np.sum(inputArr1))
    
    """
    #### laser test
    amp = laseramppv.get()
    w0  = laserw0pv.get()
    sigx = sigy = w0/1.414*1e3
    tmpdata2 = gauss2d(x1, y1, 6, 6, sigx, sigy) * (np.log(amp)*(np.random.randn()*0.1 + 1))
    arrdata2 = np.array(tmpdata2, dtype = np.int8)
    inputArr2 = arrdata2.flatten()
    laserarrpv.put(inputArr2)
    """

    """
    #### ebeam test
    amp1 = ebeamamppv.get()
    w01  = ebeamw0pv.get()
    sigx1 = sigy1 = w01*1e3
    tmpdata3 = gauss2d(x1, y1, 6, 6, sigx1, sigy1) * (np.log(amp)*(np.random.randn()*0.1 + 1))
    arrdata3 = np.array(tmpdata3, dtype = np.int8)
    inputArr3 = arrdata3.flatten()
    ebeamarrpv.put(inputArr3)
    """

    time.sleep(0.5)

