#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------#

"""
Author: Tong Zhang
Created Time: 11:09, Jan. 29, 2015

utilities/functions for convenience
"""

#-------------------------------------------------------------------------#

from __future__ import division

import wx
import numpy as np
import os
import matplotlib.colors as colors

from . import EnhancedStatusBar as ESB

#-------------------------------------------------------------------------#

def rescaleImage(image0, scaledFac):
    """
    Jan. 28, 2105
    rescale image, given the image full path on disk
    """

    #originalImage = wx.Image(imagePath, type = wx.BITMAP_TYPE_ANY)
    originalImage = image0
    imgW, imgH = originalImage.GetSize()
    scaledImage = originalImage.Scale(imgW*scaledFac, imgH*scaledFac)

    return scaledImage

#-------------------------------------------------------------------------#

def createwxStaticText(parent, label, style = wx.ALIGN_LEFT, 
        fontname=wx.SYS_SYSTEM_FONT, 
        fontsize=12,
        fontweight=wx.FONTWEIGHT_NORMAL,
        fontcolor='black'):
    font = wx.SystemSettings_GetFont(fontname)
    font.SetPointSize(fontsize)
    font.SetWeight(fontweight)
    st = wx.StaticText(parent = parent, 
            label = label, style = style)
    st.SetFont(font)
    st.SetForegroundColour(fontcolor)
    return st

def createwxButton(parent, label,
        fontname=wx.SYS_SYSTEM_FONT, 
        fontsize=10,
        fontweight=wx.FONTWEIGHT_NORMAL,
        fontcolor='black'):
    font = wx.SystemSettings_GetFont(fontname)
    font.SetPointSize(fontsize)
    font.SetWeight(fontweight)
    btn = wx.Button(parent = parent, 
            label = label)
    btn.SetFont(font)
    btn.SetForegroundColour(fontcolor)
    return btn

def createwxPanel(parent, backgroundcolor = None):
    if backgroundcolor == None:
        backgroundcolor = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE).Get()
    panel = wx.Panel(parent)
    panel.SetBackgroundColour(backgroundcolor)
    return panel

#-------------------------------------------------------------------------#

def aupmu(gap, xlamd, a = 3.44, b = -5.00, c = 1.54):
    """
    gap, xlamd: [mm]
    """
    bfield = a*np.exp(b*(gap/xlamd)+c*(gap/xlamd)**2)
    au = 0.934*(xlamd/10)*bfield/np.sqrt(2)

    return au

#-------------------------------------------------------------------------#

def r56chi(gam0, ibfield, imagl = 0.150, idril = 0.285,):
    """
    return r56 of chicane, ibfield: [T]
    """
    c0 = 299792458.0
    m0 = 9.10938188e-31
    e0 = 1.60218e-19
    r56 = (2.0/3.0*imagl + idril)*2*(np.arcsin(imagl*e0*ibfield/np.sqrt(gam0**2-1)/m0/c0))**2

    return r56

#-------------------------------------------------------------------------#

def readfld(filename, ncar = 121):
    fid = open(filename, 'rb')
    data = np.fromfile(fid, 'double').reshape(ncar*ncar, 2)
    realp = data[:,0]
    imagp = data[:,1]
    intp = sum(realp**2 + imagp**2)
    efield = np.array([complex(realp[i], imagp[i]) for i in range(realp.size)]).reshape(ncar, ncar)
    wexy = np.fft.fftshift(np.fft.fft2(efield))
    farfield = abs(wexy)**2

    return intp, farfield

#-------------------------------------------------------------------------#

def getResPath(filename, cwd = '.', resdir = '../resources'):
    """
    return absolute path for resources, e.g. images, data
    :param reshead : the relative path for resources dir
    :param filename: filename for images or data
    """

    resRoot = os.path.join(os.path.abspath(cwd), resdir)
    resPath = os.path.join(resRoot, filename)

    return resPath
    
#-------------------------------------------------------------------------#

def importCheck(moduleName):
    """
    check could import moduleName or not
    """
    try:
        #return map(__import__, moduleName)
        return __import__(moduleName)
    except ImportError:
        dial = wx.MessageDialog(None,
                message = u"Cannot import module named" + u" '" 
                          + moduleName[0] + u"', please try again!",
                caption = u"Module import error",
                style = wx.OK | wx.CANCEL | wx.ICON_ERROR | wx.CENTRE)
        if dial.ShowModal() == wx.ID_OK:
            dial.Destroy()

