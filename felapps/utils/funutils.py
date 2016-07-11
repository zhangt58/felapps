#!/usr/bin/env python
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
import wx.lib.mixins.listctrl as listmix
import numpy as np
import os
import matplotlib.colors as colors
import time
import sys
import h5py
import shutil
import random

from . import EnhancedStatusBar as ESB
from . import uiutils

import lmfit


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


def findObj(objroot, objclass):
    """
    Find all the objects that is instance of objclass belongs to objroot.
    obj
    """
    objfound = []
    for obj in dir(objroot):
        obji = eval('objroot.' +  obj)
        if isinstance(obji, objclass):
            objfound.append(obji)
    return objfound


class MySpinCtrl(wx.SpinCtrl):
    """
    font: wx.Font()
    """
    def __init__(self, parent, font=None, fontsize=10, fontcolor='black', fontweight=wx.FONTWEIGHT_NORMAL, *args, **kws):
        wx.SpinCtrl.__init__(self, parent=parent, *args, **kws)
        if font == None:
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.font = font
        self.fontcolor = fontcolor
        self.fontsize  = fontsize
        self.setFont(self.font)
        self.setFontSize(self.fontsize)
        self.setFontColor(self.fontcolor)

    def setFontSize(self, fontsize):
        self.fontsize = fontsize
        self.font.SetPointSize(fontsize)
        self.SetFont(self.font)

    def setFontColor(self, fontcolor):
        self.fontcolor = fontcolor
        self.SetForegroundColour(self.fontcolor)

    def setFontFaceName(self, facename):
        self.facename = facename
        self.font.SetFaceName(facename)
        self.SetFont(self.font)

    def setFont(self, font):
        self.font = font
        self.SetFont(font)


class MyStaticText(wx.StaticText):
    def __init__(self, parent, font=None, fontsize=10, fontcolor='black', fontweight=wx.FONTWEIGHT_NORMAL, *args, **kws):
        wx.StaticText.__init__(self, parent=parent, *args, **kws)
        if font == None:
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.font = font
        self.fontcolor = fontcolor
        self.fontsize  = fontsize
        self.setFont(self.font)
        self.setFontSize(self.fontsize)
        self.setFontColor(self.fontcolor)

    def setFontSize(self, fontsize):
        self.fontsize = fontsize
        self.font.SetPointSize(fontsize)
        self.SetFont(self.font)

    def setFontColor(self, fontcolor):
        self.fontcolor = fontcolor
        self.SetForegroundColour(self.fontcolor)

    def setFontFaceName(self, facename):
        self.facename = facename
        self.font.SetFaceName(facename)
        self.SetFont(self.font)

    def setFont(self, font):
        self.font = font
        self.SetFont(font)


class MyTextCtrl(wx.TextCtrl):
    def __init__(self, parent, font=None, fontsize=10, fontcolor='black', *args, **kws):
        wx.TextCtrl.__init__(self, parent=parent, *args, **kws)
        if font == None:
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.font = font
        self.fontcolor = fontcolor
        self.fontsize  = fontsize
        self.setFont(self.font)
        self.setFontSize(self.fontsize)
        self.setFontColor(self.fontcolor)

    def setFontSize(self, fontsize):
        self.fontsize = fontsize
        self.font.SetPointSize(fontsize)
        self.SetFont(self.font)

    def setFontColor(self, fontcolor):
        self.fontcolor = fontcolor
        self.SetDefaultStyle(wx.TextAttr(colText = self.fontcolor))

    def setFontFaceName(self, facename):
        self.facename = facename
        self.font.SetFaceName(facename)
        self.SetFont(self.font)

    def setFont(self, font):
        self.font = font
        self.SetFont(font)


class MyCheckBox(wx.CheckBox):
    def __init__(self, parent, font=None, fontsize=10, fontcolor='black', *args, **kws):
        wx.CheckBox.__init__(self, parent=parent, *args, **kws)
        if font == None:
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.font = font
        self.fontcolor = fontcolor
        self.fontsize  = fontsize
        self.setFont(self.font)
        self.setFontSize(self.fontsize)
        self.setFontColor(self.fontcolor)

    def setFontSize(self, fontsize):
        self.fontsize = fontsize
        self.font.SetPointSize(fontsize)
        self.SetFont(self.font)

    def setFontColor(self, fontcolor):
        self.fontcolor = fontcolor
        #self.SetDefaultStyle(wx.TextAttr(colText = self.fontcolor))

    def setFontFaceName(self, facename):
        self.facename = facename
        self.font.SetFaceName(facename)
        self.SetFont(self.font)

    def setFont(self, font):
        self.font = font
        self.SetFont(font)


class MyButton(wx.Button):
    def __init__(self, parent, font=None, fontsize=10, fontcolor='black', *args, **kws):
        wx.Button.__init__(self, parent=parent, *args, **kws)
        if font == None:
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.font = font
        self.fontcolor = fontcolor
        self.fontsize  = fontsize
        self.setFont(self.font)
        self.setFontSize(self.fontsize)
        self.setFontColor(self.fontcolor)

    def setFontSize(self, fontsize):
        self.fontsize = fontsize
        self.font.SetPointSize(fontsize)
        self.SetFont(self.font)

    def setFontColor(self, fontcolor):
        self.fontcolor = fontcolor
        self.SetForegroundColour(fontcolor)

    def setFontFaceName(self, facename):
        self.facename = facename
        self.font.SetFaceName(facename)
        self.SetFont(self.font)

    def setFont(self, font):
        self.font = font
        self.SetFont(font)


