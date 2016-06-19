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
from ..utils import funutils
from ..utils import parseutils
import numpy as np

import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as Toolbar
import matplotlib.ticker as tick
import wx.lib.dialogs

import os
import time
import h5py

#------------------------------------------------------------------------#

ID_BEAM_ENERGY   = wx.NewId()  
ID_ENERGY_SPREAD = wx.NewId()
ID_NORM_EMIT     = wx.NewId()
ID_AVG_BETA      = wx.NewId()     
ID_PEAK_CURRENT  = wx.NewId()
ID_UNDU_PERIOD   = wx.NewId()
ID_FEL_WVLTH     = wx.NewId()
ID_BUNCH_CHARGE  = wx.NewId()
ID_SCANFLAG      = wx.NewId()
ID_SCANPARM      = wx.NewId() 
ID_CALCBTN       = wx.NewId() 
ID_EXITBTN       = wx.NewId()
ID_PLOTBTN       = wx.NewId()
ID_SCAN_MIN      = wx.NewId()
ID_SCAN_MAX      = wx.NewId()
ID_SCAN_NUM      = wx.NewId()

#------------------------------------------------------------------------#

xchoice = {'Beam Energy'     : '$E_b\ \mathrm{[MeV]}$',
           'Energy Spread'   : '$\sigma_\gamma/\gamma_0$',
           'Norm. Emittance' : '$\epsilon_n\ \mathrm{[m]}$',
           'Peak Current'    : '$I_p\ \mathrm{[A]}$',
           'Undulator Period': '$\lambda_u\ \mathrm{[m]}$',
           'FEL Wavelength'  : '$\lambda_s\ \mathrm{[m]}$',
           'Avg. Beta Func.' : '$\langle{\\beta}\\rangle\ \mathrm{[m]}$',
           'Bunch Charge'    : '$Q\ \mathrm{[C]}$'}

ychoice = {'01-au'     : ['$a_u$',                             'Normalized undulator parameter.'],
           '02-K'      : ['$K$',                               'Undulator parameter.'],
           '03-Bu'     : ['$B_u\ \mathrm{[T]}$',               'Undulator magnetic peak field [T].'],
           '04-gap'    : ['$\mathrm{Gap\ [mm]}$',              'Permanent undulator gap [mm].'],
           '05-rho1D'  : ['$\\rho^{\mathrm{1D}}$',             'FEL parameter or Pierce parameter (1D).'],
           '06-rho3D'  : ['$\\rho^{\mathrm{3D}}$',             'FEL parameter or Pierce parameter (3D).'],
           '07-Lg1D'   : ['$L_g^{\mathrm{1D}}\ \mathrm{[m]}$', 'FEL power gain length (1D) [m].'],
           '08-Lg3D'   : ['$L_g^{\mathrm{3D}}\ \mathrm{[m]}$', 'FEL power gain length (3D) [m].'],
           '09-Psat'   : ['$P_{\mathrm{sat}}\ \mathrm{[W]}$',  'FEL saturation power (M.Xie formulae) [W].'],
           '10-Pshot'  : ['$P_{\mathrm{shot}}\ \mathrm{[W]}$', 'FEL initial shotnoise power [W].'],
           '11-Pss'    : ['$P_{\mathrm{ss}}\ \mathrm{[W]}$',   'FEL saturation power (SASE) [W].'],
           '12-Lsat'   : ['$L_{\mathrm{sat}}\ \mathrm{[m]}$',  'FEL saturation length (SASE) [m].'],
           '13-sigmar' : ['$\sigma_r\ \mathrm{[\mu m]}$',      'Transverse e-beam radius size (rms) [micro m].'],
           '14-sigmat' : ['$\sigma_t\ \mathrm{[fs]}$',         'Temporal bunch length (rms) [fs].'],
           '15-bandWidth'      : ['$\Delta\lambda/\lambda$ [%]', 'FEL bandwidth [%].'],
           '16-PhotonEnergy'   : ['$E_p\ \mathrm{[eV]}$',        'FEL photon energy [eV].'],
           '17-PulseEnergy'    : ['$W\ \mathrm{[\mu J]}$',       'FEL pulse energy [micro J].'],
           '18-PhotonPerPulse' : ['$\mathrm{Photon\ \#/pulse}$', 'FEL photon number per pulse.'],
           }

#------------------------------------------------------------------------#

class MainFrame(wx.Frame):

#------------------------------------------------------------------------#

    def __init__(self, parent, size = (800, 600), appversion = '1.0', **kwargs):
        super(self.__class__, self).__init__(parent = parent, size = size, id = wx.ID_ANY, **kwargs)
        self.parent = parent
        self.appversion = appversion
        #self.paramdict = {'00-info':{}, ''} # hierach dict to keep input & output parameters
        self.initUI()

#------------------------------------------------------------------------#

    def initUI(self):
        self.createMenu()
        self.createStatusbar()
        self.createPanel()

