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

from . import funutils

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
        pass

    def postInit(self):
        pass

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
        self.statusbar.appinfo = wx.StaticText(self.statusbar, id = wx.ID_ANY, label = u"DataWorkshop powered by Python")
        self.timenow_st        = wx.StaticText(self.statusbar, id = wx.ID_ANY, label = u"2015-06-05 14:00:00 CST")
        appversion             = wx.StaticText(self.statusbar, id = wx.ID_ANY, label = u" (Version: " + self.appversion + ")")
        self.statusbar.AddWidget(self.statusbar.appinfo, funutils.ESB.ESB_ALIGN_LEFT )
        self.statusbar.AddWidget(self.timenow_st,        funutils.ESB.ESB_ALIGN_RIGHT)
        self.statusbar.AddWidget(appversion,             funutils.ESB.ESB_ALIGN_RIGHT)


    def createPanel(self):
        # make background panel
        self.panel = funutils.createwxPanel(self, funutils.hex2rgb('#B1B1B1'))

        #hbox = 

        # set sizer
        #self.panel.SetSizer(hbox)
        osizer = wx.BoxSizer(wx.HORIZONTAL)
        osizer.SetMinSize((1000, 750))
        osizer.Add(self.panel, proportion = 1, flag = wx.EXPAND)
        self.SetSizerAndFit(osizer)
 