class MyComboBox(wx.ComboBox):
    def __init__(self, parent, font=None, fontsize=12, fontcolor='black', fontweight=wx.FONTWEIGHT_NORMAL, *args, **kws):
        wx.ComboBox.__init__(self, parent=parent, *args, **kws)
        if font == None:
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.font = font
        self.fontcolor = fontcolor
        self.fontsize  = fontsize
        self.setFont(self.font)
        self.setFontSize(self.fontsize)
        self.setFontColor(self.fontcolor)

    def setFontSize(self, fontsize):
        self.fontsize = fontsize
        self.font.SetPointSize(fontsize)
        self.SetFont(self.font)

    def setFontColor(self, fontcolor):
        self.fontcolor = fontcolor
        self.SetForegroundColour(self.fontcolor)

    def setFontFaceName(self, facename):
        self.facename = facename
        self.font.SetFaceName(facename)
        self.SetFont(self.font)

    def setFont(self, font):
        self.font = font
        self.SetFont(font)


class MyListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)


def createwxStaticText(parent, label, size=wx.DefaultSize, style=wx.ALIGN_LEFT, 
        fontname=wx.SYS_DEFAULT_GUI_FONT, 
        fontsize=10,
        fontweight=wx.FONTWEIGHT_NORMAL,
        fontcolor='black'):
    font = wx.SystemSettings_GetFont(fontname)
    font.SetPointSize(fontsize)
    font.SetWeight(fontweight)
    st = wx.StaticText(parent=parent, 
            label=label, style=style)
    st.SetFont(font)
    st.SetForegroundColour(fontcolor)
    return st


def createwxTextCtrl(parent, value='', style = wx.TE_LEFT,
        fontname=wx.SYS_DEFAULT_GUI_FONT,
        fontsize=10,
        fontweight=wx.FONTWEIGHT_NORMAL,
        fontcolor='black'):
    font = wx.SystemSettings_GetFont(fontname)
    font.SetPointSize(fontsize)
    font.SetWeight(fontweight)
    textctrl = wx.TextCtrl(parent = parent, 
            value = value, style = style)
    textctrl.SetFont(font)
    textctrl.SetDefaultStyle(wx.TextAttr(font = font, colText = fontcolor))
    return textctrl


def createwxButton(parent, label,
        fontname=wx.SYS_DEFAULT_GUI_FONT, 
        fontsize=10,
        fontweight=wx.FONTWEIGHT_NORMAL,
        fontcolor='black',
        size = wx.DefaultSize):
    font = wx.SystemSettings_GetFont(fontname)
    font.SetPointSize(fontsize)
    font.SetWeight(fontweight)
    btn = wx.Button(parent = parent, 
            label = label, size = size)
    btn.SetFont(font)
    btn.SetForegroundColour(fontcolor)
    return btn


def createwxPanel(parent, backgroundcolor = None, id = wx.ID_ANY):
    if backgroundcolor == None:
        backgroundcolor = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE).Get()
    panel = wx.Panel(parent, id = id)
    panel.SetBackgroundColour(backgroundcolor)
    return panel


def createwxStaticBox(parent, label='', style=wx.ALIGN_LEFT,
                      fontname=wx.SYS_DEFAULT_GUI_FONT, 
                      fontsize=10,
                      fontweight=wx.FONTWEIGHT_NORMAL,
                      fontcolor='black'):
    font = wx.SystemSettings_GetFont(fontname)
    font.SetPointSize(fontsize)
    font.SetWeight(fontweight)
    sbox = wx.StaticBox(parent, id=wx.ID_ANY, label=label, style=style)
    sbox.SetFont(font)
    sbox.SetForegroundColour(fontcolor)
    return sbox


def aupmu(gap, xlamd, a = 3.44, b = -5.00, c = 1.54):
    """
    gap, xlamd: [mm]
    """
    bfield = a*np.exp(b*(gap/xlamd)+c*(gap/xlamd)**2)
    au = 0.934*(xlamd/10)*bfield/np.sqrt(2)

    return au


def r56chi(gam0, ibfield, imagl = 0.150, idril = 0.285,):
    """
    return r56 of chicane, ibfield: [T]
    """
    c0 = 299792458.0
    m0 = 9.10938188e-31
    e0 = 1.60218e-19
    r56 = (2.0/3.0*imagl + idril)*2*(np.arcsin(imagl*e0*ibfield/np.sqrt(gam0**2-1)/m0/c0))**2

    return r56


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


def getResPath(filename, cwd = '.', resdir = '../resources'):
    """
    return absolute path for resources, e.g. images, data
    :param reshead : the relative path for resources dir
    :param filename: filename for images or data
    """

    resRoot = os.path.join(os.path.abspath(cwd), resdir)
    resPath = os.path.join(resRoot, filename)

    return resPath
    

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


def hex2rgb(hex_string):
    """
    convert hexadecimal color into rgb form.
    :param hex_string: hex color string, e.g. white color: '#FFFFFF'
    
    Example:
    >>> hex2rgb('#FFAABB')
    (255, 170, 187)
    """
    rgb = colors.hex2color(hex_string)
    return tuple([int(255*x) for x in rgb])


def rgb2hex(rgb_tuple):
    """
    convert color rgb into hex form.
    :param rgb_tuple: tuple of rgb color, e.g. white color: (255, 255, 255)
    
    Example:
    >>> rgb2hex((255, 170, 187))
    u'ffaabb'
    """
    return colors.rgb2hex([1.0*x/255 for x in rgb_tuple])


