#!/usr/bin/env python
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------#

"""
Author: Tong Zhang
Created Time: 20:14, Jan. 28, 2015

FEL utilities:
    1 Three functional sections for HGHG:
    1.1: ModdsPanel
    1.2: MatchPanel
    1.3: RadisPanel
"""

#------------------------------------------------------------------------#

import wx
import epics
import time
import os
import numpy as np
from . import funutils
from . import pltutils
from . import resutils
import matplotlib.pyplot as plt

ID_POWER      = wx.NewId()
ID_LENGTH     = wx.NewId()
ID_OMEGA      = wx.NewId()
ID_PHASE      = wx.NewId()
ID_WVLTH      = wx.NewId()
ID_ENERGY     = wx.NewId()
ID_ESPREAD    = wx.NewId()
ID_BSIZE      = wx.NewId()
ID_EMITN      = wx.NewId()
ID_CURPEAK    = wx.NewId()
ID_MODXLAMD   = wx.NewId()
ID_MODNUM     = wx.NewId()
ID_MODGAP     = wx.NewId()
ID_IMAGL      = wx.NewId()
ID_IDRIL      = wx.NewId()
ID_IBFIELD    = wx.NewId()
ID_DISPERSION = wx.NewId()

#------------------------------------------------------------------------#

class ModdsPanel(wx.Frame):

#------------------------------------------------------------------------#

    def __init__(self, parent, **kwargs):
        super(self.__class__, self).__init__(parent = parent,
                id = wx.ID_ANY, **kwargs)
        self.parent = parent
        self.InitUI()

#------------------------------------------------------------------------#

    def InitUI(self):
        self.createMenu()
        self.createPanel()
        self.createStatusbar()

#------------------------------------------------------------------------#

    def createMenu(self):
        self.menubar = wx.MenuBar()

        ## File (menu structure)
        ### Save
        ### Load
        ### --------------------
        ### Exit
        fileMenu = wx.Menu()
        self.saveItem = fileMenu.Append(wx.ID_ANY, 
                u'&Save\tCtrl+S', u'Save data to file')
        self.loadItem = fileMenu.Append(wx.ID_ANY,
                u'&Load\tCtrl+L', u'Load data from file')
        fileMenu.AppendSeparator()
        self.exitItem = fileMenu.Append(wx.ID_EXIT, u'E&xit\tCtrl+W',
                u'Exit this frame')

        ## Help (menu structure)
        ### About
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT, '&About\tF1',
                'About information')
        self.Bind(wx.EVT_MENU, self.onAbout, id = wx.ID_ABOUT)

        ##setup menubar
        self.menubar.Append(fileMenu, '&File')
        self.menubar.Append(helpMenu, '&Help')
        
        self.SetMenuBar(self.menubar)

        ## bind events
        self.Bind(wx.EVT_MENU, self.onSave, id = self.saveItem.GetId())
        self.Bind(wx.EVT_MENU, self.onLoad, id = self.loadItem.GetId())
        self.Bind(wx.EVT_MENU, self.onExit, id = self.exitItem.GetId())

#------------------------------------------------------------------------#

    def createPanel(self):
        ## create the base container: panel
        self.panel = wx.Panel(self, id = wx.ID_ANY)
        ### configure the panel
        #self.panel.SetBackgroundColour('red')

        vbox = wx.BoxSizer(wx.VERTICAL)

        ## Title: 'Laser-beam Interaction --- Harmonic Generation'
        title_st = wx.StaticText(self.panel, 
                label = u'Laser-beam Interaction --- Harmonic Generation',
                style = wx.ALIGN_CENTRE)
        ### configure title_st
        title_st.SetForegroundColour('MEDIUM SEA GREEN')
        titlefont =wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        titlefont.SetPointSize(20)
        titlefont.SetWeight(wx.FONTWEIGHT_BOLD)
        title_st.SetFont(titlefont)
        ### add to boxsizer
        vbox.Add(title_st, flag = wx.ALIGN_CENTRE | wx.ALL, border = 15)

        ## horizontal separate line
        sl_below_title = wx.StaticLine(self.panel, style = wx.LI_HORIZONTAL)
        ### add to boxsizer
        vbox.Add(sl_below_title, flag = wx.EXPAND | wx.ALIGN_CENTRE, border = 15)

        ## font for staticbox
        sbfont = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        sbfont.SetPointSize(12)
        sbfont.SetWeight(wx.FONTWEIGHT_BOLD)
        sbfontcolor = 'VIOLET RED'

        ## staticbox for detailed information of modulator+chicane (layout)
        sbox1 = wx.StaticBox(self.panel, id = wx.ID_ANY, 
                label = u'Harmonic Generation')
        ### config staticbox
        sbox1.SetFont(sbfont)
        sbox1.SetForegroundColour(sbfontcolor)
        ### create the sizer
        sbsizer_layout = wx.StaticBoxSizer(sbox1, orient = wx.VERTICAL)
        
        ### put the image
        #layoutBitmap = wx.StaticBitmap(self.panel, wx.ID_ANY, wx.BitmapFromImage(funutils.rescaleImage(funutils.getResPath('moddslayout.png'), 1.0)))
        layoutBitmap = wx.StaticBitmap(self.panel, wx.ID_ANY, wx.BitmapFromImage(funutils.rescaleImage(resutils.moddslayouticon.GetImage(), 1.0)))
        sbsizer_layout.Add(layoutBitmap, proportion = 1, flag = wx.ALIGN_CENTRE)

        ### add to boxsizer
        vbox.Add(sbsizer_layout, proportion = 3, flag = wx.EXPAND | wx.ALIGN_CENTRE | wx.TOP | wx.LEFT | wx.RIGHT, border = 15)

        ## hbox to put two staticbox
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        ### staticbox for parameters configuration
        sbox21 = wx.StaticBox(self.panel, id = wx.ID_ANY,
                label = u'Parameters Configuration')
        ### config staticbox
        sbox21.SetFont(sbfont)
        sbox21.SetForegroundColour(sbfontcolor)
        ### create sizer
        sbsizer_paramsconfig = wx.StaticBoxSizer(sbox21, orient = wx.VERTICAL)

        ### put four buttons here: Seedlaser, E-beam, Modulator, Chicane

        self.paramslaserbtn     = wx.Button(self.panel, id = wx.ID_ANY, label = 'Seedlaser')
        self.paramsebeambtn     = wx.Button(self.panel, id = wx.ID_ANY, label = 'E-beam'   )
        self.paramsmodulatorbtn = wx.Button(self.panel, id = wx.ID_ANY, label = 'Modulator')
        self.paramschicanebtn   = wx.Button(self.panel, id = wx.ID_ANY, label = 'Chicane'  )

        #### bind events
        self.Bind(wx.EVT_BUTTON, self.OnConfigLaser,     self.paramslaserbtn)
        self.Bind(wx.EVT_BUTTON, self.OnConfigEbeam,     self.paramsebeambtn)
        self.Bind(wx.EVT_BUTTON, self.OnConfigModulator, self.paramsmodulatorbtn)
        self.Bind(wx.EVT_BUTTON, self.OnConfigChicane,   self.paramschicanebtn)

        #### config buttons
        ##### button label font
        btnfont = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        btnfont.SetPointSize(18)
        btnfont.SetWeight(wx.FONTWEIGHT_NORMAL)
        btnfontcolor = '#CF4913'
        btnfacecolor = '#B1D28F'
        ##### do configuration
        self.paramslaserbtn.SetFont(btnfont)
        self.paramsebeambtn.SetFont(btnfont)
        self.paramsmodulatorbtn.SetFont(btnfont)
        self.paramschicanebtn.SetFont(btnfont)
        self.paramslaserbtn.SetForegroundColour(btnfontcolor)
        self.paramsebeambtn.SetForegroundColour(btnfontcolor)
        self.paramsmodulatorbtn.SetForegroundColour(btnfontcolor)
        self.paramschicanebtn.SetForegroundColour(btnfontcolor)
        self.paramslaserbtn.SetBackgroundColour(btnfacecolor)
        self.paramsebeambtn.SetBackgroundColour(btnfacecolor)
        self.paramsmodulatorbtn.SetBackgroundColour(btnfacecolor)
        self.paramschicanebtn.SetBackgroundColour(btnfacecolor)
        
        sbsizer_paramsconfig.Add(self.paramslaserbtn,     proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border = 18)
        sbsizer_paramsconfig.Add(self.paramsebeambtn,     proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border = 18)
        sbsizer_paramsconfig.Add(self.paramsmodulatorbtn, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border = 18)
        sbsizer_paramsconfig.Add(self.paramschicanebtn,   proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border = 18)
        sbsizer_paramsconfig.Add((-1, 18))

        ### add sbsizer_paramsconfig sizer to hbox2
        hbox2.Add(sbsizer_paramsconfig, proportion = 1, 
                flag = wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM, border = 15)

        ### staticbox for two phasespace imagepanel
        sbox22 = wx.StaticBox(self.panel, id = wx.ID_ANY,
                label = u'Longitudianl Phase-space')
        sbox22.SetFont(sbfont)
        sbox22.SetForegroundColour(sbfontcolor)
        sbsizer_phasespace  = wx.StaticBoxSizer(sbox22, orient = wx.HORIZONTAL)
        
        ## font for staticbox
        sb1font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        sb1font.SetPointSize(10)
        sb1font.SetWeight(wx.FONTWEIGHT_BOLD)
        sb1fontcolor = 'blue'

        #### modulated phasespace
        sbox221 = wx.StaticBox(self.panel, id = wx.ID_ANY,
                label = u'Modulated Beam', style = wx.ALIGN_CENTER)
        sbox221.SetFont(sb1font)
        sbox221.SetForegroundColour(sb1fontcolor)
        sbsizer_psmod = wx.StaticBoxSizer(sbox221, orient = wx.VERTICAL)

        #### plotpanel for psmod
        self.psmodgraph = pltutils.ImagePanelxy(self.panel, 
                                              figsize = (3.9,3.9), 
                                              dpi = 60, 
                                              bgcolor = None)
        sbsizer_psmod.Add(self.psmodgraph, proportion = 1, flag = wx.ALIGN_CENTER | wx.ALL, border = 3)
        
        #### add to sbsizer_phasespace
        sbsizer_phasespace.Add(sbsizer_psmod, proportion = 1,
                flag = wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT | wx.TOP | wx.BOTTOM, border = 8)
        
        #### dispersed phasespace
        sbox222 = wx.StaticBox(self.panel, id = wx.ID_ANY,
                label = u'Dispersed Beam', style = wx.ALIGN_CENTER)
        sbox222.SetFont(sb1font)
        sbox222.SetForegroundColour(sb1fontcolor)
        sbsizer_pschi = wx.StaticBoxSizer(sbox222, orient = wx.VERTICAL)

        #### plotpanel for pschi
        self.pschigraph = pltutils.ImagePanelxy(self.panel, 
                                              figsize = (3.9,3.9), 
                                              dpi = 60, 
                                              bgcolor = None)
        sbsizer_pschi.Add(self.pschigraph, proportion = 1, flag = wx.ALIGN_CENTER | wx.ALL, border = 3)

        #### add to sbsizer_phasespace
        sbsizer_phasespace.Add(sbsizer_pschi, proportion = 1,
                flag = wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT | wx.TOP | wx.BOTTOM, border = 8)
        sbsizer_phasespace.Add((8,-1))

        ### add sbsizer_phasespace sizer to hbox2
        hbox2.Add(sbsizer_phasespace, proportion = 2, 
                flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, border = 15)
        ### add hbox2 to vbox
        vbox.Add(hbox2, proportion = 4, flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER | wx.EXPAND)

        ## set boxsizer
        self.panel.SetSizer(vbox)

        ## bind events
        self.Bind(wx.EVT_CLOSE, self.onExit)

