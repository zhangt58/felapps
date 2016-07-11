#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
classes and functions for image processing
    data2Image: generate image from data file, hdf5, asc, dat

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
from . import analysisframe

import wx.lib.scrolledpanel as scrolled
import wx.dataview as dv

from scipy.misc import imsave

def data2Image(filename, datatype='hdf5', figtype='jpg', wdir=None, width=None, height=None, whflag='h', cmtype='hot', *args, **kwargs):
    """
    generate image thumbnails from data file, by default from hdf5 array.

    :param filename: data filename, f.
    :param datatype: data format, 
        'hdf5' or 'h5': image data could be extracted by fid = h5py.File(f); fid['image']['data'].
        'asc' or 'dat': image data could be extracted by np.loadtxt(f).
    :param figtype: 'jpg', 'png' or others.
    :param wdir: working directory, to put generated jpg figures, if None, use cwd.
    :param width:  image size in w, if None, take original values.
    :param height: image size in h, if None, take original values.
    :param whflag: 'w' (h prop with w) or 'h' (w prop with h) 
        or 'None' (take size as w x h).
    :param cmtype: colormap type, hot by default.
    """
    if datatype == 'hdf5' or datatype == 'h5':
        f = h5py.File(os.path.expanduser(filename))
        data = f['image']['data']
    elif datatype == 'asc' or datatype == 'dat':
        data = np.loadtxt(filename)
        
    if wdir is None:
        wdir = os.getcwd()
    imgdir = os.path.join(wdir, '._img')
    tmpdir = os.path.join(wdir, '._tmp')
    if not os.path.exists(imgdir):
        os.mkdir(imgdir)
    if not os.path.exists(tmpdir):
        os.mkdir(tmpdir)

    filenamebase = os.path.basename(filename)

    thumbname = '.'.join(filenamebase.split('.')[:-1] + [figtype])
    thumbfullpath = os.path.join(tmpdir, thumbname)
    thumbrelpath = os.path.join(imgdir, thumbname)
    
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
        self.image_file_list = []  # image file list
        self.image_bitmap_obj = [] # staticbitmap list
        self.wpsizer = wx.WrapSizer()

        self._workspace_list = []
        self._ws_panel = parent.GetParent().GetParent().ws_panel

        # make UI
        self.initUI()

        self.Bind(wx.EVT_RIGHT_DOWN, self.onRightPopup)

    def onRightPopup(self, event):
        obj = event.GetEventObject().GetChildren()
        self.id_add_all = wx.ID_BACKWARD
        self.id_rm_all = wx.ID_FORWARD
        menu = wx.Menu()
        menu.Append(self.id_add_all, "Add all to workspace")
        menu.Append(self.id_rm_all, "Remove all from workspace")
        self.Bind(wx.EVT_MENU, lambda evt: self.onPopAddAll(evt, obj), id=self.id_add_all)
        self.Bind(wx.EVT_MENU, lambda evt: self.onPopRemoveAll(evt, obj), id=self.id_rm_all)
        self.PopupMenu(menu)
        menu.Destroy()
        event.Skip()
    
    def onPopAddAll(self, event, obj):
        self._workspace_list = [i.GetName() for i in obj]
        self._ws_panel.clear()
        self._ws_panel.update(self.get_workspace())

    def onPopRemoveAll(self, event, obj):
        self._workspace_list = []
        self._ws_panel.clear()
        self._ws_panel.update(self.get_workspace())

    def onLeftClick(self, event):
        """ when left click image, select corresponding item on workspace panel
        """
        obj = event.GetEventObject()
        itemstr = obj.GetName()
        if itemstr in self._workspace_list:
            rowidx = self._workspace_list.index(obj.GetName())
            self._ws_panel.dv_lc.SelectRow(rowidx)
            item_sel = self._ws_panel.dv_lc.RowToItem(rowidx)
            self._ws_panel.dv_lc.EnsureVisible(item_sel)
    
    def onRightClick(self, event):
        obj = event.GetEventObject()
        self.id_add = wx.ID_ADD
        self.id_pop = wx.ID_UP
        self.id_remove = wx.ID_REMOVE
        menu = wx.Menu()
        if obj.GetName() in self._workspace_list:
            menu.Append(self.id_remove, "Out Workspace")
            self.Bind(wx.EVT_MENU, lambda evt: self.onPopRemove(evt, obj), id=self.id_remove)
        else:
            menu.Append(self.id_add, "To Workspace")
            self.Bind(wx.EVT_MENU, lambda evt: self.onPopAdd(evt, obj), id=self.id_add)
        self.Bind(wx.EVT_MENU, lambda evt: self.onPopAnalysis(evt, obj), id=self.id_pop)
        menu.Append(self.id_pop, "Pop up Analysis")
        self.PopupMenu(menu)
        menu.Destroy()
        #event.Skip()

    def onPopAdd(self, event, obj):
        self._workspace_list.append(obj.GetName())
        self._ws_panel.clear()
        self._ws_panel.update(self.get_workspace())
        print "Add selected image to workspace"

    def onPopRemove(self, event, obj):
        self._workspace_list.remove(obj.GetName())
        self._ws_panel.clear()
        self._ws_panel.update(self.get_workspace())
        print "Remove selected image from workspace"

    def onPopAnalysis(self, event, obj):
        datasrc = obj.GetName().split(';;;')[-1]
        self.analysis_frame = analysisframe.AnalysisFrame(self, datasrc)
        self.analysis_frame.SetTitle(datasrc)
        self.analysis_frame.Show()

    def get_workspace(self, fmt='dvc'):
        """ _workspace_list element format: "image_file_full_path;;;data_file_fullpath"
        """
        if fmt == 'dvc':
            return [[str(idx+1)] + [os.path.basename(n) for n in e.split(';;;')] 
                        for idx, e in enumerate(self._workspace_list)]
        elif fmt == 'sta': # return data file list
            return [e.split(';;;')[-1] for e in self._workspace_list]
        else:
            return None
        
        #return self._workspace_list

    def genImage(self, imagelist, fdir, ftype):
        imageobj_list = []
        if imagelist is None: # not load any image data files, i.e. default status
            #for imgid in xrange(16):
            #    img = resizeImage('/home/tong/Programming/learning/python/PIL/test.jpg', 160)
            #    self.imageobj.append(wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(img)))
            pass
        else:
            for imagefilepath in imagelist:
                img = resizeImage(imagefilepath, self.pxsize)
                datafilename = '.'.join(os.path.basename(imagefilepath).split('.')[0:-1])
                datafilepath = os.path.join(fdir, datafilename + '.' + ftype)
                #print imagefilepath
                #print datafilename, datafilepath
                name = ';;;'.join([imagefilepath, datafilepath])
                imageobj_list.append(wx.StaticBitmap(self, wx.ID_ANY,
                                                     wx.BitmapFromImage(img), 
                                                     name=name))
        return imageobj_list

    def initUI(self):
        self.SetBackgroundColour('light grey')

    def onUpdate(self, image_list=None, fdir=None, ftype=None):
        """ update image grid panel
        :param image_list: image file list, jpg
        :parma fdir: dirname of data files
        :param ftype: ext of data format, which generate image_list
        """
        if image_list != []:
            self.image_file_list.extend(image_list)  # merge into image fullpath list (.jpg)

        # wx.StaticBitmap objs generated from imagelist
        image_objs = self.genImage(image_list, fdir, ftype)
        self.image_bitmap_obj.extend(image_objs)

        wpsizer = self.wpsizer
        # define a wrapsizer
        for imgobj in image_objs:
            wpsizer.Add(imgobj, 0, wx.ALL, 4)
            imgobj.Bind(wx.EVT_RIGHT_DOWN, self.onRightClick)
            imgobj.Bind(wx.EVT_LEFT_DOWN, self.onLeftClick)
            name = imgobj.GetName()
            #print "---"
            #print name
            #print "---"
            f_img, f_data = name.split(';;;')
            f_img_info = funutils.get_file_info(f_img)
            f_data_info = funutils.get_file_info(f_data)
            ttext = "Image filename: {img_n}\nData source: {data_n}\nCreate: {ctime}\nBytes: {s_i} [image], {s_d} [data]".format(
                    img_n=f_img_info['name'],
                    data_n=f_data_info['name'],
                    ctime=f_data_info['ctime'],
                    s_i=f_img_info['bytes'],
                    s_d=f_data_info['bytes'])
            imgobj.SetToolTip(wx.ToolTip(ttext))

        self.SetSizer(wpsizer)
        self.Layout()
        self.SetupScrolling()

    def onScaleImageSize(self, fdata_list, image_list):
        """ just rescale image size to show on image grid
        :param fdata_list: data file list, fullpath
        :param image_list: image file list, fullpath
        """
        if fdata_list == [] or image_list == []:
            return
        
        image_obj = []
        for (f_data, f_img) in zip(fdata_list, image_list):
            img = resizeImage(f_img, self.pxsize)
            name = ';;;'.join([f_img, f_data])
            image_obj.append(wx.StaticBitmap(self, wx.ID_ANY, 
                                             wx.BitmapFromImage(img),
                                             name=name))

        self.image_bitmap_obj = image_obj  # update bitmap objects
        wpsizer = wx.WrapSizer()
        for imgobj in image_obj:
            wpsizer.Add(imgobj, 0, wx.ALL, 4)
            imgobj.Bind(wx.EVT_RIGHT_DOWN, self.onRightClick)
            imgobj.Bind(wx.EVT_LEFT_DOWN, self.onLeftClick)
            name = imgobj.GetName()
            f_img, f_data = name.split(';;;')
            f_img_info = funutils.get_file_info(f_img)
            f_data_info = funutils.get_file_info(f_data)
            ttext = "Image filename: {img_n}\nData source: {data_n}\nCreate: {ctime}\nBytes: {s_i} [image], {s_d} [data]".format(
                    img_n=f_img_info['name'],
                    data_n=f_data_info['name'],
                    ctime=f_data_info['ctime'],
                    s_i=f_img_info['bytes'],
                    s_d=f_data_info['bytes'])
            imgobj.SetToolTip(wx.ToolTip(ttext))

        self.SetSizer(wpsizer)
        self.Layout()
        self.SetupScrolling()

    def onClear(self):
        """
        clear all objs on panel
        """
        for child in self.GetChildren():
            child.Destroy()
        self.image_bitmap_obj = []
        self.image_file_list = []
        self.wpsizer = wx.WrapSizer()

    def onScaleInc(self, percent, fdata_list, image_list):
        """
        enlarge image by percent
        """
        self.pxsize *= (1.0+percent)
        self.onClear()
        self.onScaleImageSize(fdata_list, image_list)

    def onScaleDec(self, percent, fdata_list, image_list):
        """
        shrink image by percent
        """
        self.pxsize *= (1.0-percent)
        self.onClear()
        self.onScaleImageSize(fdata_list, image_list)

