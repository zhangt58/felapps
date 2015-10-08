#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
python modules for data processing utilities:
    dataworkshop: main GUI framework for data post-processing

Author: Tong Zhang
Created: Sep. 23rd, 2015
"""

import wx
import time
import threading
import numpy as np
import matplotlib.pyplot as plt
import h5py

from . import funutils
from . import pltutils
from . import imageutils
from . import resutils

class DataWorkshop(wx.Frame):
    def __init__(self, parent, config = 'config.xml', size = (1000, 750), appversion = '1.0', **kwargs):
        super(self.__class__, self).__init__(parent = parent, size = size, id = wx.ID_ANY, **kwargs) #style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        self.parent = parent
        self.appversion = appversion

        self.Bind(wx.EVT_CLOSE, self.onExit)

        # initialize UI
        self.initUI()

        # timer
        self.timernow = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTickTime, self.timernow)
        self.timernow.Start(1000)
 
    def onTickTime(self, event):
        fmt='%Y-%m-%d %H:%M:%S %Z'
        self.timenow_st.SetLabel(time.strftime(fmt, time.localtime()))

    def initUI(self):
        self.preInit()
        self.createMenubar()
        self.createPanel()
        self.createStatusbar()
        self.createToolbar()
        self.postInit()

    def createMenubar(self):
        self.menubar = wx.MenuBar()
        
        ## File menu
        fileMenu = wx.Menu()
        openItem = fileMenu.Append(wx.ID_OPEN, '&Open file\tCtrl+O', 'Open file to view')
        saveItem = fileMenu.Append(wx.ID_SAVE, '&Save\tCtrl+S',      'Save')
        fileMenu.AppendSeparator()
        exitItem = fileMenu.Append(wx.ID_EXIT, 'E&xit\tCtrl+W', 'Exit application')
        self.Bind(wx.EVT_MENU, self.onOpen, id = openItem.GetId())
        self.Bind(wx.EVT_MENU, self.onSave, id = saveItem.GetId())
        self.Bind(wx.EVT_MENU, self.onExit, id = exitItem.GetId())
        
        ## Configurations menu
        configMenu = wx.Menu()
        loadConfigItem = configMenu.Append(wx.ID_ANY, 'Load from file\tCtrl+Shift+L', 'Loading configurations from file')
        saveConfigItem = configMenu.Append(wx.ID_ANY, 'Save to file\tCtrl+Shift+S',   'Saving configurations to file')
        appsConfigItem = configMenu.Append(wx.ID_ANY, 'Preferences\tCtrl+Shift+I',    'Preferences for application')
        self.Bind(wx.EVT_MENU, self.onConfigLoad, id = loadConfigItem.GetId())
        self.Bind(wx.EVT_MENU, self.onConfigSave, id = saveConfigItem.GetId())
        self.Bind(wx.EVT_MENU, self.onConfigApps, id = appsConfigItem.GetId())
        
        ## Help menu
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT, '&About\tF1', 'Show about information')
        self.Bind(wx.EVT_MENU, self.onAbout, id = wx.ID_ABOUT)
        
        ## make menu
        self.menubar.Append(fileMenu,   '&File')
        self.menubar.Append(configMenu, '&Configurations')
        self.menubar.Append(helpMenu,   '&Help')
        
        ## set menu
        self.SetMenuBar(self.menubar)

        self.Bind(wx.EVT_MENU_HIGHLIGHT, self.onMenuHL)

    def onMenuHL(self, event):
        try:
            hltext = event.GetEventObject().GetHelpString(event.GetMenuId())
            self.statusbar.appinfo.SetLabel(hltext)
        except:
            pass

    def onAbout(self, event):
        try:
            from wx.lib.wordwrap import wordwrap
        except:
            dial = wx.MessageDialog(self, message = u"Cannot show about information, sorry!",
                    caption = u"Unknow Error", 
                    style = wx.OK | wx.CANCEL | wx.ICON_ERROR | wx.CENTRE)
            if dial.ShowModal() == wx.ID_OK:
                dial.Destroy()
        info = wx.AboutDialogInfo()
        info.Name = "DataWorkshop"
        info.Version = self.appversion
        info.Copyright = "(C) 2014-2015 Tong Zhang, SINAP, CAS"
        info.Description = wordwrap(
            "This application is created for data post-processing.\n"

            "It is designed by Python language, using GUI module of wxPython.",
            350, wx.ClientDC(self))
        info.WebSite = ("", "Cornalyzer home page") # fill it when webpage is ready
        info.Developers = [ "Tong Zhang <zhangtong@sinap.ac.cn>"]
        licenseText = "DataWorkshop is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.\n" + "\nDataWorkshop is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.\n" + "\nYou should have received a copy of the GNU General Public License along with DataWorkshop; if not, write to the Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA"
        info.License = wordwrap(licenseText, 500, wx.ClientDC(self))
        wx.AboutBox(info)

    def preInit(self):
        self.fontsize_button     = 12 
        self.fontsize_statictext = 12
        self.fontsize_staticbox  = 10
        self.fontsize_textctrl   = 12
        self.backcolor_panel     = '#DDDDDD'
        self.fontcolor_staticbox = '#4B4B4B'
        self.bordersize          = 12
 
    def postInit(self):
        pass

    def onConfigLoad(self, event):
        pass

    def onConfigSave(self, event):
        pass

    def onConfigApps(self, event):
        pass

    def onOpen(self, event):
        """
        select data files to be visulized in imagegrid panel
        """
        self.datafiles = funutils.getFileToLoad(self, ext = '*', flag = 'multi')
        self.imggrid.onClear()
        self.visData_thread(self.datafiles)
        #self.visData(datafile)

    def onSave(self, event):
        pass

    def onExit(self, event):
        self.exitApp()

    def exitApp(self):
        dial = wx.MessageDialog(self, message = "Are you sure to exit this application?",
                                caption = 'Exit Warning',
                                style = wx.YES_NO | wx.NO_DEFAULT | wx.CENTRE | wx.ICON_QUESTION)
        if dial.ShowModal() == wx.ID_YES:
            self.Destroy()

    def createStatusbar(self):
        self.statusbar = funutils.ESB.EnhancedStatusBar(self)
        self.statusbar.SetFieldsCount(5)
        self.SetStatusBar(self.statusbar)
        self.statusbar.SetStatusWidths([-3,-1,-4,-1,-1])

        self.statusbar.appinfo = wx.StaticText(self.statusbar, id = wx.ID_ANY, label = u"DataWorkshop powered by Python")
        self.timenow_st        = wx.StaticText(self.statusbar, id = wx.ID_ANY, label = u"2015-06-05 14:00:00 CST")
        appversion             = wx.StaticText(self.statusbar, id = wx.ID_ANY, label = u" (Version: " + self.appversion + ")")
        self.info_st = funutils.MyStaticText(self.statusbar, label = u'Status: ', fontcolor = 'red')
        self.info    = funutils.MyStaticText(self.statusbar, label = u'',         fontcolor = 'red')

        self.statusbar.AddWidget(self.statusbar.appinfo, funutils.ESB.ESB_ALIGN_LEFT )
        self.statusbar.AddWidget(self.info_st,           funutils.ESB.ESB_ALIGN_RIGHT)
        self.statusbar.AddWidget(self.info,              funutils.ESB.ESB_ALIGN_LEFT )
        self.statusbar.AddWidget(self.timenow_st,        funutils.ESB.ESB_ALIGN_RIGHT)
        self.statusbar.AddWidget(appversion,             funutils.ESB.ESB_ALIGN_RIGHT)

    def createToolbar(self):
        pass

    def createPanel(self):
        # make background panel
        self.panel = funutils.createwxPanel(self, funutils.hex2rgb('#B1B1B1'))

        # layout
        sizer_l = wx.BoxSizer(wx.HORIZONTAL) # put panel_l wrapped sbsizer
        sizer_r = wx.BoxSizer(wx.HORIZONTAL) # put panel_r wrapped sbsizer

        # left and right panels
        self.panel_l = funutils.createwxPanel(self.panel, funutils.hex2rgb(self.backcolor_panel))
        self.panel_r = funutils.createwxPanel(self.panel, funutils.hex2rgb(self.backcolor_panel))

        ## --------hbox-------
        ## toolbar
        ##   vleft    vright
        ## |-------|----------|
        ## |       |          |
        ## |       |          |
        ## |       |          |
        ## |panel_l| panel_r  |
        ## |       |          |
        ## |       |          |
        ## |       |          |
        ## |-------|----------|
        ## statusbar
        ##

        hbox   = wx.BoxSizer(wx.HORIZONTAL)
        vleft  = wx.BoxSizer(wx.VERTICAL  )
        vright = wx.BoxSizer(wx.VERTICAL  )

        # vleft box
        ## control panel
        controlpanel_sb = funutils.createwxStaticBox(self.panel_l, label = 'Control Panel', fontcolor=funutils.hex2rgb(self.fontcolor_staticbox), fontsize = self.fontsize_staticbox)
        controlpanel_sbsizer = wx.StaticBoxSizer(controlpanel_sb, wx.VERTICAL)


        # push button controls for image post-processing
        animate_btn    = wx.Button(self.panel_l, label = 'Make Animation')
        statistics_btn = wx.Button(self.panel_l, label = 'Statistics'    )

        hbox1 = wx.BoxSizer(wx.VERTICAL)
        hbox1.Add(animate_btn,    proportion = 0, flag = wx.EXPAND | wx.ALL, border = 10)
        hbox1.Add(statistics_btn, proportion = 0, flag = wx.EXPAND | wx.ALL, border = 10)

        ## bindings
        self.Bind(wx.EVT_BUTTON, self.onAnimate,    animate_btn   )
        self.Bind(wx.EVT_BUTTON, self.onStatistics, statistics_btn)

        # image style controls
        imgscale_st = funutils.MyStaticText(self.panel_l, label = 'Image Size (+/-)', fontcolor = 'blue')
        scale_inc_btn = wx.BitmapButton(self.panel_l, bitmap = resutils.addicon.GetBitmap())
        scale_dec_btn = wx.BitmapButton(self.panel_l, bitmap = resutils.delicon.GetBitmap())

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(imgscale_st,   proportion = 0, flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        hbox2.Add(scale_inc_btn, proportion = 0, flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL,             border = 10)
        hbox2.Add(scale_dec_btn, proportion = 0, flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,  border = 10)
        
        ## bindings
        self.Bind(wx.EVT_BUTTON, self.onScaleInc, scale_inc_btn)
        self.Bind(wx.EVT_BUTTON, self.onScaleDec, scale_dec_btn)

        # left panel sizer
        controlpanel_sbsizer.Add(hbox1, flag = wx.ALIGN_CENTER | wx.ALL, proportion = 0, border = 10)
        controlpanel_sbsizer.Add(wx.StaticLine(self.panel_l, style = wx.LI_HORIZONTAL), flag = wx.EXPAND | wx.ALL, border = 10)
        controlpanel_sbsizer.Add(hbox2, flag = wx.ALIGN_LEFT | wx.ALL, proportion = 0, border = 10)
        
        
        # vright box
        ## image grid panel
        imagegridpanel_sb = funutils.createwxStaticBox(self.panel_r, label = 'Image Grid', fontcolor=funutils.hex2rgb(self.fontcolor_staticbox), fontsize = self.fontsize_staticbox)
        imagegridpanel_sbsizer = wx.StaticBoxSizer(imagegridpanel_sb, wx.HORIZONTAL)

        ## image plotting frame
        #self.imggrid = ImageGrid(self.panel_r, figsize = (4, 4), dpi = 75, bgcolor = funutils.hex2rgb(self.backcolor_panel))
        self.imggrid = imageutils.ImageGalleryPanel(self.panel_r)


        gsr = wx.BoxSizer(wx.HORIZONTAL)
        gsr.Add(self.imggrid, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 10)

        imagegridpanel_sbsizer.Add(gsr, proportion = 1, flag = wx.EXPAND)


        # set sizers

        ## left
        sizer_l.Add(controlpanel_sbsizer, proportion = 1, flag = wx.EXPAND | wx.ALL, border = self.bordersize)
        self.panel_l.SetSizerAndFit(sizer_l)
        vleft.Add(self.panel_l, proportion = 1, flag = wx.EXPAND)

        ## right
        sizer_r.Add(imagegridpanel_sbsizer, proportion = 1, flag = wx.EXPAND | wx.TOP | wx.BOTTOM | wx.RIGHT, border = self.bordersize)
        self.panel_r.SetSizerAndFit(sizer_r)
        vright.Add(self.panel_r, proportion = 1, flag = wx.EXPAND)
        
        # main sizer
        hbox.Add(vleft,  proportion = 1, flag = wx.EXPAND)
        hbox.Add(vright, proportion = 3, flag = wx.EXPAND)
        self.panel.SetSizer(hbox)
        osizer = wx.BoxSizer(wx.HORIZONTAL)
        osizer.SetMinSize((1000, 750))
        osizer.Add(self.panel, proportion = 1, flag = wx.EXPAND)
        self.SetSizerAndFit(osizer)

    def onAnimate(self, event):
        import shutil, glob, os, subprocess
        newpathdir = './imagetemp/'
        if not os.path.exists(newpathdir):
            os.mkdir(newpathdir)
        cnt = 0
        for imagefile in sorted(self.jpglist):
            cnt += 1
            shutil.copyfile(imagefile, os.path.join(newpathdir, ('image%03d.jpg' % cnt)))

        """
        for file in glob.glob(newpathdir + '/' + 'image0*.jpg'):
             print file
        """
        
        try:
            # create animation
            fps = 1
            moviename = 'output.avi'
            cmdline = ' '.join(['mencoder', '-fps', str(fps), '"mf://' + newpathdir + os.sep + 'image%03d.jpg"', '-o', moviename, '-ovc copy -oac copy'])
            subprocess.call(cmdline, shell=True)
        
            # show indication message
            dial = wx.MessageDialog(self, message = u"Animation successfully created!",
                    caption = u"Job done", 
                    style = wx.OK | wx.CANCEL | wx.CENTRE)
            if dial.ShowModal() == wx.ID_OK:
                dial.Destroy()
        except:
            dial = wx.MessageDialog(self, message = u"Animation creation failed!",
                    caption = u"Job failed", 
                    style = wx.OK | wx.CANCEL | wx.ICON_ERROR | wx.CENTRE)
            if dial.ShowModal() == wx.ID_OK:
                dial.Destroy()

    def onStatistics(self, event):
        self.statFrame = StatPanel(self, self.datafiles)
        self.statFrame.SetTitle('Statistical Analysis')
        #self.statFrame.SetMinSize((800, 600))
        self.statFrame.Show()

    def onScaleInc(self, event):
        self.imggrid.onScaleInc(0.1)

    def onScaleDec(self, event):
        self.imggrid.onScaleDec(0.1)

    def visData(self, datafilename):
        """
        read data file and show images on right panel
        """
        filenum = datafilename.__len__()
        self.jpglist = []

        """
        # threading approach, fancy
        self.progressbar = imageutils.ProgressBarFrame(self, 'Loading Data...', filenum)
        self.progressbar.MakeModal(True)
        dataProcessWorker = WorkerThread(self, self.progressbar, filenum, datafilename)
        dataProcessWorker.start()
        """
        
        # normal approach, not user-friendly, especially loading bunch of data files
        filecnt = 0
        for file in datafilename:
            filecnt += 1
            ftype = file.split('.')[-1]
            if ftype == 'hdf5': # hdf5 data file
                self.jpglist.append(imageutils.data2Image(file, datatype = 'hdf5'))
            elif ftype == 'dat' or ftype == 'asc':
                self.jpglist.append(imageutils.data2Image(file, datatype = 'asc'))

            print "Loading: %d/%d" %(filecnt, filenum) # need to be realized in threading approach
                
        # show images on right panel
        self.updateImageGrid()

    def updateImageGrid(self):
        self.imggrid.onUpdate(self.jpglist)

    def visData_thread(self, datafilename):
        """
        read data file and show images on right panel
        """
        filenum = datafilename.__len__()
        self.jpglist = []

        self.progressbar = imageutils.ProgressBarFrame(self, 'Loading Data...', filenum)
        self.progressbar.MakeModal(True)
        self.dataProcessWorker = WorkerThread(self, self.progressbar, filenum, datafilename)
        self.dataProcessWorker.start()
        
        # show images on right panel
        #self.updateImageGrid()
    def onStopWorker(self):
        self.dataProcessWorker.stop()
        self.info.SetLabel('Complete loading data')

class WorkerThread(threading.Thread):
    def __init__(self, parent, target, countNum, datafilename):
        threading.Thread.__init__(self, target = target)
        #self.setDaemon(True)
        self.parent = parent # point to the parent, here is DataWorkshop
        self.cnt = countNum
        self.target = target # point to progressbarframe
        self.pb = self.target.pb # point to progressbarframe.gauge
        self.datafilename = datafilename
        self.filecnt = 0

        self.quitflag = threading.Event()
        self.quitflag.clear()
    
    def stop(self):
        self.quitflag.set()

    def run(self):
        for file in self.datafilename:
            if self.quitflag.isSet():
                break
            self.filecnt += 1
            ftype = file.split('.')[-1]
            if ftype == 'hdf5': # hdf5 data file
                #time.sleep(0.2)
                self.parent.jpglist.append(imageutils.data2Image(file, datatype = 'hdf5'))
            elif ftype == 'dat' or ftype == 'asc':
                self.parent.jpglist.append(imageutils.data2Image(file, datatype = 'asc'))
            wx.CallAfter(self.pb.SetValue, self.filecnt)

        #wx.CallAfter(self.target.info.SetLabel, ("%d of %d loaded." % (self.filecnt, self.cnt)))
        wx.CallAfter(self.target.MakeModal, False)
        wx.CallAfter(self.target.Close)
        wx.CallAfter(self.parent.updateImageGrid)
        wx.CallAfter(self.parent.onStopWorker)

class StatPanel(wx.Frame):
    def __init__(self, parent, datafiles, **kwargs):
        super(self.__class__, self).__init__(parent = parent,
                id = wx.ID_ANY, style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX), **kwargs)
        self.parent = parent
        self.datafiles = datafiles
        self.shotIDArray = np.arange(1, self.datafiles.__len__()+1)
        self.InitUI()

    def InitUI(self):
        self.createPanel()
        self.postInit()

    def createPanel(self):
        self.panel = wx.Panel(self)

        # layout:
        #    lv_hbox
        # lvbox | rvbox
        #

        # left hbox
        showint_btn     = wx.Button(self.panel, label = 'Intensity Plot', size = (120, -1), style = wx.BU_LEFT)
        showinthist_btn = wx.Button(self.panel, label = 'Intensity Hist', size = (120, -1), style = wx.BU_LEFT)
        showxypos_btn   = wx.Button(self.panel, label = 'Central Pos',    size = (120, -1), style = wx.BU_LEFT)
        showradius_btn  = wx.Button(self.panel, label = 'Radius',         size = (120, -1), style = wx.BU_LEFT)

        showint_st     = funutils.MyStaticText(self.panel, label = 'Intensity',        size = (160, -1))
        showinthist_st = funutils.MyStaticText(self.panel, label = 'Intensity hist',   size = (160, -1))
        showxypos_st   = funutils.MyStaticText(self.panel, label = 'Central position', size = (160, -1))
        showradius_st  = funutils.MyStaticText(self.panel, label = 'Radius',           size = (160, -1))
        
        gbs = wx.GridBagSizer(10, 5)
        gbs.Add(showint_btn,     pos = (0, 0), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 8)
        gbs.Add(showint_st,      pos = (0, 1), span = (1, 3), flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 8)
        gbs.Add(showinthist_btn, pos = (1, 0), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 8)
        gbs.Add(showinthist_st,  pos = (1, 1), span = (1, 3), flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 8)
        gbs.Add(showxypos_btn,   pos = (2, 0), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 8)
        gbs.Add(showxypos_st,    pos = (2, 1), span = (1, 3), flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 8)
        gbs.Add(showradius_btn,  pos = (3, 0), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 8)
        gbs.Add(showradius_st,   pos = (3, 1), span = (1, 3), flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 8)
        gbs.AddGrowableCol(1)
        gbs.AddGrowableCol(2)

        lvbox = wx.BoxSizer(wx.VERTICAL)
        lvbox.Add(gbs, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 10)
        
        # right vbox
        self.plotpanel = PlotPanel(self.panel, figsize=(5,5), dpi = 80, bgcolor = None)

        rvbox = wx.BoxSizer(wx.VERTICAL)
        rvbox.Add(self.plotpanel, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 4)
        
        # left and right hbox
        lr_hbox = wx.BoxSizer(wx.HORIZONTAL)
        lr_hbox.Add(lvbox, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 4)
        lr_hbox.Add(rvbox, proportion = 2, flag = wx.EXPAND | wx.ALL, border = 4)

        # cmd hbox sizer
        cmdhbox    = wx.BoxSizer(wx.HORIZONTAL)
        ok_btn     = funutils.MyButton(self.panel, label = 'OK')
        cancel_btn = funutils.MyButton(self.panel, label = 'Cancel')
        cmdhbox.Add(cancel_btn, proportion = 0, flag = wx.RIGHT, border = 10)
        cmdhbox.Add(ok_btn,     proportion = 0, flag = wx.TOP | wx.BOTTOM | wx.RIGHT, border = 0)
        
        # main sizer
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        mainsizer.Add(lr_hbox, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 10)
        mainsizer.Add(wx.StaticLine(self.panel, wx.LI_HORIZONTAL), 0, wx.EXPAND | wx.ALL, 10)
        mainsizer.Add((-1, 10))
        mainsizer.Add(cmdhbox,  proportion = 0, flag = wx.ALIGN_RIGHT | wx.BOTTOM | wx.RIGHT, border = 10)

        self.panel.SetSizer(mainsizer)
        osizer = wx.BoxSizer(wx.VERTICAL)
        osizer.Add(self.panel, proportion = 1, flag = wx.EXPAND)
        self.SetSizerAndFit(osizer)
        
        # event bindings
        self.Bind(wx.EVT_BUTTON, self.onIntensityStat,     showint_btn    )
        self.Bind(wx.EVT_BUTTON, self.onIntensityStatHist, showinthist_btn)
        self.Bind(wx.EVT_BUTTON, self.onCentralPosStat,    showxypos_btn  )
        self.Bind(wx.EVT_BUTTON, self.onRadiusStat,        showradius_btn )
        self.Bind(wx.EVT_BUTTON, self.onOK,                ok_btn         )
        self.Bind(wx.EVT_BUTTON, self.onCancel,            cancel_btn     )
    
    def onOK(self, event):
        self.Close(True)

    def onCancel(self, event):
        self.Close(True)

    def postInit(self):
        pass

    def onIntensityStatHist(self, event):
        self.statIntArray = np.array([h5py.File(file, 'r')['image']['data'].attrs['sumint'] for file in self.datafiles])

        self.plotpanel.y = self.statIntArray
        self.plotpanel.clear()
        self.plotpanel.doHist()
        self.plotpanel.axes.set_title('Intensity Histogram')
        self.plotpanel.axes.set_xlabel('Intensity value [a.u.]')
        self.plotpanel.axes.set_ylabel('Count')
        self.plotpanel.refresh()

    def onIntensityStat(self, event):
        self.statIntArray = np.array([h5py.File(file, 'r')['image']['data'].attrs['sumint'] for file in self.datafiles])

        self.plotpanel.x = self.shotIDArray
        self.plotpanel.y = self.statIntArray
        """
        self.plotpanel.xyplot.set_marker('o')
        self.plotpanel.xyplot.set_markersize(4)
        self.plotpanel.xyplot.set_markerfacecolor('b')
        self.plotpanel.xyplot.set_markeredgecolor('b')
        self.plotpanel.xyplot.set_linestyle('-')
        self.plotpanel.xyplot.set_color('r')
        """
        self.plotpanel.clear()
        self.plotpanel.doXYplot()
        self.plotpanel.axes.set_title('Intensity')
        self.plotpanel.axes.set_xlabel('shot ID')
        self.plotpanel.axes.set_ylabel('[a.u.]')
        self.plotpanel.refresh()

    def onCentralPosStat(self, event):
        self.statXYPosArray = np.array([h5py.File(file, 'r')['image']['data'].attrs['xypos'] for file in self.datafiles])

        self.plotpanel.x = self.statXYPosArray[:,0]
        self.plotpanel.y = self.statXYPosArray[:,1]

        self.plotpanel.clear()
        self.plotpanel.doScatter()
        self.plotpanel.axes.set_title('XY pos')
        self.plotpanel.axes.set_xlabel('X')
        self.plotpanel.axes.set_ylabel('Y')
        self.plotpanel.refresh()

    def onRadiusStat(self, event):
        pass

class PlotPanel(pltutils.ImagePanelxy):
    def __init__(self, parent, figsize, dpi, bgcolor, **kwargs):
        pltutils.ImagePanelxy.__init__(self, parent, figsize, dpi, bgcolor, **kwargs)
#        self.axes.set_aspect('equal')

    def doXYplot(self):
        self.axes = self.figure.add_subplot(111)
        self.axes.plot(self.x, self.y)
        self.figure.canvas.draw()

    def doHist(self):
        self.axes = self.figure.add_subplot(111)
        self.axes.hist(self.y, 100)
        self.figure.canvas.draw()

    def doScatter(self):
        self.axes = self.figure.add_subplot(111)
        self.axes.scatter(self.x, self.y)
        self.figure.canvas.draw()
    
    def clear(self):
        self.figure.clear()

    def refresh(self):
        self.figure.canvas.draw_idle()

# ImageGrid: do not use this now
class ImageGrid(pltutils.ImagePanel):
    def __init__(self, parent, figsize, dpi, bgcolor, **kwargs):
        pltutils.ImagePanel.__init__(self, parent, figsize, dpi, bgcolor, **kwargs)

    def doPlot(self):
        if not hasattr(self, 'axes'):
            self.axes = self.figure.add_subplot(111)
        self.im = self.axes.imshow(self.z, aspect = 'equal', cmap = plt.get_cmap(self.cmaptype), 
                                   origin = 'lower left', vmin = self.cmin, vmax = self.cmax)
        #self.figure.colorbar(self.im, orientation = 'horizontal', aspect = 20, shrink = 0.95, 
        #                     fraction = 0.05, pad = 0.1)
        self.figure.canvas.draw()

    def onGetData(self):
        if self.func == 'peaks':
            x = np.linspace(-np.pi, np.pi, 100)
            y = np.linspace(-np.pi, np.pi, 100)
            self.x, self.y = np.meshgrid(x, y)
            self.z = funutils.func_peaks(self.x, self.y)
        elif self.func == 'sinc':
            x = np.linspace(-2*np.pi, 2*np.pi, 100)
            y = np.linspace(-2*np.pi, 2*np.pi, 100)
            self.x, self.y = np.meshgrid(x, y)
            self.z = funutils.func_sinc(self.x, self.y)
        self.cmin = self.z.min()
        self.cmax = self.z.max()

    def repaint(self):
        self.figure.canvas.draw_idle()

    def onMotion(self, event):
        try:
            x, y = event.xdata, event.ydata
            idx, idy = int(x+0.5), int(y+0.5)
            zval = self.z[idx, idy]
            self.GetParent().img_pos.SetLabel("(%.4f, %.4f, %.4f)" % (x, y, zval))
        except TypeError:
            pass
    
    def onPress(self, event):
        try:
            x, y= event.xdata, event.ydata
            idx, idy = int(x+0.5), int(y+0.5)
            print x,y,idx,idy,self.x[idx,idy], self.y[idx,idy], self.z[idx,idy]
            self.GetParent().img_pos.SetLabel("(%.4f, %.4f)" % (event.xdata, event.ydata))
        except TypeError:
            pass