#------------------------------------------------------------------------#

    # update phasespace after mod and chi
    def OnUpdatePS(self, psid = 'mod', newval = 0):
        import numpy as np
        import os
        gam0 = 587.87
        sigg = 0.01174
        if psid == 'mod': ## modulation
            au = funutils.aupmu(newval, 50)
            modfilecmd = 'sed -i "s/aw0.*/aw0=' + str(au) + '/;s/awd.*/awd=' + str(au) + '/i" ../sim/mod.in'
            os.system(modfilecmd)
            os.system('cd ../sim; bash runmod.sh')
            file = open('../sim/mod.out.dpa','rb')
            data = np.fromfile(file,dtype='double').reshape(6, 8192)
            self.psmodgraph.x, self.psmodgraph.y= data[1,:], (data[0,:]-gam0)/sigg
            self.psmodgraph.repaint()
                     
        elif psid == 'chi': ## dispersed
            modfilecmd = 'sed -i "s/ibfield.*/ibfield=' + str(newval) + '/i" ../sim/modp.in'
            os.system(modfilecmd)
            os.system('cd ../sim; bash runchi.sh')
            file = open('../sim/modp.out.dpa','rb')
            data = np.fromfile(file,dtype='double').reshape(6, 8192)
            self.pschigraph.x, self.pschigraph.y= data[1,:], (data[0,:]-gam0)/sigg
            self.pschigraph.repaint()

            ## update pv
            os.system('cd ../sim; bash rundiag.sh')
            intp, farfield = funutils.readfld('../sim/rad_diag.out.dfl')
            #print intp, farfield.size
            
            import epics
            fieldarrpv = epics.PV('DCLS:DIAG:PROF:ARR')
            fieldintpv = epics.PV('DCLS:DIAG:PROF:INT:SET')
            farfieldarr = np.array(farfield, dtype = np.double).flatten()
            fieldarrpv.put(farfieldarr)
            fieldintpv.put(intp)

#------------------------------------------------------------------------#

    def OnConfigLaser(self, event):
        self.laserpanel = LaserConfigPanel(self)
        self.laserpanel.SetTitle('Seedlaser Configuration Panel')
        self.laserpanel.SetSize((760,530))
        self.laserpanel.Show()

#------------------------------------------------------------------------#

    def OnConfigEbeam(self, event):
        self.ebeampanel = EbeamConfigPanel(self)
        self.ebeampanel.SetTitle('E-beam Configuration Panel')
        self.ebeampanel.SetSize((760,530))
        self.ebeampanel.Show()

#------------------------------------------------------------------------#

    def OnConfigModulator(self, event):
        self.modpanel = ModConfigPanel(self)
        self.modpanel.SetTitle('Modulator Configuration Panel')
        self.modpanel.SetSize((760,530))
        self.modpanel.Show()

#------------------------------------------------------------------------#

    def OnConfigChicane(self, event):
        self.chipanel = ChiConfigPanel(self)
        self.chipanel.SetTitle('Chicane Configuration Panel')
        self.chipanel.SetSize((760,530))
        self.chipanel.Show()

#------------------------------------------------------------------------#

    def createStatusbar(self):
        self.sb = self.CreateStatusBar()

#------------------------------------------------------------------------#

    def onExit(self, event):
        dial = wx.MessageDialog(self, 
                message = "Are you sure to exit this application?",
                caption = "Exit Warning",
                style = wx.YES_NO | wx.NO_DEFAULT | wx.CENTRE | wx.ICON_QUESTION)
        if dial.ShowModal() == wx.ID_YES:
            self.Destroy()
            self.MakeModal(False)

#------------------------------------------------------------------------#

    def onSave(self, event):
        pass

#------------------------------------------------------------------------#

    def onLoad(self, event):
        pass

#------------------------------------------------------------------------#

    def onAbout(self, event):
        from wx.lib.wordwrap import wordwrap
        aboutinfo = wx.AboutDialogInfo()
        aboutinfo.SetIcon(resutils.moddslogoicon.GetIcon())
        aboutinfo.SetName(u'Laser-beam Interaction Application')
        aboutinfo.SetVersion('\nversion: 1.0.0')
        descriptionText = u"Application designed for laser-beam interaction commissioning" + "\nPowered by Python/C/C++"
        aboutinfo.SetDescription(wordwrap(descriptionText, 500, wx.ClientDC(self)))
        aboutinfo.SetCopyright(u"(C) 2014-2015 Tong Zhang, SINAP, CAS")
        aboutinfo.SetWebSite([u"http://210.72.8.51/FELwiki/index.php/DCLS",
                u"DCLS home page"])
        aboutinfo.AddDeveloper(u"Tong Zhang <zhangtong@sinap.ac.cn>")
        licenseText = u"Laser-beam Interaction Application is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.\n" + "\nLaser-beam Interaction Application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.\n" + "\nYou should have received a copy of the GNU General Public License along with this application; if not, write to the Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA"
        aboutinfo.SetLicense(wordwrap(licenseText, 500, wx.ClientDC(self)))
        wx.AboutBox(aboutinfo)

#------------------------------------------------------------------------#

class MatchPanel(wx.Frame):

#------------------------------------------------------------------------#

    def __init__(self, parent, **kwargs):
        super(self.__class__, self).__init__(parent = parent,
                id = wx.ID_ANY, **kwargs)
        self.parent = parent
        self.InitUI()

#------------------------------------------------------------------------#

    def InitUI(self):
        self.createMenu()
        self.createPanel()
        self.createStatusbar()

#------------------------------------------------------------------------#

    def createMenu(self):
        self.menubar = wx.MenuBar()

        ## File (menu structure)
        ### Save
        ### Load
        ### --------------------
        ### Exit
        fileMenu = wx.Menu()
        self.saveItem = fileMenu.Append(wx.ID_ANY, 
                u'&Save\tCtrl+S', u'Save data to file')
        self.loadItem = fileMenu.Append(wx.ID_ANY,
                u'&Load\tCtrl+L', u'Load data from file')
        fileMenu.AppendSeparator()
        self.exitItem = fileMenu.Append(wx.ID_EXIT, u'E&xit\tCtrl+W',
                u'Exit this frame')

        ## Help (menu structure)
        ### About
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT, '&About\tF1',
                'About information')
        self.Bind(wx.EVT_MENU, self.onAbout, id = wx.ID_ABOUT)

        ##setup menubar
        self.menubar.Append(fileMenu, '&File')
        self.menubar.Append(helpMenu, '&Help')
        
        self.SetMenuBar(self.menubar)

        ## bind events
        self.Bind(wx.EVT_MENU, self.onSave, id = self.saveItem.GetId())
        self.Bind(wx.EVT_MENU, self.onLoad, id = self.loadItem.GetId())
        self.Bind(wx.EVT_MENU, self.onExit, id = self.exitItem.GetId())

