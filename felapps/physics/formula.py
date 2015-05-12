#!/usr/bin/env python
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------#

"""
Author: Tong Zhang
Create Time: 15:22, Jan. 15, 2015
first version is written in MATLAB on Dec. 25th, 2014.
"""

#------------------------------------------------------------------------#

import wx
from wx.lib.wordwrap import wordwrap
from . import felbase
#import felbase
import numpy as np

import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

#------------------------------------------------------------------------#

ID_BEAM_ENERGY   = wx.NewId()  
ID_ENERGY_SPREAD = wx.NewId()
ID_NORM_EMIT     = wx.NewId()
ID_AVG_BETA      = wx.NewId()     
ID_PEAK_CURRENT  = wx.NewId()
ID_UNDU_PERIOD   = wx.NewId()
ID_FEL_WVLTH     = wx.NewId()
ID_SCANFLAG      = wx.NewId()
ID_SCANPARM      = wx.NewId() 
ID_CALCBTN       = wx.NewId() 
ID_EXITBTN       = wx.NewId()
ID_PLOTBTN       = wx.NewId()
ID_SCAN_MIN      = wx.NewId()
ID_SCAN_MAX      = wx.NewId()
ID_SCAN_NUM      = wx.NewId()
ID_IMPORT        = wx.NewId()
ID_EXPORT        = wx.NewId()

#------------------------------------------------------------------------#

xchoice = {'Beam Energy'     : '$E_b\ \mathrm{[MeV]}$',
           'Energy Spread'   : '$\sigma_\gamma/\gamma_0$',
           'Norm. Emittance' : '$\epsilon_n\ \mathrm{[m]}$',
           'Peak Current'    : '$I_p\ \mathrm{[A]}$',
           'Undulator Period': '$\lambda_u\ \mathrm{[m]}$', 
           'FEL Wavelength'  : '$\lambda_s\ \mathrm{[m]}$',
           'Avg. Beta Func.' : '$avg.beta\ \mathrm{[m]}$'}
ychoice = {'au'     : '$a_u$',
           'bu'     : '$B_u\ \mathrm{[T]}$',
           'gap'    : '$\mathrm{Gap\ [mm]}$',
           'Lg1D'   : '$L_g^{\mathrm{1D}}\ \mathrm{[m]}$',
           'Lg3D'   : '$L_g^{\mathrm{3D}}\ \mathrm{[m]}$',
           'rho1D'  : '$\\rho^{\mathrm{1D}}$',
           'rho3D'  : '$\\rho^{\mathrm{3D}}$',
           'sigmar' : '$\sigma_r\ \mathrm{[m]}$',
           'Psat'   : '$P_{\mathrm{sat}}\ \mathrm{[W]}$'}

#------------------------------------------------------------------------#

class MainFrame(wx.Frame):

#------------------------------------------------------------------------#

    def __init__(self, parent, title, **kwargs):
        super(self.__class__, self).__init__(parent, id = wx.ID_ANY,
                title = title, **kwargs)
        self.InitUI()
        self.Centre()
        self.Show()

#------------------------------------------------------------------------#

    def createMenu(self):
        self.menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        importItem = fileMenu.Append(ID_IMPORT, '&Import\tCtrl+I', 'Import parameters from file')
        exportItem = fileMenu.Append(ID_EXPORT, '&Export\tCtrl+E', 'Export parameters to file')
        fileMenu.AppendSeparator()
        exitItem = fileMenu.Append(wx.ID_EXIT, 'E&xit\tCtrl+W', 'Exit')
        self.Bind(wx.EVT_MENU, self.onImport, id = ID_IMPORT)
        self.Bind(wx.EVT_MENU, self.onExport, id = ID_EXPORT)
        self.Bind(wx.EVT_MENU, self.onExit,   id = wx.ID_EXIT)

        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT, '&About\tF1', 'About this application')
        self.Bind(wx.EVT_MENU, self.onAbout, id = wx.ID_ABOUT)

        self.menubar.Append(fileMenu, '&File')
        self.menubar.Append(helpMenu, '&Help')
        
        self.SetMenuBar(self.menubar)

#------------------------------------------------------------------------#

    def onImport(self, event):
        pass
    
#------------------------------------------------------------------------#

    def onExport(self, event):
        pass

