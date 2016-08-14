#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
main launcher panel for all available apps from felapps

Author: Tong Zhang
Created: Oct. 8, 2015
"""

import wx
import time
from ...utils import miscutils
from ...utils import funutils
from ...utils import resutils

from .. import cornalyzer
from .. import dataworkshop
from .. import felformula
from .. import imageviewer
from .. import matchwizard
from .. import wxmpv
from beamline import ui_main as latticeviewer

import wx.lib.mixins.inspection as wit

DEBUG_FLAG = False

class AppDrawerFrame(wx.Frame):
    def __init__(self, parent, appversion='1.0', icon_set=None, **kwargs):
        wx.Frame.__init__(self, parent, **kwargs)  # style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        self.appversion = appversion
        if icon_set is None:
            icon_set = 'short'  # or 'long'
        self.icon_set = icon_set

        self.Bind(wx.EVT_CLOSE, self.onExit)

        # initialize UI
        self.initUI()

        self.SetIcon(resutils.aicon_s.GetIcon())

    def onExit(self, event):
        self.exitApp()

    def exitApp(self):
        dial = wx.MessageDialog(self, message="Are you sure to exit this application?",
                                caption='Exit Warning',
                                style=wx.YES_NO | wx.NO_DEFAULT | wx.CENTRE | wx.ICON_QUESTION)
        if dial.ShowModal() == wx.ID_YES:
            self.Destroy()

    def initUI(self):
        self.preInit()
        self.createMenubar()
        self.createPanel()
        # self.createStatusbar()
        self.createToolbar()
        self.postInit()
    
    def preInit(self):
        pass

    def postInit(self):
        pass

    def createMenubar(self):
        pass

    def createToolbar(self):
        pass

    def createStatusbar(self):
        self.statusbar = funutils.ESB.EnhancedStatusBar(self)
        self.statusbar.SetFieldsCount(3)
        self.SetStatusBar(self.statusbar)
        # self.statusbar.SetStatusWidths([-3,-1,-4,-1,-1])
        self.statusbar.SetStatusWidths([-7, -2, -1])

        self.statusbar.appinfo = wx.StaticText(self.statusbar, id=wx.ID_ANY, label=u"AppDrawer powered by Python")
        self.timenow_st        = wx.StaticText(self.statusbar, id=wx.ID_ANY, label=u"2015-06-05 14:00:00 CST")
        appversion             = wx.StaticText(self.statusbar, id=wx.ID_ANY, label=u" (Version: " + self.appversion + ")")
        #self.info_st = funutils.MyStaticText(self.statusbar, label = u'Status: ', fontcolor = 'red')
        #self.info    = funutils.MyStaticText(self.statusbar, label = u'',         fontcolor = 'red')

        self.statusbar.AddWidget(self.statusbar.appinfo, funutils.ESB.ESB_ALIGN_LEFT)
        #self.statusbar.AddWidget(self.info_st,           funutils.ESB.ESB_ALIGN_RIGHT)
        #self.statusbar.AddWidget(self.info,              funutils.ESB.ESB_ALIGN_LEFT )
        self.statusbar.AddWidget(self.timenow_st,        funutils.ESB.ESB_ALIGN_RIGHT)
        self.statusbar.AddWidget(appversion,             funutils.ESB.ESB_ALIGN_RIGHT)

    def createPanel(self):
        panel = AppDrawerPanel(self, self.appversion, self.icon_set)

        osizer = wx.BoxSizer(wx.HORIZONTAL)
        osizer.Add(panel, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER)
        self.SetSizerAndFit(osizer)


class AppDrawerPanel(wx.Panel):
    def __init__(self, parent, version, icon_set, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.version = version
        self.icon_set = icon_set

        self.timefmt='%Y-%m-%d %H:%M:%S %Z'

        self.createPanel()

    def createPanel(self):
        bkcolor = '#E1E1E1'
        self.SetBackgroundColour(funutils.hex2rgb(bkcolor))

        apptitle_st = funutils.MyStaticText(self, label=u"felapps \u2014 High-level Applications for FEL",
                                style=wx.ALIGN_CENTER, fontsize=20, fontweight=wx.FONTWEIGHT_NORMAL,
                                fontcolor='black')
        appver_st = funutils.MyStaticText(self, label=self.version,
                                style=wx.ALIGN_CENTER, fontsize=12, fontweight=wx.FONTWEIGHT_NORMAL,
                                fontcolor='grey')
        self.timenow_st = funutils.MyStaticText(self, label=time.strftime(self.timefmt, time.localtime()),
                                style=wx.ALIGN_CENTER, fontsize=14, fontweight=wx.FONTWEIGHT_NORMAL,
                                fontcolor='grey')

        applistname = ['C', 'D', 'F', 'I', 'L', 'W']
        
        if self.icon_set == 'short':
            applisticon = [resutils.cicon_s.GetBitmap(),
                           resutils.dicon_s.GetBitmap(),
                           resutils.ficon_s.GetBitmap(),
                           resutils.iicon_s.GetBitmap(),
                           resutils.licon_s.GetBitmap(),
                           resutils.wicon_s.GetBitmap(),
                           ]
        else:  # icon_set long
            applisticon = [resutils.cicon_l.GetBitmap(),
                           resutils.dicon_l.GetBitmap(),
                           resutils.ficon_l.GetBitmap(),
                           resutils.iicon_l.GetBitmap(),
                           resutils.licon_l.GetBitmap(),
                           resutils.wicon_l.GetBitmap(),
                           ]

        applistevent = [self.onClickAppC,
                        self.onClickAppD,
                        self.onClickAppF,
                        self.onClickAppI,
                        self.onClickAppL,
                        self.onClickAppW,
                        ]
        applisthint = ['run Correlation Analyzer' + '\n  Parameters Analysis Tool, e.g. SCAN',
                       'run Data Workshop' + '\n  Processing data generated from Imageviewer, e.g. AutoSaved HDF5 files',
                       'run FEL Formula' + '\n  Simple FEL physics calculations to grab the machine ideal performance',
                       'run Image Viewer' + '\n  Just feed with the waveform record PV string name',
                       'run Lattice Viewer' + '\n  Accelerator Online Modeling Tool',
                       'run Wx MatPlot Viewer' + '\n  Offline plot analysis tool for exported fitting data from Imageviewer',
                       ]
        self.nameicondict  = dict(zip(applistname, applisticon))
        self.nameeventdict = dict(zip(applistname, applistevent)) 
        self.namehintdict  = dict(zip(applistname, applisthint))
        
        apps_cnt = len(applistname)
        if self.icon_set == 'short':
            gsizer = wx.GridSizer(1, apps_cnt, 0, 0)
        else:
            gsizer = wx.GridSizer(3, apps_cnt/3, 0, 0)
            
        for appname in sorted(self.nameicondict.keys()):
            appobj = wx.BitmapButton(self, bitmap=self.nameicondict[appname], style=wx.BORDER_NONE)
            appobj.SetToolTip(wx.ToolTip(self.namehintdict[appname]))
            self.Bind(wx.EVT_BUTTON, self.nameeventdict[appname], appobj)
            gsizer.Add(appobj, flag=wx.LEFT | wx.RIGHT, border=10)

        mainsizer = wx.BoxSizer(wx.VERTICAL)
        mainsizer.Add(apptitle_st,     flag=wx.ALIGN_CENTER | wx.TOP,               border=5)
        mainsizer.Add(appver_st,       flag=wx.ALIGN_CENTER | wx.BOTTOM | wx.TOP,   border=1)
        mainsizer.Add(self.timenow_st, flag=wx.ALIGN_CENTER | wx.BOTTOM,            border=5)
        mainsizer.Add(gsizer, flag = wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT | wx.TOP, border=5)
        mainsizer.Add((-1, 10))
        self.SetSizer(mainsizer)

        # timer
        self.timernow = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTickTime, self.timernow)
        self.timernow.Start(1000)

    def onClickAppC(self, event):
        cornalyzer.cornalyzer.run(debug=DEBUG_FLAG)

    def onClickAppD(self, event):
        dataworkshop.dataworkshop.run(debug=DEBUG_FLAG)

    def onClickAppF(self, event):
        felformula.felformula.run(debug=DEBUG_FLAG)

    def onClickAppI(self, event):
        imageviewer.imageviewer.run(debug=DEBUG_FLAG)

    def onClickAppM(self, event):
        matchwizard.matchwizard.run(debug=DEBUG_FLAG)

    def onClickAppL(self, event):
        icon = resutils.licon_s.GetIcon()
        latticeviewer.run(debug=DEBUG_FLAG, icon=icon)

    def onClickAppW(self, event):
        wxmpv.wxmpv.run(debug=DEBUG_FLAG)

    def onTickTime(self, event):
        self.timenow_st.SetLabel(time.strftime(self.timefmt, time.localtime()))

#========================================================================================================
__version__ =  miscutils.AppVersions().getVersion('appdrawer')
__author__  = "Tong Zhang"

class InspectApp(wx.App, wit.InspectionMixin):
    def OnInit(self):
        self.Init()

        myframe = AppDrawerFrame(None, title=u'App Drawer \u2014 Apps collection of felapps (debug mode, CTRL+ALT+I)', 
                appversion=__version__, style=wx.DEFAULT_FRAME_STYLE)
        myframe.Show()
        self.SetTopWindow(myframe)
        return True

def run(maximize=True, logon=False, debug=True, **kws):
    """
    function to make appdrawer app run.
    """
    icon_set=kws.get('icon_set')
    if debug:
        app = InspectApp()
        app.MainLoop()
    else:
        app = wx.App(redirect = logon, filename='log')

        if maximize:
            myframe = AppDrawerFrame(None, title=u'App Drawer \u2014 Apps collection of felapps', 
                    appversion=__version__, icon_set=icon_set, style=wx.DEFAULT_FRAME_STYLE)
        else:
            myframe = AppDrawerFrame(None, title=u'App Drawer \u2014 Apps collection of felapps', 
                    appversion=__version__, icon_set=icon_set, style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        myframe.Show()
        app.MainLoop()

if __name__ == '__main__':
    #run(icon_set='short')
    run(icon_set='long', debug=False)
