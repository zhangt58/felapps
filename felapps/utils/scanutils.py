#!/usr/bin/env python
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------#

"""
Author: Tong Zhang
Created Time: 09:26, Jun. 29, 2015

Scan utilities: (p.s.) separated from felutils.py
    1 correlation analyzer:
    1.1: ScanAnalyzer
"""

import wx
import epics
import time
import os
import numpy as np
from . import funutils
from . import pltutils
from . import parseutils
import matplotlib.pyplot as plt
import threading

#------------------------------------------------------------------------#
class ScanAnalyzer(wx.Frame):
    def __init__(self, parent, size = (800, 600), appversion = '1.0', **kwargs):
        super(self.__class__, self).__init__(parent = parent, size = size, id = wx.ID_ANY, **kwargs)
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
        self.createStatusbar()
        self.createPanel()
        self.postInit()

    def createMenubar(self):
        self.menubar = wx.MenuBar()
        
        ## File menu
        fileMenu = wx.Menu()
        openItem = fileMenu.Append(wx.ID_OPEN, '&Open file\tCtrl+O', 'Open file to view')
        saveItem = fileMenu.Append(wx.ID_SAVE, '&Save Plot\tCtrl+S', 'Save plotting to file')
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
        info.Name = "Cornalyzer"
        info.Version = self.appversion
        info.Copyright = "(C) 2014-2015 Tong Zhang, SINAP, CAS"
        info.Description = wordwrap(
            "This application is created for correlation analysis of parameters.\n"

            "It is designed by Python language, using GUI module of wxPython.",
            350, wx.ClientDC(self))
        info.WebSite = ("http://everyfame.me", "Cornalyzer home page")
        info.Developers = [ "Tong Zhang <zhangtong@sinap.ac.cn>"]
        licenseText = "Cornalyzer is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.\n" + "\nCornalyzer is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.\n" + "\nYou should have received a copy of the GNU General Public License along with Cornalyzer; if not, write to the Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA"
        info.License = wordwrap(licenseText, 500, wx.ClientDC(self))
        wx.AboutBox(info)

    def onConfigLoad(self, event):
        pass

    def onConfigSave(self, event):
        pass

    def onConfigApps(self, event):
        pass

    def onOpen(self, event):
        pass

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
        self.statusbar.SetFieldsCount(3)
        self.SetStatusBar(self.statusbar)
        self.statusbar.SetStatusWidths([-7,-2,-1])
        self.statusbar.appinfo = wx.StaticText(self.statusbar, id = wx.ID_ANY, label = "Correlation Analyzer powered by Python")
        self.timenow_st        = wx.StaticText(self.statusbar, id = wx.ID_ANY, label = "2015-06-05 14:00:00 CST")
        appversion             = wx.StaticText(self.statusbar, id = wx.ID_ANY, label = " (Version: " + self.appversion + ")")
        self.statusbar.AddWidget(self.statusbar.appinfo, funutils.ESB.ESB_ALIGN_LEFT )
        self.statusbar.AddWidget(self.timenow_st,        funutils.ESB.ESB_ALIGN_RIGHT)
        self.statusbar.AddWidget(appversion,             funutils.ESB.ESB_ALIGN_RIGHT)

    def createPanel(self):
        # background panel
        self.panel    = funutils.createwxPanel(self,       funutils.hex2rgb('#B1B1B1'))
        # background sizer
        sizer1 = wx.BoxSizer(wx.HORIZONTAL) # put panel_l  wrapped sbsizer
        sizer2 = wx.BoxSizer(wx.HORIZONTAL) # put panel_ru wrapped sbsizer
        sizer3 = wx.BoxSizer(wx.HORIZONTAL) # put panel_rd wrapped sbsizer

        # three sub-panels
        self.panel_l  = funutils.createwxPanel(self.panel, funutils.hex2rgb(self.backcolor_panel))
        self.panel_ru = funutils.createwxPanel(self.panel, funutils.hex2rgb(self.backcolor_panel))
        self.panel_rd = funutils.createwxPanel(self.panel, funutils.hex2rgb(self.backcolor_panel))
        
        ## --------hbox---------- 
        ##   vleft     vright
        ## |-------|------------|
        ## |       |            |
        ## |       | vrigh1     |
        ## | vleft |------------|
        ## |       |            |
        ## |       |            |
        ## |       | vright2    |
        ## |       |            |
        ## |-------|------------|
        ##

        hbox     = wx.BoxSizer(wx.HORIZONTAL)
        vleft    = wx.BoxSizer(wx.VERTICAL  )
        vright   = wx.BoxSizer(wx.VERTICAL  )
        vright1  = wx.BoxSizer(wx.HORIZONTAL)
        vright2  = wx.BoxSizer(wx.HORIZONTAL)

        # vleft
        controlpanel_sb = funutils.createwxStaticBox(self.panel_l, label = 'Control Panel', fontcolor=funutils.hex2rgb(self.fontcolor_staticbox), fontsize = self.fontsize_staticbox)
        controlpanel_sbsizer = wx.StaticBoxSizer(controlpanel_sb, wx.VERTICAL)

        # grid sizer for horizontal entries
        gs = wx.GridBagSizer(5, 5)

        # X-AXIS input: PV name value
        self.xaxis_set_st      = funutils.MyStaticText(self.panel_l, label = 'X-AXIS (SET TO)'  )
        self.xaxis_get_st      = funutils.MyStaticText(self.panel_l, label = 'X-AXIS (GET FROM)')
        self.xaxis_set_tc = funutils.MyTextCtrl(self.panel_l, value = 'UN-BI:AMP:SET', style = wx.TE_PROCESS_ENTER, fontsize = self.fontsize_textctrl)
        self.xaxis_get_tc = funutils.MyTextCtrl(self.panel_l, value = 'UN-BI:AMP',     style = wx.TE_PROCESS_ENTER, fontsize = self.fontsize_textctrl)
        gs.Add(self.xaxis_set_st,      pos = (0, 0), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gs.Add(self.xaxis_set_tc, pos = (0, 1), span = (1, 1), flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gs.Add(self.xaxis_get_st,      pos = (0, 2), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gs.Add(self.xaxis_get_tc, pos = (0, 3), span = (1, 1), flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)

        # Y-AXIS input: PV name value
        self.yaxis_st = funutils.MyStaticText(self.panel_l, label = 'Y-AXIS')
        self.yaxis_tc = funutils.MyTextCtrl(self.panel_l, value = '', style = wx.TE_PROCESS_ENTER, fontsize = self.fontsize_textctrl)
        gs.Add(self.yaxis_st, pos = (1, 0), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gs.Add(self.yaxis_tc, pos = (1, 1), span = (1, 3), flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)

        # Z-AXIS input: PV name value
        self.zaxis_st      = funutils.MyStaticText(self.panel_l, label = 'Z-AXIS')
        self.zaxis_tc = funutils.MyTextCtrl(self.panel_l, value = '', style = wx.TE_PROCESS_ENTER, fontsize = self.fontsize_textctrl)
        gs.Add(self.zaxis_st,      pos = (2, 0), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gs.Add(self.zaxis_tc, pos = (2, 1), span = (1, 3), flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)

        # X-AXIS range: min, max, num
        self.xrange_st = funutils.MyStaticText(self.panel_l, label = 'X-Range[min:max:num]')
        self.xrange_min_tc = funutils.MyTextCtrl(self.panel_l, value = '10', style = wx.TE_PROCESS_ENTER, fontsize = self.fontsize_textctrl)
        self.xrange_max_tc = funutils.MyTextCtrl(self.panel_l, value = '50', style = wx.TE_PROCESS_ENTER, fontsize = self.fontsize_textctrl)
        self.xrange_num_tc = funutils.MyTextCtrl(self.panel_l, value = '10', style = wx.TE_PROCESS_ENTER, fontsize = self.fontsize_textctrl)
        gs.Add(self.xrange_st,          pos = (3, 0), span = (1, 1), flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gs.Add(self.xrange_min_tc, pos = (3, 1), span = (1, 1), flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gs.Add(self.xrange_max_tc, pos = (3, 2), span = (1, 1), flag = wx.EXPAND | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gs.Add(self.xrange_num_tc, pos = (3, 3), span = (1, 1), flag = wx.EXPAND | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)

        # Y-AXIS range: min, max, num
        self.yrange_st = funutils.MyStaticText(self.panel_l, label = 'Y-Range[min:max:num]')
        self.yrange_min_tc = funutils.MyTextCtrl(self.panel_l, value = '0',   style = wx.TE_PROCESS_ENTER, fontsize = self.fontsize_textctrl)
        self.yrange_max_tc = funutils.MyTextCtrl(self.panel_l, value = '1.0', style = wx.TE_PROCESS_ENTER, fontsize = self.fontsize_textctrl)
        self.yrange_num_tc = funutils.MyTextCtrl(self.panel_l, value = '10',  style = wx.TE_PROCESS_ENTER, fontsize = self.fontsize_textctrl)

        self.shotnum_st   = funutils.MyStaticText(self.panel_l, label = 'Shot Number')
        self.waitmse_st   = funutils.MyStaticText(self.panel_l, label = 'Wait Second')
        self.daqfreq_st   = funutils.MyStaticText(self.panel_l, label = 'Scan DAQ rep-rate')
        self.profreq_st   = funutils.MyStaticText(self.panel_l, label = 'Prof DAQ rep-rate')
        self.shotnum_sc   = funutils.MySpinCtrl(self.panel_l, value = '10', min = 1, max = 100, initial = 5, style = wx.SP_ARROW_KEYS, font = self.font_textctrl)
        self.waitmse_sc   = funutils.MySpinCtrl(self.panel_l, value = '1',  min = 1, max = 10,  initial = 2, style = wx.SP_ARROW_KEYS, font = self.font_textctrl)
        self.daqfreq_sc   = funutils.MySpinCtrl(self.panel_l, value = '10', min = 1, max = 50,  initial = 2, style = wx.SP_ARROW_KEYS, font = self.font_textctrl)
        self.profreq_sc   = funutils.MySpinCtrl(self.panel_l, value = '10', min = 1, max = 50,  initial = 2, style = wx.SP_ARROW_KEYS, font = self.font_textctrl)
        self.waitmse_calc = funutils.MyStaticText(self.panel_l, label = '500.0')
        self.waitmse_unit = funutils.MyStaticText(self.panel_l, label = 'msec')
        self.shotnum_unit = funutils.MyStaticText(self.panel_l, label = 'per iteration')
        self.daqfreq_unit = funutils.MyStaticText(self.panel_l, label = 'Hz')
        self.profreq_unit = funutils.MyStaticText(self.panel_l, label = 'Hz')

        fontbtn = funutils.MyButton(self.panel_l, label = 'Choose Font')

        gs.Add(self.yrange_st,     pos = (4, 0), span = (1, 1), flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gs.Add(self.yrange_min_tc, pos = (4, 1), span = (1, 1), flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gs.Add(self.yrange_max_tc, pos = (4, 2), span = (1, 1), flag = wx.EXPAND | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gs.Add(self.yrange_num_tc, pos = (4, 3), span = (1, 1), flag = wx.EXPAND | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)

        gs.Add(self.shotnum_st, pos = (5, 0), span = (1, 1), flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gs.Add(self.waitmse_st, pos = (6, 0), span = (1, 1), flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gs.Add(self.daqfreq_st, pos = (7, 0), span = (1, 1), flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gs.Add(self.profreq_st, pos = (8, 0), span = (1, 1), flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)

        gs.Add(fontbtn, pos = (8, 3), span = (1, 1), flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        fontbtn.Bind(wx.EVT_BUTTON, self.onChooseFont)

        gs.Add(self.shotnum_sc, pos = (5, 1), span = (1, 1), flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gs.Add(self.waitmse_sc, pos = (6, 1), span = (1, 1), flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gs.Add(self.daqfreq_sc, pos = (7, 1), span = (1, 1), flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gs.Add(self.profreq_sc, pos = (8, 1), span = (1, 1), flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)

        gs.Add(self.shotnum_unit,      pos = (5, 2), span = (1, 1), flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gs.Add(self.waitmse_calc, pos = (6, 2), span = (1, 1), flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gs.Add(self.waitmse_unit,      pos = (6, 3), span = (1, 1), flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gs.Add(self.daqfreq_unit,      pos = (7, 2), span = (1, 1), flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gs.Add(self.profreq_unit,      pos = (8, 2), span = (1, 1), flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)

        gs.AddGrowableCol(1, 0)
        gs.AddGrowableCol(2, 0)
        gs.AddGrowableCol(3, 0)

        # tick control methods
        gsm = wx.GridBagSizer(5, 5)
        self.scan2flag = funutils.MyCheckBox(self.panel_l, label = u'Two Dimensional')
        self.swapxz    = funutils.MyCheckBox(self.panel_l, label = u'Swap XZ')
        self.swapxy    = funutils.MyCheckBox(self.panel_l, label = u'Swap XY')

        gsm.Add(self.scan2flag, pos = (0, 0), span = (1, 2), flag = wx.EXPAND | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gsm.Add(self.swapxz,    pos = (0, 2), span = (1, 1), flag = wx.EXPAND | wx.RIGHT |  wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gsm.Add(self.swapxy,    pos = (1, 2), span = (1, 1), flag = wx.EXPAND | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gsm.AddGrowableCol(0, 0)

        # splitter line 1
        hline1 = wx.StaticLine(self.panel_l, style = wx.LI_HORIZONTAL)

        # mathematical methods control
        gsf = wx.GridBagSizer(5, 5)
        self.fitflag = funutils.MyCheckBox(self.panel_l, label = u'Curve Fitting')
        self.fittype = funutils.MyComboBox(self.panel_l, value = 'Gaussian', choices = ['Gaussian','Polynomial'], style = wx.CB_READONLY)
        gsf.Add(self.fitflag, pos = (0, 0), span = (1, 2), flag = wx.EXPAND | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gsf.Add(self.fittype, pos = (0, 2), span = (1, 1), flag = wx.EXPAND | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gsf.AddGrowableCol(0, 0)

        # splitter line 2
        hline2 = wx.StaticLine(self.panel_l, style = wx.LI_HORIZONTAL)

        # command pushbuttons
        gsb = wx.GridBagSizer(10, 10)
        self.start_btn  = funutils.MyButton(self.panel_l, label = u'START',  fontcolor=funutils.hex2rgb('#1111FF'), fontsize = self.fontsize_button)
        self.retake_btn = funutils.MyButton(self.panel_l, label = u'RETAKE', fontcolor=funutils.hex2rgb('#1111FF'), fontsize = self.fontsize_button)   
        self.pause_btn  = funutils.MyButton(self.panel_l, label = u'PAUSE',  fontcolor=funutils.hex2rgb('#1111FF'), fontsize = self.fontsize_button)
        self.close_btn  = funutils.MyButton(self.panel_l, label = u'CLOSE',  fontcolor=funutils.hex2rgb('#1111FF'), fontsize = self.fontsize_button)

        self.profdaq_btn= funutils.MyButton(self.panel_l, label = u'Prof DAQ START' ,fontcolor = funutils.hex2rgb('#000000'), fontsize = self.fontsize_button, size = (-1, -1))

        gsb.Add(self.start_btn,  pos = (0, 0), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gsb.Add(self.retake_btn, pos = (0, 1), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gsb.Add(self.pause_btn,  pos = (1, 0), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gsb.Add(self.close_btn,  pos = (1, 1), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gsb.Add(self.profdaq_btn,pos = (0, 3), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)

        # splitter line 3
        hline3 = wx.StaticLine(self.panel_l, style = wx.LI_HORIZONTAL)

        # log container
        vboxlog = wx.BoxSizer(wx.VERTICAL)
        self.logcnt_title   = funutils.MyStaticText(self.panel_l, label = 'Shot Number Counter:')
        self.logcnt_st = funutils.MyStaticText(self.panel_l, label = '', fontcolor = 'red',  fontsize = int(1.5*self.fontsize_statictext))
        self.logcnt_gauge = wx.Gauge(self.panel_l)
        
        hbox_logcnt = wx.BoxSizer(wx.HORIZONTAL)
        hbox_logcnt.Add(self.logcnt_title,      proportion = 0, flag = wx.TOP | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT, border = self.bordersize)
        hbox_logcnt.Add(self.logcnt_st,    proportion = 1, flag = wx.TOP | wx.EXPAND | wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER, border = self.bordersize)
        hbox_logcnt.Add(self.logcnt_gauge, proportion = 2, flag = wx.TOP | wx.EXPAND | wx.LEFT | wx.ALIGN_CENTER, border = self.bordersize)
        
        self.scanlog_tc = funutils.MyTextCtrl(self.panel_l, value = 'SCAN LOG GOES', style = wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_LEFT, fontsize = self.fontsize_textctrl, fontcolor = 'red')
        self.scanlog_clear_btn  = funutils.MyButton(self.panel_l, label = u'Clear Log',  fontcolor=funutils.hex2rgb('#000000'), fontsize = self.fontsize_button)
        vboxlog.Add(hbox_logcnt,            proportion = 0, flag = wx.EXPAND | wx.BOTTOM | wx.ALIGN_LEFT, border = self.bordersize)
        vboxlog.Add(self.scanlog_tc,        proportion = 1, flag = wx.EXPAND | wx.BOTTOM | wx.ALIGN_CENTER_VERTICAL, border = self.bordersize)
        vboxlog.Add(self.scanlog_clear_btn, proportion = 0, flag = wx.ALIGN_RIGHT, border = self.bordersize)

        # set layout
        controlpanel_sbsizer.Add(gs,     proportion = 0, flag = wx.EXPAND | wx.TOP | wx.BOTTOM, border = self.bordersize)
        controlpanel_sbsizer.Add(gsm,    proportion = 0, flag = wx.EXPAND | wx.TOP | wx.BOTTOM, border = self.bordersize)

        controlpanel_sbsizer.Add(hline1, proportion = 0, flag = wx.EXPAND | wx.LEFT | wx.RIGHT, border = self.bordersize)
        controlpanel_sbsizer.Add((-1,10))

        controlpanel_sbsizer.Add(gsf,    proportion = 0, flag = wx.EXPAND | wx.TOP | wx.BOTTOM, border = self.bordersize)

        controlpanel_sbsizer.Add(hline2, proportion = 0, flag = wx.EXPAND | wx.LEFT | wx.RIGHT, border = self.bordersize)
        controlpanel_sbsizer.Add((-1,10))

        controlpanel_sbsizer.Add(vboxlog,proportion = 1, flag = wx.EXPAND | wx.ALL, border = self.bordersize)

        controlpanel_sbsizer.Add(hline3, proportion = 0, flag = wx.EXPAND | wx.LEFT | wx.RIGHT, border = self.bordersize)
        controlpanel_sbsizer.Add((-1,10))

        controlpanel_sbsizer.Add(gsb,    proportion = 0, flag = wx.ALIGN_LEFT | wx.TOP | wx.BOTTOM, border = self.bordersize)

        sizer1.Add(controlpanel_sbsizer, proportion = 1, flag = wx.EXPAND | wx.ALL, border = self.bordersize)

        self.panel_l.SetSizerAndFit(sizer1)

        vleft.Add(self.panel_l,  proportion = 1, flag = wx.EXPAND)

        # vright1

        imagepanel_sb      = funutils.createwxStaticBox(self.panel_ru, label = 'Image Monitor Panel', fontcolor=funutils.hex2rgb(self.fontcolor_staticbox), fontsize = self.fontsize_staticbox)
        imagepanel_sbsizer = wx.StaticBoxSizer(imagepanel_sb, wx.HORIZONTAL)

        vr1hbox    = wx.BoxSizer(wx.HORIZONTAL) # container for vr1hbox_l and vr1hbox_r
        vr1hbox_lv = wx.BoxSizer(wx.VERTICAL  ) # container for imgprofile
        vr1hbox_rv = wx.BoxSizer(wx.VERTICAL  ) # container for control for imgprofile

        # imageviewer

        self.imgprofile               = ImagePanel(self.panel_ru, figsize = (4, 4), dpi = 75, bgcolor = funutils.hex2rgb(self.backcolor_panel))
        self.panel_ru.imgprof_pos_st  = funutils.MyStaticText(self.panel_ru, label = 'Current Pos:')
        self.panel_ru.imgprof_pos     = funutils.MyStaticText(self.panel_ru, label = '')
        self.panel_ru.imgprof_pos1_st = funutils.MyStaticText(self.panel_ru, label = 'Picked Pos:', fontcolor = 'red')
        self.panel_ru.imgprof_pos1    = funutils.MyStaticText(self.panel_ru, label = '',            fontcolor = 'red')
        self.imgpv_st                 = funutils.MyStaticText(self.panel_ru, label = 'Image PV:')
        self.imgpv_tc                 = funutils.MyTextCtrl(self.panel_ru, value = 'UN-BI:PROF19:ARR', style = wx.TE_PROCESS_ENTER)
        self.imgcm_st                 = funutils.MyStaticText(self.panel_ru, label = 'Color Map:')
        self.imgcm_cb                 = funutils.MyComboBox(self.panel_ru, value = 'jet', choices = ['jet', 'hot','gnuplot'], style = wx.CB_READONLY)
        self.imgcm_rcb                = funutils.MyCheckBox(self.panel_ru, label = u'Reverse:')
        self.imgcr_st                 = funutils.MyStaticText(self.panel_ru, label = 'Color Range:')
        self.imgcr_fs_min             = funutils.FloatSlider(self.panel_ru, value = self.imgcmin, minValue = self.imgcmin, maxValue = self.imgcmax, increment = 0.1)
        self.imgcr_fs_max             = funutils.FloatSlider(self.panel_ru, value = self.imgcmax, minValue = self.imgcmin, maxValue = self.imgcmax, increment = 0.1)
        self.imgcr_fs_min_val         = funutils.MyStaticText(self.panel_ru, label = ('%.1f' % (self.imgcmin)), style = wx.ALIGN_CENTER, fontsize = int(self.fontsize_statictext*0.8))
        self.imgcr_fs_max_val         = funutils.MyStaticText(self.panel_ru, label = ('%.1f' % (self.imgcmax)), style = wx.ALIGN_CENTER, fontsize = int(self.fontsize_statictext*0.8))

        self.imgconfig_pathvalue_tc   = funutils.MyTextCtrl(self.panel_ru, value = os.path.abspath(os.path.expanduser(os.curdir)), style = wx.CB_READONLY)
        self.imgconfig_pathchoose_btn = funutils.MyButton(self.panel_ru, label = u'Config Path:' , fontcolor = funutils.hex2rgb('#000000'), fontsize = 12)
        self.imgconfig_fetch_btn      = funutils.MyButton(self.panel_ru, label = u'Fetch Setting', fontcolor = funutils.hex2rgb('#1111FF'), fontsize = 12, size = (120, -1))
        self.imgconfig_dump_btn       = funutils.MyButton(self.panel_ru, label = u'Dump Setting' , fontcolor = funutils.hex2rgb('#1111FF'), fontsize = 12, size = (120, -1))
        self.imgconfig_pathvalue_tc.SetToolTip(wx.ToolTip('Path where config file stays, push "Config Path" button to locate.'))

        gsimg = wx.GridBagSizer(5, 5)
        gsimg.Add(self.imgpv_st,     pos = (0, 0), span = (1, 1), flag = wx.ALIGN_RIGHT |  wx.LEFT | wx.ALIGN_CENTRE_VERTICAL | wx.TOP | wx.BOTTOM, border = self.bordersize)
        gsimg.Add(self.imgpv_tc,     pos = (0, 1), span = (1, 2), flag = wx.EXPAND | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL | wx.TOP | wx.BOTTOM, border = self.bordersize)
        
        gsimg.Add(self.imgcm_st,     pos = (1, 0), span = (1, 1), flag = wx.ALIGN_RIGHT | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL | wx.BOTTOM, border = self.bordersize)
        gsimg.Add(self.imgcm_rcb,    pos = (1, 1), span = (1, 1), flag = wx.EXPAND | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL | wx.BOTTOM, border = self.bordersize)
        gsimg.Add(self.imgcm_cb,     pos = (1, 2), span = (1, 1), flag = wx.EXPAND | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL | wx.BOTTOM, border = self.bordersize)
        
        gsimg.Add(self.imgcr_st,     pos = (2, 0), span = (1, 1), flag = wx.ALIGN_RIGHT | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gsimg.Add(self.imgcr_fs_min, pos = (2, 1), span = (1, 1), flag = wx.EXPAND | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gsimg.Add(self.imgcr_fs_max, pos = (2, 2), span = (1, 1), flag = wx.EXPAND | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        
        gsimg.Add(self.imgcr_fs_min_val, pos = (3, 1), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTRE, border = self.bordersize)
        gsimg.Add(self.imgcr_fs_max_val, pos = (3, 2), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTRE, border = self.bordersize)
        
        gsimg.Add(self.imgconfig_pathchoose_btn, pos = (4, 0), span = (1, 1), flag = wx.LEFT | wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gsimg.Add(self.imgconfig_pathvalue_tc,   pos = (4, 1), span = (1, 2), flag = wx.LEFT | wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gsimg.Add(self.imgconfig_fetch_btn,      pos = (5, 2), span = (1, 1), flag = wx.LEFT | wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)
        gsimg.Add(self.imgconfig_dump_btn,       pos = (6, 2), span = (1, 1), flag = wx.LEFT | wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = self.bordersize)

        gsimg.AddGrowableCol(1, 0)
        gsimg.AddGrowableCol(2, 0)

        vr1hbox_lv_gs = wx.GridBagSizer(5, 5)
        vr1hbox_lv_gs.Add(self.panel_ru.imgprof_pos_st,  pos = (0, 0), span = (1, 1), flag = wx.ALIGN_CENTRE_VERTICAL | wx.LEFT | wx.ALIGN_RIGHT, border = self.bordersize)
        vr1hbox_lv_gs.Add(self.panel_ru.imgprof_pos,     pos = (0, 1), span = (1, 1), flag = wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT | wx.RIGHT | wx.LEFT, border = self.bordersize)
        vr1hbox_lv_gs.Add(self.panel_ru.imgprof_pos1_st, pos = (1, 0), span = (1, 1), flag = wx.ALIGN_CENTRE_VERTICAL | wx.LEFT | wx.ALIGN_RIGHT, border = self.bordersize)
        vr1hbox_lv_gs.Add(self.panel_ru.imgprof_pos1,    pos = (1, 1), span = (1, 1), flag = wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT | wx.RIGHT | wx.LEFT, border = self.bordersize)

        # set layout 
        vr1hbox_lv.Add(self.imgprofile, proportion = 1, flag = wx.EXPAND | wx.ALIGN_CENTRE)
        vr1hbox_lv.Add(vr1hbox_lv_gs,   proportion = 0, flag = wx.ALIGN_LEFT | wx.ALL, border = max(int(self.bordersize*0.5), 5))

        vr1hbox_rv.Add(gsimg, proportion = 0, flag = wx.EXPAND | wx.ALIGN_RIGHT)

        vr1hbox.Add(vr1hbox_lv, proportion = 3, flag = wx.EXPAND | wx.ALIGN_CENTER)
        vr1hbox.Add(wx.StaticLine(self.panel_ru, style = wx.LI_VERTICAL), flag = wx.EXPAND | wx.TOP | wx.BOTTOM, border = self.bordersize)
        vr1hbox.Add(vr1hbox_rv, proportion = 2, flag = wx.EXPAND | wx.ALIGN_RIGHT)

        imagepanel_sbsizer.Add(vr1hbox, proportion = 1, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border = self.bordersize)

        sizer2.Add(imagepanel_sbsizer, proportion = 1, flag = wx.EXPAND | wx.ALL, border = self.bordersize)
        self.panel_ru.SetSizerAndFit(sizer2)
        vright1.Add(self.panel_ru, proportion = 1, flag = wx.EXPAND | wx.ALIGN_CENTER)
        
        # vright2
        analysispanel_sb      = funutils.createwxStaticBox(self.panel_rd, label = 'Correlation Analysis Panel', fontcolor=funutils.hex2rgb(self.fontcolor_staticbox), fontsize = self.fontsize_staticbox)
        analysispanel_sbsizer = wx.StaticBoxSizer(analysispanel_sb, wx.VERTICAL)

        vr2vbox = wx.BoxSizer(wx.VERTICAL)

        vr2hbox    = wx.BoxSizer(wx.HORIZONTAL) # container for vr2hbox_l and vr2hbox_r
        vr2hbox_lv = wx.BoxSizer(wx.VERTICAL  ) # container for scanfig
        vr2hbox_rv = wx.BoxSizer(wx.VERTICAL  ) # container for reserved space for other controls

        self.scanfig = ImagePanelxy(self.panel_rd, figsize = (3, 3), dpi = 75, bgcolor = funutils.hex2rgb(self.backcolor_panel))

        self.clrfig_btn = funutils.MyButton(self.panel_rd, label = u'Clear', fontsize = self.fontsize_button)
        self.scan_cb    = funutils.MyCheckBox(self.panel_rd, label = u'Show Scan Fig')

        self.panel_rd.sfig_pos_st  = funutils.MyStaticText(self.panel_rd, label = 'Current Pos:')
        self.panel_rd.sfig_pos     = funutils.MyStaticText(self.panel_rd, label = '')
        self.panel_rd.sfig_pos1_st = funutils.MyStaticText(self.panel_rd, label = 'Picked Pos:', fontcolor = 'blue')
        self.panel_rd.sfig_pos1    = funutils.MyStaticText(self.panel_rd, label = '',            fontcolor = 'blue')
        
        gss = wx.GridBagSizer(5, 5)
        gss.Add(self.panel_rd.sfig_pos_st,  pos = (0, 0), span = (1, 1), flag = wx.ALIGN_CENTRE_VERTICAL | wx.LEFT | wx.ALIGN_RIGHT, border = self.bordersize)
        gss.Add(self.panel_rd.sfig_pos,     pos = (0, 1), span = (1, 1), flag = wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT | wx.RIGHT | wx.LEFT, border = self.bordersize)
        gss.Add(self.panel_rd.sfig_pos1_st, pos = (1, 0), span = (1, 1), flag = wx.ALIGN_CENTRE_VERTICAL | wx.LEFT | wx.ALIGN_RIGHT, border = self.bordersize)
        gss.Add(self.panel_rd.sfig_pos1,    pos = (1, 1), span = (1, 1), flag = wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT | wx.RIGHT | wx.LEFT, border = self.bordersize)

        vr2hbox_lv.Add(self.scanfig,    proportion = 1, flag = wx.EXPAND | wx.ALIGN_CENTER)
        vr2hbox_rv.Add(self.scan_cb,    proportion = 0, flag = wx.TOP | wx.ALIGN_CENTER, border = 2*self.bordersize)
        vr2hbox_rv.Add(self.clrfig_btn, proportion = 0, flag = wx.TOP | wx.ALIGN_CENTER, border = 2*self.bordersize)
        vr2hbox.Add(vr2hbox_lv, proportion = 6, flag = wx.EXPAND | wx.ALL, border = self.bordersize)
        vr2hbox.Add(wx.StaticLine(self.panel_rd, style = wx.LI_VERTICAL), flag = wx.EXPAND | wx.TOP | wx.BOTTOM, border = self.bordersize)
        vr2hbox.Add(vr2hbox_rv, proportion = 1, flag = wx.EXPAND | wx.ALL, border = self.bordersize)

        vr2vbox.Add(vr2hbox, proportion = 1, flag = wx.EXPAND | wx.ALIGN_CENTER)
        vr2vbox.Add(gss,     proportion = 0, flag = wx.ALIGN_LEFT | wx.ALL, border = max(int(self.bordersize*0.5), 5))

        analysispanel_sbsizer.Add(vr2vbox, proportion = 1, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border = self.bordersize)

        sizer3.Add(analysispanel_sbsizer, proportion = 1, flag = wx.EXPAND | wx.ALL, border = self.bordersize)
        self.panel_rd.SetSizerAndFit(sizer3)
        vright2.Add(self.panel_rd, proportion = 1, flag = wx.EXPAND)

        vright.Add(vright1, proportion = 2, flag = wx.EXPAND)
        vright.Add(vright2, proportion = 3, flag = wx.EXPAND)

        hbox.Add(vleft,  proportion = 2, flag = wx.EXPAND)
        hbox.Add(vright, proportion = 3, flag = wx.EXPAND)

        # set outer hbox
        self.panel.SetSizer(hbox)
        osizer = wx.BoxSizer(wx.HORIZONTAL)
        osizer.SetMinSize((1280, 800))
        osizer.Add(self.panel, proportion = 1, flag = wx.EXPAND)
        self.SetSizerAndFit(osizer)
        
        # timers

        # scan timer
        self.scanctrltimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onUpdateScan, self.scanctrltimer)

        # scan daq timer
        self.scandaqtimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onScanDAQ, self.scandaqtimer)

        # profile daq timer
        self.profdaqtimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onProfDAQ, self.profdaqtimer)

        # delay timer
        self.delaytimer = wx.Timer(self)
        #self.Bind(wx.EVT_TIMER, self.delaytimer)

        # for debug only
        #self.dtimer1 = wx.Timer(self)
        #self.Bind(wx.EVT_TIMER, self.onDEBUG1, self.dtimer1)

        # binding events
        self.Bind(wx.EVT_CHECKBOX,   self.onCheckScan2,   self.scan2flag   )
        self.Bind(wx.EVT_CHECKBOX,   self.onCheckFitting, self.fitflag     )
        self.Bind(wx.EVT_CHECKBOX,   self.onCheckScan,    self.scan_cb     )
        self.Bind(wx.EVT_CHECKBOX,   self.onSetImgCMR,    self.imgcm_rcb   )
        self.Bind(wx.EVT_BUTTON,     self.onPushStart,    self.start_btn   )
        self.Bind(wx.EVT_BUTTON,     self.onPushRetake,   self.retake_btn  )
        self.Bind(wx.EVT_BUTTON,     self.onPushPause,    self.pause_btn   )
        self.Bind(wx.EVT_BUTTON,     self.onPushClose,    self.close_btn   )
        self.Bind(wx.EVT_BUTTON,     self.onPushProfDAQ,  self.profdaq_btn )
        self.Bind(wx.EVT_BUTTON,     self.onChoosePath,   self.imgconfig_pathchoose_btn)
        self.Bind(wx.EVT_BUTTON,     self.onScanfigClear, self.clrfig_btn  )
        self.Bind(wx.EVT_BUTTON,     self.onScanlogClear, self.scanlog_clear_btn)
        self.Bind(wx.EVT_TEXT_ENTER, self.onSetImgPV,     self.imgpv_tc    )
        self.Bind(wx.EVT_SCROLL,     self.onSetImgCR,     self.imgcr_fs_min)
        self.Bind(wx.EVT_SCROLL,     self.onSetImgCR,     self.imgcr_fs_max)
        self.Bind(wx.EVT_COMBOBOX,   self.onSetImgCM,     self.imgcm_cb    )
        self.Bind(wx.EVT_SPINCTRL,   self.onSetWaitTime,  self.waitmse_sc  )
        self.Bind(wx.EVT_SPINCTRL,   self.onSetShotNum,   self.shotnum_sc  )
        self.Bind(wx.EVT_SPINCTRL,   self.onSetDaqFreq,   self.daqfreq_sc  )
        self.Bind(wx.EVT_SPINCTRL,   self.onSetProFreq,   self.profreq_sc  )

    def onChooseFont(self, event):
        fontdata = wx.FontData()
        fontdata.EnableEffects(True)
        fontdata.SetInitialFont(self.Font)
        dial = wx.FontDialog(self, fontdata)
        if dial.ShowModal() == wx.ID_OK:
            self.font = dial.GetFontData().GetChosenFont()
            self.updateFont(self.font)
        else:
            dial.Destroy()

    def updateFont(self, font):
        for classtype in (wx.SpinCtrl, wx.StaticText, wx.TextCtrl, wx.CheckBox, wx.Button, wx.ComboBox):
            objs = funutils.findObj(self, classtype)
            for iobj in objs:
                try:
                    iobj.setFont(self.font)
                except:
                    pass

    def postInit(self):
        # initialization after UI creation
        
        ## UI control
        self.yaxis_st.Disable()
        self.yaxis_tc.Disable()
        self.yrange_st.Disable()
        self.yrange_min_tc.Disable()
        self.yrange_max_tc.Disable()
        self.yrange_num_tc.Disable()
        self.swapxy.Disable()
        self.fittype.Disable()
        self.scan_cb.SetValue(True)

        # scan log 
        self.scanlog_tc.SetValue('')
        self.scanX_range_num = int(self.xrange_num_tc.GetValue())
        self.shotnum_val     = self.shotnum_sc.GetValue()
        self.logcnt_gauge.SetRange(range = self.scanX_range_num*self.shotnum_val)

        ## set image
        self.postSetImage()

        ## set scan parameters
        self.postSetScan()

    def postSetScan(self):
        self.waitmsec_val     = float(self.waitmse_calc.GetLabel()) # time wait after every scan data setup, in millisecond
        self.shotnum_val      = self.shotnum_sc.GetValue() # shots number to be recorded for each scan data setup
        self.scandaqfreq_val  = self.daqfreq_sc.GetValue() # scan rep-rate [Hz]
        self.profdaqfreq_val  = self.profreq_sc.GetValue() # prof rep-rate [Hz]
        self.scandaqdelt_msec = 1000.0/float(self.scandaqfreq_val) # scan daq timer interval [ms]
        self.profdaqdelt_msec = 1000.0/float(self.profdaqfreq_val) # prof daq timer interval [ms]
        self.scandelt_msec = self.waitmsec_val + (self.shotnum_val + 1)* self.scandaqdelt_msec

    def postSetImage(self):
        ## image color range setting
        self.imgprofile.cmin = self.imgprofile.z.min()
        self.imgprofile.cmax = self.imgprofile.z.max()
        self.imgcmin = self.imgprofile.cmin
        self.imgcmax = self.imgprofile.cmax
        self.imgcr_fs_min_val.SetLabel('%.1f' % (self.imgcmin))
        self.imgcr_fs_max_val.SetLabel('%.1f' % (self.imgcmax))
        self.imgcr_fs_min.SetMin  (self.imgcmin*2)
        self.imgcr_fs_min.SetMax  (self.imgcmax*2)
        self.imgcr_fs_min.SetValue(self.imgcmin)
        self.imgcr_fs_max.SetMin  (self.imgcmin*2)
        self.imgcr_fs_max.SetMax  (self.imgcmax*2)
        self.imgcr_fs_max.SetValue(self.imgcmax)

        ## image plotting panel
        self.imgprofile.im.set_clim(vmin = self.imgcmin, vmax= self.imgcmax)
        self.imgprofile.im.set_array(self.imgprofile.z)
        self.imgprofile.repaint()

    def preInit(self):
        # initialization before UI creation
        self.fontsize_button     = 12 
        self.fontsize_statictext = 12
        self.fontsize_staticbox  = 10
        self.fontsize_textctrl   = 12
        self.backcolor_panel     = '#DDDDDD'
        self.fontcolor_staticbox = '#4B4B4B'
        self.bordersize          = 12
        
        self.font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.font_textctrl   = self.font
        self.font_statictext = self.font

        self.imgcmin = 0
        self.imgcmax = 1
        self.rcmflag = ''
        self.mypv    = ''
        self.wpx, self.hpx = 494, 659
        self.roixy = [0, self.wpx, 0, self.hpx]
        
        self.scanflag = 1 # scan enabled when set to nonzero, by default

        # scan dimension
        self.scanndim = 1
#        self.scanX_range_num = -1
#       self.scanX_range = np.array([-1])

        # scanfig plot style configuration
        self.sf_mkshape     = 'o'
        self.sf_mksize      = 4
        self.sf_mkfacecolor = 'b'
        self.sf_mkedgecolor = 'b'
        self.sf_linestyle   = '-'
        self.sf_linecolor   = 'r'

    def onCheckScan(self, event):
        if event.GetEventObject().IsChecked():
            self.scanflag = 1 
        else:
            self.scanflag = 0 # do not scan, just show intensity v.s. timeline

    def onCheckScan2(self, event):
        if event.GetEventObject().IsChecked():
            self.scanndim = 2
            self.yaxis_st.Enable()
            self.yaxis_tc.Enable()
            self.yrange_st.Enable()
            self.yrange_min_tc.Enable()
            self.yrange_max_tc.Enable()
            self.yrange_num_tc.Enable()
            self.swapxy.Enable()
        else:
            self.scanndim = 1
            self.yaxis_st.Disable()
            self.yaxis_tc.Disable()
            self.yrange_st.Disable()
            self.yrange_min_tc.Disable()
            self.yrange_max_tc.Disable()
            self.yrange_num_tc.Disable()
            self.swapxy.Disable()

    def onCheckFitting(self, event):
        if event.GetEventObject().IsChecked():
            self.fittype.Enable()
        else:
            self.fittype.Disable()

    def onPushStart(self, event):
        if not isinstance(self.mypv, epics.pv.PV):
            self.mypv = epics.PV(self.imgpv_tc.GetValue(), auto_monitor = True)
        # set up parameters for scan
        self.setScanParams()

        # start scan
        self.accumScanNum = 0
        self.scanctrltimer.Start(self.scandelt_msec)
        
        # for debug only
        #self.Dcnt = 0
        #self.Dt = time.time()
        #self.idx = 0
        #self.Ddt = np.zeros((1000,2))
        #self.dtimer1.Start(1000)

    def onPushRetake(self, event):
        pass

    def onPushPause(self, event):
        self.scanctrltimer.Stop()
        self.scandaqtimer.Stop()

        # for debug only
        #self.dtimer1.Stop()
        #np.savetxt('log.dat', self.Ddt, delimiter= ' ', fmt='%.2f')

    def onPushClose(self, event):
        self.exitApp()

    def onPushProfDAQ(self, event):
        btnobj = event.GetEventObject()
        if self.profdaqtimer.IsRunning():
            self.profdaqtimer.Stop()
            btnobj.SetLabel('Prof DAQ START')
        else:
            self.profdaqtimer.Start(self.profdaqdelt_msec)
            btnobj.SetLabel('Prof DAQ STOP')

    def onProfDAQ(self, event):
        self.updateImage()

    def onScanDAQ(self, event):
        self.scandatatmp[self.daqcnt,:] = self.scanXget_PV.get(), np.sum(self.mypv.get())
        if self.daqcnt == self.shotnum_val-1:
            self.scandaqtimer.Stop()
            # write scan log
            logmsg = 'Scan #%02d is DONE, scan value is: %.3f\n' % (self.scanidx+1, self.scanX_range[self.xidx-1])
            self.scanlog_tc.AppendText(logmsg)
            self.scanZ[self.scanidx*self.shotnum_val:(self.scanidx+1)*self.shotnum_val, :] = self.scandatatmp
            self.updateScanfig()
        self.daqcnt += 1
        self.accumScanNum += 1
        self.logcnt_gauge.SetValue(self.accumScanNum)
        self.logcnt_st.SetLabel(str(self.daqcnt))

    def onUpdateScan(self, event):
        self.logcnt_gauge.SetRange(range = self.scanX_range_num*self.shotnum_val)
        if self.scanflag == 1:
            try:
                assert self.xidx < self.scanX_range_num
                self.scanXset_PV.put(self.scanX_range[self.xidx])
                wx.MilliSleep(self.waitmsec_val)
                self.startScanDAQ(self.scandaqdelt_msec, self.xidx)
                self.xidx += 1
            except AssertionError:
                self.scanctrltimer.Stop()
                self.scandaqtimer.Stop()
                self.daqcnt = 0
                #print 'timers stop'
                #print self.scanZ

        #self.updateImage()
        #self.updateScanfig()

    def startScanDAQ(self, ms, scanidx):
        self.scanidx = scanidx
        self.daqcnt = 0
        self.scandaqtimer.Start(ms)

    def updateImage(self):
        # for debug
        #self.Dcnt += 1
        if self.mypv.connected == True:
            self.imgprofile.z = self.mypv.get()[0:self.wpx*self.hpx].reshape((self.wpx,self.hpx))[self.roixy[0]:self.roixy[1],self.roixy[2]:self.roixy[3]]
            self.imgprofile.im.set_array(self.imgprofile.z)
            self.imgprofile.repaint()
        else:
            dial = wx.MessageDialog(self, message = u"Lost connection, may be caused by network error or the IOC server is down.",
                    caption = u"Lost Connection", 
                    style = wx.OK | wx.CANCEL | wx.ICON_ERROR | wx.CENTRE)
            if dial.ShowModal() == wx.ID_OK:
                dial.Destroy()

    def updateScanfig(self):
        if self.scanflag == 1:
            scandata_ins = funutils.ScanDataFactor(self.scanZ, int(self.scanX_range_num), self.shotnum_val)
            xerr_ins = scandata_ins.getXerrbar()
            yerr_ins = scandata_ins.getYerrbar()
            idx = scandata_ins.getYavg().nonzero()
            self.scanfig.x = scandata_ins.getXavg()[idx]
            self.scanfig.y = scandata_ins.getYavg()[idx]
            self.scanfig.xerrarr = xerr_ins[idx]
            self.scanfig.yerrarr = yerr_ins[idx]

        else:
            scanshotdata = funutils.ImageDataFactor(self.imgprofile.z)
            self.cnt += 1
            self.x.append(self.cnt)
            self.y.append(factdata.getInt())
            self.scanfig.x = np.array(self.x)
            self.scanfig.y = np.array(self.y)

        #self.scanfig.xyplot.set_marker(self.sf_mkshape)
        #self.scanfig.xyplot.set_markersize(self.sf_mksize)
        #self.scanfig.xyplot.set_markerfacecolor(self.sf_mkfacecolor)
        #self.scanfig.xyplot.set_markeredgecolor(self.sf_mkedgecolor)
        #self.scanfig.xyplot.set_linestyle(self.sf_linestyle)
        #self.scanfig.xyplot.set_color(self.sf_linecolor)
        self.scanfig.repaint()

    def onSetImgPV(self, event):
        # set image PV source to show
        self.mypv = epics.PV(event.GetEventObject().GetValue(), auto_monitor = True)
        self.imgprofile.z = self.mypv.get()[0:self.wpx*self.hpx].reshape((self.wpx,self.hpx))[self.roixy[0]:self.roixy[1],self.roixy[2]:self.roixy[3]]
        self.postSetImage()

    def onSetImgCR(self, event):
        clickedobj = event.GetEventObject()
        if clickedobj.GetId() == self.imgcr_fs_min.GetId():
            self.imgcr_fs_min_val.SetLabel('%.1f' % (clickedobj.GetValue()))
        elif clickedobj.GetId() == self.imgcr_fs_max.GetId():
            self.imgcr_fs_max_val.SetLabel('%.1f' % (clickedobj.GetValue()))

        cmin = self.imgcr_fs_min.GetValue()
        cmax = self.imgcr_fs_max.GetValue()
        self.imgprofile.onSetCr(sorted([cmin, cmax]))

    def onSetImgCM(self, event):
        self.imgprofile.onSetcm(event.GetEventObject().GetValue() + self.rcmflag)

    def onSetImgCMR(self, event):
        if event.GetEventObject().IsChecked(): # checked
            self.rcmflag = '_r'
        else:
            self.rcmflag = ''
        cmap = self.imgcm_cb.GetValue() + self.rcmflag
        self.imgprofile.onSetcm(cmap)
 
    def onChoosePath(self, event):
        dlg = wx.DirDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            dirpath = dlg.GetPath()
            self.imgconfig_pathvalue_tc.SetValue(dirpath)
        dlg.Destroy()

    def onSetWaitTime(self, event):
        self.waitmsec_val = 500.0*float(event.GetEventObject().GetValue())  
        self.waitmse_calc.SetLabel(str(self.waitmsec_val))
        self.postSetScan()

    def onSetShotNum(self, event):
        self.shotnum_val = int(event.GetEventObject().GetValue())
        self.postSetScan()

    def onSetDaqFreq(self, event):
        self.scandaqfreq_val = int(event.GetEventObject().GetValue())
        self.postSetScan()

    def onSetProFreq(self, event):
        self.profdaqfreq_val = int(event.GetEventObject().GetValue())
        self.postSetScan()

    def onScanfigClear(self, event):
        self.x = []
        self.y = []
        self.updateScanfig()

    def onScanlogClear(self, event):
        self.scanlog_tc.SetValue('')

    def onDEBUG1(self, event):
        self.Ddt[self.idx,:] = self.Dcnt, time.time() - self.Dt
        self.idx += 1
        #print("%.2f | %.2f" % (float(self.Dcnt), time.time() - self.Dt))

    def setScanParams(self):
        if self.scanflag == 0: # show intensity v.s. timeline
            self.cnt = 0 # shot count
            self.x = [] # blank list for counted shot number
            self.y = [] # blank list for monitored objective function
        else: # scan checkbox is checked, do scan
            self.xidx = 0

            self.scanXset_PV = epics.PV(self.xaxis_set_tc.GetValue())
            self.scanXget_PV = epics.PV(self.xaxis_get_tc.GetValue())
            self.scanX_range_min = float(self.xrange_min_tc.GetValue())
            self.scanX_range_max = float(self.xrange_max_tc.GetValue())
            self.scanX_range_num = int(self.xrange_num_tc.GetValue())
            self.scanX_range = np.linspace(self.scanX_range_min, self.scanX_range_max, self.scanX_range_num)

            if self.scanndim == 2: # two-dimensional scan enabled
                self.scanY_PV = epics.PV(self.yaxis_tc.GetValue())
                self.scanY_range_min = float(self.yrange_min_tc.GetValue())
                self.scanY_range_max = float(self.yrange_max_tc.GetValue())
                self.scanY_range_num = float(self.yrange_num_tc.GetValue())
                self.scanY_range = np.linspace(self.scanY_range_min, self.scanY_range_max, self.scanY_range_num)

            self.scanZ = np.zeros((self.scanX_range_num*self.shotnum_val, self.scanndim+1))
            self.scandatatmp = np.zeros((self.shotnum_val, self.scanndim+1))
            
#------------------------------------------------------------------------#
# do not use right now
class ScanThread(threading.Thread):
    """
    Thread do scan routine, as well as show the progress bar.
    
    Dated: Jul. 1, 2015
    """
    def __init__(self, target):
        threading.Thread.__init__(self, target = target)
        self.setDaemon(True)
        self.target = target
        self.pb = self.target.pbframe.pb

    def run(self):
        for xidx in xrange(self.target.scanX_range_num):
            wx.MilliSleep(self.target.waitmsec_val)
            #wx.CallAfter(self.target.startScanDAQ, self.target.scandaqdelt_msec, xidx+1)
            wx.CallAfter(self.pb.SetValue, xidx)
        
        #self.target.scanctrltimer.Stop()
        #self.target.scandaqtimer.Stop()
        wx.CallAfter(self.target.pbframe.Close)

#------------------------------------------------------------------------#
class ImagePanel(pltutils.ImagePanel):
    def __init__(self, parent, figsize, dpi, bgcolor, **kwargs):
        pltutils.ImagePanel.__init__(self, parent, figsize, dpi, bgcolor, **kwargs)

    def doPlot(self):
        if not hasattr(self, 'axes'):
            self.axes = self.figure.add_subplot(111)
        self.im = self.axes.imshow(self.z, aspect = 'equal', cmap = plt.get_cmap(self.cmaptype), 
                                   origin = 'lower left', vmin = self.cmin, vmax = self.cmax)
        self.figure.colorbar(self.im, orientation = 'horizontal', aspect = 20, shrink = 0.95, 
                             fraction = 0.05, pad = 0.1)
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
            self.GetParent().imgprof_pos.SetLabel("(%.4f, %.4f)" % (event.xdata, event.ydata))
        except TypeError:
            pass
    
    def onPress(self, event):
        try:
            self.GetParent().imgprof_pos1.SetLabel("(%.4f, %.4f)" % (event.xdata, event.ydata))
        except TypeError:
            pass

class ImagePanelxy(pltutils.ImagePanelxy):
    def __init__(self, parent, figsize, dpi, bgcolor, **kwargs):
        pltutils.ImagePanelxy.__init__(self, parent, figsize, dpi, bgcolor, **kwargs)
        
    def onMotion(self, event):
        try:
            self.GetParent().sfig_pos.SetLabel("(%.4f, %.4f)" % (event.xdata, event.ydata))
        except TypeError:
            pass
    
    def onPress(self, event):
        try:
            self.GetParent().sfig_pos1.SetLabel("(%.4f, %.4f)" % (event.xdata, event.ydata))
        except TypeError:
            pass

    def doPlot(self):
        if not hasattr(self, 'axes'):
            self.axes = self.figure.add_subplot(111)
        self.ebplot = self.axes.errorbar(self.x, self.y,
                                         xerr = self.xerrarr, yerr = self.yerrarr,
                                         fmt = self.eb_fmt, 

                                         color      = 'g',
                                         linewidth  = 1,
                                         linestyle = '-',
                                         marker     = 'H',
                                         markersize = 10,
                                         markerfacecolor = 'b',
                                         markeredgecolor = 'b',

                                         elinewidth = 2,
                                         ecolor = self.eb_markercolor, capthick = self.eb_markersize)
        self.figure.canvas.draw()

    def onGetData(self):
        self.x, self.y, self.xerrarr, self.yerrarr = 1, 1, 0.1, 0.1

    def onConfigPlot(self):
        self.eb_fmt         = ''
        self.eb_markercolor = 'r'
        self.eb_markersize  = 10
        """
        self.avg_linestyle  = '--'
        self.avg_linewidth  = 5
        self.avg_linecolor  = 'b'
        self.avg_markerfacecolor = 'b'
        self.avg_markeredgecolor = 'b'
        self.avg_markersize      = 8
        """

    def repaint(self):
        self.adjustErrbar(self.ebplot, self.x, self.y, self.xerrarr, self.yerrarr)
        self.axes.set_xlim(0.9*min(self.x), 1.1*max(self.x))
        self.axes.set_ylim(0.1*min(self.y), 2.0*max(self.y))
        self.figure.canvas.draw_idle()

    def adjustErrbar(self, err, x, y, x_error, y_error):
        ln, (errx_top, errx_bot, erry_top, erry_bot), (barsx, barsy) = err

        ln.set_data(x, y)

        x_base = x
        y_base = y

        xerr_top = x_base + x_error
        xerr_bot = x_base - x_error
        yerr_top = y_base + y_error
        yerr_bot = y_base - y_error

        errx_top.set_xdata(xerr_top)
        errx_bot.set_xdata(xerr_bot)
        errx_top.set_ydata(y_base)
        errx_bot.set_ydata(y_base)

        erry_top.set_xdata(x_base)
        erry_bot.set_xdata(x_base)
        erry_top.set_ydata(yerr_top)
        erry_bot.set_ydata(yerr_bot)

        new_segments_x = [np.array([[xt, y], [xb,y]]) for xt, xb, y in zip(xerr_top, xerr_bot, y_base)]
        new_segments_y = [np.array([[x, yt], [x,yb]]) for x, yt, yb in zip(x_base, yerr_top, yerr_bot)]
        barsx.set_segments(new_segments_x)
        barsy.set_segments(new_segments_y)

class ScanConfigFile(parseutils.ConfigFile):
    def __init__(self, infilename = '.cornalyzer.conf', *args, **kwargs):
        parseutils.ConfigFile.__init__(self, infilename = infilename, *args, **kwargs)

    def parseConfigs(self):
        pass
