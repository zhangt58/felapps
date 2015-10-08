#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
python modules for beamline matching utilities:
    matchwizard: main GUI framework for beamline matching

Author: Tong Zhang
Created: Sep. 23rd, 2015
"""

import wx
import time

from . import funutils
from . import pltutils

import beamline
import os

class MatchWizard(wx.Frame):
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
        self.createStatusbar()
        self.createPanel()
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
        info.Name = "MatchWizard"
        info.Version = self.appversion
        info.Copyright = "(C) 2014-2015 Tong Zhang, SINAP, CAS"
        info.Description = wordwrap(
            "This application is created for beamline matching.\n"

            "It is designed by Python language, using GUI module of wxPython.",
            350, wx.ClientDC(self))
        info.WebSite = ("", "Cornalyzer home page") # fill it when webpage is ready
        info.Developers = [ "Tong Zhang <zhangtong@sinap.ac.cn>"]
        licenseText = "MatchWizard is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.\n" + "\nMatchWizard is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.\n" + "\nYou should have received a copy of the GNU General Public License along with MatchWizard; if not, write to the Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA"
        info.License = wordwrap(licenseText, 500, wx.ClientDC(self))
        wx.AboutBox(info)

    def postInit(self):
        self.matchsec_udn_flag_cb.SetValue(False)
        self.matchsec_udn_tc.Disable()
        self.matchsec_udn_btn.Disable()
        self.matchsec1_rb.Enable()
        self.matchsec2_rb.Enable()
        self.matchsec3_rb.Enable()
        self.matchsec4_rb.Enable()

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
        self.statusbar.appinfo = wx.StaticText(self.statusbar, id = wx.ID_ANY, label = u"MatchWizard powered by Python")
        self.timenow_st        = wx.StaticText(self.statusbar, id = wx.ID_ANY, label = u"2015-06-05 14:00:00 CST")
        appversion             = wx.StaticText(self.statusbar, id = wx.ID_ANY, label = u" (Version: " + self.appversion + ")")
        self.statusbar.AddWidget(self.statusbar.appinfo, funutils.ESB.ESB_ALIGN_LEFT )
        self.statusbar.AddWidget(self.timenow_st,        funutils.ESB.ESB_ALIGN_RIGHT)
        self.statusbar.AddWidget(appversion,             funutils.ESB.ESB_ALIGN_RIGHT)

    def preInit(self):
        self.fontsize_button     = 12 
        self.fontsize_statictext = 12
        self.fontsize_staticbox  = 10
        self.fontsize_textctrl   = 12
        self.backcolor_panel     = '#DDDDDD'
        self.fontcolor_staticbox = '#4B4B4B'
        self.bordersize          = 12

        # beamline filenames
        self.latticefile = './lattice/testbl.list'
 
    def createPanel(self):
        # make background panel
        self.panel = funutils.createwxPanel(self, funutils.hex2rgb('#B1B1B1'))

        # vertical box sizer for holding panel_u and panel_d
        topbox    = wx.BoxSizer(wx.VERTICAL)
        bottombox = wx.BoxSizer(wx.VERTICAL)

        # top and bottom panels
        self.panel_u = funutils.createwxPanel(self.panel, funutils.hex2rgb(self.backcolor_panel))
        self.panel_d = funutils.createwxPanel(self.panel, funutils.hex2rgb(self.backcolor_panel))

        # hbox in top panel 
        latvispanel_sb      = funutils.createwxStaticBox(self.panel_u, label = 'Lattice Visualization', fontcolor=funutils.hex2rgb(self.fontcolor_staticbox), fontsize = self.fontsize_staticbox)
        latvispanel_sbsizer = wx.StaticBoxSizer(latvispanel_sb, wx.HORIZONTAL)

        # up left
        # choose matching section
        self.matchsec1_rb = wx.RadioButton(self.panel_u, label = 'Beamline #1', style = wx.RB_GROUP)
        self.matchsec2_rb = wx.RadioButton(self.panel_u, label = 'Beamline #2')
        self.matchsec3_rb = wx.RadioButton(self.panel_u, label = 'Beamline #3')
        self.matchsec4_rb = wx.RadioButton(self.panel_u, label = 'Beamline #4')
        self.matchsec_udn_flag_cb = wx.CheckBox(self.panel_u, label = 'User defined')
        self.matchsec_udn_tc      = wx.TextCtrl(self.panel_u, value = '', style = wx.TE_READONLY)
        self.matchsec_udn_btn     = wx.Button(self.panel_u, label = 'Browse')

        matchsec_udn_hbox = wx.BoxSizer(wx.HORIZONTAL)
        matchsec_udn_hbox.Add(self.matchsec_udn_tc, 1, wx.ALIGN_CENTER_VERTICAL, 10)
        matchsec_udn_hbox.Add(self.matchsec_udn_btn, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        
        matchbl_sb = funutils.createwxStaticBox(self.panel_u, label = 'Choose Beamline', fontcolor=funutils.hex2rgb(self.fontcolor_staticbox), fontsize = self.fontsize_staticbox*0.8)
        matchbl_sbsizer = wx.StaticBoxSizer(matchbl_sb, wx.VERTICAL)
        matchbl_sbsizer.Add(self.matchsec1_rb, proportion = 0, flag = wx.EXPAND | wx.TOP | wx.LEFT | wx.ALIGN_LEFT, border = 10)
        matchbl_sbsizer.Add(self.matchsec2_rb, proportion = 0, flag = wx.EXPAND | wx.TOP | wx.LEFT | wx.ALIGN_LEFT, border = 10)
        matchbl_sbsizer.Add(self.matchsec3_rb, proportion = 0, flag = wx.EXPAND | wx.TOP | wx.LEFT | wx.ALIGN_LEFT, border = 10)
        matchbl_sbsizer.Add(self.matchsec4_rb, proportion = 0, flag = wx.EXPAND | wx.TOP | wx.LEFT | wx.ALIGN_LEFT, border = 10)
        matchbl_sbsizer.Add(self.matchsec_udn_flag_cb, proportion = 0, flag = wx.EXPAND | wx.TOP | wx.LEFT | wx.ALIGN_LEFT, border = 10)
        matchbl_sbsizer.Add(matchsec_udn_hbox, proportion = 0, flag = wx.EXPAND | wx.TOP | wx.LEFT | wx.ALIGN_LEFT, border = 10)
        
        # up right
        self.blvizpanel = LatVisPanel(self.panel_u, figsize=(5, 3), dpi = 80, bgcolor = funutils.hex2rgb(self.backcolor_panel))

        # set sizer for panel_u
        latvispanel_sbsizer.Add(matchbl_sbsizer, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 10)
        latvispanel_sbsizer.Add(self.blvizpanel, proportion = 3, flag = wx.EXPAND | wx.TOP | wx.BOTTOM | wx.RIGHT, border = 10)

        sizer_u = wx.BoxSizer(wx.VERTICAL)
        sizer_u.Add(latvispanel_sbsizer, proportion = 1, flag = wx.EXPAND | wx.ALL, border = self.bordersize)
        self.panel_u.SetSizerAndFit(sizer_u)
        topbox.Add(self.panel_u, proportion = 1, flag = wx.EXPAND)

        #--------------------------------------------------------------------------------------------#

        # hbox in bottom panel
        matchpanel_sb      = funutils.createwxStaticBox(self.panel_d, label = 'Matching Operation', fontcolor=funutils.hex2rgb(self.fontcolor_staticbox), fontsize = self.fontsize_staticbox)
        matchpanel_sbsizer = wx.StaticBoxSizer(matchpanel_sb, wx.HORIZONTAL)


        # to be implemented
        test_statictext = funutils.MyStaticText(self.panel_d, label = 'TO BE IMPLEMENTED...', fontsize = 30, fontcolor = 'grey')
        matchpanel_sbsizer.Add(test_statictext, flag = wx.ALIGN_CENTER | wx.ALL, border = 30)


        # set sizer for panel_d
        sizer_d = wx.BoxSizer(wx.VERTICAL)
        sizer_d.Add(matchpanel_sbsizer, proportion = 1, flag = wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT, border = self.bordersize)
        self.panel_d.SetSizerAndFit(sizer_d)
        bottombox.Add(self.panel_d, proportion = 1, flag = wx.EXPAND)

        # set sizer
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(topbox,    proportion = 2, flag = wx.EXPAND | wx.ALL)
        vbox.Add(bottombox, proportion = 3, flag = wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT)
        self.panel.SetSizer(vbox)
        osizer = wx.BoxSizer(wx.HORIZONTAL)
        osizer.SetMinSize((1000, 750))
        osizer.Add(self.panel, proportion = 1, flag = wx.EXPAND)
        self.SetSizerAndFit(osizer)

        # event bindings
        self.Bind(wx.EVT_CHECKBOX,    self.onCheckUserDefinedBL, self.matchsec_udn_flag_cb)
        self.Bind(wx.EVT_BUTTON,      self.onChooseBL,           self.matchsec_udn_btn    )
        self.Bind(wx.EVT_RADIOBUTTON, self.onVisLattice)

    def onVisLattice(self, event):
        rblabel = event.GetEventObject().GetLabel()

        if rblabel == 'Beamline #1':
            bllist = beamline.blparser.madParser(self.latticefile, 'BL1')
            vistitle = 'Lattice #1'
        elif rblabel == 'Beamline #2':
            bllist = beamline.blparser.madParser(self.latticefile, 'BL2')
            vistitle = 'Lattice #2'
        elif rblabel == 'Beamline #3':
            bllist = beamline.blparser.madParser(self.latticefile, 'BL3')
            vistitle = 'Lattice #3'
        elif rblabel == 'Beamline #4':
            bllist = beamline.blparser.madParser(self.latticefile, 'BL4')
            vistitle = 'Lattice #4'

        blpatchlist, xlim, ylim = beamline.makeBeamline(bllist, startpoint = (5, 5))

        self.blvizpanel.blpatchlist = blpatchlist
        self.blvizpanel.xranges = xlim
        self.blvizpanel.yranges = ylim
        self.blvizpanel.clear()
        self.blvizpanel.visBeamline()
        self.blvizpanel.axes.set_title(vistitle)
        self.blvizpanel.refresh()

    def onCheckUserDefinedBL(self, event):
        if event.GetEventObject().IsChecked():
            self.matchsec_udn_btn.Enable()
            self.matchsec_udn_tc.Enable()
            self.matchsec1_rb.Disable()
            self.matchsec2_rb.Disable()
            self.matchsec3_rb.Disable()
            self.matchsec4_rb.Disable()
        else:
            self.matchsec_udn_tc.Disable()
            self.matchsec_udn_btn.Disable()
            self.matchsec1_rb.Enable()
            self.matchsec2_rb.Enable()
            self.matchsec3_rb.Enable()
            self.matchsec4_rb.Enable()

    def onChooseBL(self, event):
        try:
            latfile = funutils.getFileToLoad(self, ext = '*', flag = 'single')
            self.matchsec_udn_tc.SetValue(latfile)

            bllist = beamline.blparser.madParser(latfile, 'BL')
            vistitle = os.path.basename(latfile)

            blpatchlist, xlim, ylim = beamline.makeBeamline(bllist, startpoint = (5, 5))

            self.blvizpanel.blpatchlist = blpatchlist
            self.blvizpanel.xranges = xlim
            self.blvizpanel.yranges = ylim
            self.blvizpanel.clear()
            self.blvizpanel.visBeamline()
            self.blvizpanel.axes.set_title(vistitle)
            self.blvizpanel.refresh()
        except:
            pass

class LatVisPanel(pltutils.ImagePanelxy):
    def __init__(self, parent, figsize, dpi, bgcolor, **kwargs):
        pltutils.ImagePanelxy.__init__(self, parent, figsize, dpi, bgcolor, **kwargs)

    def clear(self):
        self.figure.clear()

    def refresh(self):
        self.figure.canvas.draw_idle()

    def visBeamline(self, zoomfac = 1.5): 
        # define self.blpatchlist first
        # and xranges = (xmin, xmax), yranges = (ymin, ymax) if set x, y ranges
        self.axes = self.figure.add_subplot(111)
        for ins in self.blpatchlist:
            [self.axes.add_patch(inspatch) for inspatch in ins.patch]
        
        x1, x2 = self.xranges
        y1, y2 = self.yranges
        minx = 0.5 * (x2 + x1) - 0.5 * zoomfac * (x2 - x1)
        maxx = 0.5 * (x2 + x1) + 0.5 * zoomfac * (x2 - x1)
        miny = 0.5 * (y2 + y1) - 0.5 * zoomfac * (y2 - y1)
        maxy = 0.5 * (y2 + y1) + 0.5 * zoomfac * (y2 - y1)
        self.axes.set_xlim([minx, maxx])
        self.axes.set_ylim([miny, maxy])

        self.figure.canvas.draw()