#------------------------------------------------------------------------#

    def createPanel(self):
        ## create the base container: panel
        self.panel = wx.Panel(self, id = wx.ID_ANY)
        ### configure the panel
        #self.panel.SetBackgroundColour('red')

        vbox = wx.BoxSizer(wx.VERTICAL)

        ## Title: 'Beam Envelope Matching Operation'
        title_st = wx.StaticText(self.panel, 
                label = u'Beam Envelope Matching Operation',
                style = wx.ALIGN_CENTRE)
        ### configure title_st
        title_st.SetForegroundColour('MEDIUM SEA GREEN')
        titlefont =wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        titlefont.SetPointSize(20)
        titlefont.SetWeight(wx.FONTWEIGHT_BOLD)
        title_st.SetFont(titlefont)
        ### add to boxsizer
        vbox.Add(title_st, flag = wx.ALIGN_CENTRE | wx.ALL, border = 15)

        ## horizontal separate line
        sl_below_title = wx.StaticLine(self.panel, style = wx.LI_HORIZONTAL)
        ### add to boxsizer
        vbox.Add(sl_below_title, flag = wx.EXPAND | wx.ALIGN_CENTRE, border = 15)

        ## font for staticbox
        sbfont = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        sbfont.SetPointSize(12)
        sbfont.SetWeight(wx.FONTWEIGHT_BOLD)
        sbfontcolor = 'VIOLET RED'

        ## staticbox for detailed information of radiator line (layout)
        sbox1 = wx.StaticBox(self.panel, id = wx.ID_ANY, 
                label = u'Beam Matching')
        ### config staticbox
        sbox1.SetFont(sbfont)
        sbox1.SetForegroundColour(sbfontcolor)
        ### create the sizer
        sbsizer_layout = wx.StaticBoxSizer(sbox1, orient = wx.VERTICAL)
        
        ### put the image
        layoutBitmap = wx.StaticBitmap(self.panel, wx.ID_ANY, wx.BitmapFromImage(funutils.rescaleImage(resutils.matchlayouticon.GetImage(), 1.0)))
        sbsizer_layout.Add(layoutBitmap, proportion = 1, flag = wx.ALIGN_CENTRE)

        ### add to boxsizer
        vbox.Add(sbsizer_layout, proportion = 3, flag = wx.EXPAND | wx.ALIGN_CENTRE | wx.TOP | wx.LEFT | wx.RIGHT, border = 15)


        ## set sizer
        self.panel.SetSizer(vbox)

        ## bind events
        self.Bind(wx.EVT_CLOSE, self.onExit)

#------------------------------------------------------------------------#

    def createStatusbar(self):
        self.sb = self.CreateStatusBar()

#------------------------------------------------------------------------#

    def onExit(self, event):
        dial = wx.MessageDialog(self, 
                message = "Are you sure to exit this application?",
                caption = "Exit Warning",
                style = wx.YES_NO | wx.NO_DEFAULT | wx.CENTRE | wx.ICON_QUESTION)
        if dial.ShowModal() == wx.ID_YES:
            self.Destroy()
            self.MakeModal(False)

#------------------------------------------------------------------------#

    def onSave(self, event):
        pass

#------------------------------------------------------------------------#

    def onLoad(self, event):
        pass

#------------------------------------------------------------------------#

    def onAbout(self, event):
        from wx.lib.wordwrap import wordwrap
        aboutinfo = wx.AboutDialogInfo()
        aboutinfo.SetIcon(resutils.matchlogoicon.GetIcon())
        aboutinfo.SetName(u'Beam-matching Application')
        aboutinfo.SetVersion('\nversion: 1.0.0')
        descriptionText = u"Application designed for beam matching commissioning" + "\nPowered by Python/C/C++"
        aboutinfo.SetDescription(wordwrap(descriptionText, 500, wx.ClientDC(self)))
        aboutinfo.SetCopyright(u"(C) 2014-2015 Tong Zhang, SINAP, CAS")
        aboutinfo.SetWebSite([u"http://210.72.8.51/FELwiki/index.php/DCLS",
                u"DCLS home page"])
        aboutinfo.AddDeveloper(u"Tong Zhang <zhangtong@sinap.ac.cn>")
        licenseText = u"Beam-matching Application is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.\n" + "\nBeam-matching Application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.\n" + "\nYou should have received a copy of the GNU General Public License along with this application; if not, write to the Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA"
        aboutinfo.SetLicense(wordwrap(licenseText, 500, wx.ClientDC(self)))
        wx.AboutBox(aboutinfo)

#------------------------------------------------------------------------#

class RadisPanel(wx.Frame):

#------------------------------------------------------------------------#

    def __init__(self, parent, **kwargs):
        super(self.__class__, self).__init__(parent = parent,
                id = wx.ID_ANY, **kwargs)
        self.parent = parent
        self.InitUI()

#------------------------------------------------------------------------#

    def InitUI(self):
        self.createMenu()
        self.createPanel()
        self.createStatusbar()

#------------------------------------------------------------------------#

    def createMenu(self):
        self.menubar = wx.MenuBar()

        ## File (menu structure)
        ### Save
        ### Load
        ### --------------------
        ### Exit
        fileMenu = wx.Menu()
        self.saveItem = fileMenu.Append(wx.ID_ANY, 
                u'&Save\tCtrl+S', u'Save data to file')
        self.loadItem = fileMenu.Append(wx.ID_ANY,
                u'&Load\tCtrl+L', u'Load data from file')
        fileMenu.AppendSeparator()
        self.exitItem = fileMenu.Append(wx.ID_EXIT, u'E&xit\tCtrl+W',
                u'Exit this frame')

        ## Help (menu structure)
        ### About
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT, '&About\tF1',
                'About information')
        self.Bind(wx.EVT_MENU, self.onAbout, id = wx.ID_ABOUT)

        ##setup menubar
        self.menubar.Append(fileMenu, '&File')
        self.menubar.Append(helpMenu, '&Help')
        
        self.SetMenuBar(self.menubar)

        ## bind events
        self.Bind(wx.EVT_MENU, self.onSave, id = self.saveItem.GetId())
        self.Bind(wx.EVT_MENU, self.onLoad, id = self.loadItem.GetId())
        self.Bind(wx.EVT_MENU, self.onExit, id = self.exitItem.GetId())

#------------------------------------------------------------------------#

    def createPanel(self):
        ## create the base container: panel
        self.panel = wx.Panel(self, id = wx.ID_ANY)
        ### configure the panel
        #self.panel.SetBackgroundColour('red')

        vbox = wx.BoxSizer(wx.VERTICAL)

        ## Title: 'Free-electron Laser Radiation Generation'
        title_st = wx.StaticText(self.panel, 
                label = u'Free-electron Laser Radiation Generation',
                style = wx.ALIGN_CENTRE)
        ### configure title_st
        title_st.SetForegroundColour('MEDIUM SEA GREEN')
        titlefont =wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        titlefont.SetPointSize(20)
        titlefont.SetWeight(wx.FONTWEIGHT_BOLD)
        title_st.SetFont(titlefont)
        ### add to boxsizer
        vbox.Add(title_st, flag = wx.ALIGN_CENTRE | wx.ALL, border = 10)

        ## horizontal separate line
        sl_below_title = wx.StaticLine(self.panel, style = wx.LI_HORIZONTAL)
        ### add to boxsizer
        vbox.Add(sl_below_title, flag = wx.EXPAND | wx.ALIGN_CENTRE, border = 10)

        ## font for staticbox
        sbfont = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        sbfont.SetPointSize(12)
        sbfont.SetWeight(wx.FONTWEIGHT_BOLD)
        sbfontcolor = 'VIOLET RED'

        ## staticbox for detailed information of radiator line (layout)
        sbox1 = wx.StaticBox(self.panel, id = wx.ID_ANY, 
                label = u'FEL Generation')
        ### config staticbox
        sbox1.SetFont(sbfont)
        sbox1.SetForegroundColour(sbfontcolor)
        ### create the sizer
        sbsizer_layout = wx.StaticBoxSizer(sbox1, orient = wx.VERTICAL)
        
        ### put the image
        layoutBitmap = wx.StaticBitmap(self.panel, wx.ID_ANY, wx.BitmapFromImage(funutils.rescaleImage(resutils.radislayouticon.GetImage(), 1.0)))
        sbsizer_layout.Add(layoutBitmap, proportion = 1, flag = wx.ALIGN_CENTRE)

        ### add to boxsizer
        vbox.Add(sbsizer_layout, proportion = 3, flag = wx.EXPAND | wx.ALIGN_CENTRE | wx.TOP | wx.LEFT | wx.RIGHT, border = 10)

        ## hbox to hold three staticbox
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        sbox21 = wx.StaticBox(self.panel, id = wx.ID_ANY, label = u'Taper Control')
        sbox22 = wx.StaticBox(self.panel, id = wx.ID_ANY, label = u'FEL Gaincurve')
        sbox23 = wx.StaticBox(self.panel, id = wx.ID_ANY, label = u'Field Pattern')
        sbox21.SetFont(sbfont)
        sbox21.SetForegroundColour(sbfontcolor)
        sbox22.SetFont(sbfont)
        sbox22.SetForegroundColour(sbfontcolor)
        sbox23.SetFont(sbfont)
        sbox23.SetForegroundColour(sbfontcolor)
        ### create sb sizer
        sbsizer_tapercontrol = wx.StaticBoxSizer(sbox21, orient = wx.VERTICAL)
        sbsizer_felgaincurve = wx.StaticBoxSizer(sbox22, orient = wx.VERTICAL)
        sbsizer_fieldpattern = wx.StaticBoxSizer(sbox23, orient = wx.VERTICAL)

        ### add sb sizers to hbox2
        hbox2.Add((5,-1))
        hbox2.Add(sbsizer_tapercontrol, proportion = 1, 
                flag = wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM, border = 5)
        hbox2.Add(sbsizer_felgaincurve, proportion = 1,
                flag = wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM, border = 5)
        hbox2.Add(sbsizer_fieldpattern, proportion = 1, 
                flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, border = 5)
        hbox2.Add((5,-1))
        
        vbox.Add(hbox2, proportion = 4, flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER | wx.EXPAND)

        ## hbox to hold two staticbox
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        sbox31 = wx.StaticBox(self.panel, id = wx.ID_ANY, label = u'FODO Control')
        sbox32 = wx.StaticBox(self.panel, id = wx.ID_ANY, label = u'Beam Envelope')
        sbox31.SetFont(sbfont)
        sbox31.SetForegroundColour(sbfontcolor)
        sbox32.SetFont(sbfont)
        sbox32.SetForegroundColour(sbfontcolor)
        ### create sb sizer
        sbsizer_fodocontrol = wx.StaticBoxSizer(sbox31, orient = wx.VERTICAL)
        sbsizer_beamenvelop = wx.StaticBoxSizer(sbox32, orient = wx.VERTICAL)

        ### add sb sizers to hbox3
        hbox3.Add((5,-1))
        hbox3.Add(sbsizer_fodocontrol, proportion = 1, 
                flag = wx.EXPAND | wx.LEFT | wx.BOTTOM, border = 5)
        hbox3.Add(sbsizer_beamenvelop, proportion = 1, 
                flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border = 5)
        hbox3.Add((5,-1))
        
        vbox.Add(hbox3, proportion = 4, flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER | wx.EXPAND)


        ## set sizer
        self.panel.SetSizer(vbox)

        ## bind events
        self.Bind(wx.EVT_CLOSE, self.onExit)