#------------------------------------------------------------------------#

    def onAbout(self, event):
        # First we create and fill the info object
        info = wx.AboutDialogInfo()
        info.Name = "FEL Formula"
        info.Version = "2015.01.20"
        info.Copyright = "(C) 2014-2015 Tong Zhang, SINAP, CAS"
        info.Description = wordwrap(
            "This program is designed for fast FEL physics calculations.\n"

            "It is designed by Python language, using GUI module of wxPython.",
            350, wx.ClientDC(self))
        info.WebSite = ("http://everyfame.me", "FEL Formula home page")
        info.Developers = [ "Tong Zhang <zhangtong@sinap.ac.cn>"]
        licenseText = "FEL Formula is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.\n" + "\nFEL Formula is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.\n" + "\nYou should have received a copy of the GNU General Public License along with FEL Formula; if not, write to the Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA"
        info.License = wordwrap(licenseText, 500, wx.ClientDC(self))

        # Then we call wx.AboutBox giving it that info object
        wx.AboutBox(info)

#------------------------------------------------------------------------#

    def InitUI(self):

        self.createMenu()

        ## statictext result color
        resultcolor = 'red'
        
        ## staticboxsizer staticbox font and color
        sbfont = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        sbfont.SetPointSize(10)
        sbfont.SetWeight(wx.FONTWEIGHT_BOLD)
        sbcolor = 'MAGENTA'

        panel = wx.Panel(self, id = wx.ID_ANY)
        gbsizer = wx.GridBagSizer(vgap = 8, hgap = 8)
        
        font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(18)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        st0 = wx.StaticText(panel, 
                label = 'Cheat Sheet for FEL Physics', style = wx.ALIGN_CENTRE)
        st0.SetForegroundColour(wx.BLUE)
        st0.SetFont(font)
        gbsizer.Add(st0, pos = (0, 0), span = (1, 2), 
                flag = wx.ALIGN_CENTER | wx.LEFT | wx.TOP | wx.BOTTOM, border = 10)

        sl1 = wx.StaticLine(panel, style = wx.LI_HORIZONTAL)
        gbsizer.Add(sl1, pos = (1, 0), span = (1, 2),
                flag = wx.EXPAND | wx.LEFT | wx.RIGHT, border = 10)

        sbox1 = wx.StaticBox(panel, id = wx.ID_ANY, 
                label = 'Beam Parameters')
        sbox2 = wx.StaticBox(panel, id = wx.ID_ANY,
                label = 'FEL Calculations')
        sbox3 = wx.StaticBox(panel, id = wx.ID_ANY,
                label = 'Operations')
        sbox4 = wx.StaticBox(panel, id = wx.ID_ANY,
                label = 'Brief Guide')
        sbox1.SetFont(sbfont)
        sbox2.SetFont(sbfont)
        sbox3.SetFont(sbfont)
        sbox4.SetFont(sbfont)
        sbox1.SetForegroundColour(sbcolor)
        sbox2.SetForegroundColour(sbcolor)
        sbox3.SetForegroundColour(sbcolor)
        sbox4.SetForegroundColour(sbcolor)
        sbsizer1 = wx.StaticBoxSizer(sbox1, orient = wx.VERTICAL)
        sbsizer2 = wx.StaticBoxSizer(sbox2, orient = wx.VERTICAL)
        sbsizer3 = wx.StaticBoxSizer(sbox3, orient = wx.VERTICAL)
        sbsizer4 = wx.StaticBoxSizer(sbox4, orient = wx.VERTICAL)

        ## sbsizer1: 'Beam Parameters'  StaticBoxSizer
        box1 = wx.FlexGridSizer(7, 2, 8, 40)

        b1st1 = wx.StaticText(panel, label = 'Beam Energy [MeV]',    style = wx.ALIGN_LEFT)
        b1st2 = wx.StaticText(panel, label = 'Energy Spread',        style = wx.ALIGN_LEFT)
        b1st3 = wx.StaticText(panel, label = 'Norm. Emittance [m]',  style = wx.ALIGN_LEFT)
        b1st4 = wx.StaticText(panel, label = 'Avg. Beta Func. [m]',  style = wx.ALIGN_LEFT)
        b1st5 = wx.StaticText(panel, label = 'Peak Current [A]',     style = wx.ALIGN_LEFT)
        b1st6 = wx.StaticText(panel, label = 'Undulator Period [m]', style = wx.ALIGN_LEFT)
        b1st7 = wx.StaticText(panel, label = 'FEL Wavelength [m]',   style = wx.ALIGN_LEFT)

        self.b1tc1 = wx.TextCtrl(panel, id = ID_BEAM_ENERGY,   value = '150'   , style = wx.TE_PROCESS_ENTER)
        self.b1tc2 = wx.TextCtrl(panel, id = ID_ENERGY_SPREAD, value = '0.0001', style = wx.TE_PROCESS_ENTER)
        self.b1tc3 = wx.TextCtrl(panel, id = ID_NORM_EMIT,     value = '4e-6'  , style = wx.TE_PROCESS_ENTER)
        self.b1tc4 = wx.TextCtrl(panel, id = ID_AVG_BETA,      value = '4'     , style = wx.TE_PROCESS_ENTER)
        self.b1tc5 = wx.TextCtrl(panel, id = ID_PEAK_CURRENT,  value = '100'   , style = wx.TE_PROCESS_ENTER)
        self.b1tc6 = wx.TextCtrl(panel, id = ID_UNDU_PERIOD,   value = '0.025' , style = wx.TE_PROCESS_ENTER)
        self.b1tc7 = wx.TextCtrl(panel, id = ID_FEL_WVLTH,     value = '350e-9', style = wx.TE_PROCESS_ENTER)

        box1.Add(b1st1,      proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT,  border = 15)
        box1.Add(self.b1tc1, proportion = 1, flag = wx.EXPAND | wx.RIGHT, border = 15)
        box1.Add(b1st2,      proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT,  border = 15)
        box1.Add(self.b1tc2, proportion = 1, flag = wx.EXPAND | wx.RIGHT, border = 15)
        box1.Add(b1st3,      proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT,  border = 15)
        box1.Add(self.b1tc3, proportion = 1, flag = wx.EXPAND | wx.RIGHT, border = 15)
        box1.Add(b1st4,      proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT,  border = 15)
        box1.Add(self.b1tc4, proportion = 1, flag = wx.EXPAND | wx.RIGHT, border = 15)
        box1.Add(b1st5,      proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT,  border = 15)
        box1.Add(self.b1tc5, proportion = 1, flag = wx.EXPAND | wx.RIGHT, border = 15)
        box1.Add(b1st6,      proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT,  border = 15)
        box1.Add(self.b1tc6, proportion = 1, flag = wx.EXPAND | wx.RIGHT, border = 15)
        box1.Add(b1st7,      proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT,  border = 15)
        box1.Add(self.b1tc7, proportion = 1, flag = wx.EXPAND | wx.RIGHT, border = 15)

        box1.AddGrowableCol(1)

        sbsizer1.Add(box1, proportion = 1, flag = wx.ALIGN_CENTER | wx.EXPAND | wx.ALL, border = 10)

        ## sbsizer2: 'FEL Calculations' StaticBoxSizer

        ### undulator
        b2sb1 = wx.StaticBox(panel, id = wx.ID_ANY, label = 'Undulator')
        b2sb1sizer = wx.StaticBoxSizer(b2sb1, orient = wx.VERTICAL)

        b2sb1st1 = wx.StaticText(panel, label = 'Field [T]:', style = wx.ALIGN_LEFT)
        b2sb1st2 = wx.StaticText(panel, label = 'Gap [mm]:',  style = wx.ALIGN_LEFT)
        b2sb1st3 = wx.StaticText(panel, label = 'K:',         style = wx.ALIGN_LEFT)

        self.b2sb1vst1 = wx.StaticText(panel, label = '0.720', style = wx.ALIGN_LEFT)
        self.b2sb1vst2 = wx.StaticText(panel, label = '7.801', style = wx.ALIGN_LEFT)
        self.b2sb1vst3 = wx.StaticText(panel, label = '1.681', style = wx.ALIGN_LEFT)
        self.b2sb1vst1.SetForegroundColour(resultcolor)
        self.b2sb1vst2.SetForegroundColour(resultcolor) 
        self.b2sb1vst3.SetForegroundColour(resultcolor) 
        
        b2sb1fgs = wx.FlexGridSizer(3, 2, 10, 20)
        b2sb1fgs.Add(b2sb1st1,  proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb1fgs.Add(self.b2sb1vst1, proportion = 1, flag = wx.EXPAND | wx.RIGHT, border = 10)
        b2sb1fgs.Add(b2sb1st2,  proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb1fgs.Add(self.b2sb1vst2, proportion = 1, flag = wx.EXPAND | wx.RIGHT, border = 10)
        b2sb1fgs.Add(b2sb1st3,  proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb1fgs.Add(self.b2sb1vst3, proportion = 1, flag = wx.EXPAND | wx.RIGHT, border = 10)
        b2sb1fgs.AddGrowableCol(1)
        
        b2sb1sizer.Add(b2sb1fgs, proportion = 1, flag = wx.ALIGN_CENTER | wx.EXPAND | wx.ALL, border = 10)

        ### radiation
        b2sb2 = wx.StaticBox(panel, id = wx.ID_ANY, label = 'FEL Radiation')
        b2sb2sizer = wx.StaticBoxSizer(b2sb2, orient = wx.VERTICAL)
        b2sb2st1 = wx.StaticText(panel, label = 'FEL parameter (1D):',       style = wx.ALIGN_LEFT)
        b2sb2st2 = wx.StaticText(panel, label = 'FEL parameter (3D):',       style = wx.ALIGN_LEFT)
        b2sb2st3 = wx.StaticText(panel, label = 'FEL gainlength (1D) [m]:',  style = wx.ALIGN_LEFT)
        b2sb2st4 = wx.StaticText(panel, label = 'FEL gainlength (3D) [m]:',  style = wx.ALIGN_LEFT)
        b2sb2st5 = wx.StaticText(panel, label = 'FEL saturation power [W]:', style = wx.ALIGN_LEFT)

        self.b2sb2vst1 = wx.StaticText(panel, label = '2.022e-03', style = wx.ALIGN_LEFT)
        self.b2sb2vst2 = wx.StaticText(panel, label = '1.622e-03', style = wx.ALIGN_LEFT)
        self.b2sb2vst3 = wx.StaticText(panel, label = '0.568',     style = wx.ALIGN_LEFT)
        self.b2sb2vst4 = wx.StaticText(panel, label = '0.708',     style = wx.ALIGN_LEFT)
        self.b2sb2vst5 = wx.StaticText(panel, label = '3.121e+07', style = wx.ALIGN_LEFT)
        self.b2sb2vst1.SetForegroundColour(resultcolor)
        self.b2sb2vst2.SetForegroundColour(resultcolor)
        self.b2sb2vst3.SetForegroundColour(resultcolor)
        self.b2sb2vst4.SetForegroundColour(resultcolor)
        self.b2sb2vst5.SetForegroundColour(resultcolor)
        
        b2sb2fgs = wx.FlexGridSizer(5, 2, 10, 30)
        b2sb2fgs.Add(b2sb2st1,  proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb2fgs.Add(self.b2sb2vst1, proportion = 1, flag = wx.EXPAND | wx.RIGHT, border = 10)
        b2sb2fgs.Add(b2sb2st2,  proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb2fgs.Add(self.b2sb2vst2, proportion = 1, flag = wx.EXPAND | wx.RIGHT, border = 10)
        b2sb2fgs.Add(b2sb2st3,  proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb2fgs.Add(self.b2sb2vst3, proportion = 1, flag = wx.EXPAND | wx.RIGHT, border = 10)
        b2sb2fgs.Add(b2sb2st4,  proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb2fgs.Add(self.b2sb2vst4, proportion = 1, flag = wx.EXPAND | wx.RIGHT, border = 10)
        b2sb2fgs.Add(b2sb2st5,  proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb2fgs.Add(self.b2sb2vst5, proportion = 1, flag = wx.EXPAND | wx.RIGHT, border = 10)
        b2sb2fgs.AddGrowableCol(1)

        b2sb2sizer.Add(b2sb2fgs, proportion = 1, flag = wx.ALIGN_CENTER | wx.EXPAND | wx.ALL, border = 10)

        sbsizer2.Add(b2sb1sizer, proportion = 1, flag = wx.ALIGN_LEFT | wx.EXPAND | wx.ALL, border = 10)
        sbsizer2.Add(b2sb2sizer, proportion = 1, flag = wx.ALIGN_LEFT | wx.EXPAND | wx.ALL, border = 10)
        
        ## sbsizer3: 'Operations'        StaticBoxSizer
        b3sb1 = wx.StaticBox(panel, id = wx.ID_ANY, label = 'Scan Control')
        b3sb1sizer = wx.StaticBoxSizer(b3sb1, orient = wx.VERTICAL)
        
        self.chkbox31 = wx.CheckBox(panel, id = ID_SCANFLAG, label = 'Enable Scan')
        self.combobox31 = wx.ComboBox(panel, id = ID_SCANPARM, value = 'Beam Energy', 
                choices = ['Beam Energy','Energy Spread', 
                           'Norm. Emittance', 'Peak Current', 
                           'Undulator Period', 'FEL Wavelength',
                           'Avg. Beta Func.'],
                style = wx.CB_READONLY)
        self.combobox31.Disable()

        ### scan range box
        scansb = wx.StaticBox(panel, id = wx.ID_ANY, label = 'Scan Range')
        scansbsizer = wx.StaticBoxSizer(scansb, orient = wx.VERTICAL)
        self.sminst = wx.StaticText(panel, label = 'Min', style = wx.ALIGN_LEFT)
        self.smaxst = wx.StaticText(panel, label = 'Max', style = wx.ALIGN_LEFT)
        self.snumst = wx.StaticText(panel, label = 'N',   style = wx.ALIGN_LEFT)
        self.smintc = wx.TextCtrl(panel, id = ID_SCAN_MIN, value = '100', style = wx.TE_PROCESS_ENTER)
        self.smaxtc = wx.TextCtrl(panel, id = ID_SCAN_MAX, value = '200', style = wx.TE_PROCESS_ENTER)
        self.snumtc = wx.TextCtrl(panel, id = ID_SCAN_NUM, value = '100', style = wx.TE_PROCESS_ENTER)
        self.smintc.Disable()
        self.smaxtc.Disable()
        self.snumtc.Disable()
        scanfgs = wx.FlexGridSizer(2, 3, 4, 4)
        scanfgs.Add(self.sminst, proportion = 1, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT, border = 10)
        scanfgs.Add(self.smaxst, proportion = 1, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, border = 10)
        scanfgs.Add(self.snumst, proportion = 1, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.RIGHT, border = 10)
        scanfgs.Add(self.smintc, proportion = 1, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT, border = 10)
        scanfgs.Add(self.smaxtc, proportion = 1, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, border = 10)
        scanfgs.Add(self.snumtc, proportion = 1, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.RIGHT, border = 10)
        scansbsizer.Add(scanfgs, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border = 10)
        scanfgs.AddGrowableCol(0)
        scanfgs.AddGrowableCol(1)
        scanfgs.AddGrowableCol(2)

        ### scan control box
        scangbs = wx.GridBagSizer(10, 0)
        scangbs.Add(self.chkbox31,   pos = (0, 0), flag = wx.EXPAND | wx.LEFT,  border = 10)
        scangbs.Add(self.combobox31, pos = (0, 1), flag = wx.EXPAND | wx.RIGHT, border = 10)
        scangbs.Add(scansbsizer, pos = (1, 0), span = (1, 2), flag = wx.EXPAND | wx.LEFT | wx.RIGHT, border = 10)
        scangbs.AddGrowableCol(0)
        scangbs.AddGrowableCol(1)
        b3sb1sizer.Add(scangbs, flag = wx.BOTTOM | wx.EXPAND | wx.ALIGN_CENTER, border = 10)
        
        ###
        b3sb2 = wx.StaticBox(panel, id = wx.ID_ANY, label = 'Command')
        b3sb2sizer = wx.StaticBoxSizer(b3sb2, orient = wx.VERTICAL)

        ### command box
        cmdgbs = wx.GridBagSizer(5, 5)
        self.calcbtn = wx.Button(panel ,id = ID_CALCBTN, label = '&Calculate', size = (90, 40))
        self.exitbtn = wx.Button(panel ,id = ID_EXITBTN, label = 'E&xit',      size = (90, 40))
        self.plotbtn = wx.Button(panel, id = ID_PLOTBTN, label = 'Show &Plot', size = (90, 40))
        self.plotbtn.Disable()

        cmdgbs.Add(self.calcbtn, pos = (0, 0), span = (1, 1), flag = wx.ALIGN_CENTER | wx.LEFT, border = 10)
        cmdgbs.Add(self.plotbtn, pos = (0, 1), span = (1, 1), flag = wx.ALIGN_CENTER)
        cmdgbs.Add(self.exitbtn, pos = (0, 2), span = (1, 1), flag = wx.ALIGN_CENTER | wx.RIGHT, border = 10)
        cmdgbs.AddGrowableCol(1)

        b3sb2sizer.Add(cmdgbs, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border = 10)

        sbsizer3.Add(b3sb1sizer, proportion = 1, flag = wx.ALIGN_CENTER | wx.EXPAND | wx.ALL, border = 10)
        sbsizer3.Add(b3sb2sizer, proportion = 0, flag = wx.ALIGN_CENTER | wx.EXPAND | wx.ALL, border = 10)
        
        ## sbsizer4: 'Brief Guide'            StaticBoxSizer
        aboutstring = "How to use this application:\n" + \
                      "1: Input the parameters in 'Beam Parameters' panel;\n" + \
                      "2: Push 'Calculate' button to show the calculated results;\n" + \
                      "3: If 'Enable Scan' is checked, scan function is enabled;\n" + \
                      "  3.1: Choose the scan parameter and the scan range;\n" + \
                      "  3.2: Push 'Calculate' button, then 'Show Plot' to check plot."
        aboutinfo = wx.StaticText(panel, label = aboutstring, style = wx.ALIGN_LEFT | wx.TE_MULTILINE)
        font1 = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        font1.SetPointSize(10)
        font1.SetWeight(wx.FONTWEIGHT_NORMAL)
        aboutinfo.SetFont(font1)
        aboutinfo.SetForegroundColour('gray')
        sbsizer4.Add(aboutinfo, flag = wx.ALIGN_CENTER | wx.LEFT | wx.TOP, border = 5)


        gbsizer.Add(sbsizer1, pos = (2, 0), span = (2, 1),
                flag = wx.EXPAND | wx.LEFT, border = 15)
        gbsizer.Add(sbsizer2, pos = (2, 1), span = (3, 1),
                flag = wx.EXPAND | wx.RIGHT, border = 15)
        gbsizer.Add(sbsizer3, pos = (4, 0), span = (2, 1),
                flag = wx.EXPAND | wx.LEFT | wx.BOTTOM, border = 15)
        gbsizer.Add(sbsizer4, pos = (5, 1), span = (1, 1),
                flag = wx.EXPAND | wx.RIGHT | wx.BOTTOM, border = 15)

        gbsizer.AddGrowableCol(0, 1)
        gbsizer.AddGrowableCol(1, 1)
        gbsizer.AddGrowableRow(2, 1)
        gbsizer.AddGrowableRow(4, 1)
        gbsizer.AddGrowableRow(5, 1)

        panel.SetSizer(gbsizer)
        osizer = wx.BoxSizer(wx.HORIZONTAL)
        osizer.Add(panel, proportion = 1, flag = wx.EXPAND)
        self.SetSizerAndFit(osizer)

        # callback bindings
        self.Bind(wx.EVT_CLOSE,  self.onExit)
        self.Bind(wx.EVT_BUTTON, self.onCalc, id = ID_CALCBTN)
        self.Bind(wx.EVT_BUTTON, self.onExit, id = ID_EXITBTN)
        self.Bind(wx.EVT_BUTTON, self.onPlot, id = ID_PLOTBTN)
        self.Bind(wx.EVT_TEXT_ENTER, self.onTextEnter,  id = ID_BEAM_ENERGY  )
        self.Bind(wx.EVT_TEXT_ENTER, self.onTextEnter,  id = ID_ENERGY_SPREAD)
        self.Bind(wx.EVT_TEXT_ENTER, self.onTextEnter,  id = ID_NORM_EMIT    )
        self.Bind(wx.EVT_TEXT_ENTER, self.onTextEnter,  id = ID_AVG_BETA     )
        self.Bind(wx.EVT_TEXT_ENTER, self.onTextEnter,  id = ID_PEAK_CURRENT )
        self.Bind(wx.EVT_TEXT_ENTER, self.onTextEnter,  id = ID_UNDU_PERIOD  )
        self.Bind(wx.EVT_TEXT_ENTER, self.onTextEnter,  id = ID_FEL_WVLTH    )
        self.Bind(wx.EVT_TEXT_ENTER, self.onTextEnter,  id = ID_SCAN_MIN     )
        self.Bind(wx.EVT_TEXT_ENTER, self.onTextEnter,  id = ID_SCAN_MAX     )
        self.Bind(wx.EVT_TEXT_ENTER, self.onTextEnter,  id = ID_SCAN_NUM     )
        self.Bind(wx.EVT_CHECKBOX,   self.onEnableScan, id = ID_SCANFLAG     )

#------------------------------------------------------------------------#

    def onCalc(self, event):
        beamEnergy   = float(self.b1tc1.GetValue())
        energySpread = float(self.b1tc2.GetValue())
        normEmit     = float(self.b1tc3.GetValue())
        avgBeta      = float(self.b1tc4.GetValue())
        peakCurrent  = float(self.b1tc5.GetValue())
        unduPeriod   = float(self.b1tc6.GetValue())
        FELwvlth     = float(self.b1tc7.GetValue())

        if not self.chkbox31.IsChecked():
            instFEL = felbase.FELcalc(beamEnergy,
                                      energySpread,
                                      unduPeriod,
                                      avgBeta,
                                      FELwvlth,
                                      normEmit,
                                      peakCurrent)
            result = instFEL.MXieFormulae()
            self.b2sb1vst1.SetLabel('%.3f' % (result['bu']))
            self.b2sb1vst2.SetLabel('%.3f' % (result['gap'][0]))
            self.b2sb1vst3.SetLabel('%.3f' % (result['au']*2.0**0.5))
            self.b2sb2vst1.SetLabel('%.3e' % (result['rho1D']))
            self.b2sb2vst2.SetLabel('%.3e' % (result['rho3D']))
            self.b2sb2vst3.SetLabel('%.3f' % (result['Lg1D']))
            self.b2sb2vst4.SetLabel('%.3f' % (result['Lg3D']))
            self.b2sb2vst5.SetLabel('%.3e' % (result['Psat']))
        else: # Scan is enabled
            scanparam = self.combobox31.GetStringSelection()
            scanmin   = float(self.smintc.GetValue())
            scanmax   = float(self.smaxtc.GetValue())
            scanpoint =   int(self.snumtc.GetValue())
            if scanparam == u'Beam Energy':
                beamEnergy = np.linspace(scanmin,scanmax,scanpoint)
                self.scanX = beamEnergy
            elif scanparam == u'Energy Spread':
                energySpread = np.linspace(scanmin,scanmax,scanpoint)
                self.scanX = energySpread
            elif scanparam == u'Norm. Emittance':
                normEmit = np.linspace(scanmin,scanmax,scanpoint)
                self.scanX = normEmit
            elif scanparam == u'Peak Current':
                peakCurrent = np.linspace(scanmin,scanmax,scanpoint)
                self.scanX = peakCurrent
            elif scanparam == u'Undulator Period':
                unduPeriod = np.linspace(scanmin,scanmax,scanpoint)
                self.scanX = unduPeriod
            elif scanparam == u'FEL Wavelength':
                FELwvlth = np.linspace(scanmin,scanmax,scanpoint)
                self.scanX = FELwvlth
            elif scanparam == u'Avg. Beta Func.':
                avgBeta    = np.linspace(scanmin,scanmax,scanpoint)
                self.scanX = avgBeta
                #print self.scanX
            else:
                print('Scan parameters ERROR!')

            instFEL = felbase.FELcalc(beamEnergy,
                                      energySpread,
                                      unduPeriod,
                                      avgBeta,
                                      FELwvlth,
                                      normEmit,
                                      peakCurrent)
            self.result = instFEL.MXieFormulae()

#------------------------------------------------------------------------#

    def onPlot(self, event):
        self.plotframe = PlotFrame(self,title = 'Plot Frame', 
                size = (750, 700))
        self.plotframe.Show()
        self.plotframe.Centre()

#------------------------------------------------------------------------#

    def onTextEnter(self, event):
        try:
            float(event.GetEventObject().GetValue())
        except ValueError:
            dial = wx.MessageDialog(self, message = u"Input data error, should be valid real number, please try again!", 
                    caption = u"Data Input Error", 
                    style = wx.OK | wx.CANCEL | wx.ICON_ERROR | wx.CENTRE)
            if dial.ShowModal() == wx.ID_OK:
                event.GetEventObject().SetValue('')
                dial.Destroy()

#------------------------------------------------------------------------#

    def onEnableScan(self, event):
        if self.chkbox31.GetValue():
            self.combobox31.Enable()
            self.smintc.Enable()
            self.smaxtc.Enable()
            self.snumtc.Enable()
            self.plotbtn.Enable()
        else:
            self.combobox31.Disable()
            self.smintc.Disable()
            self.smaxtc.Disable()
            self.snumtc.Disable()
            self.plotbtn.Disable()

#------------------------------------------------------------------------#

    def onExit(self, event):
        dial = wx.MessageDialog(self, message = "Are you sure to exit this application?",
                                caption = "Exit Warning", style = wx.YES_NO | wx.NO_DEFAULT | wx.CENTRE | wx.ICON_QUESTION)
        if dial.ShowModal() == wx.ID_YES:
            self.Destroy()

#------------------------------------------------------------------------#

class PlotFrame(wx.Frame):

#------------------------------------------------------------------------#

    def __init__(self, parent, title, **kwargs):
        super(self.__class__, self).__init__(parent = parent,
                id = wx.ID_ANY, title = title, **kwargs)
        self.parent = parent
        self.InitUI()
    
#------------------------------------------------------------------------#

    def InitUI(self):
        self.createMenu ()
        self.createPanel()

#------------------------------------------------------------------------#

    def createMenu(self):
        self.menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        saveItem = fileMenu.Append(wx.ID_SAVE, '&Save plot\tCtrl-S', 'Save plot to file')
        fileMenu.AppendSeparator()
        exitItem = fileMenu.Append(wx.ID_EXIT, 'E&xit\tCtrl-W', 'Exit')
        self.Bind(wx.EVT_MENU, self.onSavePlot, id = wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.onExitPlot, id = wx.ID_EXIT)

        helpMenu = wx.Menu()
        self.aboutItem = helpMenu.Append(wx.ID_ANY, '&About\tCtrl-A', 'Show about information')
        self.Bind(wx.EVT_MENU, self.onAboutPlot, self.aboutItem)

        self.menubar.Append(fileMenu, '&File')
        self.menubar.Append(helpMenu, '&Help')
        
        self.SetMenuBar(self.menubar)

#------------------------------------------------------------------------#

    def createPanel(self):
        self.panel = wx.Panel(self, id = wx.ID_ANY)

        vbox = wx.BoxSizer(wx.VERTICAL)

        # figure panel
        self.dpi = 100
        self.fig = Figure((5.0, 4.0), dpi = self.dpi)
        self.axes = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.panel, wx.ID_ANY, self.fig)

        # combobox for result plot
        params = self.parent.result.keys()
        self.plotparamcombo = wx.ComboBox(self.panel, id = wx.ID_ANY, value = params[0],
                choices = params, style = wx.CB_READONLY | wx.CB_SORT)
        st1 = wx.StaticText(self.panel, id = wx.ID_ANY, label = 'Y Axis:', style = wx.ALIGN_LEFT)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(st1, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        hbox.Add(self.plotparamcombo, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.TOP | wx.BOTTOM, border = 10)

        vbox.Add(self.canvas, proportion = 1, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border = 0)
        vbox.Add(hbox, flag = wx.LEFT, border = 10)

        self.panel.SetSizer(vbox)
        
        self.Bind(wx.EVT_COMBOBOX, self.onPlotChoice, self.plotparamcombo)

#------------------------------------------------------------------------#

    def onPlotChoice(self, event):
        ykey = self.plotparamcombo.GetValue()
        xkey = self.parent.combobox31.GetValue() 
        x = self.parent.scanX
        y = self.parent.result[ykey]
        self.axes.clear()
        try:
            self.axes.plot(x,y,'r')
            self.axes.set_xlabel(r''+xchoice[xkey]+'')
            self.axes.set_ylabel(r''+ychoice[ykey]+'')
            self.canvas.draw()
        except ValueError:
            pass

#------------------------------------------------------------------------#

    def onExitPlot(self, event):
        self.Close()

#------------------------------------------------------------------------#

    def onSavePlot(self, event):
        pass

#------------------------------------------------------------------------#

    def onAboutPlot(self, event):
        dial = wx.MessageDialog(self.panel, message = "This panel is designed to show the plot figure.",
                caption = 'About plot panel', style = wx.ICON_INFORMATION)
        dial.ShowModal()

#------------------------------------------------------------------------#

def run():
    app = wx.App(redirect = True)
    MainFrame(None, title = 'FEL Formula', size = (880, 668))
    app.MainLoop()

#------------------------------------------------------------------------#

if __name__ == '__main__':
    run()

#------------------------------------------------------------------------#