def setPath(pathstr):
    return os.path.expanduser(os.path.sep.join(pathstr.replace('\\',' ').replace('/',' ').split(' ')))


def getFileToLoad(parent, ext='*', flag='single'):
    if isinstance(ext, list):
        if len(ext) > 1:
            exts = [x.upper() + ' files (*.' + x + ')|*.' + x for x in ext]
            wildcardpattern = '|'.join(exts)
        else:
            x = ext[0]
            wildcardpattern = x.upper() + ' files ' + '(*.' + x + ')|*.' + x
    else:
        wildcardpattern = ext.upper() + ' files ' + '(*.' + ext + ')|*.' + ext

    if flag == 'single':
        dial = wx.FileDialog(parent, message = "Please select file",
                defaultDir=".", defaultFile="", wildcard = wildcardpattern, style = wx.FD_DEFAULT_STYLE | wx.FD_FILE_MUST_EXIST)
        if dial.ShowModal() == wx.ID_OK:
            fullfilename = os.path.join(dial.GetDirectory(), dial.GetFilename())
            return fullfilename
        else:
            return None

    else: #flag = 'multi':
        dial = wx.FileDialog(parent, message = "Please select file",
                defaultDir=".", defaultFile="", wildcard = wildcardpattern, style = wx.FD_DEFAULT_STYLE | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE)
        if dial.ShowModal() == wx.ID_OK:
            fullfilenames = [os.path.join(dial.GetDirectory(), filename) for filename in dial.GetFilenames()]
            return fullfilenames
        else:
            return None
    
    dial.Destroy()