#------------------------------------------------------------------------#

    def createStatusbar(self):
        self.sb = self.CreateStatusBar()

#------------------------------------------------------------------------#

    def onExit(self, event):
        dial = wx.MessageDialog(self, 
                message = "Are you sure to exit this application?",
                caption = "Exit Warning",
                style = wx.YES_NO | wx.NO_DEFAULT | wx.CENTRE | wx.ICON_QUESTION)
        if dial.ShowModal() == wx.ID_YES:
            self.Destroy()
            self.MakeModal(False)

#------------------------------------------------------------------------#

    def onSave(self, event):
        pass

#------------------------------------------------------------------------#

    def onLoad(self, event):
        pass

#------------------------------------------------------------------------#

    def onAbout(self, event):
        from wx.lib.wordwrap import wordwrap
        aboutinfo = wx.AboutDialogInfo()
        aboutinfo.SetIcon(resutils.radislogoicon.GetIcon())
        aboutinfo.SetName(u'FEL Generation Application')
        aboutinfo.SetVersion('\nversion: 1.0.0')
        descriptionText = u"Application designed for free-electron laser radiation generation commissioning" + "\nPowered by Python/C/C++"
        aboutinfo.SetDescription(wordwrap(descriptionText, 500, wx.ClientDC(self)))
        aboutinfo.SetCopyright(u"(C) 2014-2015 Tong Zhang, SINAP, CAS")
        aboutinfo.SetWebSite([u"http://210.72.8.51/FELwiki/index.php/DCLS",
                u"DCLS home page"])
        aboutinfo.AddDeveloper(u"Tong Zhang <zhangtong@sinap.ac.cn>")
        licenseText = u"FEL Generation Application is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.\n" + "\nFEL Generation Application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.\n" + "\nYou should have received a copy of the GNU General Public License along with this application; if not, write to the Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA"
        aboutinfo.SetLicense(wordwrap(licenseText, 500, wx.ClientDC(self)))
        wx.AboutBox(aboutinfo)

#------------------------------------------------------------------------#

class LaserConfigPanel(wx.Frame):

#------------------------------------------------------------------------#

    def __init__(self, parent, **kwargs):
        super(self.__class__, self).__init__(parent = parent, 
                id = wx.ID_ANY, style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX), **kwargs)
        self.parent = parent
        self.InitUI()
    
#------------------------------------------------------------------------#

    def InitUI(self):
        self.createMenu()
        self.createPanel()
        self.createStatusbar()

#------------------------------------------------------------------------#

    def createMenu(self):
        pass

#------------------------------------------------------------------------#

    def createStatusbar(self):
        pass

#------------------------------------------------------------------------#

    def createPanel(self):
        self.panel = wx.Panel(self, id = wx.ID_ANY)

        vbox = wx.BoxSizer(wx.VERTICAL)
        
        ## Title: 'Seedlaser Parameters Configuration'
        title_st = wx.StaticText(self.panel, 
                label = u'Seedlaser Parameters Configuration',
                style = wx.ALIGN_CENTRE)
        ### configure title_st
        title_st.SetForegroundColour('#CF5ECA')
        titlefont =wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        titlefont.SetPointSize(14)
        titlefont.SetWeight(wx.FONTWEIGHT_BOLD)
        title_st.SetFont(titlefont)
        ### add to boxsizer
        vbox.Add(title_st, flag = wx.ALIGN_CENTRE | wx.ALL, border = 15)

        ## horizontal separate line
        sl_below_title = wx.StaticLine(self.panel, style = wx.LI_HORIZONTAL)
        ### add to boxsizer
        vbox.Add(sl_below_title, flag = wx.EXPAND | wx.ALIGN_CENTRE, border = 10)

        sbox = wx.StaticBox(self.panel, id = wx.ID_ANY, 
                label = u'(C) 2014-2015 Designed for DCLS', style = wx.ALIGN_LEFT)
        sbfont = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        sbfont.SetPointSize(8)
        sbfont.SetWeight(wx.FONTWEIGHT_NORMAL)
        sbfontcolor = 'GREY'
        sbox.SetFont(sbfont)
        sbox.SetForegroundColour(sbfontcolor)
        sbsizer = wx.StaticBoxSizer(sbox, orient = wx.HORIZONTAL)

        ### put items and values
        sboxparams = wx.StaticBox(self.panel, id = wx.ID_ANY, label = u'Parameters',  style = wx.ALIGN_CENTER)
        sboximage  = wx.StaticBox(self.panel, id = wx.ID_ANY, label = u'Laser Image', style = wx.ALIGN_CENTER)
        sbparams_sizer = wx.StaticBoxSizer(sboxparams, orient = wx.VERTICAL)
        sbimage_sizer  = wx.StaticBoxSizer(sboximage,  orient = wx.VERTICAL)
        
        #### set staticbox font
        sb1font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        sb1font.SetPointSize(12)
        sb1font.SetWeight(wx.FONTWEIGHT_BOLD)
        sb1fontcolor = '#465FCF'
        sboxparams.SetFont(sb1font)
        sboxparams.SetForegroundColour(sb1fontcolor)
        sboximage.SetFont(sb1font)
        sboximage.SetForegroundColour(sb1fontcolor)

        #### laser items
        fgslaser = wx.FlexGridSizer(5, 2, 10, 10)
        item11st = wx.StaticText(self.panel, label = u'Peak Power [W]'          + ' ' + u'(\N{LATIN CAPITAL LETTER P})',
                style = wx.ALIGN_LEFT)
        item21st = wx.StaticText(self.panel, label = u'Pulse Width (FWHM) [fs]' + ' ' + u'(\N{GREEK SMALL LETTER TAU})', 
                style = wx.ALIGN_LEFT)
        item31st = wx.StaticText(self.panel, label = u'Beam Waist Size [m]'     + ' ' + u'(\N{GREEK SMALL LETTER OMEGA}\N{SUBSCRIPT ZERO})',
                style = wx.ALIGN_LEFT)
#        item41st = wx.StaticText(self.panel, label = u'Rayleigh Range [m]'      + ' ' + u'(\N{LATIN CAPITAL LETTER Z}\N{LATIN SUBSCRIPT SMALL LETTER R})',
#                style = wx.ALIGN_LEFT)
        item51st = wx.StaticText(self.panel, label = u'Phase [rad]'             + ' ' + u'(\N{GREEK SMALL LETTER PHI})',
                style = wx.ALIGN_LEFT)
        item61st = wx.StaticText(self.panel, label = u'Wavelength [nm]'         + ' ' + u'(\N{GREEK SMALL LETTER LAMDA})',
                style = wx.ALIGN_LEFT)

        self.item12tc = wx.TextCtrl(self.panel, id = ID_POWER,  value = '1.0e6',  style = wx.TE_PROCESS_ENTER)
        self.item22tc = wx.TextCtrl(self.panel, id = ID_LENGTH, value = '100',    style = wx.TE_PROCESS_ENTER)
        self.item32tc = wx.TextCtrl(self.panel, id = ID_OMEGA,  value = '1.0e-3', style = wx.TE_PROCESS_ENTER)