#-------------------------------------------------------------------------#

def hex2rgb(hex_string):
    """
    convert hexadecimal color into rgb form.
    """
    rgb = colors.hex2color(hex_string)
    return tuple([int(255*x) for x in rgb])

#-------------------------------------------------------------------------#

def rgb2hex(rgb_tuple):
    """
    convert color rgb into hex form.
    """
    return colors.rgb2hex([1.0*x/255 for x in rgb_tuple])

#-------------------------------------------------------------------------#

def setPath(pathstr):
    return os.path.expanduser(os.path.sep.join(pathstr.replace('\\',' ').replace('/',' ').split(' ')))

#-------------------------------------------------------------------------#

def getFilename(parent):
    dial = wx.FileDialog(parent, message = "Please select the configuration file",
            defaultDir=".", defaultFile="", wildcard = "XML files (*.xml)|*.xml", style = wx.FD_DEFAULT_STYLE | wx.FD_FILE_MUST_EXIST)
    if dial.ShowModal() == wx.ID_OK:
        fullfilename = os.path.join(dial.GetDirectory(),dial.GetFilename())
    dial.Destroy()
    return fullfilename

#-------------------------------------------------------------------------#

class SaveData(object):
    def __init__(self, data, fname, type):
        """
        type: asc, hdf5, sdds
        """
        self.data  = data
        self.fname = fname
        if type == ".asc":
            self.onSaveASC()
        elif type == '.hdf5':
            self.onSaveHDF5()
        elif type == '.sdds':
            self.onSaveSDDS()

    def onSaveASC(self):
        np.savetxt(self.fname, self.data, fmt='%.16e', delimiter=' ')

    def onSaveHDF5(self):
        import h5py
        f = h5py.File(self.fname,'w')
        dset = f.create_dataset('image/data', shape=self.data.shape, dtype=self.data.dtype)
        dset[...] = self.data

    def onSaveSDDS(self):
        print 'save sdds format to be implemented.'
        
#-------------------------------------------------------------------------#

def func_sinc(x, y):
    r = np.sqrt(x**2 + y**2)
    return np.sin(r)/r

def func_peaks(x, y):
    return 3*(1-x)**2*np.exp(-(x**2) - (y+1)**2) - 10*(x/5 - x**3 - y**5)*np.exp(-x**2-y**2) - 1/3*np.exp(-(x+1)**2 - y**2)

#-------------------------------------------------------------------------#

class FloatSlider(wx.Slider):

    def __init__(self, parent, id = wx.ID_ANY, value = 0, minValue = 0, maxValue = 10, increment = 0.1, 
                 size = wx.DefaultSize, style = wx.SL_HORIZONTAL, *args, **kws):
        self._value = value
        self._min = minValue
        self._max = maxValue
        self._inc = increment
        ival, imin, imax = [round(v/increment) for v in (value, minValue, maxValue)]
        self._islider = super(FloatSlider, self)
        self._islider.__init__(parent = parent, value = ival, minValue = imin, maxValue = imax, id = id, size = size, style = style, *args, **kws)
        self.Bind(wx.EVT_SCROLL, self._OnScroll, self._islider)

    def _OnScroll(self, event):
        ival = self._islider.GetValue()
        imin = self._islider.GetMin()
        imax = self._islider.GetMax()
        if ival == imin:
            self._value = self._min
        elif ival == imax:
            self._value = self._max
        else:
            self._value = ival * self._inc
        event.Skip()

    def GetValue(self):
        return self._value

    def GetMin(self):
        return self._min

    def GetMax(self):
        return self._max

    def GetInc(self):
        return self._inc

    def GetRange(self):
        return self._min, self._max

    def SetValue(self, value):
        self._islider.SetValue(round(value/self._inc))
        self._value = value

    def SetMin(self, minval):
        self._islider.SetMin(round(minval/self._inc))
        self._min = minval

    def SetMax(self, maxval):
        self._islider.SetMax(round(maxval/self._inc))
        self._max = maxval

    def SetInc(self, inc):
        self._islider.SetRange(round(self._min/inc), round(self._max/inc))
        self._islider.SetValue(round(self._value/inc))
        self._inc = inc

    def SetRange(self, minval, maxval):
        self._islider.SetRange(round(minval/self._inc), round(maxval/self._inc))
        self._min = minval
        self._max = maxval

#-------------------------------------------------------------------------#
