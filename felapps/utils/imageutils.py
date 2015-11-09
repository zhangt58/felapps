#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
classes and functions for image processing
    Hdf2Image: generate image from hdf5 data

Author: Tong Zhang
Created: Sep. 28, 2015
"""

from PIL import Image
import matplotlib.pyplot as plt
import h5py
import os
import wx
import numpy as np
import time
from . import funutils

import wx.lib.scrolledpanel as scrolled

from scipy.misc import imsave

def data2Image(filename, datatype = 'hdf5', figtype = 'jpg', width = None, height = None, whflag = 'h', cmtype = 'hot', *args, **kwargs):
    """
    generate image thumbnails from data file, by default from hdf5 array.

    :param filename: data filename, f.
    :param datatype: data format, 
        'hdf5' or 'h5': image data could be extracted by fid = h5py.File(f); fid['image']['data'].
        'asc' or 'dat': image data could be extracted by np.loadtxt(f).
    :param figtype: 'jpg', 'png' or others.
    :param width:  image size in w, if None, take original values.
    :param height: image size in h, if None, take original values.
    :param whflag: 'w' (h prop with w) or 'h' (w prop with h) 
        or 'None' (take size as w x h).
    :param cmtype: colormap type, hot by default.
    ::
    """
    if datatype == 'hdf5' or datatype == 'h5':
        f = h5py.File(os.path.expanduser(filename))
        data = f['image']['data']
    elif datatype == 'asc' or datatype == 'dat':
        data = np.loadtxt(filename)
        
    tmpdir = '/tmp'
    cwdir = os.getcwd()

    filenamebase = os.path.basename(filename)

    thumbname = '.'.join(filenamebase.split('.')[:-1] + [figtype])
    thumbfullpath = os.path.join(tmpdir, thumbname)

    thumbrelpath = os.path.join(cwdir, thumbname)
    
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_axis_off()
    im = ax.imshow(data, cmap = cmtype, aspect = 'equal')
    extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    plt.savefig(thumbfullpath, bbox_inches = extent, pad_inches = 0)
    """
    imsave(thumbfullpath, data)

    # use PIL to resize image in accurate pixel
    rawimg = Image.open(thumbfullpath)
    rawsize_w, rawsize_h = rawimg.size

    w, h = width, height

    if w == None:
        w = rawsize_w
    if h == None:
        h = rawsize_h
    
    if whflag == 'h':
        sizecoef = float(h)/rawsize_h
    elif whflag == 'w':
        sizecoef = float(w)/rawsize_w
    elif whflag == 'None':
        sizecoef = 1.0

    newsize = int(rawsize_w * sizecoef), int(rawsize_h * sizecoef)
    resizedimg = rawimg.resize(newsize)

    resizedimg.save(thumbrelpath)

    #plt.close(fig)
    
    return thumbrelpath

class ImageGalleryPanel(scrolled.ScrolledPanel):
    """
    Panel for image gallery show
    """
    def __init__(self, parent, *args, **kwargs):
        scrolled.ScrolledPanel.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.pxsize = 160

        # make UI
        self.initUI()

    def genImage(self):
        if self.imagelist == None: # not load any image data files, i.e. default status
            #for imgid in xrange(16):
            #    img = resizeImage('/home/tong/Programming/learning/python/PIL/test.jpg', 160)
            #    self.imageobj.append(wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(img)))
            pass
        else:
            for imagefilepath in self.imagelist:
                img = resizeImage(imagefilepath, self.pxsize)
                self.imageobj.append(wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(img)))

    def initUI(self):
        self.SetBackgroundColour('light grey')

    def onUpdate(self, jpglist = None):
        if jpglist != None:
            self.imagelist = jpglist # jpg fullpath list
        self.imageobj = []       # wx.StaticBitmap objs generated from imagelist
        self.genImage()
        # define a wrapsizer
        wpsizer = wx.WrapSizer()
        for imgobj in self.imageobj:
            wpsizer.Add(imgobj, proportion = 0, flag = wx.ALL, border = 4)

        self.SetSizer(wpsizer)
        self.Layout()
        self.SetupScrolling()

    def onClear(self):
        """
        clear all objs on panel
        """
        for child in self.GetChildren():
            child.Destroy()

    def onScaleInc(self, percent):
        """
        enlarge image by percent
        """
        self.pxsize *= (1.0+percent)
        self.onClear()
        self.onUpdate()

    def onScaleDec(self, percent):
        """
        shrink image by percent
        """
        self.pxsize *= (1.0-percent)
        self.onClear()
        self.onUpdate()

class ProgressBarFrame(wx.Frame):
    def __init__(self, parent, title, range = 100) :
        wx.Frame.__init__(self, parent = parent, title = title)
        self.range = range
        self.createProgressbar()
        self.SetMinSize((400, 10))
        self.Centre()
        self.t0 = time.time()
        self.elapsed_time_timer.Start(1000)

        self.Show()

    def createProgressbar(self):
        self.pb       = wx.Gauge(self)
        self.pb.SetRange(range = self.range)

        self.elapsed_time_st  = wx.StaticText(self, label = 'Elapsed Time:')
        self.elapsed_time_val = wx.StaticText(self, label = '00:00:00')

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

def resizeImage(imagepath, height, width = None, whflag = 'h', quality = wx.IMAGE_QUALITY_NORMAL):
    """
    resize image read from file, return wx.Image obj
    :param imagepath: jpg image file path
    :param height: height in pixel after resizing
    :param width:  width in pixel after resizing
    :param whflag: w.r.t. height ('h') or width ('w')
    """
    oimage = wx.Image(imagepath, type = wx.BITMAP_TYPE_ANY) # recommend jpg type
    w, h = oimage.GetSize()
    if whflag == 'h':
        scalingfactor = float(height)/h
    elif whflag == 'w':
        scalingfactor = float(width)/w
    
    return oimage.Scale(w*scalingfactor, h*scalingfactor, quality)

def test_Hdf2Image():
    """
    test function Hdf2Image
    """
    Hdf2Image('~/Desktop/20150923/data.hdf5', height=100, cmtype = 'jet')

def main():
    test_Hdf2Image()

if __name__ == '__main__':
    test_Hdf2Image()
    