#        self.item42tc = wx.TextCtrl(self.panel, value = '1.0',    style = wx.TE_PROCESS_ENTER)
        self.item52tc = wx.TextCtrl(self.panel, id = ID_PHASE,  value = '0',      style = wx.TE_PROCESS_ENTER)
        self.item62tc = wx.TextCtrl(self.panel, id = ID_WVLTH,  value = '300',    style = wx.TE_PROCESS_ENTER)

        fgslaser.Add(item11st, proportion = 0, flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(self.item12tc, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(item21st, proportion = 0, flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(self.item22tc, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(item31st, proportion = 0, flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(self.item32tc, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
#        fgslaser.Add(item41st, proportion = 0, flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
#        fgslaser.Add(self.item42tc, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(item51st, proportion = 0, flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(self.item52tc, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(item61st, proportion = 0, flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(self.item62tc, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.AddGrowableCol(1)
        sbparams_sizer.Add(fgslaser, proportion = 0, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT | wx.TOP, border = 15)

        sbparams_sizer.Add((-1, 10))
        
        #### external data IO control
        self.loadbtn = wx.Button(self.panel, label = 'Load')
        self.helpbtn = wx.Button(self.panel, label = 'Help')

        self.Bind(wx.EVT_BUTTON, self.OnLaserLoad, self.loadbtn)
        self.Bind(wx.EVT_BUTTON, self.OnLaserHelp, self.helpbtn)

        lbtnfont = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        lbtnfont.SetPointSize(14)
        lbtnfont.SetWeight(wx.FONTWEIGHT_NORMAL)
        lbtnfontcolor = '#FF00B0'
        lbtnfacecolor = '#BFD9F0'
        self.loadbtn.SetFont(lbtnfont)
        self.helpbtn.SetFont(lbtnfont)
        self.loadbtn.SetForegroundColour(lbtnfontcolor)
        self.helpbtn.SetForegroundColour(lbtnfontcolor)
        self.loadbtn.SetBackgroundColour(lbtnfacecolor)
        self.helpbtn.SetBackgroundColour(lbtnfacecolor)
        
        hboxbtn = wx.BoxSizer(orient = wx.HORIZONTAL)
        hboxbtn.Add(self.loadbtn, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border = 10)
        hboxbtn.Add(self.helpbtn, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border = 10)
        sbparams_sizer.Add(hboxbtn, flag = wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, border = 10)


        #### laser image (transverse profile)
        vbox2 = wx.BoxSizer(orient = wx.VERTICAL)
        imgsrc_st = funutils.createStaticText(self.panel, label = u'Laser Source:', style = wx.ALIGN_LEFT,
                                              fontsize = 10, fontweight = wx.FONTWEIGHT_NORMAL,
                                              fontcolor = 'BLACK')
        self.imgsrc_tc = wx.TextCtrl(self.panel, value = 'OPA:PROF:ARR', style = wx.TE_PROCESS_ENTER)
        self.lasergraph = pltutils.ImagePanel(self.panel, 
                                              figsize = (4,4), 
                                              dpi = 60, 
                                              bgcolor = None)
        self.showbtn = wx.Button(self.panel, label = 'Single Shot')
        self.daqbtn  = wx.Button(self.panel, label = 'DAQ START')
        imgcr_st = funutils.createStaticText(self.panel, label = u'Color Range:', style = wx.ALIGN_LEFT,
                                                 fontsize = 10, fontweight = wx.FONTWEIGHT_NORMAL,
                                                 fontcolor = 'BLACK')
        self.imgcr_min_tc = wx.TextCtrl(self.panel, value = '0'  )
        self.imgcr_max_tc = wx.TextCtrl(self.panel, value = '100')
        hbox_imgcr = wx.BoxSizer(wx.HORIZONTAL)
        hbox_imgcr.Add(imgcr_st, proportion = 0, flag = wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border = 5)
        hbox_imgcr.Add(self.imgcr_min_tc, proportion = 1, flag = wx.EXPAND | wx.ALIGN_RIGHT | wx.RIGHT, border = 8)
        hbox_imgcr.Add(self.imgcr_max_tc, proportion = 1, flag = wx.EXPAND | wx.ALIGN_RIGHT | wx.RIGHT, border = 8)
        
        vbox2.Add(imgsrc_st, flag = wx.TOP | wx.ALIGN_LEFT, border =10)
        vbox2.Add(self.imgsrc_tc, flag = wx.TOP | wx.EXPAND | wx.ALIGN_LEFT, border = 10)
        vbox2.Add(self.lasergraph, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 10)
        
        vbox2.Add(hbox_imgcr, proportion = 0, flag = wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL)

        hbox_fetchimg = wx.BoxSizer(wx.HORIZONTAL)

        hbox_fetchimg.Add(self.showbtn, proportion = 0, flag = wx.RIGHT | wx.BOTTOM, border = 10)
        hbox_fetchimg.Add(self.daqbtn,  proportion = 0, flag = wx.BOTTOM, border = 10)

        vbox2.Add(hbox_fetchimg, flag = wx.ALIGN_CENTER |  wx.TOP, border = 10)

        sbimage_sizer.Add(vbox2, flag = wx.ALIGN_CENTER, border = 10)
        
        sbsizer.Add(sbparams_sizer, proportion = 3, flag = wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM, border = 10)
        sbsizer.Add(sbimage_sizer,  proportion = 2, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, border = 10)
        
        vbox.Add(sbsizer, proportion = 1, 
                flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border = 10)

        ## set boxsizer
        self.panel.SetSizer(vbox)

        ## bind events
        self.Bind(wx.EVT_BUTTON,     self.OnSingleShot,   self.showbtn  )
        self.Bind(wx.EVT_BUTTON,     self.OnDAQ,          self.daqbtn   )
        self.Bind(wx.EVT_TEXT_ENTER, self.OnTextEnter,    self.imgsrc_tc)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnUpdateParams, self.item12tc)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnUpdateParams, self.item32tc)

        ## create a timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnUpdate, self.timer)

#------------------------------------------------------------------------#

    def OnTextEnter(self, event):
        self.imgpv = epics.PV(self.imgsrc_tc.GetValue())
        if self.imgpv.connected == False:
            dial = wx.MessageDialog(self, message = u"PV entered cannot be reached at this moment, please check the input name and try again later.",
                    caption = u"PV Input Error",
                    style = wx.OK | wx.CANCEL | wx.ICON_ERROR | wx.CENTRE)
            if dial.ShowModal() == wx.ID_OK:
                event.GetEventObject().SetValue('')
                dial.Destroy()

#------------------------------------------------------------------------#

    def OnUpdateParams(self, event):
        obj = event.GetEventObject() 
        if obj.GetId() == ID_POWER:
            epics.PV('OPA:POWER:SET').put(obj.GetValue())
        elif obj.GetId() == ID_OMEGA:
            epics.PV('OPA:OMEGA:SET').put(obj.GetValue())

#------------------------------------------------------------------------#

    def OnDAQ(self, event):
        label = event.GetEventObject().GetLabel()
        try:
            isinstance(self.imgpv, epics.pv.PV)
        except AttributeError:
            self.imgpv = epics.PV(self.imgsrc_tc.GetValue(), auto_monitor = True)
        if self.timer.IsRunning():
            self.timer.Stop()
            self.daqbtn.SetLabel('DAQ START')
        else:
            self.timer.Start(1000)
            self.daqbtn.SetLabel('DAQ STOP')

#------------------------------------------------------------------------#

    def OnUpdate(self, event):
        if self.imgpv.connected == True:
            self.wpx, self.hpx = 494, 659
            try:
                cmin_now = float(self.imgcr_min_tc.GetValue())
                cmax_now = float(self.imgcr_max_tc.GetValue())
            except ValueError:
                cmin_now = None
                cmax_now = None
            self.lasergraph.z = self.imgpv.get().reshape((self.wpx, self.hpx))
            self.lasergraph.im.set_clim(vmin = cmin_now, vmax = cmax_now)
            self.lasergraph.im.set_array(self.lasergraph.z)
            self.lasergraph.repaint()
        else:
            dial = wx.MessageDialog(self, message = u"Lost connection, may be caused by network error or the IOC server is down.",
                                    caption = u"Lost Connection", style = wx.OK | wx.CANCEL | wx.ICON_ERROR | wx.CENTRE)
            if dial.ShowModal() == wx.ID_OK:
                dial.Destroy()

#------------------------------------------------------------------------#

    def OnSingleShot(self, event):
        self.wpx, self.hpx = 494, 659
        try:
            cmin_now = float(self.imgcr_min_tc.GetValue())
            cmax_now = float(self.imgcr_max_tc.GetValue())
        except ValueError:
            cmin_now = None
            cmax_now = None
        try:
            self.lasergraph.z = self.imgpv.get().reshape((self.wpx, self.hpx))
            self.lasergraph.im.set_clim(vmin = cmin_now, vmax = cmax_now)
            self.lasergraph.im.set_array(self.lasergraph.z)
            self.lasergraph.repaint()
        except AttributeError:
            dial = wx.MessageDialog(self, message = u"PV cannot be reached at this moment, please try again later.",
                    caption = u"PV Get Error",
                    style = wx.OK | wx.CANCEL | wx.ICON_ERROR | wx.CENTRE)
            if dial.ShowModal() == wx.ID_OK:
                dial.Destroy()

#------------------------------------------------------------------------#

    def OnLaserLoad(self, event):
        pass

#------------------------------------------------------------------------#

    def OnLaserHelp(self, event):
        pass

#------------------------------------------------------------------------#

class EbeamConfigPanel(wx.Frame):

#------------------------------------------------------------------------#

    def __init__(self, parent, **kwargs):
        super(self.__class__, self).__init__(parent = parent, 
                id = wx.ID_ANY, style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX), **kwargs)
        self.parent = parent
        self.InitUI()
    
#------------------------------------------------------------------------#

    def InitUI(self):
        self.createMenu()
        self.createPanel()
        self.createStatusbar()

#------------------------------------------------------------------------#

    def createMenu(self):
        pass

#------------------------------------------------------------------------#

    def createStatusbar(self):
        pass

#------------------------------------------------------------------------#

    def createPanel(self):
        self.panel = wx.Panel(self, id = wx.ID_ANY)

        vbox = wx.BoxSizer(wx.VERTICAL)
        
        ## Title: 'E-beam Parameters Configuration'
        title_st = wx.StaticText(self.panel, 
                label = u'E-beam Parameters Configuration',
                style = wx.ALIGN_CENTRE)
        ### configure title_st
        title_st.SetForegroundColour('#CF5ECA')
        titlefont =wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        titlefont.SetPointSize(14)
        titlefont.SetWeight(wx.FONTWEIGHT_BOLD)
        title_st.SetFont(titlefont)
        ### add to boxsizer
        vbox.Add(title_st, flag = wx.ALIGN_CENTRE | wx.ALL, border = 15)

        ## horizontal separate line
        sl_below_title = wx.StaticLine(self.panel, style = wx.LI_HORIZONTAL)
        ### add to boxsizer
        vbox.Add(sl_below_title, flag = wx.EXPAND | wx.ALIGN_CENTRE, border = 10)

        sbox = wx.StaticBox(self.panel, id = wx.ID_ANY, 
                label = u'(C) 2014-2015 Designed for DCLS', style = wx.ALIGN_LEFT)
        sbfont = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        sbfont.SetPointSize(8)
        sbfont.SetWeight(wx.FONTWEIGHT_NORMAL)
        sbfontcolor = 'GREY'
        sbox.SetFont(sbfont)
        sbox.SetForegroundColour(sbfontcolor)
        sbsizer = wx.StaticBoxSizer(sbox, orient = wx.HORIZONTAL)

        ### put items and values
        sboxparams = wx.StaticBox(self.panel, id = wx.ID_ANY, label = u'Parameters',  style = wx.ALIGN_CENTER)
        sboximage  = wx.StaticBox(self.panel, id = wx.ID_ANY, label = u'Image Profile', style = wx.ALIGN_CENTER)
        sbparams_sizer = wx.StaticBoxSizer(sboxparams, orient = wx.VERTICAL)
        sbimage_sizer  = wx.StaticBoxSizer(sboximage,  orient = wx.VERTICAL)
        
        #### set staticbox font
        sb1font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        sb1font.SetPointSize(12)
        sb1font.SetWeight(wx.FONTWEIGHT_BOLD)
        sb1fontcolor = '#465FCF'
        sboxparams.SetFont(sb1font)
        sboxparams.SetForegroundColour(sb1fontcolor)
        sboximage.SetFont(sb1font)
        sboximage.SetForegroundColour(sb1fontcolor)

        #### ebeam items
        fgslaser = wx.FlexGridSizer(5, 2, 10, 10)
        item11st = wx.StaticText(self.panel, label = u'Beam Energy [MeV]' + ' ' + u'(\N{LATIN CAPITAL LETTER E}\N{LATIN SMALL LETTER B})',
                style = wx.ALIGN_LEFT)
        item21st = wx.StaticText(self.panel, label = u'Energy Spread' + ' ' + u'(\N{GREEK SMALL LETTER SIGMA}\N{GREEK SMALL LETTER GAMMA})', 
                style = wx.ALIGN_LEFT)
        item31st = wx.StaticText(self.panel, label = u'Beam Size [m]' + ' ' + u'(\N{GREEK SMALL LETTER SIGMA}\N{LATIN SUBSCRIPT SMALL LETTER R})',
                style = wx.ALIGN_LEFT)
        item51st = wx.StaticText(self.panel, label = u'Emittance [m]' + ' ' + u'(\N{GREEK SMALL LETTER EPSILON}\N{LATIN SMALL LETTER N})',
                style = wx.ALIGN_LEFT)
        item61st = wx.StaticText(self.panel, label = u'Peak Current [A]' + ' ' + u'(\N{LATIN CAPITAL LETTER I})',
                style = wx.ALIGN_LEFT)

        self.item12tc = wx.TextCtrl(self.panel, id = ID_ENERGY,  value = '840',    style = wx.TE_PROCESS_ENTER)
        self.item22tc = wx.TextCtrl(self.panel, id = ID_ESPREAD, value = '0.0001', style = wx.TE_PROCESS_ENTER)
        self.item32tc = wx.TextCtrl(self.panel, id = ID_BSIZE,   value = '1.0e-4', style = wx.TE_PROCESS_ENTER)
        self.item52tc = wx.TextCtrl(self.panel, id = ID_EMITN,   value = '1.0e-6', style = wx.TE_PROCESS_ENTER)
        self.item62tc = wx.TextCtrl(self.panel, id = ID_CURPEAK, value = '500',    style = wx.TE_PROCESS_ENTER)

        fgslaser.Add(item11st, proportion = 0, flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(self.item12tc, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(item21st, proportion = 0, flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(self.item22tc, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(item31st, proportion = 0, flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(self.item32tc, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(item51st, proportion = 0, flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(self.item52tc, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(item61st, proportion = 0, flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(self.item62tc, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.AddGrowableCol(1)
        sbparams_sizer.Add(fgslaser, proportion = 0, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT | wx.TOP, border = 15)

        sbparams_sizer.Add((-1, 10))
        
        #### 
        self.calcbtn = wx.Button(self.panel, label = 'FEL Calculation')
        self.helpbtn = wx.Button(self.panel, label = 'Help')

        self.Bind(wx.EVT_BUTTON, self.OnCalc, self.calcbtn)
        self.Bind(wx.EVT_BUTTON, self.OnHelp, self.helpbtn)

        lbtnfont = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        lbtnfont.SetPointSize(14)
        lbtnfont.SetWeight(wx.FONTWEIGHT_NORMAL)
        lbtnfontcolor = '#FF00B0'
        lbtnfacecolor = '#BFD9F0'
        self.calcbtn.SetFont(lbtnfont)
        self.helpbtn.SetFont(lbtnfont)
        self.calcbtn.SetForegroundColour(lbtnfontcolor)
        self.helpbtn.SetForegroundColour(lbtnfontcolor)
        self.calcbtn.SetBackgroundColour(lbtnfacecolor)
        self.helpbtn.SetBackgroundColour(lbtnfacecolor)
        
        hboxbtn = wx.BoxSizer(orient = wx.HORIZONTAL)
        hboxbtn.Add(self.calcbtn, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border = 10)
        hboxbtn.Add(self.helpbtn, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border = 10)
        sbparams_sizer.Add(hboxbtn, flag = wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, border = 10)


        #### e-beam profile
        vbox2 = wx.BoxSizer(orient = wx.VERTICAL)
        imgsrc_st = funutils.createStaticText(self.panel, label = u'Profile Source:', style = wx.ALIGN_LEFT,
                                              fontsize = 10, fontweight = wx.FONTWEIGHT_NORMAL,
                                              fontcolor = 'BLACK')
        self.imgsrc_tc = wx.TextCtrl(self.panel, value = 'DCLS:EBEAM:PROF:ARR', style = wx.TE_PROCESS_ENTER)
        self.ebeamgraph = pltutils.ImagePanel(self.panel, 
                                              figsize = (4,4), 
                                              dpi = 60, 
                                              bgcolor = None)
        self.showbtn = wx.Button(self.panel, label = 'Single Shot')
        self.daqbtn  = wx.Button(self.panel, label = 'DAQ START')
        imgcr_st = funutils.createStaticText(self.panel, label = u'Color Range:', style = wx.ALIGN_LEFT,
                                                 fontsize = 10, fontweight = wx.FONTWEIGHT_NORMAL,
                                                 fontcolor = 'BLACK')
        self.imgcr_min_tc = wx.TextCtrl(self.panel, value = '0'  )
        self.imgcr_max_tc = wx.TextCtrl(self.panel, value = '100')
        hbox_imgcr = wx.BoxSizer(wx.HORIZONTAL)
        hbox_imgcr.Add(imgcr_st, proportion = 0, flag = wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border = 5)
        hbox_imgcr.Add(self.imgcr_min_tc, proportion = 1, flag = wx.EXPAND | wx.ALIGN_RIGHT | wx.RIGHT, border = 8)
        hbox_imgcr.Add(self.imgcr_max_tc, proportion = 1, flag = wx.EXPAND | wx.ALIGN_RIGHT | wx.RIGHT, border = 8)
        
        vbox2.Add(imgsrc_st, flag = wx.TOP | wx.ALIGN_LEFT, border =10)
        vbox2.Add(self.imgsrc_tc, flag = wx.TOP | wx.EXPAND | wx.ALIGN_LEFT, border = 10)
        vbox2.Add(self.ebeamgraph, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 10)
        
        vbox2.Add(hbox_imgcr, proportion = 0, flag = wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL)

        hbox_fetchimg = wx.BoxSizer(wx.HORIZONTAL)

        hbox_fetchimg.Add(self.showbtn, proportion = 0, flag = wx.RIGHT | wx.BOTTOM, border = 10)
        hbox_fetchimg.Add(self.daqbtn,  proportion = 0, flag = wx.BOTTOM, border = 10)

        vbox2.Add(hbox_fetchimg, flag = wx.ALIGN_CENTER |  wx.TOP, border = 10)

        sbimage_sizer.Add(vbox2, flag = wx.ALIGN_CENTER, border = 10)
        
        sbsizer.Add(sbparams_sizer, proportion = 3, flag = wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM, border = 10)
        sbsizer.Add(sbimage_sizer,  proportion = 2, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, border = 10)
        
        vbox.Add(sbsizer, proportion = 1, 
                flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border = 10)

        ## set boxsizer
        self.panel.SetSizer(vbox)

        ## bind events
        self.Bind(wx.EVT_BUTTON,     self.OnSingleShot,   self.showbtn  )
        self.Bind(wx.EVT_BUTTON,     self.OnDAQ,          self.daqbtn   )
        self.Bind(wx.EVT_TEXT_ENTER, self.OnTextEnter,    self.imgsrc_tc)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnUpdateParams, self.item12tc)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnUpdateParams, self.item32tc)

        ## create a timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnUpdate, self.timer)

#------------------------------------------------------------------------#

    def OnTextEnter(self, event):
        self.imgpv = epics.PV(self.imgsrc_tc.GetValue())
        if self.imgpv.connected == False:
            dial = wx.MessageDialog(self, message = u"PV entered cannot be reached at this moment, please check the input name and try again later.",
                    caption = u"PV Input Error",
                    style = wx.OK | wx.CANCEL | wx.ICON_ERROR | wx.CENTRE)
            if dial.ShowModal() == wx.ID_OK:
                event.GetEventObject().SetValue('')
                dial.Destroy()

#------------------------------------------------------------------------#

    def OnUpdateParams(self, event):
        obj = event.GetEventObject() 
        if obj.GetId() == ID_ENERGY:
            epics.PV('DCLS:ENERGY:SET').put(obj.GetValue())
        elif obj.GetId() == ID_BSIZE:
            epics.PV('DCLS:BSIZE:SET').put(obj.GetValue())

#------------------------------------------------------------------------#

    def OnDAQ(self, event):
        label = event.GetEventObject().GetLabel()
        try:
            isinstance(self.imgpv, epics.pv.PV)
        except AttributeError:
            self.imgpv = epics.PV(self.imgsrc_tc.GetValue(), auto_monitor = True)
        if self.timer.IsRunning():
            self.timer.Stop()
            self.daqbtn.SetLabel('DAQ START')
        else:
            self.timer.Start(1000)
            self.daqbtn.SetLabel('DAQ STOP')

#------------------------------------------------------------------------#

    def OnUpdate(self, event):
        if self.imgpv.connected == True:
            self.wpx, self.hpx = 494, 659
            try:
                cmin_now = float(self.imgcr_min_tc.GetValue())
                cmax_now = float(self.imgcr_max_tc.GetValue())
            except ValueError:
                cmin_now = None
                cmax_now = None
            self.ebeamgraph.z = self.imgpv.get().reshape((self.wpx, self.hpx))
            self.ebeamgraph.im.set_clim(vmin = cmin_now, vmax = cmax_now)
            self.ebeamgraph.im.set_array(self.ebeamgraph.z)
            self.ebeamgraph.repaint()
        else:
            dial = wx.MessageDialog(self, message = u"Lost connection, may be caused by network error or the IOC server is down.",
                                    caption = u"Lost Connection", style = wx.OK | wx.CANCEL | wx.ICON_ERROR | wx.CENTRE)
            if dial.ShowModal() == wx.ID_OK:
                dial.Destroy()

#------------------------------------------------------------------------#

    def OnSingleShot(self, event):
        self.wpx, self.hpx = 494, 659
        try:
            cmin_now = float(self.imgcr_min_tc.GetValue())
            cmax_now = float(self.imgcr_max_tc.GetValue())
        except ValueError:
            cmin_now = None
            cmax_now = None
        try:
            self.ebeamgraph.z = self.imgpv.get().reshape((self.wpx, self.hpx))
            self.ebeamgraph.im.set_clim(vmin = cmin_now, vmax = cmax_now)
            self.ebeamgraph.im.set_array(self.ebeamgraph.z)
            self.ebeamgraph.repaint()
        except AttributeError:
            dial = wx.MessageDialog(self, message = u"PV cannot be reached at this moment, please try again later.",
                    caption = u"PV Get Error",
                    style = wx.OK | wx.CANCEL | wx.ICON_ERROR | wx.CENTRE)
            if dial.ShowModal() == wx.ID_OK:
                dial.Destroy()

#------------------------------------------------------------------------#

    def OnCalc(self, event):
        from ..physics import formula
        formula.run()

#------------------------------------------------------------------------#

    def OnHelp(self, event):
        pass

#------------------------------------------------------------------------#

class ModConfigPanel(wx.Frame):

#------------------------------------------------------------------------#

    def __init__(self, parent, **kwargs):
        super(self.__class__, self).__init__(parent = parent, 
                id = wx.ID_ANY, style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX), **kwargs)
        self.parent = parent
        self.InitUI()
    
#------------------------------------------------------------------------#

    def InitUI(self):
        self.createMenu()
        self.createPanel()
        self.createStatusbar()

#------------------------------------------------------------------------#

    def createMenu(self):
        pass

#------------------------------------------------------------------------#

    def createStatusbar(self):
        pass

#------------------------------------------------------------------------#

    def createPanel(self):
        self.panel = wx.Panel(self, id = wx.ID_ANY)

        vbox = wx.BoxSizer(wx.VERTICAL)
        
        ## Title: 'Modulator Parameters Configuration'
        title_st = wx.StaticText(self.panel, 
                label = u'Modulator Parameters Configuration',
                style = wx.ALIGN_CENTRE)
        ### configure title_st
        title_st.SetForegroundColour('#CF5ECA')
        titlefont =wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        titlefont.SetPointSize(14)
        titlefont.SetWeight(wx.FONTWEIGHT_BOLD)
        title_st.SetFont(titlefont)
        ### add to boxsizer
        vbox.Add(title_st, flag = wx.ALIGN_CENTRE | wx.ALL, border = 15)

        ## horizontal separate line
        sl_below_title = wx.StaticLine(self.panel, style = wx.LI_HORIZONTAL)
        ### add to boxsizer
        vbox.Add(sl_below_title, flag = wx.EXPAND | wx.ALIGN_CENTRE, border = 10)

        sbox = wx.StaticBox(self.panel, id = wx.ID_ANY, 
                label = u'(C) 2014-2015 Designed for DCLS', style = wx.ALIGN_LEFT)
        sbfont = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        sbfont.SetPointSize(8)
        sbfont.SetWeight(wx.FONTWEIGHT_NORMAL)
        sbfontcolor = 'GREY'
        sbox.SetFont(sbfont)
        sbox.SetForegroundColour(sbfontcolor)
        sbsizer = wx.StaticBoxSizer(sbox, orient = wx.HORIZONTAL)

        ### put items and values
        sboxparams = wx.StaticBox(self.panel, id = wx.ID_ANY, label = u'Parameters',  style = wx.ALIGN_CENTER)
        #sboximage  = wx.StaticBox(self.panel, id = wx.ID_ANY, label = u'Image Profile', style = wx.ALIGN_CENTER)
        sbparams_sizer = wx.StaticBoxSizer(sboxparams, orient = wx.VERTICAL)
        #sbimage_sizer  = wx.StaticBoxSizer(sboximage,  orient = wx.VERTICAL)
        
        #### set staticbox font
        sb1font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        sb1font.SetPointSize(12)
        sb1font.SetWeight(wx.FONTWEIGHT_BOLD)
        sb1fontcolor = '#465FCF'
        sboxparams.SetFont(sb1font)
        sboxparams.SetForegroundColour(sb1fontcolor)

        #### ebeam items
        fgslaser = wx.FlexGridSizer(3, 2, 10, 10)
        item11st = wx.StaticText(self.panel, label = u'Period Length [m]',
                style = wx.ALIGN_LEFT)
        item21st = wx.StaticText(self.panel, label = u'Period Number',
                style = wx.ALIGN_LEFT)
        item31st = wx.StaticText(self.panel, label = u'Undulator Gap [mm]',
                style = wx.ALIGN_LEFT)

        self.item12tc = wx.TextCtrl(self.panel, id = ID_MODXLAMD,  value = '50', style = wx.TE_PROCESS_ENTER)
        self.item22tc = wx.TextCtrl(self.panel, id = ID_MODNUM,    value = '10', style = wx.TE_PROCESS_ENTER)
        self.item32sc = wx.SpinCtrlDouble(self.panel, id = ID_MODGAP, value = '', 
                style = wx.SP_ARROW_KEYS, min = 10.0, max = 40.0, initial = 23.0, inc = 0.1)


        fgslaser.Add(item11st, proportion = 0, flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(self.item12tc, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(item21st, proportion = 0, flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(self.item22tc, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(item31st, proportion = 0, flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(self.item32sc, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.AddGrowableCol(1)
        sbparams_sizer.Add(fgslaser, proportion = 0, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT | wx.TOP, border = 15)

        sbparams_sizer.Add((-1, 10))
        
        #### 
        self.interbtn = wx.Button(self.panel, label = 'TBD')
        self.helpbtn = wx.Button(self.panel, label = 'Help')

        self.Bind(wx.EVT_BUTTON, self.OnInter, self.interbtn)
        self.Bind(wx.EVT_BUTTON, self.OnHelp, self.helpbtn)

        lbtnfont = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        lbtnfont.SetPointSize(14)
        lbtnfont.SetWeight(wx.FONTWEIGHT_NORMAL)
        lbtnfontcolor = '#FF00B0'
        lbtnfacecolor = '#BFD9F0'
        self.interbtn.SetFont(lbtnfont)
        self.helpbtn.SetFont(lbtnfont)
        self.interbtn.SetForegroundColour(lbtnfontcolor)
        self.helpbtn.SetForegroundColour(lbtnfontcolor)
        self.interbtn.SetBackgroundColour(lbtnfacecolor)
        self.helpbtn.SetBackgroundColour(lbtnfacecolor)
        
        hboxbtn = wx.BoxSizer(orient = wx.HORIZONTAL)
        hboxbtn.Add(self.interbtn, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border = 10)
        hboxbtn.Add(self.helpbtn, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border = 10)
        sbparams_sizer.Add(hboxbtn, flag = wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, border = 10)


        sbsizer.Add(sbparams_sizer, proportion = 3, flag = wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM, border = 10)
        
        vbox.Add(sbsizer, proportion = 1, 
                flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border = 10)

        ## set boxsizer
        self.panel.SetSizer(vbox)

        ## bind events
        self.Bind(wx.EVT_SPINCTRLDOUBLE, self.OnUpdateParams, self.item32sc)

        ## create a timer
        #self.timer = wx.Timer(self)
        #self.Bind(wx.EVT_TIMER, self.OnUpdate, self.timer)

#------------------------------------------------------------------------#

    def OnUpdateParams(self, event):
        obj = event.GetEventObject() 
        if obj.GetId() == ID_MODGAP:
            epics.PV('DCLS:MODGAP:SET').put(obj.GetValue())
        ## update modulated phase space
        curval = epics.PV('DCLS:MODGAP').get()
        self.parent.OnUpdatePS(psid = 'mod', newval = curval)

#------------------------------------------------------------------------#

    def OnHelp(self, event):
        pass

#------------------------------------------------------------------------#

    def OnInter(self, event):
        pass

#------------------------------------------------------------------------#

class ChiConfigPanel(wx.Frame):

#------------------------------------------------------------------------#

    def __init__(self, parent, **kwargs):
        super(self.__class__, self).__init__(parent = parent, 
                id = wx.ID_ANY, style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX), **kwargs)
        self.parent = parent
        self.InitUI()
    
#------------------------------------------------------------------------#

    def InitUI(self):
        self.createMenu()
        self.createPanel()
        self.createStatusbar()

#------------------------------------------------------------------------#

    def createMenu(self):
        pass

#------------------------------------------------------------------------#

    def createStatusbar(self):
        pass

#------------------------------------------------------------------------#

    def createPanel(self):
        self.panel = wx.Panel(self, id = wx.ID_ANY)

        vbox = wx.BoxSizer(wx.VERTICAL)
        
        ## Title: 'Chicane Parameters Configuration'
        title_st = wx.StaticText(self.panel, 
                label = u'Chicane Parameters Configuration',
                style = wx.ALIGN_CENTRE)
        ### configure title_st
        title_st.SetForegroundColour('#CF5ECA')
        titlefont =wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        titlefont.SetPointSize(14)
        titlefont.SetWeight(wx.FONTWEIGHT_BOLD)
        title_st.SetFont(titlefont)
        ### add to boxsizer
        vbox.Add(title_st, flag = wx.ALIGN_CENTRE | wx.ALL, border = 15)

        ## horizontal separate line
        sl_below_title = wx.StaticLine(self.panel, style = wx.LI_HORIZONTAL)
        ### add to boxsizer
        vbox.Add(sl_below_title, flag = wx.EXPAND | wx.ALIGN_CENTRE, border = 10)

        sbox = wx.StaticBox(self.panel, id = wx.ID_ANY, 
                label = u'(C) 2014-2015 Designed for DCLS', style = wx.ALIGN_LEFT)
        sbfont = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        sbfont.SetPointSize(8)
        sbfont.SetWeight(wx.FONTWEIGHT_NORMAL)
        sbfontcolor = 'GREY'
        sbox.SetFont(sbfont)
        sbox.SetForegroundColour(sbfontcolor)
        sbsizer = wx.StaticBoxSizer(sbox, orient = wx.HORIZONTAL)

        ### put items and values
        sboxparams = wx.StaticBox(self.panel, id = wx.ID_ANY, label = u'Parameters',  style = wx.ALIGN_CENTER)
        #sboximage  = wx.StaticBox(self.panel, id = wx.ID_ANY, label = u'Image Profile', style = wx.ALIGN_CENTER)
        sbparams_sizer = wx.StaticBoxSizer(sboxparams, orient = wx.VERTICAL)
        #sbimage_sizer  = wx.StaticBoxSizer(sboximage,  orient = wx.VERTICAL)
        
        #### set staticbox font
        sb1font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        sb1font.SetPointSize(12)
        sb1font.SetWeight(wx.FONTWEIGHT_BOLD)
        sb1fontcolor = '#465FCF'
        sboxparams.SetFont(sb1font)
        sboxparams.SetForegroundColour(sb1fontcolor)

        #### ebeam items
        fgslaser = wx.FlexGridSizer(4, 2, 10, 10)
        item11st = wx.StaticText(self.panel, label = u'Dipole Length [m]',
                style = wx.ALIGN_LEFT)
        item21st = wx.StaticText(self.panel, label = u'Drift Length [m]',
                style = wx.ALIGN_LEFT)
        item31st = wx.StaticText(self.panel, label = u'Dipole Field [T]',
                style = wx.ALIGN_LEFT)
        item41st = wx.StaticText(self.panel, label = u'R56 [mm]',
                style = wx.ALIGN_LEFT)

        self.item12tc = wx.TextCtrl(self.panel, id = ID_IMAGL,  value = '0.150', style = wx.TE_PROCESS_ENTER)
        self.item22tc = wx.TextCtrl(self.panel, id = ID_IDRIL,    value = '0.285', style = wx.TE_PROCESS_ENTER)
        self.item32sc = wx.SpinCtrlDouble(self.panel, id = ID_IBFIELD, value = '', 
                style = wx.SP_ARROW_KEYS, min = 0.04, max = 0.30, initial = 0.14, inc = 0.002)
        self.item42tc = wx.TextCtrl(self.panel, id = ID_DISPERSION, value = '0.528', style = wx.TE_PROCESS_ENTER)

        fgslaser.Add(item11st, proportion = 0, flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(self.item12tc, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(item21st, proportion = 0, flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(self.item22tc, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(item31st, proportion = 0, flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(self.item32sc, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(item41st, proportion = 0, flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.Add(self.item42tc, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        fgslaser.AddGrowableCol(1)
        sbparams_sizer.Add(fgslaser, proportion = 0, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT | wx.TOP, border = 15)

        sbparams_sizer.Add((-1, 10))
        
        #### 
        self.interbtn = wx.Button(self.panel, label = 'TBD')
        self.helpbtn = wx.Button(self.panel, label = 'Help')

        self.Bind(wx.EVT_BUTTON, self.OnInter, self.interbtn)
        self.Bind(wx.EVT_BUTTON, self.OnHelp, self.helpbtn)

        lbtnfont = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        lbtnfont.SetPointSize(14)
        lbtnfont.SetWeight(wx.FONTWEIGHT_NORMAL)
        lbtnfontcolor = '#FF00B0'
        lbtnfacecolor = '#BFD9F0'
        self.interbtn.SetFont(lbtnfont)
        self.helpbtn.SetFont(lbtnfont)
        self.interbtn.SetForegroundColour(lbtnfontcolor)
        self.helpbtn.SetForegroundColour(lbtnfontcolor)
        self.interbtn.SetBackgroundColour(lbtnfacecolor)
        self.helpbtn.SetBackgroundColour(lbtnfacecolor)
        
        hboxbtn = wx.BoxSizer(orient = wx.HORIZONTAL)
        hboxbtn.Add(self.interbtn, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border = 10)
        hboxbtn.Add(self.helpbtn, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border = 10)
        sbparams_sizer.Add(hboxbtn, flag = wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, border = 10)


        sbsizer.Add(sbparams_sizer, proportion = 3, flag = wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM, border = 10)
        
        vbox.Add(sbsizer, proportion = 1, 
                flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border = 10)

        ## set boxsizer
        self.panel.SetSizer(vbox)

        ## bind events
        self.Bind(wx.EVT_SPINCTRLDOUBLE, self.OnUpdateParams, self.item32sc)

        ## create a timer
        #self.timer = wx.Timer(self)
        #self.Bind(wx.EVT_TIMER, self.OnUpdate, self.timer)

#------------------------------------------------------------------------#

    def OnUpdateParams(self, event):
        obj = event.GetEventObject() 
        if obj.GetId() == ID_IBFIELD:
            epics.PV('DCLS:CHIFIELD:SET').put(obj.GetValue())
        
        curval = epics.PV('DCLS:CHIFIELD').get()
        gam0 = 587.87
        r56 = funutils.r56chi(gam0, curval)*1e3
        self.parent.OnUpdatePS(psid = 'chi', newval = curval)
        self.item42tc.SetValue('%.3f' % (r56))

#------------------------------------------------------------------------#

    def OnHelp(self, event):
        pass

#------------------------------------------------------------------------#

    def OnInter(self, event):
        pass

#------------------------------------------------------------------------#

def main(ClassName=ModdsPanel):
    app = wx.App(redirect = False)
    myframe = ClassName(None, style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
    if ClassName == ModdsPanel: 
        myframe.SetTitle('Laser-beam Interaction and Harmonic Generation')
    elif ClassName == MatchPanel:
        myframe.SetTitle('Beam Envelope Matching Operation')
    elif ClassName == RadisPanel:
        myframe.SetTitle('FEL Radiation Generation')
    myframe.SetSize((880, 668))
    #myframe.Centre()
    myframe.Show()
    app.MainLoop()

#------------------------------------------------------------------------#

if __name__ == '__main__':
    main(ClassName=ModdsPanel)
    #main(ClassName=MatchPanel)
    #main(ClassName=RadisPanel)

#------------------------------------------------------------------------#
