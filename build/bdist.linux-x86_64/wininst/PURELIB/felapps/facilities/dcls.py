#!/usr/bin/env python
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------#

"""
Author: Tong Zhang
Created Time: 10:58, Jan. 28, 2015

FEL experiment panel for Dalian Coherent Light Source.
This is the main GUI frame.
"""

#------------------------------------------------------------------------#

import wx
from ..utils import funutils
from ..utils import felutils
from ..utils import resutils

#------------------------------------------------------------------------#

class MainFrame(wx.Frame):

#------------------------------------------------------------------------#

    def __init__(self, parent, **kwargs):
        super(self.__class__, self).__init__(parent, id = wx.ID_ANY, **kwargs)
        self.InitUI()
        self.Show()

#------------------------------------------------------------------------#

    def InitUI(self):
        self.createMenu()
        self.createPanel()
        self.createStatusbar()

#------------------------------------------------------------------------#

    def createMenu(self):
        self.menubar = wx.MenuBar()
        
        ## File (menu structure)
        ### Import Configuration
        ### Export Configuration
        ### --------------------
        ### Exit
        fileMenu = wx.Menu()
        self.importItem = fileMenu.Append(wx.ID_ANY, 
                u'&Import Configuration\tCtrl+Shift+I', u'Import config file')
        self.exportItem = fileMenu.Append(wx.ID_ANY,
                u'&Export Configuration\tCtrl+Shift+E', u'Export config file')
        fileMenu.AppendSeparator()
        self.exitItem = fileMenu.Append(wx.ID_EXIT, u'E&xit\tCtrl+W',
                u'Exit this application')
        
        ### define accelerator table (not working 2015-01-28)
        """
        accel_entries = [wx.AcceleratorEntry() for i in range(3)]
        accel_entries[0].Set(wx.ACCEL_CTRL | wx.ACCEL_SHIFT, ord('I'), self.importItem.GetId())
        accel_entries[1].Set(wx.ACCEL_CTRL | wx.ACCEL_SHIFT, ord('E'), self.exportItem.GetId())
        accel_entries[2].Set(wx.ACCEL_CTRL,                  ord('W'), self.exitItem.GetId()  )
        accel_table = wx.AcceleratorTable(accel_entries)
        self.SetAcceleratorTable(accel_table)
        """

        ### bind events
        self.Bind(wx.EVT_MENU, self.onImport, id = self.importItem.GetId())
        self.Bind(wx.EVT_MENU, self.onExport, id = self.exportItem.GetId())
        self.Bind(wx.EVT_MENU, self.onExit,   id = self.exitItem.GetId())

        ## Help (menu structure)
        ### About
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT, '&About\tF1',
                'About this application')
        self.Bind(wx.EVT_MENU, self.onAbout, id = wx.ID_ABOUT)

        ##setup menubar
        self.menubar.Append(fileMenu, '&File')
        self.menubar.Append(helpMenu, '&Help')
        
        self.SetMenuBar(self.menubar)

#------------------------------------------------------------------------#

    def onImport(self, event):
        print "you call me (import) for what?"

#------------------------------------------------------------------------#

    def onExport(self, event):
        print "you call me (export) for what?"

#------------------------------------------------------------------------#

    def onExit(self, event):
        dial = wx.MessageDialog(self, 
                message = "Are you sure to exit this application?",
                caption = "Exit Warning",
                style = wx.YES_NO | wx.NO_DEFAULT | wx.CENTRE | wx.ICON_QUESTION)
        if dial.ShowModal() == wx.ID_YES:
            self.Destroy()

#------------------------------------------------------------------------#

    def onAbout(self, event):
        from wx.lib.wordwrap import wordwrap
        aboutinfo = wx.AboutDialogInfo()
        #aboutinfo.SetIcon(wx.Icon(funutils.getResPath('logo.jpg'), wx.BITMAP_TYPE_PNG))
        aboutinfo.SetIcon(resutils.mainlogoicon.GetIcon())
        aboutinfo.SetName(u'FEL Commissioning Application for DCLS')
        aboutinfo.SetVersion('\nversion: 1.0.0')
        descriptionText = u"Application designed for DCLS FEL commissioning." + "\nPowered by Python/C/C++"
        aboutinfo.SetDescription(wordwrap(descriptionText, 500, wx.ClientDC(self)))
        aboutinfo.SetCopyright(u"(C) 2014-2015 Tong Zhang, SINAP, CAS")
        aboutinfo.SetWebSite([u"http://210.72.8.51/FELwiki/index.php/DCLS",
                u"DCLS home page"])
        aboutinfo.AddDeveloper(u"Tong Zhang <zhangtong@sinap.ac.cn>")
        licenseText = u"FEL commissioning application for DCLS is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.\n" + "\nFEL commissioning application for DCLS is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.\n" + "\nYou should have received a copy of the GNU General Public License along with this application; if not, write to the Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA"
        aboutinfo.SetLicense(wordwrap(licenseText, 500, wx.ClientDC(self)))
        wx.AboutBox(aboutinfo)

#------------------------------------------------------------------------#

    def createStatusbar(self):
        self.sb = self.CreateStatusBar()
    