class WorkspacePanel(wx.Panel):
    def __init__(self, parent, data=None):
        # input data format:
        # [['1', 'image1.jpg', 'hdf5'], ['2', 'image2.jpg', 'asc']]
        self.data = data
        wx.Panel.__init__(self, parent, -1)
        self.SetBackgroundColour('light grey')

        self._init_ui()

    def set_data(self, data):
        self.data = data

    def _init_ui(self):
        self.dv_lc = dv_lc = dv.DataViewListCtrl(self)

        # id, image file name, data file ext
        dv_lc.AppendTextColumn('ID',    width=30)
        dv_lc.AppendTextColumn('Image', width=-1)
        dv_lc.AppendTextColumn('Data',  width=-1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(dv_lc, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def clear(self):
        self.dv_lc.DeleteAllItems()

    def update(self, data):
        self.set_data(data)
        for itemval in self.data:
            self.dv_lc.AppendItem(itemval)

#class AnalysisFrame(wx.Frame):
#    def __init__(self, parent, datasrc, **kws):
#        wx.Frame.__init__(self, parent, **kws)
#        self.datasrc = datasrc
#
#        self.image_data = self.set_data(datasrc)
#        self._init_ui()
#
#    def set_data(self, datasrc):
#        f = h5py.File(datasrc, 'r')
#        data = f['image']['data'][...]
#        return data
#        #hx, hy = np.sum(data, 0), np.sum(data, 1)
#        #x, y = np.arange(hx.size), np.arange(hy.size)
#        #x0, sx = self._gaussian_fit(x, hx)
#        #y0, sy = self._gaussian_fit(y, hy)
#        #print x0, sx
#        #print y0, sy
# 
#
#    def _init_ui(self):
#        self.psplitter = wx.SplitterWindow(self, style=wx.SP_3D)
#        self.psplitter.SetSashGravity(0.7)
#        self.psplitter.SetMinimumPaneSize(200)
#        self.psplitter.Bind(wx.EVT_IDLE, self.psplitterOnIdle)
#
#        # left
#        self.psplitter_leftpanel  = wx.Panel(self.psplitter)
#        self.plotpanel = funutils.AnalysisPlotPanel(self.psplitter_leftpanel, self.image_data,
#                type='image', toolbar=True)
#        
#        vbox_l = wx.BoxSizer()
#        vbox_l.Add(self.plotpanel, 1, wx.EXPAND)
#
#        self.psplitter_leftpanel.SetSizerAndFit(vbox_l)
#        
#        # right
#        self.psplitter_rightpanel = wx.Panel(self.psplitter)
#        exit_btn = wx.Button(self.psplitter_rightpanel, label=u"E&xit")
#        vbox_r = wx.BoxSizer()
#        vbox_r.Add(exit_btn, 0)
#
#        self.psplitter_rightpanel.SetSizerAndFit(vbox_r)
#        
#        # set splitter
#        self.psplitter.SplitVertically(self.psplitter_leftpanel,
#                                       self.psplitter_rightpanel, 0)
#    
#        # plot sizer
#        p_sizer = wx.BoxSizer(wx.HORIZONTAL)
#        p_sizer.Add(self.psplitter, 1, wx.EXPAND, 0)
#
#        # main sizer
#        m_sizer = wx.BoxSizer()
#        m_sizer.Add(p_sizer, 1, wx.EXPAND, 10)
#        
#        self.SetSizerAndFit(m_sizer)
#
#        # events
#        self.Bind(wx.EVT_BUTTON, self.onExit, exit_btn)
#
#    def onExit(self, event):
#        self.Close(True)
#
#    def psplitterOnIdle(self, event):
#        self.psplitter.SetSashPosition(0)
#        self.psplitter.Unbind(wx.EVT_IDLE)
#        

class ProgressBarFrame(wx.Frame):
    def __init__(self, parent, title, range=100) :
        wx.Frame.__init__(self, parent=parent, title=title)
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

def test_data2Image():
    """
    test function Hdf2Image
    """
    data2Image('~/Desktop/20150923/data.hdf5', height=100, cmtype = 'jet')

def main():
    test_data2Image()

if __name__ == '__main__':
    main()
    