#------------------------------------------------------------------------#

    def createMenu(self):
        self.menubar = wx.MenuBar()

        fileMenu = wx.Menu()
        importItem = fileMenu.Append(wx.ID_ANY, '&Import\tCtrl+Shift+I', 'Import parameters from file')
        exportItem = fileMenu.Append(wx.ID_ANY, '&Export\tCtrl+Shift+E', 'Export parameters to file')
        # database
        #exportJsonItem = fileMenu.Append(wx.ID_ANY, '&Export as String\tCtrl+Shift+J', 'Export parameters to as a string to file')
        fileMenu.AppendSeparator()
        exitItem = fileMenu.Append(wx.ID_EXIT, 'E&xit\tCtrl+W', 'Exit')

        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT, '&About\tCtrl-I',      'About this application')
        infoItem  = helpMenu.Append(wx.ID_ANY,   '&Info\tF1',           'Show brief guide')
        clogItem  = helpMenu.Append(wx.ID_ANY,   '&Change log\tCtrl-L', "See what's new" )

        self.menubar.Append(fileMenu, '&File')
        self.menubar.Append(helpMenu, '&Help')
        
        self.SetMenuBar(self.menubar)

        # event bindings
        self.Bind(wx.EVT_MENU, self.onImport,    importItem)
        self.Bind(wx.EVT_MENU, self.onExport,    exportItem)
        #self.Bind(wx.EVT_MENU, self.onExportJ,   exportJsonItem)
        self.Bind(wx.EVT_MENU, self.onExit,      id = wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.onAbout,     id = wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.onInfo,      infoItem)
        self.Bind(wx.EVT_MENU, self.onChangelog, clogItem)
        self.Bind(wx.EVT_MENU_HIGHLIGHT,      self.onMenuHL)

    def createStatusbar(self):
        self.statusbar = funutils.ESB.EnhancedStatusBar(self)
        self.statusbar.SetFieldsCount(2)
        self.SetStatusBar(self.statusbar)
        self.statusbar.SetStatusWidths([-4,-1])
        self.statusbar.appinfo= wx.StaticText(self.statusbar, wx.ID_ANY,
                label = 'FEL formula powered by Python')
        versionfield = wx.StaticText(self.statusbar, wx.ID_ANY,
                label = time.strftime('%Y-%m-%d', time.localtime()) + ' ' + ' (Version: ' + self.appversion + ')')
        self.statusbar.AddWidget(self.statusbar.appinfo, funutils.ESB.ESB_ALIGN_LEFT )
        self.statusbar.AddWidget(versionfield, funutils.ESB.ESB_ALIGN_RIGHT)

    def onMenuHL(self, event):
        try:
            hltext = event.GetEventObject().GetHelpString(event.GetMenuId())
            self.statusbar.appinfo.SetLabel(hltext)
        except:
            pass

    def onInfo(self, event):
        infoframe = InfoFrame(self, title='Brief Guide to This Application', style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        infoframe.Show()
        infoframe.Centre()

    def onChangelog(self, event):
        clogframe = LogFrame(self, title='Changelogs', style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        clogframe.Show()
        clogframe.Centre()

    def onImport(self, event):
        """
        Import parameters from external configuration file
        """
        try:
            configfile = funutils.getFileToLoad(self, ext = '*')
            paramsconf = parseutils.ParamParser(configfile)
            paramsconf.readConfig()
            paramsdict = paramsconf.makeHierDict()
            self.updateUI(paramsdict)
        except:
            pass

    def onExport(self, event):
        """
        Export input parameters and output results into file (for next import or archive)
        """
        exportframe = ExportFrame(self, title = 'Export Parameters to File')
        exportframe.SetMinSize((500, 360))
        exportframe.Show()
        exportframe.Centre()

    def onExportJ(self, event):
        """
        Export input parameters and output results as a json string to file
        """
        pass
        
    def onAbout(self, event):
        # First we create and fill the info object
        info = wx.AboutDialogInfo()
        info.Name = "FEL Formula"
        info.Version = self.appversion
        info.Copyright = "(C) 2014-2016 Tong Zhang, SINAP, CAS"
        info.Description = wordwrap(
            "This program is designed for fast FEL physics calculations.\n"

            "It is designed by Python language, using wxPython as the GUI package.",
            350, wx.ClientDC(self))
        #info.WebSite = ("", "FEL Formula home page")
        info.Developers = [ "Tong Zhang <zhangtong@sinap.ac.cn>"]
        licenseText = "FEL Formula is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.\n" + "\nFEL Formula is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.\n" + "\nYou should have received a copy of the GNU General Public License along with FEL Formula; if not, write to the Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA"
        info.License = wordwrap(licenseText, 500, wx.ClientDC(self))

        # Then we call wx.AboutBox giving it that info object
        wx.AboutBox(info)

#------------------------------------------------------------------------#
    
    def updateUI(self, paramsdict):
        """
        update UI with import parameters from .conf file
        """
        # 02-electron_beam
        avgBeta      = paramsdict['02-electron_beam']['average_beta_function(m)']
        bunchCharge  = paramsdict['02-electron_beam']['bunch_charge(C)']
        beamEnergy   = paramsdict['02-electron_beam']['central_energy(MeV)']
        energySpread = paramsdict['02-electron_beam']['energy_spread']
        normEmit     = paramsdict['02-electron_beam']['normalized_emittance(m)']
        bunchShape   = paramsdict['02-electron_beam']['bunch_shape']
        peakCurrent  = paramsdict['02-electron_beam']['peak_current(A)']
        sigmar       = paramsdict['02-electron_beam']['transverse_beam_size(m)']
        sigma_z      = paramsdict['02-electron_beam']['bunch_length_z(um)']
        sigma_t      = paramsdict['02-electron_beam']['bunch_length_t(fs)']

        # 03-undulator
        unduLength   = paramsdict['03-undulator']['total_length(m)']
        unduPeriod   = paramsdict['03-undulator']['period_length(m)']
        peakField    = paramsdict['03-undulator']['peak_field(T)']
        gap          = paramsdict['03-undulator']['gap(mm)']
        K            = paramsdict['03-undulator']['K']
        au           = paramsdict['03-undulator']['au']
        utype        = paramsdict['03-undulator']['type']

        # 04-FEL_radiation
        FELwvlth     = paramsdict['04-FEL_radiation']['wavelength(m)']

        photonEnergy = paramsdict['04-FEL_radiation']['photon_energy(eV)']         
        rho1D        = paramsdict['04-FEL_radiation']['FEL_parameter_1D']          
        rho3D        = paramsdict['04-FEL_radiation']['FEL_parameter_3D']          
        Lg1D         = paramsdict['04-FEL_radiation']['gainlength_1D(m)']          
        Lg3D         = paramsdict['04-FEL_radiation']['gainlength_3D(m)']          
        Psat_MXie    = paramsdict['04-FEL_radiation']['saturation_power_MXie(W)']  
        Psat_SASE    = paramsdict['04-FEL_radiation']['saturation_power_SASE(W)']  
        Lgsat_SASE   = paramsdict['04-FEL_radiation']['saturation_length_SASE(m)'] 
        bw           = paramsdict['04-FEL_radiation']['bandwidth(%)']              
        pulseEnergy  = paramsdict['04-FEL_radiation']['pulse_energy(uJ)']          
        Pshot_SASE   = paramsdict['04-FEL_radiation']['shotnoise_power_SASE(W)']   
        ppp          = paramsdict['04-FEL_radiation']['photon_per_pulse']          
        Pexit        = paramsdict['04-FEL_radiation']['output_power(W)']           


        # set up value
        ## input
        self.b1tc1.SetValue(beamEnergy)
        self.b1tc2.SetValue(energySpread)
        self.b1tc3.SetValue(normEmit)
        self.b1tc4.SetValue(avgBeta)
        self.b1tc5.SetValue(peakCurrent)
        self.b1tc6.SetValue(unduPeriod)
        self.b1tc7.SetValue(FELwvlth)
        self.b1tc8.SetValue(bunchCharge)
        self.b1tc9.SetValue(unduLength)
        self.b1cb10.SetValue(bunchShape)
        self.b1cb11.SetValue(utype)

        ## output
        self.b2sb1vst1.SetLabel((peakField))
        self.b2sb1vst2.SetLabel((gap))
        self.b2sb1vst3.SetLabel((K))
        self.b2sb1vst4.SetLabel((au))
        self.b2sb1vst5.SetLabel((sigma_t))
        self.b2sb1vst6.SetLabel((sigma_z))
        self.b2sb1vst7.SetLabel((sigmar))
        self.b2sb2vst1.SetLabel((rho1D))
        self.b2sb2vst2.SetLabel((rho3D))
        self.b2sb2vst3.SetLabel((Lg1D))
        self.b2sb2vst4.SetLabel((Lg3D))
        self.b2sb2vst5.SetLabel((Psat_MXie))
        self.b2sb2vst6.SetLabel((Psat_SASE))
        self.b2sb2vst7.SetLabel((Lgsat_SASE))
        self.b2sb2vst8.SetLabel((photonEnergy))
        self.b2sb2vst9.SetLabel((bw))
        self.b2sb2vst12.SetLabel((Pshot_SASE))
        self.b2sb2vst10.SetLabel((pulseEnergy))
        self.b2sb2vst11.SetLabel((ppp))
        self.b2sb2vst13.SetLabel((Pexit))

#------------------------------------------------------------------------#
    
    def collectAllParams(self):
        # initial paramdict
        self.paramdict = {'00-info':{}, '01-facility':{}, '02-electron_beam':{},
                          '03-undulator':{}, '04-FEL_radiation':{}}
        # 02-electron_beam section
        ## input
        self.paramdict['02-electron_beam']['average_beta_function(m)'] = self.b1tc4.GetValue()
        self.paramdict['02-electron_beam']['bunch_charge(C)']          = self.b1tc8.GetValue()
        self.paramdict['02-electron_beam']['central_energy(MeV)']      = self.b1tc1.GetValue()
        self.paramdict['02-electron_beam']['energy_spread']            = self.b1tc2.GetValue()
        self.paramdict['02-electron_beam']['normalized_emittance(m)']  = self.b1tc3.GetValue()
        self.paramdict['02-electron_beam']['peak_current(A)']          = self.b1tc5.GetValue()
        self.paramdict['02-electron_beam']['bunch_shape']              = self.b1cb10.GetStringSelection()
        ## output
        self.paramdict['02-electron_beam']['transverse_beam_size(m)']  = self.b2sb1vst7.GetLabel()
        self.paramdict['02-electron_beam']['bunch_length_z(um)']       = self.b2sb1vst6.GetLabel()
        self.paramdict['02-electron_beam']['bunch_length_t(fs)']       = self.b2sb1vst5.GetLabel()
        
        # 03-undulator section
        ## input
        self.paramdict['03-undulator']['period_length(m)'] = self.b1tc6.GetValue()
        self.paramdict['03-undulator']['total_length(m)']  = self.b1tc9.GetValue()
        self.paramdict['03-undulator']['type']             = self.b1cb11.GetStringSelection()
        ## output
        self.paramdict['03-undulator']['peak_field(T)']    = self.b2sb1vst1.GetLabel()
        self.paramdict['03-undulator']['gap(mm)']          = self.b2sb1vst2.GetLabel()
        self.paramdict['03-undulator']['K']                = self.b2sb1vst3.GetLabel()
        self.paramdict['03-undulator']['au']               = self.b2sb1vst4.GetLabel()

        # 04-FEL_radiation section
        ## input
        self.paramdict['04-FEL_radiation']['wavelength(m)']             = self.b1tc7.GetValue()
        ## output
        self.paramdict['04-FEL_radiation']['photon_energy(eV)']         = self.b2sb2vst8.GetLabel()
        self.paramdict['04-FEL_radiation']['FEL_parameter_1D']          = self.b2sb2vst1.GetLabel()
        self.paramdict['04-FEL_radiation']['FEL_parameter_3D']          = self.b2sb2vst2.GetLabel()
        self.paramdict['04-FEL_radiation']['gainlength_1D(m)']          = self.b2sb2vst3.GetLabel()
        self.paramdict['04-FEL_radiation']['gainlength_3D(m)']          = self.b2sb2vst4.GetLabel()
        self.paramdict['04-FEL_radiation']['saturation_power_MXie(W)']  = self.b2sb2vst5.GetLabel()
        self.paramdict['04-FEL_radiation']['saturation_power_SASE(W)']  = self.b2sb2vst6.GetLabel()
        self.paramdict['04-FEL_radiation']['saturation_length_SASE(m)'] = self.b2sb2vst7.GetLabel()
        self.paramdict['04-FEL_radiation']['bandwidth(%)']              = self.b2sb2vst9.GetLabel()
        self.paramdict['04-FEL_radiation']['pulse_energy(uJ)']          = self.b2sb2vst10.GetLabel()
        self.paramdict['04-FEL_radiation']['shotnoise_power_SASE(W)']   = self.b2sb2vst12.GetLabel()
        self.paramdict['04-FEL_radiation']['photon_per_pulse']          = self.b2sb2vst11.GetLabel()
        self.paramdict['04-FEL_radiation']['output_power(W)']           = self.b2sb2vst13.GetLabel()

#------------------------------------------------------------------------#

    def createPanel(self):
        ## statictext result color
        resultcolor = 'red'
        
        ## staticboxsizer staticbox font and color
        sbfont = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        sbfont.SetPointSize(10)
        sbfont.SetWeight(wx.FONTWEIGHT_BOLD)
        sbcolor = 'MAGENTA'

        panel = wx.Panel(self, id = wx.ID_ANY)
        
        st0 = funutils.MyStaticText(panel, label = 'Cheat Sheet for FEL Physics', style = wx.ALIGN_CENTRE, fontcolor = 'blue', fontsize = 18, fontweight = wx.FONTWEIGHT_BOLD)

        sl1 = wx.StaticLine(panel, style = wx.LI_HORIZONTAL)

        sbox1 = wx.StaticBox(panel, id = wx.ID_ANY, 
                label = 'Beam Parameters')
        sbox2 = wx.StaticBox(panel, id = wx.ID_ANY,
                label = 'FEL Calculations')
        sbox3 = wx.StaticBox(panel, id = wx.ID_ANY,
                label = 'Operations')
        #sbox4 = wx.StaticBox(panel, id = wx.ID_ANY,
        #        label = 'Brief Guide')
        sbox1.SetFont(sbfont)
        sbox2.SetFont(sbfont)
        sbox3.SetFont(sbfont)
        #sbox4.SetFont(sbfont)
        sbox1.SetForegroundColour(sbcolor)
        sbox2.SetForegroundColour(sbcolor)
        sbox3.SetForegroundColour(sbcolor)
        #sbox4.SetForegroundColour(sbcolor)
        sbsizer1 = wx.StaticBoxSizer(sbox1, orient = wx.VERTICAL)
        sbsizer2 = wx.StaticBoxSizer(sbox2, orient = wx.VERTICAL)
        sbsizer3 = wx.StaticBoxSizer(sbox3, orient = wx.VERTICAL)
        #sbsizer4 = wx.StaticBoxSizer(sbox4, orient = wx.VERTICAL)

        ## sbsizer1: 'Beam Parameters'  StaticBoxSizer
        box1 = wx.FlexGridSizer(11, 2, 1, 40)

        b1st1 = wx.StaticText(panel, label = 'Beam Energy [MeV]',    style = wx.ALIGN_LEFT)
        b1st2 = wx.StaticText(panel, label = 'Energy Spread',        style = wx.ALIGN_LEFT)
        b1st3 = wx.StaticText(panel, label = 'Norm. Emittance [m]',  style = wx.ALIGN_LEFT)
        b1st4 = wx.StaticText(panel, label = 'Avg. Beta Func. [m]',  style = wx.ALIGN_LEFT)
        b1st5 = wx.StaticText(panel, label = 'Peak Current [A]',     style = wx.ALIGN_LEFT)
        b1st6 = wx.StaticText(panel, label = 'Undulator Period [m]', style = wx.ALIGN_LEFT)
        b1st7 = wx.StaticText(panel, label = 'FEL Wavelength [m]',   style = wx.ALIGN_LEFT)
        b1st8 = wx.StaticText(panel, label = 'Bunch Charge [C]',     style = wx.ALIGN_LEFT)
        b1st9 = wx.StaticText(panel, label = 'Undulator Length [m]', style = wx.ALIGN_LEFT)
        b1st10 = wx.StaticText(panel, label = 'Bunch Shape',         style = wx.ALIGN_LEFT)
        b1st11 = wx.StaticText(panel, label = 'Undulator Type',      style = wx.ALIGN_LEFT)

        self.b1tc1 = wx.TextCtrl(panel, id = ID_BEAM_ENERGY,   value = '150'   , style = wx.TE_PROCESS_ENTER)
        self.b1tc2 = wx.TextCtrl(panel, id = ID_ENERGY_SPREAD, value = '0.0001', style = wx.TE_PROCESS_ENTER)
        self.b1tc3 = wx.TextCtrl(panel, id = ID_NORM_EMIT,     value = '4e-6'  , style = wx.TE_PROCESS_ENTER)
        self.b1tc4 = wx.TextCtrl(panel, id = ID_AVG_BETA,      value = '4'     , style = wx.TE_PROCESS_ENTER)
        self.b1tc5 = wx.TextCtrl(panel, id = ID_PEAK_CURRENT,  value = '100'   , style = wx.TE_PROCESS_ENTER)
        self.b1tc6 = wx.TextCtrl(panel, id = ID_UNDU_PERIOD,   value = '0.025' , style = wx.TE_PROCESS_ENTER)
        self.b1tc7 = wx.TextCtrl(panel, id = ID_FEL_WVLTH,     value = '350e-9', style = wx.TE_PROCESS_ENTER)
        self.b1tc8 = wx.TextCtrl(panel, id = ID_BUNCH_CHARGE,  value = '0.2e-9', style = wx.TE_PROCESS_ENTER)
        self.b1tc9 = wx.TextCtrl(panel,                        value = '10',     style = wx.TE_PROCESS_ENTER)
        self.b1cb10 = wx.ComboBox(panel, value = 'gaussian', choices = ['gaussian', 'flattop'], style = wx.CB_READONLY)
        self.b1cb11 = wx.ComboBox(panel, value = 'planar',   choices = ['planar', 'helical'],   style = wx.CB_READONLY)

        box1.Add(b1st1,      proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT,  border = 10)
        box1.Add(self.b1tc1, proportion = 1, flag = wx.EXPAND | wx.RIGHT,                border = 10)
        box1.Add(b1st2,      proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT,  border = 10)
        box1.Add(self.b1tc2, proportion = 1, flag = wx.EXPAND | wx.RIGHT,                border = 10)
        box1.Add(b1st3,      proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT,  border = 10)
        box1.Add(self.b1tc3, proportion = 1, flag = wx.EXPAND | wx.RIGHT,                border = 10)
        box1.Add(b1st4,      proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT,  border = 10)
        box1.Add(self.b1tc4, proportion = 1, flag = wx.EXPAND | wx.RIGHT,                border = 10)
        box1.Add(b1st5,      proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT,  border = 10)
        box1.Add(self.b1tc5, proportion = 1, flag = wx.EXPAND | wx.RIGHT,                border = 10)
        box1.Add(b1st6,      proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT,  border = 10)
        box1.Add(self.b1tc6, proportion = 1, flag = wx.EXPAND | wx.RIGHT,                border = 10)
        box1.Add(b1st7,      proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT,  border = 10)
        box1.Add(self.b1tc7, proportion = 1, flag = wx.EXPAND | wx.RIGHT,                border = 10)
        box1.Add(b1st8,      proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT,  border = 10)
        box1.Add(self.b1tc8, proportion = 1, flag = wx.EXPAND | wx.RIGHT,                border = 10)
        box1.Add(b1st9,      proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT,  border = 10)
        box1.Add(self.b1tc9, proportion = 1, flag = wx.EXPAND | wx.RIGHT,                border = 10)
        box1.Add(b1st11,      proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        box1.Add(self.b1cb11, proportion = 1, flag = wx.EXPAND | wx.RIGHT,               border = 10)
        box1.Add(b1st10,      proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        box1.Add(self.b1cb10, proportion = 1, flag = wx.EXPAND | wx.RIGHT,               border = 10)

        box1.AddGrowableCol(1)

        sbsizer1.Add(box1, proportion = 1, flag = wx.ALIGN_CENTER | wx.EXPAND | wx.ALL, border = 10)

        ## sbsizer2: 'FEL Calculations' StaticBoxSizer

        ### undulator
        b2sb1 = wx.StaticBox(panel, id = wx.ID_ANY, label = 'Undulator and E-beam')
        b2sb1sizer = wx.StaticBoxSizer(b2sb1, orient = wx.VERTICAL)

        b2sb1st1 = wx.StaticText(panel, label = 'Field [T]:',    style = wx.ALIGN_LEFT)
        b2sb1st2 = wx.StaticText(panel, label = 'Gap [mm]:',     style = wx.ALIGN_LEFT)
        b2sb1st3 = wx.StaticText(panel, label = 'K:',            style = wx.ALIGN_LEFT)
        b2sb1st4 = wx.StaticText(panel, label = 'au:',           style = wx.ALIGN_LEFT)
        b2sb1st5 = wx.StaticText(panel, label = 'Bunch length (fs):', style = wx.ALIGN_LEFT)
        b2sb1st6 = wx.StaticText(panel, label = 'Bunch length (um):', style = wx.ALIGN_LEFT)
        b2sb1st5_note = funutils.MyStaticText(panel, label = 'gaussian: rms width', style = wx.ALIGN_LEFT, fontcolor = 'grey')
        b2sb1st6_note = funutils.MyStaticText(panel, label = 'flattop: full width', style = wx.ALIGN_LEFT, fontcolor = 'grey')
        b2sb1st7 = wx.StaticText(panel, label = 'Beam size (um):',    style = wx.ALIGN_LEFT)

        self.b2sb1vst1 = funutils.MyStaticText(panel, label = '0.720', style = wx.ALIGN_LEFT, fontcolor = resultcolor)
        self.b2sb1vst2 = funutils.MyStaticText(panel, label = '7.801', style = wx.ALIGN_LEFT, fontcolor = resultcolor)
        self.b2sb1vst3 = funutils.MyStaticText(panel, label = '1.681', style = wx.ALIGN_LEFT, fontcolor = resultcolor)
        self.b2sb1vst4 = funutils.MyStaticText(panel, label = '1.189', style = wx.ALIGN_LEFT, fontcolor = resultcolor)
        self.b2sb1vst5 = funutils.MyStaticText(panel, label = '797.9', style = wx.ALIGN_LEFT, fontcolor = resultcolor)
        self.b2sb1vst6 = funutils.MyStaticText(panel, label = '239.4', style = wx.ALIGN_LEFT, fontcolor = resultcolor)
        self.b2sb1vst7 = funutils.MyStaticText(panel, label = '233.5', style = wx.ALIGN_LEFT, fontcolor = resultcolor)
        
        b2sb1fgs = wx.GridBagSizer(10, 4)
        b2sb1fgs.Add(b2sb1st1,       pos = (0, 0), span = (1, 1), flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb1fgs.Add(self.b2sb1vst1, pos = (0, 1), span = (1, 1), flag = wx.EXPAND | wx.RIGHT, border = 20)
        b2sb1fgs.Add(b2sb1st2,       pos = (0, 2), span = (1, 1), flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb1fgs.Add(self.b2sb1vst2, pos = (0, 3), span = (1, 1), flag = wx.EXPAND | wx.RIGHT, border = 20)
        b2sb1fgs.Add(b2sb1st3,       pos = (1, 0), span = (1, 1), flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb1fgs.Add(self.b2sb1vst3, pos = (1, 1), span = (1, 1), flag = wx.EXPAND | wx.RIGHT, border = 20)
        b2sb1fgs.Add(b2sb1st4,       pos = (1, 2), span = (1, 1), flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb1fgs.Add(self.b2sb1vst4, pos = (1, 3), span = (1, 1), flag = wx.EXPAND | wx.RIGHT, border = 20)
        b2sb1fgs.Add(b2sb1st5,       pos = (2, 0), span = (1, 1), flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb1fgs.Add(self.b2sb1vst5, pos = (2, 1), span = (1, 1), flag = wx.EXPAND | wx.RIGHT, border = 20)
        b2sb1fgs.Add(b2sb1st5_note,  pos = (2, 2), span = (1, 2), flag = wx.EXPAND | wx.RIGHT, border = 20)
        b2sb1fgs.Add(b2sb1st6,       pos = (3, 0), span = (1, 1), flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb1fgs.Add(self.b2sb1vst6, pos = (3, 1), span = (1, 1), flag = wx.EXPAND | wx.RIGHT, border = 20)
        b2sb1fgs.Add(b2sb1st6_note,  pos = (3, 2), span = (1, 2), flag = wx.EXPAND | wx.RIGHT, border = 20)
        b2sb1fgs.Add(b2sb1st7,       pos = (4, 0), span = (1, 1), flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb1fgs.Add(self.b2sb1vst7, pos = (4, 1), span = (1, 1), flag = wx.EXPAND | wx.RIGHT, border = 20)
        b2sb1fgs.AddGrowableCol(1)
        b2sb1fgs.AddGrowableCol(3)
        
        b2sb1sizer.Add(b2sb1fgs, proportion = 1, flag = wx.ALIGN_CENTER | wx.EXPAND | wx.ALL, border = 10)

        ### radiation
        b2sb2 = wx.StaticBox(panel, id = wx.ID_ANY, label = 'FEL Radiation')
        b2sb2sizer = wx.StaticBoxSizer(b2sb2, orient = wx.VERTICAL)
        b2sb2st1 = wx.StaticText(panel, label = 'FEL parameter (1D):',       style = wx.ALIGN_LEFT)
        b2sb2st2 = wx.StaticText(panel, label = 'FEL parameter (3D):',       style = wx.ALIGN_LEFT)
        b2sb2st3 = wx.StaticText(panel, label = 'FEL gainlength (1D) [m]:',  style = wx.ALIGN_LEFT)
        b2sb2st4 = wx.StaticText(panel, label = 'FEL gainlength (3D) [m]:',  style = wx.ALIGN_LEFT)
        b2sb2st5 = wx.StaticText(panel, label = 'FEL saturation power (MXie) [W]:',  style = wx.ALIGN_LEFT)
        b2sb2st6 = wx.StaticText(panel, label = 'FEL saturation power (SASE) [W]:',  style = wx.ALIGN_LEFT)
        b2sb2st13= wx.StaticText(panel, label = 'FEL output power (SASE) [W]:',      style = wx.ALIGN_LEFT)
        b2sb2st7 = wx.StaticText(panel, label = 'FEL saturation length (SASE) [m]:', style = wx.ALIGN_LEFT)
        b2sb2st12= wx.StaticText(panel, label = 'FEL shotnoise power (SASE) [W]:',   style = wx.ALIGN_LEFT)
        b2sb2st8 = wx.StaticText(panel, label = 'FEL photon energy [eV]:',           style = wx.ALIGN_LEFT)
        b2sb2st9 = wx.StaticText(panel, label = 'FEL bandwidth [%]:',                style = wx.ALIGN_LEFT)
        b2sb2st10= wx.StaticText(panel, label = 'FEL pulse energy [uJ]:',            style = wx.ALIGN_LEFT)
        b2sb2st11= wx.StaticText(panel, label = 'FEL photons per pulse (saturation):',  style = wx.ALIGN_LEFT)

        self.b2sb2vst1 = funutils.MyStaticText(panel, label = '2.022e-03', style = wx.ALIGN_LEFT, fontcolor = resultcolor)
        self.b2sb2vst2 = funutils.MyStaticText(panel, label = '1.622e-03', style = wx.ALIGN_LEFT, fontcolor = resultcolor)
        self.b2sb2vst3 = funutils.MyStaticText(panel, label = '0.568',     style = wx.ALIGN_LEFT, fontcolor = resultcolor)
        self.b2sb2vst4 = funutils.MyStaticText(panel, label = '0.708',     style = wx.ALIGN_LEFT, fontcolor = resultcolor)
        self.b2sb2vst5 = funutils.MyStaticText(panel, label = '3.121e+07', style = wx.ALIGN_LEFT, fontcolor = resultcolor)
        self.b2sb2vst6 = funutils.MyStaticText(panel, label = '3.932e+07', style = wx.ALIGN_LEFT, fontcolor = resultcolor)
        self.b2sb2vst7 = funutils.MyStaticText(panel, label = '15.08',     style = wx.ALIGN_LEFT, fontcolor = resultcolor)
        self.b2sb2vst8 = funutils.MyStaticText(panel, label = '3.5',       style = wx.ALIGN_LEFT, fontcolor = resultcolor)
        self.b2sb2vst9 = funutils.MyStaticText(panel, label = '0.46',      style = wx.ALIGN_LEFT, fontcolor = resultcolor)
        self.b2sb2vst10= funutils.MyStaticText(panel, label = '0.061',     style = wx.ALIGN_LEFT, fontcolor = resultcolor)
        self.b2sb2vst11= funutils.MyStaticText(panel, label = '1.07e+11',  style = wx.ALIGN_LEFT, fontcolor = resultcolor)
        self.b2sb2vst12= funutils.MyStaticText(panel, label = '0.2',       style = wx.ALIGN_LEFT, fontcolor = resultcolor)
        self.b2sb2vst13= funutils.MyStaticText(panel, label = '3.034e+04', style = wx.ALIGN_LEFT, fontcolor = resultcolor)
        
        b2sb2fgs = wx.FlexGridSizer(13, 2, 10, 40)
        b2sb2fgs.Add(b2sb2st1,       proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb2fgs.Add(self.b2sb2vst1, proportion = 1, flag = wx.EXPAND | wx.RIGHT,               border = 10)
        b2sb2fgs.Add(b2sb2st2,       proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb2fgs.Add(self.b2sb2vst2, proportion = 1, flag = wx.EXPAND | wx.RIGHT,               border = 10)
        b2sb2fgs.Add(b2sb2st3,       proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb2fgs.Add(self.b2sb2vst3, proportion = 1, flag = wx.EXPAND | wx.RIGHT,               border = 10)
        b2sb2fgs.Add(b2sb2st4,       proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb2fgs.Add(self.b2sb2vst4, proportion = 1, flag = wx.EXPAND | wx.RIGHT,               border = 10)
        b2sb2fgs.Add(b2sb2st5,       proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb2fgs.Add(self.b2sb2vst5, proportion = 1, flag = wx.EXPAND | wx.RIGHT,               border = 10)
        b2sb2fgs.Add(b2sb2st6,       proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb2fgs.Add(self.b2sb2vst6, proportion = 1, flag = wx.EXPAND | wx.RIGHT,               border = 10)
        b2sb2fgs.Add(b2sb2st13,      proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb2fgs.Add(self.b2sb2vst13,proportion = 1, flag = wx.EXPAND | wx.RIGHT,               border = 10)
        b2sb2fgs.Add(b2sb2st7,       proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb2fgs.Add(self.b2sb2vst7, proportion = 1, flag = wx.EXPAND | wx.RIGHT,               border = 10)
        b2sb2fgs.Add(b2sb2st12,      proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb2fgs.Add(self.b2sb2vst12,proportion = 1, flag = wx.EXPAND | wx.RIGHT,               border = 10)
        b2sb2fgs.Add(b2sb2st8,       proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb2fgs.Add(self.b2sb2vst8, proportion = 1, flag = wx.EXPAND | wx.RIGHT,               border = 10)
        b2sb2fgs.Add(b2sb2st9,       proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb2fgs.Add(self.b2sb2vst9, proportion = 1, flag = wx.EXPAND | wx.RIGHT,               border = 10)
        b2sb2fgs.Add(b2sb2st10,      proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb2fgs.Add(self.b2sb2vst10,proportion = 1, flag = wx.EXPAND | wx.RIGHT,               border = 10)
        b2sb2fgs.Add(b2sb2st11,      proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        b2sb2fgs.Add(self.b2sb2vst11,proportion = 1, flag = wx.EXPAND | wx.RIGHT,               border = 10)
        b2sb2fgs.AddGrowableCol(1)

        b2sb2sizer.Add(b2sb2fgs, proportion = 1, flag = wx.ALIGN_CENTER | wx.EXPAND | wx.ALL, border = 10)

        sbsizer2.Add(b2sb1sizer, proportion = 0, flag = wx.ALIGN_LEFT | wx.EXPAND | wx.ALL, border = 10)
        sbsizer2.Add(b2sb2sizer, proportion = 1, flag = wx.ALIGN_LEFT | wx.EXPAND | wx.ALL, border = 10)
        
        ## sbsizer3: 'Operations'        StaticBoxSizer
        b3sb1 = wx.StaticBox(panel, id = wx.ID_ANY, label = 'Scan Control')
        b3sb1sizer = wx.StaticBoxSizer(b3sb1, orient = wx.VERTICAL)
        
        self.chkbox31 = wx.CheckBox(panel, id = ID_SCANFLAG, label = 'Enable Scan')
        self.combobox31 = wx.ComboBox(panel, id = ID_SCANPARM, value = 'Beam Energy', 
                choices = ['Beam Energy','Energy Spread', 
                           'Norm. Emittance', 'Peak Current', 
                           'Undulator Period', 'FEL Wavelength',
                           'Avg. Beta Func.', 'Bunch Charge'],
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
        scanfgs = wx.FlexGridSizer(2, 3, 2, 4)
        scanfgs.Add(self.sminst, proportion = 1, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT, border = 6)
        scanfgs.Add(self.smaxst, proportion = 1, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, border = 6)
        scanfgs.Add(self.snumst, proportion = 1, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.RIGHT, border = 6)
        scanfgs.Add(self.smintc, proportion = 1, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT, border = 6)
        scanfgs.Add(self.smaxtc, proportion = 1, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, border = 6)
        scanfgs.Add(self.snumtc, proportion = 1, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.RIGHT, border = 6)
        scansbsizer.Add(scanfgs, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border = 8)
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
        self.calcbtn = wx.Button(panel ,id = ID_CALCBTN, label = '&Calculate', size = (104, 44))
        self.exitbtn = wx.Button(panel ,id = ID_EXITBTN, label = 'E&xit',      size = (104, 44))
        self.plotbtn = wx.Button(panel, id = ID_PLOTBTN, label = 'Show &Plot', size = (104, 44))
        self.plotbtn.Disable()

        cmdgbs.Add(self.calcbtn, pos = (0, 0), span = (1, 1), flag = wx.ALIGN_CENTER | wx.LEFT, border = 10)
        cmdgbs.Add(self.plotbtn, pos = (0, 1), span = (1, 1), flag = wx.ALIGN_CENTER)
        cmdgbs.Add(self.exitbtn, pos = (0, 2), span = (1, 1), flag = wx.ALIGN_CENTER | wx.RIGHT, border = 10)
        cmdgbs.AddGrowableCol(1)

        b3sb2sizer.Add(cmdgbs, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border = 10)

        sbsizer3.Add(b3sb1sizer, proportion = 1, flag = wx.ALIGN_CENTER | wx.EXPAND | wx.ALL, border = 10)
        sbsizer3.Add(b3sb2sizer, proportion = 0, flag = wx.ALIGN_CENTER | wx.EXPAND | wx.ALL, border = 10)
        
        # set 4 sbsizers and title with one staticline
        overallbox = wx.BoxSizer(wx.VERTICAL)
        leftarightbox = wx.BoxSizer(wx.HORIZONTAL)
        leftbox    = wx.BoxSizer(wx.VERTICAL)
        rightbox   = wx.BoxSizer(wx.VERTICAL)

        leftbox.Add(sbsizer1,  proportion = 1, flag = wx.EXPAND | wx.ALL, border = 10)
        leftbox.Add(sbsizer3,  proportion = 0, flag = wx.EXPAND | wx.ALL, border = 10)
        rightbox.Add(sbsizer2, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 10)
        leftarightbox.Add(leftbox,  proportion = 1, flag = wx.EXPAND)
        leftarightbox.Add(rightbox, proportion = 1, flag = wx.EXPAND)

        overallbox.Add(st0, proportion = 0, flag = wx.ALIGN_CENTER | wx.ALL, border = 10)
        overallbox.Add(sl1, proportion = 0, flag = wx.EXPAND)
        overallbox.Add(leftarightbox, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 0)

        panel.SetSizer(overallbox)
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
        self.Bind(wx.EVT_TEXT_ENTER, self.onTextEnter,  id = ID_BUNCH_CHARGE )
        self.Bind(wx.EVT_TEXT_ENTER, self.onTextEnter,  id = ID_SCAN_MIN     )
        self.Bind(wx.EVT_TEXT_ENTER, self.onTextEnter,  id = ID_SCAN_MAX     )
        self.Bind(wx.EVT_TEXT_ENTER, self.onTextEnter,  id = ID_SCAN_NUM     )
        self.Bind(wx.EVT_CHECKBOX,   self.onEnableScan, id = ID_SCANFLAG     )
        self.Bind(wx.EVT_COMBOBOX,   self.onSetInitalScanRange, id = ID_SCANPARM)
        self.Bind(wx.EVT_COMBOBOX,   self.onCalc, self.b1cb11)
        self.Bind(wx.EVT_COMBOBOX,   self.onCalc, self.b1cb10)

#------------------------------------------------------------------------#

    def onCalc(self, event):
        beamEnergy   = float(self.b1tc1.GetValue())
        energySpread = float(self.b1tc2.GetValue())
        normEmit     = float(self.b1tc3.GetValue())
        avgBeta      = float(self.b1tc4.GetValue())
        peakCurrent  = float(self.b1tc5.GetValue())
        unduPeriod   = float(self.b1tc6.GetValue())
        FELwvlth     = float(self.b1tc7.GetValue())
        bunchCharge  = float(self.b1tc8.GetValue())
        unduLength   = float(self.b1tc9.GetValue())
        bunchShape   = self.b1cb10.GetStringSelection()
        utype        = self.b1cb11.GetStringSelection()
        
        if not self.chkbox31.IsChecked():
            instFEL = felbase.FELcalc(beamEnergy,
                                      energySpread,
                                      unduPeriod,
                                      avgBeta,
                                      FELwvlth,
                                      normEmit,
                                      peakCurrent,
                                      bunchCharge,
                                      unduLength,
                                      bunchShape,
                                      utype)
            result = instFEL.onFELAnalyse()
            self.b2sb1vst1.SetLabel('%.3f' % (result['03-Bu']))
            self.b2sb1vst2.SetLabel('%.3f' % (result['04-gap'][0]))
            self.b2sb1vst3.SetLabel('%.3f' % (result['02-K']))
            self.b2sb1vst4.SetLabel('%.3f' % (result['01-au']))
            self.b2sb1vst5.SetLabel('%.1f' % (result['14-sigmat']))
            self.b2sb1vst6.SetLabel('%.1f' % (result['14-sigmat']*0.3))
            self.b2sb1vst7.SetLabel('%.1f' % (result['13-sigmar']))

            self.b2sb2vst1.SetLabel('%.3e' % (result['05-rho1D']))
            self.b2sb2vst2.SetLabel('%.3e' % (result['06-rho3D']))
            self.b2sb2vst3.SetLabel('%.3f' % (result['07-Lg1D']))
            self.b2sb2vst4.SetLabel('%.3f' % (result['08-Lg3D']))
            self.b2sb2vst5.SetLabel('%.3e' % (result['09-Psat']))
            self.b2sb2vst6.SetLabel('%.3e' % (result['11-Pss']))
            self.b2sb2vst7.SetLabel('%.2f' % (result['12-Lsat']))
            self.b2sb2vst8.SetLabel('%.2g' % (result['16-PhotonEnergy']))
            self.b2sb2vst9.SetLabel('%.2f' % (result['15-bandWidth']))
            self.b2sb2vst12.SetLabel('%.2g' % (result['10-Pshot']))

            Psat = result['11-Pss']
            # power, power energy, photon per pulse at exit of undulator
            Pexit = 1.0/9.0*result['10-Pshot']*np.exp(min(unduLength, result['12-Lsat'])/result['08-Lg3D'])
            Wexit = result['17-PulseEnergy']/Psat*Pexit
            Nexit = result['18-PhotonPerPulse']/Psat*Pexit

            self.b2sb2vst10.SetLabel('%.2g' % (Wexit))
            self.b2sb2vst11.SetLabel('%.2e' % (Nexit))
            self.b2sb2vst13.SetLabel('%.3e' % (Pexit))
            
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
            elif scanparam == u'Bunch Charge':
                bunchCharge = np.linspace(scanmin,scanmax,scanpoint)
                self.scanX  = bunchCharge
            else:
                print('Scan parameters ERROR!')

            instFEL = felbase.FELcalc(beamEnergy,
                                      energySpread,
                                      unduPeriod,
                                      avgBeta,
                                      FELwvlth,
                                      normEmit,
                                      peakCurrent,
                                      bunchCharge,
                                      unduLength,
                                      bunchShape,
                                      utype)
            self.result = instFEL.onFELAnalyse()
            
#------------------------------------------------------------------------#
    
    def onSetInitalScanRange(self, event):
        scanparam = event.GetEventObject().GetStringSelection()
        if scanparam == u'Beam Energy':
            sval0 = float(self.b1tc1.GetValue())
        elif scanparam == u'Energy Spread':
            sval0 = float(self.b1tc2.GetValue())
        elif scanparam == u'Norm. Emittance':
            sval0 = float(self.b1tc3.GetValue())
        elif scanparam == u'Peak Current':
            sval0 = float(self.b1tc5.GetValue())
        elif scanparam == u'Undulator Period':
            sval0 = float(self.b1tc6.GetValue())
        elif scanparam == u'FEL Wavelength':
            sval0 = float(self.b1tc7.GetValue())
        elif scanparam == u'Avg. Beta Func.':
            sval0 = float(self.b1tc4.GetValue())
        elif scanparam == u'Bunch Charge':
            sval0 = float(self.b1tc8.GetValue())

        vmin, vmax = sval0*0.7, sval0*1.3
        self.smintc.SetValue('%.3e' % vmin)
        self.smaxtc.SetValue('%.3e' % vmax)
        

#------------------------------------------------------------------------#

    def onPlot(self, event):
        self.plotframe = PlotFrame(self, title = 'Scan Data Visualization', 
                size = (780, 700))
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

class ExportFrame(wx.Frame):
    def __init__(self, parent, title, **kwargs):
        super(self.__class__, self).__init__(parent = parent,
                id = wx.ID_ANY, title = title, **kwargs)
        self.parent = parent
        self.InitUI()

    def InitUI(self):

        ##
        usernamepath = os.path.expanduser('~')
        username = os.path.split(usernamepath)[-1]
        ##

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        ##
        filepath_st      = funutils.MyStaticText(panel, label = u'Save To', style = wx.ALIGN_LEFT)
        self.filepath_tc = funutils.MyTextCtrl(panel, value = os.path.join(os.getcwd(), 'fel.conf'), style = wx.CB_READONLY)
        filepath_btn     = wx.Button(panel, label = 'Browse')

        hbox_path = wx.BoxSizer(wx.HORIZONTAL)
        hbox_path.Add(filepath_st,      proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.TOP, border = 4)
        hbox_path.Add(self.filepath_tc, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT, border = 4)
        hbox_path.Add(filepath_btn,     proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.TOP, border = 4)
        ##
        
        ##
        export_btn = wx.Button(panel, label = 'Export')
        cancel_btn = wx.Button(panel, label = 'Cancel')

        hbox_cmd = wx.BoxSizer(wx.HORIZONTAL)
        hbox_cmd.Add(cancel_btn, proportion = 0, flag = wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, border = 6)
        hbox_cmd.Add(export_btn, proportion = 0, flag = wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, border = 6)
        ##

        ##
        infosb = wx.StaticBox(panel, label = 'Additional Information')
        infosbsizer = wx.StaticBoxSizer(infosb, orient = wx.VERTICAL)

        author_st                    = funutils.MyStaticText(panel, label = u'Author', style = wx.ALIGN_LEFT)
        self.author_tc               = funutils.MyTextCtrl(panel, value = username)
        facility_st                  = funutils.MyStaticText(panel, label = u'FACILITY INFO', style = wx.ALIGN_LEFT, fontcolor='blue')
        facility_name_st             = funutils.MyStaticText(panel, label = u'Name',        style = wx.ALIGN_LEFT)
        self.facility_name_tc        = funutils.MyTextCtrl(panel, value = u'')
        facility_country_st          = funutils.MyStaticText(panel, label = u'Country',     style = wx.ALIGN_LEFT)
        self.facility_country_tc     = funutils.MyTextCtrl(panel, value = u'')
        facility_affiliation_st      = funutils.MyStaticText(panel, label = u'Affiliation', style = wx.ALIGN_LEFT)
        self.facility_affiliation_tc = funutils.MyTextCtrl(panel, value = u'')
        note_st      = funutils.MyStaticText(panel, label = u'Note', style = wx.ALIGN_LEFT)
        self.note_tc = funutils.MyTextCtrl(panel, value = u'', style = wx.TE_MULTILINE)
        
        gbs = wx.GridBagSizer(4, 4)

        gbs.Add(author_st,      pos = (0, 0), span = (1, 1), flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 8)
        gbs.Add(self.author_tc, pos = (0, 1), span = (1, 2), flag = wx.EXPAND | wx.LEFT | wx.RIGHT, border = 8)

        gbs.Add(facility_st,                  pos = (1, 0), span = (1, 1), flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.ALIGN_LEFT, border = 8)
        gbs.Add(facility_name_st,             pos = (2, 0), span = (1, 1), flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 8)
        gbs.Add(self.facility_name_tc,        pos = (2, 1), span = (1, 2), flag = wx.EXPAND | wx.LEFT | wx.RIGHT, border = 8)
        gbs.Add(facility_country_st,          pos = (3, 0), span = (1, 1), flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 8)
        gbs.Add(self.facility_country_tc,     pos = (3, 1), span = (1, 2), flag = wx.EXPAND | wx.LEFT | wx.RIGHT, border = 8)
        gbs.Add(facility_affiliation_st,      pos = (4, 0), span = (1, 1), flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 8)
        gbs.Add(self.facility_affiliation_tc, pos = (4, 1), span = (1, 2), flag = wx.EXPAND | wx.LEFT | wx.RIGHT, border = 8)

        gbs.Add(note_st,                      pos = (5, 0), span = (1, 1), flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 8)
        gbs.Add(self.note_tc,                 pos = (5, 1), span = (4, 2), flag = wx.EXPAND | wx.LEFT | wx.RIGHT, border = 8)

        gbs.AddGrowableCol(1)
        infosbsizer.Add(gbs, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 10) 
        ##
        
        ##
        vbox.Add(hbox_path,   proportion = 0, flag = wx.EXPAND | wx.ALL, border = 6)
        vbox.Add(infosbsizer, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 8)
        vbox.Add(hbox_cmd,    proportion = 0, flag = wx.ALIGN_RIGHT | wx.ALL, border = 4)

        panel.SetSizer(vbox)
        osizer = wx.BoxSizer(wx.HORIZONTAL)
        osizer.Add(panel, proportion = 1, flag = wx.EXPAND)
        self.SetSizerAndFit(osizer)
        ##

        self.Bind(wx.EVT_BUTTON, self.onChoose, filepath_btn)
        self.Bind(wx.EVT_BUTTON, self.onExport, export_btn)
        self.Bind(wx.EVT_BUTTON, self.onCancel, cancel_btn)

    def onChoose(self, event):
        filename = funutils.getFileToSave(self, ext = 'conf')
        self.filepath_tc.SetValue(filename)

    def onExport(self, event):
        try:
            # choose configfile
            configfile = self.filepath_tc.GetValue()

            # collect all the intput and output parameters into self.paramdict
            self.parent.collectAllParams() 

            self.parent.paramdict['00-info']['author']          = self.author_tc.GetValue()
            self.parent.paramdict['00-info']['created_time']    = time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime())
            self.parent.paramdict['00-info']['note']            = self.note_tc.GetValue()
            self.parent.paramdict['01-facility']['name']        = self.facility_name_tc.GetValue()
            self.parent.paramdict['01-facility']['country']     = self.facility_country_tc.GetValue()
            self.parent.paramdict['01-facility']['affiliation'] = self.facility_affiliation_tc.GetValue()

            # save to configfile
            paramsconf = parseutils.ParamParser()
            paramsconf.dumpDictToConfig(self.parent.paramdict, configfile)
            
            # show successful dialog
            msg = "All parameters are exported to " + configfile + '.'
            dlg = wx.MessageDialog(self, message = msg, caption = u'Export Succeed',
                    style = wx.OK | wx.CANCEL | wx.CENTRE)
            if dlg.ShowModal() == wx.ID_OK:
                dlg.Destroy()
        except:
            msg = "Export Error"
            dlg = wx.MessageDialog(self, message = msg, caption = u'Export Failed',
                    style = wx.OK | wx.CANCEL | wx.CENTRE | wx.ICON_ERROR)
            if dlg.ShowModal() == wx.ID_OK:
                dlg.Destroy()
        self.Close(True)

    def onCancel(self, event):
        self.Close(True)


#------------------------------------------------------------------------#

class InfoFrame(wx.Frame):
    def __init__(self, parent, title, **kwargs):
        super(self.__class__, self).__init__(parent = parent,
                id = wx.ID_ANY, title = title, **kwargs)
        self.parent = parent
        self.InitUI()

    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        aboutstring = "How to use this application:\n" + \
                      "1: Input the parameters in 'Beam Parameters' panel;\n" + \
                      "2: Push 'Calculate' button to show the calculated results;\n" + \
                      "3: If 'Enable Scan' is checked, scan function is enabled;\n" + \
                      " 3.1: Choose the scan parameter and the scan range;\n" + \
                      " 3.2: Push 'Calculate' button, then 'Show Plot' to check plot;\n" + \
                      " 3.3: In 'Scan Data Visualization' frame, Ctrl+S can save figure\n" + \
                      "      into '.jpg' format or use the toolbar at the bottom;\n" + \
                      "      use Ctrl+Shift+S to save scan data as guided;\n" + \
                      "4: Import and Export in File menu, use as how it guides."
        aboutinfo = funutils.MyStaticText(panel, label = aboutstring, style = wx.ALIGN_LEFT | wx.TE_MULTILINE)
        vbox.Add(aboutinfo, flag = wx.ALIGN_CENTER | wx.ALL, border = 10)
        panel.SetSizer(vbox)
        osizer = wx.BoxSizer(wx.HORIZONTAL)
        osizer.Add(panel, proportion = 1, flag = wx.EXPAND)
        self.SetSizerAndFit(osizer)
 
#------------------------------------------------------------------------#

class LogFrame(wx.Frame):
    def __init__(self, parent, title, **kwargs):
        super(self.__class__, self).__init__(parent = parent,
                id = wx.ID_ANY, title = title, **kwargs)
        self.parent = parent
        self.InitUI()

    def InitUI(self):
        panel = wx.Panel(self)
        v14_btn = wx.Button(panel, label = 'Version 1.4')
        v13_btn = wx.Button(panel, label = 'Version 1.3')
        v12_btn = wx.Button(panel, label = 'Version 1.2')
        v11_btn = wx.Button(panel, label = 'Version 1.1')
        v14_st  = funutils.MyStaticText(panel, label = u'Released: 2016-05-19', fontcolor = 'blue')
        v13_st  = funutils.MyStaticText(panel, label = u'Released: 2015-11-03', fontcolor = 'blue')
        v12_st  = funutils.MyStaticText(panel, label = u'Released: 2015-09-18', fontcolor = 'blue')
        v11_st  = funutils.MyStaticText(panel, label = u'Released: 2015-09-11', fontcolor = 'blue')

        gs = wx.GridBagSizer(8, 4)
        gs.Add(v14_btn, pos = (0, 0), span = (1, 1), flag = wx.EXPAND | wx.LEFT | wx.RIGHT, border = 10)
        gs.Add(v14_st,  pos = (0, 1), span = (1, 2), flag = wx.ALIGN_CENTER | wx.LEFT, border = 10)
        gs.Add(v13_btn, pos = (1, 0), span = (1, 1), flag = wx.EXPAND | wx.LEFT | wx.RIGHT, border = 10)
        gs.Add(v13_st,  pos = (1, 1), span = (1, 2), flag = wx.ALIGN_CENTER | wx.LEFT, border = 10)
        gs.Add(v12_btn, pos = (2, 0), span = (1, 1), flag = wx.EXPAND | wx.LEFT | wx.RIGHT, border = 10)
        gs.Add(v12_st,  pos = (2, 1), span = (1, 2), flag = wx.ALIGN_CENTER | wx.LEFT, border = 10)
        gs.Add(v11_btn, pos = (3, 0), span = (1, 1), flag = wx.EXPAND | wx.LEFT | wx.RIGHT, border = 10)
        gs.Add(v11_st,  pos = (3, 1), span = (1, 2), flag = wx.ALIGN_CENTER | wx.LEFT, border = 10)
        gs.AddGrowableCol(1)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(gs, proportion = 0, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.TOP, border = 20)
        panel.SetSizer(vbox)
        
        self.msg_v14 = "1: Add save data menuitem for Scan Data Visualization frame, support 'txt' and 'hdf5'."
        self.msg_v13 = "1: Add undulator type parameter;\n" + \
                       "2: Add callbacks to undulator type/bunch shape switch."
        self.msg_v12 = "1: Add more input parameters and more output results;\n" + \
                       "2: Implement 'Import' and 'Export' features under 'File' menu;\n" + \
                       "3: Imported or exported files are with ext of '.conf', could be viewd or archived;\n" + \
                       "4: Update 'Scan Data Visulization' frame to support more parameters;\n" + \
                       "5: Support save figure in 'Scan Data Visulization' frame;\n" + \
                       "5.1: Type Ctrl+S to save figure as .jpg format;\n" +\
                       "5.2: Use the save button in the bottom toolbar to save as other formats."

        self.msg_v11 = "1: Calculate FEL radiation by applying analytical formulae;\n" + \
                       "2: Scan results visulization."
                

        self.Bind(wx.EVT_BUTTON, self.onShowCLog, v14_btn)
        self.Bind(wx.EVT_BUTTON, self.onShowCLog, v13_btn)
        self.Bind(wx.EVT_BUTTON, self.onShowCLog, v12_btn)
        self.Bind(wx.EVT_BUTTON, self.onShowCLog, v11_btn)

    def onShowCLog(self, event):
        label = event.GetEventObject().GetLabel()
        if label == 'Version 1.4':
            msg = self.msg_v14
            caption = 'V1.4 Change Log'
        elif label == 'Version 1.3':
            msg = self.msg_v13
            caption = 'V1.3 Change Log'
        elif label == 'Version 1.2':
            msg = self.msg_v12
            caption = 'V1.2 Change Log'
        elif label == 'Version 1.1':
            msg = self.msg_v11
            caption = 'V1.1 Change Log'

        dlg = wx.lib.dialogs.ScrolledMessageDialog(self, msg, caption)
        dlg.ShowModal()
#------------------------------------------------------------------------#

class PlotFrame(wx.Frame):

#------------------------------------------------------------------------#

    def __init__(self, parent, title, **kwargs):
        super(self.__class__, self).__init__(parent = parent,
                id = wx.ID_ANY, title = title, **kwargs)
        self.parent = parent
        self.InitUI()
        self.setColor()
    
#------------------------------------------------------------------------#
    
    def setColor(self, rgbtuple = None):
        if rgbtuple is None:
            rgbtuple = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE).Get()
        
        clr = [c/255. for c in rgbtuple]
        self.fig.set_facecolor(clr)
        self.fig.set_edgecolor(clr)
        self.canvas.SetBackgroundColour(wx.Colour(*rgbtuple))

#------------------------------------------------------------------------#

    def InitUI(self):
        self.createMenu ()
        self.createPanel()
        self.createToolbar()

#------------------------------------------------------------------------#

    def createMenu(self):
        self.menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        savefigItem  = fileMenu.Append(wx.ID_SAVE, '&Save plot\tCtrl-S', 'Save plot figure to file')
        savedataItem = fileMenu.Append(wx.ID_ANY,  'Save data\tCtrl-Shift-S', 'Save plot data to file')
        fileMenu.AppendSeparator()
        exitItem = fileMenu.Append(wx.ID_EXIT, 'E&xit\tCtrl-W', 'Exit')
        self.Bind(wx.EVT_MENU, self.onSavePlot, id = wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.onExitPlot, id = wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.onSaveData, id = savedataItem.GetId())

        helpMenu = wx.Menu()
        self.aboutItem = helpMenu.Append(wx.ID_ANY, '&About\tCtrl-A', 'Show about information')
        self.Bind(wx.EVT_MENU, self.onAboutPlot, self.aboutItem)

        self.menubar.Append(fileMenu, '&File')
        self.menubar.Append(helpMenu, '&Help')
        
        self.SetMenuBar(self.menubar)

#------------------------------------------------------------------------#

    def createPanel(self):
        self.panel = wx.Panel(self, id = wx.ID_ANY)

        self.vbox = wx.BoxSizer(wx.VERTICAL)

        # figure panel
        self.dpi = 100
        self.ongrid = False
        self.fig = Figure((5.0, 4.0), dpi = self.dpi)
        self.axes = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.panel, wx.ID_ANY, self.fig)

        # combobox for result plot
        params = sorted(self.parent.result.keys())
        self.plotparamcombo = wx.ComboBox(self.panel, id = wx.ID_ANY, value = params[0],
                choices = params, style = wx.CB_READONLY | wx.CB_SORT)
        st1 = wx.StaticText(self.panel, id = wx.ID_ANY, label = 'Choose Y Axis to plot:', style = wx.ALIGN_LEFT)
        self.plotparam_hint = funutils.MyStaticText(self.panel, label = u'', style = wx.ALIGN_RIGHT, fontcolor = 'blue')

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(st1, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        hbox.Add(self.plotparamcombo, flag = wx.ALIGN_CENTER_VERTICAL | wx.ALL, border = 10)
        hbox.Add(self.plotparam_hint, proportion = 1, flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border = 10)

        self.vbox.Add(self.canvas, proportion = 1, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border = 0)
        self.vbox.Add(hbox,        proportion = 0, flag = wx.LEFT, border = 10)

        self.panel.SetSizer(self.vbox)
        
        self.Bind(wx.EVT_COMBOBOX, self.onPlotChoice, self.plotparamcombo)
        self.canvas.mpl_connect('motion_notify_event', self.onMotion)

#------------------------------------------------------------------------#
        
    def onMotion(self, event):
        try:
            self.xyposlabel_val.SetLabel("(%.4g, %.4g)" % (event.xdata, event.ydata))
        except TypeError:
            pass

#------------------------------------------------------------------------#
    
    def createToolbar(self):
        #self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar = Toolbar(self.canvas)
        self.toolbar.Realize()
        tw, th = self.toolbar.GetSizeTuple()
        fw, fh = self.canvas.GetSizeTuple()
        self.toolbar.SetSize(wx.Size(fw, th))

        grid_chkbox         = wx.CheckBox(self.panel, label = 'Show Grid')
        xyposlabel          = funutils.MyStaticText(self.panel, label = u'(x, y): ', style = wx.ALIGN_RIGHT)
        self.xyposlabel_val = funutils.MyStaticText(self.panel, label = u'',         style = wx.ALIGN_RIGHT, fontcolor = 'red')
        
        toolbarbox = wx.BoxSizer(wx.HORIZONTAL)
        toolbarbox.Add(self.toolbar,        proportion = 0 ,flag = wx.LEFT | wx.ALIGN_LEFT)
        toolbarbox.Add(xyposlabel,          proportion = 0 ,flag = wx.LEFT | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 20)
        toolbarbox.Add(self.xyposlabel_val, proportion = 2 ,flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 10)
        toolbarbox.Add(grid_chkbox,         proportion = 1 ,flag = wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border = 20)

        self.vbox.Add(toolbarbox, proportion = 0, flag = wx.EXPAND | wx.LEFT | wx.BOTTOM, border = 10)
        self.toolbar.update()

        self.Bind(wx.EVT_CHECKBOX, self.onGridCheck, grid_chkbox)

#------------------------------------------------------------------------#
        
    def repaint(self):
        self.canvas.draw_idle()

#------------------------------------------------------------------------#
    
    def onGridCheck(self, event):
        if event.GetEventObject().IsChecked():
            self.ongrid = True
        else:
            self.ongrid = False
        
        self.axes.grid(self.ongrid)
        self.repaint()

#------------------------------------------------------------------------#

    def onPlotChoice(self, event):
        ykey = self.plotparamcombo.GetValue()
        xkey = self.parent.combobox31.GetValue() 
        self.plotparam_hint.SetLabel(ychoice[ykey][1])
        x = self.parent.scanX
        y = self.parent.result[ykey]
        self.axes.clear()
        try:
            self.axes.plot(x,y,'r')
            self.axes.set_xlabel(r''+xchoice[xkey]+'')
            self.axes.set_ylabel(r''+ychoice[ykey][0]+'')
            #self.axes.ticklabel_format(style = 'scientific', axis = 'both')
            #self.axes.yaxis.set_major_formatter(tick.FormatStrFormatter('%g'))
            self.axes.grid(self.ongrid)
            self.repaint()
        except ValueError:
            pass

#------------------------------------------------------------------------#

    def onExitPlot(self, event):
        self.Close()

#------------------------------------------------------------------------#

    def onSavePlot(self, event):
        fighead = 'figure'
        figext  = 'jpg'
        figname = fighead + time.strftime('%H%m%S', time.localtime()) + '.' + figext
        filefullpath = os.path.join(os.getcwdu(), figname)
        self.fig.savefig(filefullpath)
        dial = wx.MessageDialog(self, message = 'Figure is saved as ' + filefullpath, caption = "File Saved Message", style = wx.OK)
        if dial.ShowModal() == wx.ID_YES:
            self.Destroy()

#------------------------------------------------------------------------#

    def onSaveData(self, event):
        #print self.parent.combobox31.GetValue(), 
        savedataframe = DataSaveFrame(self, self.parent, title = 'Save Data to File')
        savedataframe.SetMinSize((800, 450))
        savedataframe.Show()
        savedataframe.Centre()

        
#------------------------------------------------------------------------#

    def onAboutPlot(self, event):
        dial = wx.MessageDialog(self.panel, message = "This panel is designed to show the plot figure.",
                caption = 'About plot panel', style = wx.ICON_INFORMATION)
        dial.ShowModal()

#------------------------------------------------------------------------#

class DataSaveFrame(wx.Frame):
    def __init__(self, parent, dataparent, title, **kwargs):
        super(self.__class__,self).__init__(parent=parent, id=wx.ID_ANY, title=title, **kwargs)
        self.parent = parent
        self.gparent = dataparent
        self.fmt = 'txt'  # save to ascii format by default
        self.InitUI()

    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        data_fmt_st  = funutils.MyStaticText(panel, label=u'Data File Format', style=wx.ALIGN_LEFT)
        data_fmt_cb  = wx.ComboBox(panel, value='txt', choices=['txt','hdf5'], style=wx.CB_READONLY)
        data_pth_st  = funutils.MyStaticText(panel, label=u'Data File Path', style=wx.ALIGN_LEFT)
        self.data_pth_tc = data_pth_tc = funutils.MyTextCtrl(panel, value=os.path.join(os.getcwd(), 'data.txt'), style=wx.CB_READONLY)
        data_pth_btn = wx.Button(panel, label=u'Browse')
        data_cols_st = funutils.MyStaticText(panel, label=u'Available Data Columns:', style=wx.ALIGN_LEFT, fontcolor='blue')
        data_cols_ck1 = wx.CheckBox(panel, label=u'Select All')
        data_cols_ck2 = wx.CheckBox(panel, label=u'Inverse Select')
        self.data_fmt_cb = data_fmt_cb
        self.datafilename = os.path.join(os.getcwd(), 'data.txt')

        self.chb_dict = {}
        xkey = self.gparent.combobox31.GetValue()
        chb_tmp = wx.CheckBox(panel, label=xkey) 
        data_cols_ws = wx.FlexGridSizer(5, 4, 2, 10)
        data_cols_ws.Add(chb_tmp, flag=wx.LEFT | wx.EXPAND, border=5)
        chb_tmp.SetValue(False)
        self.chb_dict['00-' + xkey] = {'val':self.gparent.scanX, 'obj':chb_tmp}

        for k,v in self.gparent.result.items():
            if isinstance(v, np.ndarray):
                chb_tmp = wx.CheckBox(panel, label=k.split('-')[1]) 
                chb_tmp.SetValue(False)
                data_cols_ws.Add(chb_tmp, flag=wx.LEFT | wx.EXPAND, border=5)
                self.chb_dict[k] = {'val':self.gparent.result[k], 'obj':chb_tmp}
            else:
                chb_tmp = wx.CheckBox(panel, label=k.split('-')[1]) 
                chb_tmp.Disable()
                data_cols_ws.Add(chb_tmp, flag=wx.LEFT | wx.EXPAND, border=5)
        data_cols_ws.Add(wx.StaticText(panel, label=''), flag=wx.LEFT | wx.EXPAND, border=5)

        gbs = wx.GridBagSizer(10, 0)
        gbs.Add(data_fmt_st,  pos=(0, 0), span=(1, 1), flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=10)
        gbs.Add(data_fmt_cb,  pos=(0, 1), span=(1, 2), flag=wx.LEFT | wx.RIGHT | wx.EXPAND,                border=10)
        gbs.Add(data_pth_st,  pos=(1, 0), span=(1, 1), flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT,            border=10)
        gbs.Add(data_pth_tc,  pos=(1, 1), span=(1, 2), flag=wx.LEFT | wx.RIGHT | wx.EXPAND,                border=10)
        gbs.Add(data_pth_btn, pos=(1, 3), span=(1, 1), flag=wx.LEFT | wx.RIGHT,                            border=10)
        gbs.Add(data_cols_st, pos=(2, 0), span=(1, 2), flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT,            border=10)
        gbs.Add(data_cols_ck1,pos=(2, 2), span=(1, 1), flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT,            border=10)
        gbs.Add(data_cols_ck2,pos=(2, 3), span=(1, 1), flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT,            border=10)
        gbs.Add(data_cols_ws, pos=(3, 0), span=(3, 4), flag=wx.LEFT | wx.RIGHT | wx.EXPAND,                border=10)
        gbs.AddGrowableCol(1)
        gbs.AddGrowableRow(3)

        vbox.Add(gbs, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        save_btn = wx.Button(panel, label='Save')
        exit_btn = wx.Button(panel, label='Exit')
        hbox_cmd = wx.BoxSizer(wx.HORIZONTAL)
        hbox_cmd.Add(save_btn, proportion=0, flag=wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, border=6)
        hbox_cmd.Add(exit_btn, proportion=0, flag=wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, border=6)

        vbox.Add(hbox_cmd, proportion=0, flag=wx.ALIGN_RIGHT | wx.ALL, border=5)

        panel.SetSizer(vbox)
        osizer = wx.BoxSizer(wx.VERTICAL)
        osizer.Add(panel, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        self.SetSizerAndFit(osizer)

        self.Bind(wx.EVT_BUTTON,   self.onChoosePth,  data_pth_btn)
        self.Bind(wx.EVT_BUTTON,   self.onSave,       save_btn)
        self.Bind(wx.EVT_BUTTON,   self.onExit,       exit_btn)
        self.Bind(wx.EVT_COMBOBOX, self.onChooseFmt,  data_fmt_cb)
        self.Bind(wx.EVT_CHECKBOX, self.onCheckCols1, data_cols_ck1)
        self.Bind(wx.EVT_CHECKBOX, self.onCheckCols2, data_cols_ck2)

    def onCheckCols1(self, event):
        if event.GetEventObject().IsChecked():
            for v in self.chb_dict.values():
                if isinstance(v['obj'], wx._controls.CheckBox) and not v['obj'].IsChecked():
                    v['obj'].SetValue(True)

    def onCheckCols2(self, event):
        if event.GetEventObject().IsChecked():
            for v in self.chb_dict.values():
                if isinstance(v['obj'], wx._controls.CheckBox):
                    if v['obj'].IsChecked():
                        v['obj'].SetValue(False)
                    else:
                        v['obj'].SetValue(True)

    def onChoosePth(self, event):
        self.datafilename = funutils.getFileToSave(self, ext=self.fmt)
        self.data_pth_tc.SetValue(self.datafilename)

    def onChooseFmt(self, event):
        self.fmt = self.data_fmt_cb.GetValue()
        newname = os.path.join(os.path.dirname(self.datafilename),
                               os.path.basename(self.datafilename).split('.')[0] + '.' + self.fmt)
        self.datafilename = newname
        self.data_pth_tc.SetValue(self.datafilename)

    def onExit(self, event):
        self.Close()

    def onSave(self, event):
        cols_selected_val  = []
        cols_selected_name = []
        for k,v in sorted(self.chb_dict.items()):
            if isinstance(v['obj'], wx._controls.CheckBox) and v['obj'].IsChecked():
                cols_selected_val.append(v['val'])
                cols_selected_name.append(k)
        if self.fmt == 'txt':
            np.savetxt(self.datafilename, np.vstack(cols_selected_val).T, header=' '.join(cols_selected_name), fmt='%.8e')
        else:  # hdf5
            f = h5py.File(self.datafilename, 'w')
            for data, name in zip(cols_selected_val, cols_selected_name):
                dset = f.create_dataset('data/' + name, shape=data.shape, dtype=data.dtype)
                dset[...] = data
            f.close()

        dial = wx.MessageDialog(self, message = 'Saved data to ' + self.datafilename, caption = "Data Saved Message", style = wx.OK)
        if dial.ShowModal() == wx.ID_YES:
            self.Destroy()

def run():
    app = wx.App(redirect = True)
    MainFrame(None, title = 'FEL Formula', size = (880, 668))
    app.MainLoop()

#------------------------------------------------------------------------#

if __name__ == '__main__':
    run()

#------------------------------------------------------------------------#