def getFileToSave(parent, ext='*'):
    if isinstance(ext, list):
        if len(ext) > 1:
            exts = [x.upper() + ' files (*.' + x + ')|*.' + x for x in ext]
            wildcardpattern = '|'.join(exts)
        else:
            x = ext[0]
            wildcardpattern = x.upper() + ' files ' + '(*.' + x + ')|*.' + x
    else:
        wildcardpattern = ext.upper() + ' files ' + '(*.' + ext + ')|*.' + ext
    dial = wx.FileDialog(parent, "Save it as", wildcard = wildcardpattern, style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
    if dial.ShowModal() == wx.ID_OK:
        savetofilename = dial.GetPath()
        return savetofilename
    else:
        return None
    dial.Destroy()
    

class SaveData(object):
    def __init__(self, data, fname, type):
        """
        type: asc, hdf5, sdds
        """
        self.data  = data
        self.fname = fname

        self.onDataProcess()

        if type == ".asc":
            self.onSaveASC()
        elif type == '.hdf5':
            self.onSaveHDF5()
        elif type == '.sdds':
            self.onSaveSDDS()

    def onDataProcess(self):
        xx, yy = np.sum(self.data, 0), np.sum(self.data, 1)
        idx, idy = np.where(xx == xx.max()), np.where(yy == yy.max())
        self.xpos, self.ypos = idx[0][0], idy[0][0]
        self.maxint = self.data.max()
        self.sumint = self.data.sum()

    def onSaveASC(self):
        np.savetxt(self.fname, self.data, fmt='%.16e', delimiter=' ')

    def onSaveHDF5(self):
        f = h5py.File(self.fname,'w')

        rg = f.create_group('image')
        rg.attrs['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime())

        dset = f.create_dataset('image/data', shape=self.data.shape, dtype=self.data.dtype)
        dset[...] = self.data
        dset.attrs['xypos']  = (self.xpos, self.ypos)
        dset.attrs['sumint'] = self.sumint
        dset.attrs['maxint'] = self.maxint
        f.close()

    def onSaveSDDS(self):
        print 'save sdds format to be implemented.'
        

class ExportData(object):
    def __init__(self, data_raw, data_fit, model_x, model_y, fname):

        self.data_raw = data_raw
        self.data_fit = data_fit
        self.model_x = model_x
        self.model_y = model_y
        self.fname = fname
        self.onProcess()
        self.onSave()

    def onProcess(self):
        # fit:
        res_x = self.model_x.get_fit_result()
        res_y = self.model_x.get_fit_result()
        self.x0 = res_x.params['x0'].value
        self.y0 = res_y.params['x0'].value
        self.sx = res_x.params['xstd'].value
        self.sy = res_y.params['xstd'].value

    def onSave(self):
        f = h5py.File(self.fname, 'w')

        rg = f.create_group('data')
        rg.attrs['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime())

        for k, v in self.data_raw.items():
            dset = f.create_dataset('data/raw/' + k, shape=v.shape, dtype=v.dtype, compression=None)
            dset[...] = v


        dg = f.create_group('data/fit')
        dg.attrs['x0'] = self.x0
        dg.attrs['y0'] = self.y0
        dg.attrs['xstd'] = self.sx
        dg.attrs['ystd'] = self.sy
        for k, v in self.data_fit.items():
            dset = f.create_dataset('data/fit/' + k, shape=v.shape, dtype=v.dtype, compression=None)
            dset[...] = v
        
        f.close()

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


def func_sinc(x, y):
    r = np.sqrt(x**2 + y**2)
    return np.sin(r)/r


def func_peaks(x, y):
    return 3*(1-x)**2*np.exp(-(x**2) - (y+1)**2) - 10*(x/5 - x**3 - y**5)*np.exp(-x**2-y**2) - 1/3*np.exp(-(x+1)**2 - y**2)


class ImageDataFactor(object): # will write into C module, 2015-06-16
    def __init__(self, z):
        self.imgdata = z

    def setData(self, z):
        self.imgdata = z

    def getData(self):
        return imgdata

    def getInt(self):
        return np.sum(self.imgdata)


class ScanDataFactor(object): # will write into C module, 2015-06-17
    def __init__(self, z, scannum, shotnum, ndim = 2):
        self.scanshape = [scannum, shotnum, ndim]
        self.scandata = z.reshape(self.scanshape)
        self.scanmean = self.scandata.mean(axis = 1)

    def show(self):
        print [self.scandata[i,:,:][:,1].std() for i in range(0, self.scanshape[0])]

    def setData(self, z):
        self.scandata = z

    def getXerrbar(self):
        self.xerr = [self.scandata[i,:,:][:,0].std() for i in range(0, self.scanshape[0])]
        return np.array(self.xerr)

    def getYerrbar(self):
        self.yerr = [self.scandata[i,:,:][:,1].std() for i in range(0, self.scanshape[0])]
        return np.array(self.yerr)

    def getXavg(self):
        return self.scanmean[:,0]

    def getYavg(self):
        return self.scanmean[:,1]


class ProgressBarFrame(wx.Frame):
    def __init__(self, parent, title, range = 100, *args, **kws) :
        wx.Frame.__init__(self, parent = parent, title = title, *args, **kws)
        self.range = range
        self.createProgressbar()
        self.SetMinSize((400, 10))
        self.Centre()
        self.Show()
        self.t0 = time.time()
        self.elapsed_time_timer.Start(1000)

    def createProgressbar(self):
        self.pb = wx.Gauge(self)
        self.pb.SetRange(range = self.range)

        self.elapsed_time_st  = createwxStaticText(self, 'Elapsed Time:', fontsize = 10)
        self.elapsed_time_val = createwxStaticText(self, '00:00:00',      fontsize = 10, fontcolor = 'red')

        vbox_main = wx.BoxSizer(wx.VERTICAL)
        hbox_time = wx.BoxSizer(wx.HORIZONTAL)
        hbox_time.Add(self.elapsed_time_st,  0, wx.ALIGN_LEFT | wx.EXPAND | wx.ALL, 5)
        hbox_time.Add(self.elapsed_time_val, 0, wx.ALIGN_LEFT | wx.EXPAND | wx.ALL, 5)
        vbox_main.Add(self.pb,   0, wx.EXPAND | wx.ALL, 5)
        vbox_main.Add(hbox_time, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizerAndFit(vbox_main)

        self.elapsed_time_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTickTimer, self.elapsed_time_timer)
    
    def onTickTimer(self, event):
        fmt='%H:%M:%S'
        self.elapsed_time_val.SetLabel(time.strftime(fmt, time.gmtime(time.time()-self.t0)))


def handleConfig(config_name='imageviewer.xml'):
    """
    handle configuration files issues:
        1 load configuration files from app data
        2 create user specific configuration files
    :param config_name: configuration file name, by default is 'imageviewer.xml' (for app Image Viewer)
    reutrn valid configuration file at default user location
    """
    default_location    = os.path.expanduser("~/.felapps/config/")
    if not os.path.exists(default_location):
        os.system('mkdir -p ' + default_location)
    default_configfile  = os.path.join(default_location, config_name)
    optional_configfile = os.path.join(sys.prefix, 'local/share/felapps/', config_name)
    if os.path.isfile(default_configfile):  # configuration file is found at default location
        retval = default_configfile
    elif os.path.isfile(optional_configfile):  # load from system location, copy to default user location
        shutil.copy2(optional_configfile, default_configfile)
        retval = default_configfile
    else:  # pop window to let user select config file and copy to default user location
        config_selected = getFileToLoad(None, ext = 'xml')
        shutil.copy2(config_selected, default_configfile)
        retval = default_configfile

    return retval
 

class FitModels(object):
    def __init__(self, model='gaussian', params=None, **kws):
        """
        fitting models: 'gaussuan'  : a * exp(-(x-x0)^2/2/xstd^2) + y0
                        'linear'    : a + b*x 
                        'quadratic' : a + b*x + c*x^2
                        'polynomial': \Sigma_i=0^n x^i * a_i
                        'power'     : a * x ^ b
                        'sin'       : a * sin(b * x + c) + d
        """
        if params is None:
            params = lmfit.Parameters()
        self._model  = model
        self._params = params
        try:
            self._x, self._y = kws['x'], kws['y']
        except:
            self._x, self._y = [], []
        self._method = 'leastsq'

        self._set_params_func = {
                'gaussian': self._set_params_gaussian,
                }
        self._fitfunc = {
                'gaussian': self._fit_gaussian,
                }
        self._gen_func_text = {
                'gaussian': self._gen_func_text_gaussian,
                }
        
        self._fit_result = None
        
    @property
    def model(self):
        return self._model

    @model.setter
    def mode(self, model):
        self._model = model

    @property
    def method(self):
        return self._method
    
    @method.setter
    def method(self, method):
        self._method = method

    def _fit_gaussian(self, p, x):
        a = p['a'].value
        x0 = p['x0'].value
        y0 = p['y0'].value
        xstd = p['xstd'].value
        return a * np.exp(-(x-x0)**2.0/2.0/xstd/xstd) + y0
    
    def _errfunc(self, p, f, x, y):
        return f(p, x) - y

    def set_data(self, data=None, x=None, y=None):
        """ set raw data to fit
        """
        if data is not None:
            self._x, self._y = data[:,0], data[:,1]
        else:
            if x is not None: self._x = x
            if y is not None: self._y = y

    def get_data(self):
        """ return raw data
        """
        return self._x, self._y
            
    def _set_fitfunc(self, type=None):
        """ type: gaussian, linear, quadratic, polynomial, power, sin
        """
        if type is not None:
            self._model = type

    def _gen_func_text_gaussian(self, p0):
        a = p0['a'].value
        x0 = p0['x0'].value
        y0 = p0['y0'].value
        xstd =p0['xstd'].value
        return '$a e^{-\\frac{(x-x_0)^2}{2\sigma_x^2}}+y_0$' 

    def set_params(self, **p0):
        """p0: initial parameters dict"""
        self._set_params_func[self._model](p0)

    def _set_params_gaussian(self, p0):
        self._params.add('a',    value=p0['a']   )
        self._params.add('x0',   value=p0['x0']  )
        self._params.add('y0',   value=p0['y0']  )
        self._params.add('xstd', value=p0['xstd'])

    def get_fitfunc(self, p0=None):
        if p0 is None:
            p0 = self._fit_result.params
        f_func = self._fitfunc[self._model]
        gen_func = self._gen_func_text[self._model]
        f_text = gen_func(p0)
        return f_func, f_text

    def get_fit_result(self):
        return self._fit_result

    def fit(self):
        p = self._params
        f = self._fitfunc[self._model]
        x, y = self._x, self._y
        m = self._method
        res = lmfit.minimize(self._errfunc, p, method=m, args=(f, x, y))
        self._fit_result = res
        return res
    
    def fit_report(self):
        # gaussian model
        if self._fit_result is not None:
            p = self._fit_result.params
            retstr1 = "Fitting Function:" + "\n"
            retstr2 = "a*exp(-(x-x0)^2/2/sx^2)+y0" + "\n"
            retstr3 = "Fitting Output:" + "\n"
            retstr4 = "{a0_k:<3s}: {a0_v:>10.4f}\n".format(a0_k='a' , a0_v=p['a'].value)
            retstr5 = "{x0_k:<3s}: {x0_v:>10.4f}\n".format(x0_k='x0', x0_v=p['x0'].value)
            retstr6 = "{sx_k:<3s}: {sx_v:>10.4f}\n".format(sx_k='sx', sx_v=p['xstd'].value)
            retstr7 = "{y0_k:<3s}: {y0_v:>10.4f}".format(y0_k='y0', y0_v=p['y0'].value)
            return retstr1 + retstr2 + retstr3 + retstr4 + retstr5 + retstr6 + retstr7
        else:
            return "Nothing to report."
        
    
    def fit_report1(self):
        if self._fit_result is not None:
            return lmfit.fit_report(self._fit_result.params)
        else:
            return "Nothing to report."


def get_randstr(length=1):
    """ return string of random picked up chars
    :param length: string length to return
    """
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz'
    retval = ''.join([random.choice(chars) for _ in range(length)])
    return retval


def get_file_info(filepath):
    """ return file information
    :param filepath: file full path name
    """
    f_info = os.stat(filepath)
    f_ctime = time.strftime("%Y-%m-%d %H:%M:%S",
                            time.localtime(f_info.st_ctime))
    f_size_bytes = f_info.st_size
    f_name = os.path.basename(filepath)

    return {'name'  : f_name,
            'ctime' : f_ctime,
            'bytes' : f_size_bytes}


def gaussian_fit(x, xdata, mode='full'):
    """ return fit result and fitmodels
    """
    fm = FitModels()
    x0 = np.sum(x*xdata)/np.sum(xdata)
    p0 = {'a'   : xdata.max(),
          'x0'  : x0,
          'xstd': (np.sum((x-x0)**2*xdata)/np.sum(xdata))**0.5,
          'y0'  : 0
         }
    fm.set_data(x=x,y=xdata)
    fm.set_params(**p0)
    res = fm.fit()
    if mode == 'full':
        return res, fm
    elif mode == 'simple':
        return [res.params[k].value for k in ('x0', 'xstd')]


class AnalysisPlotPanel(uiutils.MyPlotPanel):
    def __init__(self, parent, data=None, **kwargs):
        """ data: m x n image array
        """
        if data is None:
            x = y = np.linspace(-np.pi, np.pi, 100)
            xx, yy = np.meshgrid(x, y)
            data = func_sinc(xx, yy)
            #data = np.zeros([50, 50])
        self.data = data
        self.cmap = 'jet'

        # axis directions
        self.xaxis_direction = True # left->right: small->big
        self.yaxis_direction = True # bottom->up : small->big

        self.line_color = wx.Colour(255, 165, 0).GetAsString(wx.C2S_HTML_SYNTAX)
        self.mec = wx.Colour(255, 0, 0).GetAsString(wx.C2S_HTML_SYNTAX)
        self.mfc = wx.Colour(255, 0, 0).GetAsString(wx.C2S_HTML_SYNTAX)

        # pos markers M1 and M2
        self.mkc1 = wx.Colour(255, 0, 0).GetAsString(wx.C2S_HTML_SYNTAX)
        self.mkc2 = wx.Colour(240, 230, 140).GetAsString(wx.C2S_HTML_SYNTAX)
        self.pcc = wx.Colour(0, 0, 0).GetAsString(wx.C2S_HTML_SYNTAX)
        self.mk1, self.mk2 = False, False

        uiutils.MyPlotPanel.__init__(self, parent, **kwargs)
    
        # specific relationship between self and the parent? frame
        self.mframe_point = self.parent.GetParent().GetParent()
        
    def set_color(self, rgb_tuple):
        """ set figure and canvas with the same color.
        :param rgb_tuple: rgb color tuple, 
                          e.g. (255, 255, 255) for white color
        """
        if rgb_tuple is None:
            rgb_tuple = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWFRAME).Get()
        clr = [c/255.0 for c in rgb_tuple]
        self.figure.set_facecolor(clr)
        self.figure.set_edgecolor(clr)

    def _init_plot(self):
        pass

    def on_press(self, event):
        if event.inaxes:
            x0, y0 = event.xdata, event.ydata
            self.draw_hvlines(x0, y0)

    def on_release(self, event):
        pass
        #x0, y0 = event.xdata, event.ydata
        #self.x0, self.y0 = x0, y0

    def set_markflags(self, mk1=False, mk2=False):
        self.mk1, self.mk2 = mk1, mk2
        try:
            if self.mk1 == True:
                self._draw_hvlines1(self.x_pos1, self.y_pos1)
            elif self.mk2 == True:
                self._draw_hvlines2(self.x_pos2, self.y_pos2)
        except:
            return

    def set_mkc1(self, color):
        self.mkc1 = color

    def set_mkc2(self, color):
        self.mkc2 = color

    def set_pcc(self, color):
        self.pcc = color
        if hasattr(self, 'pc1'):
            self.pc1.set_mec(color)
            self.pc1.set_mfc(color)
        if hasattr(self, 'pc2'):
            self.pc2.set_mec(color)
            self.pc2.set_mfc(color)
        if hasattr(self, 'plbl1'):
            self.plbl1.set_color(color)
        if hasattr(self, 'plbl2'):
            self.plbl2.set_color(color)
        self.refresh()

    def draw_hvlines(self, x0, y0):
        if self.mk1 == True:
            self._draw_hvlines1(x0, y0)
        elif self.mk2 == True:
            self._draw_hvlines2(x0, y0)
        try:
            self.update_deltxy()
        except:
            pass

    def _draw_hvlines1(self, x0, y0):
        if hasattr(self, 'hl1'):
            self.hl1.set_ydata([y0, y0])
        else:
            self.hl1 = self.axes.axhline(y0, ls='--')
        self.hl1.set_color(self.mkc1)

        if hasattr(self, 'vl1'):
            self.vl1.set_xdata([x0, x0])
        else:
            self.vl1 = self.axes.axvline(x0, ls='--')
        self.vl1.set_color(self.mkc1)

        if hasattr(self, 'pc1'):
            self.pc1.set_data(x0, y0)
        else:
            self.pc1, = self.axes.plot(x0, y0, 'ko', ms=6, mfc='k', mec='k')
        self.pc1.set_mec(self.pcc)
        self.pc1.set_mfc(self.pcc)

        if hasattr(self, 'plbl1'):
            self.plbl1.set_position((x0, y0))
        else:
            self.plbl1 = self.axes.text(x0, y0, r'$\mathsf{M1}$', fontsize=16)
        self.plbl1.set_color(self.pcc)

        self.x_pos1, self.y_pos1 = x0, y0
        try:
            self.mframe_point.m1_pos_st.SetLabel('{0:.1f},{1:.1f}'.format(x0, y0))
        except:
            pass

        self.refresh()

    def _draw_hvlines2(self, x0, y0):
        if hasattr(self, 'hl2'):
            self.hl2.set_ydata([y0, y0])
        else:
            self.hl2 = self.axes.axhline(y0, color='r', ls='--')
        self.hl2.set_color(self.mkc2)

        if hasattr(self, 'vl2'):
            self.vl2.set_xdata([x0, x0])
        else:
            self.vl2 = self.axes.axvline(x0, color='r', ls='--')
        self.vl2.set_color(self.mkc2)

        if hasattr(self, 'pc2'):
            self.pc2.set_data(x0, y0)
        else:
            self.pc2, = self.axes.plot(x0, y0, 'ko', ms=6, mfc='k', mec='k')
        self.pc2.set_mec(self.pcc)
        self.pc2.set_mfc(self.pcc)

        if hasattr(self, 'plbl2'):
            self.plbl2.set_position((x0, y0))
        else:
            self.plbl2 = self.axes.text(x0, y0, r'$\mathsf{M2}$', fontsize=16)
        self.plbl2.set_color(self.pcc)

        self.x_pos2, self.y_pos2 = x0, y0
        try:
            self.mframe_point.m2_pos_st.SetLabel('{0:.1f},{1:.1f}'.format(x0, y0))
        except:
            pass

        self.refresh()

    def update_deltxy(self):
        m1_pos_val = self.mframe_point.m1_pos_st.GetLabel()
        m2_pos_val = self.mframe_point.m2_pos_st.GetLabel()
        if m1_pos_val != '' and m2_pos_val != '':
            x1, y1 = [float(i) for i in m1_pos_val.split(',')]
            x2, y2 = [float(i) for i in m2_pos_val.split(',')]
            dx = abs(x1 - x2)
            dy = abs(y1 - y2)
            self.mframe_point.delx_val_st.SetLabel("{0:.1f}".format(dx))
            self.mframe_point.dely_val_st.SetLabel("{0:.1f}".format(dy))

    def set_colormap(self, cmap):
        self.cmap = cmap
        self.image.set_cmap(cmap)
        self.refresh()

    def set_linecolor(self, color):
        self.line_color = color
        [line.set_color(color) for line in self.line_list]
        self.refresh()

    def set_fontsize(self, fontsize):
        x_lbl = self.axes.get_xlabel()
        y_lbl = self.axes.get_ylabel()
        self.axes.set_xlabel(x_lbl, fontsize=fontsize+4)
        self.axes.set_ylabel(y_lbl, fontsize=fontsize+4)
        self.axes.tick_params(labelsize=fontsize)
        self.refresh()

    
    def set_line_id(self, line='raw'):
        """ selected current editable line,
            'raw': raw data
            'fitted': fitted lines
            'none': hide all lines
            'show': show all lines
        """
        if line == 'none':
            self.linex.set_visible(False)
            self.liney.set_visible(False)
            self.linex_fit.set_visible(False)
            self.liney_fit.set_visible(False)
            self.line_list = []
        elif line == 'show':
            self.linex.set_visible(True)
            self.liney.set_visible(True)
            self.linex_fit.set_visible(True)
            self.liney_fit.set_visible(True)
            self.line_list = [self.linex, self.liney, self.linex_fit, self.liney_fit]
        elif line == 'raw':
            self.linex.set_visible(True)
            self.liney.set_visible(True)
            self.linex_fit.set_visible(False)
            self.liney_fit.set_visible(False)
            self.line_list = [self.linex, self.liney]
        elif line == 'fit':
            self.linex.set_visible(False)
            self.liney.set_visible(False)
            self.linex_fit.set_visible(True)
            self.liney_fit.set_visible(True)
            self.line_list = [self.linex_fit, self.liney_fit]
        self.refresh()

    def set_lines(self):
        if self.data is None:
            return
        data = self.data
        hx, hy = np.sum(data, 0), np.sum(data, 1)
        idxmaxx, idxmaxy = np.where(hx == hx.max()), np.where(hy == hy.max())
        maxidx, maxidy = idxmaxx[0][0], idxmaxy[0][0]
        x, y = np.arange(hx.size), np.arange(hy.size)
        hx = hx/hx.max()*maxidy
        hy = hy/hy.max()*maxidx

        res_x, fm_x = gaussian_fit(x, hx)
        res_y, fm_y = gaussian_fit(y, hy)

        self.linex, = self.axes.plot(x, hx)
        self.liney, = self.axes.plot(hy, y)

        self.linex.set_color(self.line_color)
        self.liney.set_color(self.line_color)

        self.linex.set_marker('')
        self.linex.set_markersize(5)
        self.linex.set_mec(self.mec)
        self.linex.set_mfc(self.mfc)

        self.liney.set_marker('')
        self.liney.set_markersize(5)
        self.liney.set_mec(self.mec)
        self.liney.set_mfc(self.mfc)

        # fitted lines
        x_fit = np.linspace(x.min(), x.max(), 200)
        y_fit = np.linspace(y.min(), y.max(), 200)
        fx, tx = fm_x.get_fitfunc(res_x.params)
        fy, ty = fm_y.get_fitfunc(res_y.params)
        
        self.linex_fit, = self.axes.plot(x_fit, fx(res_x.params, x_fit))
        self.liney_fit, = self.axes.plot(fy(res_y.params, y_fit), y_fit)

        self.linex_fit.set_color(self.line_color)
        self.liney_fit.set_color(self.line_color)

        self.linex_fit.set_marker('')
        self.linex_fit.set_markersize(5)
        self.linex_fit.set_mec(self.mec)
        self.linex_fit.set_mfc(self.mfc)

        self.liney_fit.set_marker('')
        self.liney_fit.set_markersize(5)
        self.liney_fit.set_mec(self.mec)
        self.liney_fit.set_mfc(self.mfc)

        self.axes.set_xlim([x.min(), x.max()])
        self.axes.set_ylim([y.min(), y.max()])

        # hide all lines
        self.linex.set_visible(False)
        self.liney.set_visible(False)
        self.linex_fit.set_visible(False)
        self.liney_fit.set_visible(False)

        self.refresh()
        self.res_x, self.res_y = res_x, res_y
        self.line_list = []

    def get_fit_report(self, xoy='x'):
        if xoy == 'x':
            p = self.res_x.params
        else:
            p = self.res_y.params
        retstr2 = "f(x) = a*exp(-(x-x0)^2/2/sx^2)+y0" + "\n"
        retstr4 = " {a0_k:<3s}: {a0_v:>10.4f}\n".format(a0_k='a' , a0_v=p['a'].value)
        retstr5 = " {x0_k:<3s}: {x0_v:>10.4f}\n".format(x0_k='x0', x0_v=p['x0'].value)
        retstr6 = " {sx_k:<3s}: {sx_v:>10.4f}\n".format(sx_k='sx', sx_v=p['xstd'].value)
        retstr7 = " {y0_k:<3s}: {y0_v:>10.4f}".format(y0_k='y0', y0_v=p['y0'].value)
        retval = retstr2 + retstr4 + retstr5 + retstr6 + retstr7
        return retval

    def set_figure_data(self, data, fit=True):
        self.data = data
        if not hasattr(self, 'axes'):
            self.axes = self.figure.add_subplot(111, aspect=1.0)
        self.z = data
        self.image = self.axes.imshow(self.z, cmap=self.cmap)
        
        if fit:
            self.set_lines()
        else:
            dimx, dimy = self.z.shape
            x, y = np.arange(dimy), np.arange(dimx)
            self.image.set_extent([x.min(), x.max(), y.min(), y.max()])

        self.refresh()

    def set_linestyle(self, ls):
        [line.set_linestyle(ls) for line in self.line_list]
        self.refresh()

    def set_marker(self, mk):
        [line.set_marker(mk) for line in self.line_list]
        self.refresh()

    def set_markersize(self, ms):
        [line.set_markersize(ms) for line in self.line_list]
        self.refresh()

    def set_mec(self, c):
        self.mec = c
        [line.set_mec(c) for line in self.line_list]
        self.refresh()

    def set_mfc(self, c):
        self.mfc = c
        [line.set_mfc(c) for line in self.line_list]
        self.refresh()

    def set_linewidth(self, lw):
        [line.set_linewidth(lw) for line in self.line_list]
        self.refresh()

    def set_ticks(self, flag='half'):
        # ticks position
        if flag == 'half':
            s = ['on','on','off','off']
            self.axes.tick_params(labelbottom=s[0]) 
            self.axes.tick_params(labelleft=s[1]) 
            self.axes.tick_params(labeltop=s[2]) 
            self.axes.tick_params(labelright=s[3]) 
        elif flag == 'all':
            s = ['on','on','on','on']
            self.axes.tick_params(labelbottom=s[0]) 
            self.axes.tick_params(labelleft=s[1]) 
            self.axes.tick_params(labeltop=s[2]) 
            self.axes.tick_params(labelright=s[3]) 
        self.refresh()

    def set_mticks(self, flag='off'):
        if flag == 'on':
            self.axes.minorticks_on()
            self.refresh()
        elif flag == 'off':
            self.axes.minorticks_off()
            self.refresh()

    def set_grids(self, color, b=None, which='major'):
        if b is None:
            self.axes.grid(which=which, color=color, linestyle='--')
        else:
            self.axes.grid(b=False)
        self.refresh()

    def set_origin(self, ll=False, ul=False, ur=False, lr=False):
        if ll:
            self.direct_xyaxis(True, True)
            self.axes.xaxis.set_ticks_position('bottom')
            self.axes.yaxis.set_ticks_position('left')
            self.axes.xaxis.set_label_position('bottom')
            self.axes.yaxis.set_label_position('left')
        if ul:
            self.direct_xyaxis(True, False)
            self.axes.xaxis.set_ticks_position('top')
            self.axes.yaxis.set_ticks_position('left')
            self.axes.xaxis.set_label_position('top')
            self.axes.yaxis.set_label_position('left')
        if ur:
            self.direct_xyaxis(False, False)
            self.axes.xaxis.set_ticks_position('top')
            self.axes.yaxis.set_ticks_position('right')
            self.axes.xaxis.set_label_position('top')
            self.axes.yaxis.set_label_position('right')
        if lr:
            self.direct_xyaxis(False, True)
            self.axes.xaxis.set_ticks_position('bottom')
            self.axes.yaxis.set_ticks_position('right')
            self.axes.xaxis.set_label_position('bottom')
            self.axes.yaxis.set_label_position('right')
        self.refresh()

    def get_clim(self):
        clim = self.image.get_clim()
        return "{cmin:.1f} : {cmax:.1f}".format(cmin=clim[0], cmax=clim[1])

    def set_clim(self, cr):
        clim = sorted(float(i) for i in cr.split(':'))
        self.image.set_clim(clim)
        self.refresh()

    def direct_xyaxis(self, x_direction, y_direction):
        if self.xaxis_direction != x_direction:
            self.axes.invert_xaxis()
            self.xaxis_direction = x_direction
        if self.yaxis_direction != y_direction:
            self.axes.invert_yaxis()
            self.yaxis_direction = y_direction

    def hide_image(self, hide_flag):
        self.image.set_visible(not hide_flag)
        self.refresh()

    def clear(self):
        if hasattr(self, 'axes'):
            self.axes.cla()

    def get_data(self):
        """ return data: image, raw data, fit data
        """
        data = {}
        data['raw'] = {}
        data['fit'] = {}
        data['attr'] = {}
        data['image'] = self.image.get_array()
        data['raw']['prof_x'] = self.linex.get_data()
        data['raw']['prof_y'] = self.liney.get_data()
        data['fit']['prof_x'] = self.linex_fit.get_data()
        data['fit']['prof_y'] = self.liney_fit.get_data()
        data['attr']['x0'] = self.res_x.params['x0'].value
        data['attr']['sx'] = self.res_x.params['xstd'].value
        data['attr']['y0'] = self.res_y.params['x0'].value
        data['attr']['sy'] = self.res_y.params['xstd'].value
        return data

def pick_color():
    dlg = wx.ColourDialog(None)
    dlg.GetColourData().SetChooseFull(True)  # only windows
    if dlg.ShowModal() == wx.ID_OK:
        color = dlg.GetColourData().GetColour()
        dlg.Destroy()
        return color

def set_staticbmp_color(obj, color):
    """
    obj: staticbitmap, bitmapbutton
    color: could be returned by pick_color()
    """
    r, g, b = color.Red(), color.Green(), color.Blue()
    w, h = 16, 16
    bmp = wx.EmptyBitmap(w, h)
    img = wx.ImageFromBitmap(bmp)
    img.SetRGBRect(wx.Rect(0, 0, w, h), r, g, b)
    obj.SetBitmap(img.ConvertToBitmap())
