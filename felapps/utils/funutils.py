#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------#

"""
Author: Tong Zhang
Created Time: 11:09, Jan. 29, 2015

utilities/functions for convenience
"""

#-------------------------------------------------------------------------#

import wx
import numpy as np
import os
import matplotlib.colors as colors

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

def createStaticText(parent, label, style = wx.ALIGN_LEFT,
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
    dial = wx.FileDialog(parent, message = "Please select file",
            defaultDir=".", defaultFile="", wildcard = "XML files (*.xml)|*.xml", style = wx.FD_DEFAULT_STYLE | wx.FD_FILE_MUST_EXIST)
    if dial.ShowModal() == wx.ID_OK:
        fullfilename = os.path.join(dial.GetDirectory(),dial.GetFilename())
    dial.Destroy()
    return fullfilename

#-------------------------------------------------------------------------#