#------------------------------------------------------------------------#

    def createPanel(self):
        ## create the base container: panel
        self.panel = wx.Panel(self, id = wx.ID_ANY)
        ### configure the panel:
        #self.panel.SetBackgroundColour('red')
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        ## Title: 'Dalian Coherent Light Source --- FEL Commissioning'
        title_st = wx.StaticText(self.panel, 
                label = u'Dalian Coherent Light Source --- FEL Commissioning',
                style = wx.ALIGN_CENTRE)
        ### configure title_st
        title_st.SetForegroundColour('blue')
        titlefont =wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        titlefont.SetPointSize(20)
        titlefont.SetWeight(wx.FONTWEIGHT_BOLD)
        title_st.SetFont(titlefont)
        ### add to boxsizer
        vbox.Add(title_st, flag = wx.ALIGN_CENTRE | wx.ALL, border = 20)

        ## horizontal separate line
        sl_below_title = wx.StaticLine(self.panel, style = wx.LI_HORIZONTAL)
        ### add to boxsizer
        vbox.Add(sl_below_title, flag = wx.EXPAND | wx.ALIGN_CENTRE, border = 10)

        ## font for staticbox
        sbfont = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        sbfont.SetPointSize(12)
        sbfont.SetWeight(wx.FONTWEIGHT_BOLD)
        sbfontcolor = 'MAGENTA'

        ## staticbox for layout
        sbox1 = wx.StaticBox(self.panel, id = wx.ID_ANY, label = u'Schematic Layout of DCLS')
        ### config staticbox
        sbox1.SetFont(sbfont)
        sbox1.SetForegroundColour(sbfontcolor)
        ### create the sizer
        sbsizer_layout = wx.StaticBoxSizer(sbox1, orient = wx.VERTICAL)
        ### show image
    
        ## todo: automatic resize w.r.t. size of sizer, 2015-01-28
        #layoutBitmap = wx.StaticBitmap(self.panel, wx.ID_ANY, wx.BitmapFromImage(funutils.rescaleImage(funutils.getResPath('DCLSlayout.png'), 1.0)))
        layoutBitmap = wx.StaticBitmap(self.panel, wx.ID_ANY, wx.BitmapFromImage(funutils.rescaleImage(resutils.dclslayouticon.GetImage(), 1.0)))
        sbsizer_layout.Add(layoutBitmap, proportion = 1, flag = wx.ALIGN_CENTRE)

        ### add to boxsizer
        vbox.Add(sbsizer_layout, proportion = 1, flag = wx.EXPAND | wx.ALIGN_CENTRE | wx.TOP | wx.LEFT | wx.RIGHT, border = 20)

        ## staticbox for FEL functional box
        sbox2 = wx.StaticBox(self.panel, id = wx.ID_ANY, label = u'High-gain Harmonic Generation')
        ### config staticbox
        sbox2.SetFont(sbfont)
        sbox2.SetForegroundColour(sbfontcolor)
        ### create the sizer
        sbsizer_HGHG = wx.StaticBoxSizer(sbox2, orient = wx.VERTICAL)

        ### hyperlink to ModsPanel, MatchPanel and RadisPanel
        moddsBitbtn = wx.BitmapButton(self.panel, id = wx.ID_ANY, 
                bitmap = wx.BitmapFromImage(funutils.rescaleImage(resutils.moddsicon.GetImage(), 1.0)))
        radisBitbtn = wx.BitmapButton(self.panel, id = wx.ID_ANY, 
                bitmap = wx.BitmapFromImage(funutils.rescaleImage(resutils.radisicon.GetImage(), 1.0)))
        matchBitbtn = wx.BitmapButton(self.panel, id = wx.ID_ANY, 
                bitmap = wx.BitmapFromImage(funutils.rescaleImage(resutils.matchicon.GetImage(), 1.0)))
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(moddsBitbtn, proportion = 1, flag = wx.LEFT | wx.TOP | wx.BOTTOM, border = 10)
        hbox.Add(matchBitbtn, proportion = 1, flag = wx.LEFT | wx.TOP | wx.BOTTOM, border = 10)
        hbox.Add(radisBitbtn, proportion = 1, flag = wx.LEFT | wx.TOP | wx.BOTTOM | wx.RIGHT, border = 10)
        sbsizer_HGHG.Add(hbox, proportion = 1, flag = wx.ALIGN_CENTER | wx.EXPAND | wx.ALL, border = 10)
        ### add to boxsizer
        vbox.Add(sbsizer_HGHG, proportion = 0, flag = wx.EXPAND | wx.ALIGN_CENTRE | wx.ALL, border = 20)

        ## set boxsizer
        self.panel.SetSizer(vbox)

        ## bind events
        self.Bind(wx.EVT_CLOSE, self.onExit)
        self.Bind(wx.EVT_BUTTON, self.onModds, id = moddsBitbtn.GetId())# ID_MODDSBBTN)
        self.Bind(wx.EVT_BUTTON, self.onMatch, id = matchBitbtn.GetId())# ID_MATCHBBTN)
        self.Bind(wx.EVT_BUTTON, self.onRadis, id = radisBitbtn.GetId())# ID_RADISBBTN)

#------------------------------------------------------------------------#

    def onModds(self, event):
        self.moddspanel = felutils.ModdsPanel(self, 
                title = u'Laser-beam Interaction and Harmonic Generation',
                size = (880, 668),
                style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.moddspanel.Show()
        self.moddspanel.MakeModal()

#------------------------------------------------------------------------#

    def onMatch(self, event):
        self.matchpanel = felutils.MatchPanel(self, 
                title = u'Beam Envelope Matching Operation',
                size = (880, 668),
                style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.matchpanel.Show()
        self.matchpanel.MakeModal()

#------------------------------------------------------------------------#

    def onRadis(self, event):
        self.radispanel = felutils.RadisPanel(self, 
                title = u'FEL Radiation Generation',
                size = (880, 668),
                style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.radispanel.Show()
        self.radispanel.MakeModal()

#------------------------------------------------------------------------#

def run():
    app = wx.App(redirect = True)
    myframe = MainFrame(None, style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
    myframe.SetTitle('FEL Commissioning Application for DCLS')
    myframe.SetSize((880,668))
    myframe.Centre()
    app.MainLoop()

#------------------------------------------------------------------------#

if __name__ == '__main__':
    run()

#------------------------------------------------------------------------#
