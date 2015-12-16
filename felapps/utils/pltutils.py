#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
python modules for plot utilities:
    ImageViewer: main GUI framework for an universal image viewer

Author: Tong Zhang
Created: Feb. 3rd, 2015
"""

#import wxversion
#wxversion.ensureMinimal('2.8')

from __future__ import division

import wx
from wx.lib.agw import floatspin as fs
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.patches import Rectangle
import epics
import time
from datetime import datetime
import os
import xml.etree.cElementTree as ET
from . import resutils
from . import funutils
from . import parseutils

class ImageConfigFile(parseutils.ConfigFile):
    def __init__(self, infilename='config.xml', *args, **kwargs):
        parseutils.ConfigFile.__init__(self, infilename = infilename, *args, **kwargs)

    def parseConfigs(self):
        tree = ET.parse(self.xmlfile)
        root = tree.getroot()
        self.root = root
        self.tree = tree
        namelist_image      = {}
        namelist_control    = {}
        namelist_style      = {}
        namelist_histplot   = {}
        namestring_image    = ['width', 'height', 'savePath', 'saveImgName', 'saveImgExt', 'saveImgDatName', 'saveImgDatExt', 'saveIntName', 'saveIntExt', 'cmFavor', 'imgIniFunc']
        namestring_control  = ['frequency', 'imgsrcPV', 'imgsrcPVlist']
        namestring_histplot = ['heightRatio']
        namestring_style    = ['backgroundColor', 'fontpointsize', 'fontfamily', 'fontstyle', 'fontweight', 'fontfacename']
        for group in root.iter('group'):
            if group.get('name') == 'Image':
                namelist_image = {s:group.find('properties').get(s) for s in namestring_image}
            elif group.get('name') == 'Control':
                namelist_control   = {s:group.find('properties').get(s) for s in namestring_control}
            elif group.get('name') == 'Style':
                namelist_style  = {s:group.find('properties').get(s) for s in namestring_style}
            elif group.get('name') == 'HistPlot':
                namelist_histplot  = {s:group.find('properties').get(s) for s in namestring_histplot}
        self.namelist.update(namelist_image)
        self.namelist.update(namelist_control)
        self.namelist.update(namelist_style)
        self.namelist.update(namelist_histplot)

class ImageViewer(wx.Frame):
    def __init__(self, parent, config = 'config.xml', size = (800, 600), appversion = '1.0', **kwargs):
        super(self.__class__, self).__init__(parent = parent, size = size, id = wx.ID_ANY, **kwargs) #style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        self.parent = parent
        self.appversion = appversion
        self.cmlist_unis = ['viridis', 'inferno', 'plasma', 'magma']
        self.cmlist_seq1 = ['Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 
                            'OrRd', 'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu','Reds', 
                            'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd']
        self.cmlist_seq2 = ['afmhot', 'autumn', 'bone', 'cool', 'copper', 'gist_heat', 
                            'gray', 'hot', 'pink', 'spring', 'summer', 'winter']
        self.cmlist_dive = ['BrBG', 'bwr', 'coolwarm', 'PiYG', 'PRGn', 'PuOr', 'RdBu', 
                            'RdGy', 'RdYlBu', 'RdYlGn', 'Spectral', 'seismic']
        self.cmlist_qual = ['Accent', 'Dark2', 'Paired', 'Pastel1',
                            'Pastel2', 'Set1', 'Set2', 'Set3']
        self.cmlist_misc = ['gist_earth', 'terrain', 'ocean', 'gist_stern',
                            'brg', 'CMRmap', 'cubehelix', 'gnuplot', 'gnuplot2', 
                            'gist_ncar', 'nipy_spectral', 'jet', 'rainbow',
                            'gist_rainbow', 'hsv', 'flag', 'prism']
        self.cmlist = {'Sequential-NEW': self.cmlist_unis,
                       'Sequential-I' : self.cmlist_seq1,
                       'Sequential-II': self.cmlist_seq2,
                       'Diverging'    : self.cmlist_dive,
                       'Qualitative'  : self.cmlist_qual,
                       'Miscellaneous': self.cmlist_misc}
        
        self.rcmflag = '' # flag for reverse colormap
        self.configlist = {} # configurations dict
        self.xmlconfig = {} # xml config class

        self.loadConfig(configfilename = config)
        #self.printConfig() # just for debug

        self.Bind(wx.EVT_CLOSE, self.onExit)
        self.Bind(wx.EVT_MENU_HIGHLIGHT, self.onMenuHL)
        self.InitUI()

        # save data settings
        self.savedict = {}
        self.saveTimerLife = 0
        self.saveTimerCounter = 0
        self.savetimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onSaveTimer, self.savetimer)

    def loadConfig(self, configfilename):
        self.xmlconfig = ImageConfigFile(configfilename)
        namelist = self.xmlconfig.getConfigs()

        # Image
        self.imginifunc = namelist['imgIniFunc']
        self.wpx, self.hpx = int(float(namelist['width'])), int(float(namelist['height']))
        self.roixy = [0, self.wpx, 0, self.hpx]
        dirdate = time.strftime('%Y%m%d', time.localtime())
        self.save_path_str_head = os.path.expanduser(namelist['savePath'])
        self.save_path_str      = os.path.join(self.save_path_str_head, dirdate)
        self.save_img_name_str = namelist['saveImgName']
        self.save_img_ext_str  = namelist['saveImgExt']
        self.save_dat_name_str = namelist['saveImgDatName']
        self.save_dat_ext_str  = namelist['saveImgDatExt']
        self.save_int_name_str = namelist['saveIntName']
        self.save_int_ext_str  = namelist['saveIntExt']

        self.cmlist_favo = namelist['cmFavor'].split()
        self.cmlist['Favorites'] = self.cmlist_favo

        # Control
        self.timer_freq = float(namelist['frequency'])
        self.timer_msec = 1./self.timer_freq*1000 
        self.imgsrcPV     = namelist['imgsrcPV']
        self.imgsrcPVlist = namelist['imgsrcPVlist'].split()

        # Style
        self.bkgdcolor    = funutils.hex2rgb(namelist['backgroundColor'])
        self.fontptsize   = int(namelist['fontpointsize'])
        self.fontfamily   = int(namelist['fontfamily'])
        self.fontstyle    = int(namelist['fontstyle'])
        self.fontweight   = int(namelist['fontweight'])
        self.fontfacename = namelist['fontfacename']
        self.font         = wx.Font(self.fontptsize, self.fontfamily, self.fontstyle, self.fontweight, faceName = self.fontfacename)
        self.fontptsize_large  = int(self.fontptsize * 2.0)
        self.fontptsize_big    = int(self.fontptsize * 1.2)
        self.fontptsize_normal = int(self.fontptsize * 1.0)
        self.fontptsize_small  = int(self.fontptsize * 0.8)
        self.fontptsize_tiny   = int(self.fontptsize * 0.5)

        # HistPlot
        self.heightRatio  = float(namelist['heightRatio'])

        self.configdict = namelist

    def printConfig(self):
        for (key,value) in sorted(self.configdict.items()):
            print("%s --- %s" % (key, value))

    def InitUI(self):
        self.createMenubar()
        self.createPanel()
        self.createStatusbar()

    def createMenubar(self):
        self.menubar = wx.MenuBar()
        
        ## File menu
        fileMenu = wx.Menu()
        openItem    = fileMenu.Append(wx.ID_OPEN, '&Open file\tCtrl+O',            'Open file to view')
        saveImgItem = fileMenu.Append(wx.ID_SAVE, '&Save Image Plot\tCtrl+S',      'Save figure plotting to file')
        saveDatItem = fileMenu.Append(wx.ID_ANY,  '&Save Image Data\tCtrl+D',  'Save figure data to file')
        fileMenu.AppendSeparator()
        exitItem = fileMenu.Append(wx.ID_EXIT, 'E&xit\tCtrl+W', 'Exit application')
        self.Bind(wx.EVT_MENU, self.onOpen,    id =    openItem.GetId())
        self.Bind(wx.EVT_MENU, self.onSaveImg, id = saveImgItem.GetId())
        self.Bind(wx.EVT_MENU, self.onSaveDat, id = saveDatItem.GetId())
        self.Bind(wx.EVT_MENU, self.onExit,    id =    exitItem.GetId())
        
        ## Configurations menu
        configMenu = wx.Menu()
        loadConfigItem = configMenu.Append(wx.ID_ANY, 'Load from file\tCtrl+Shift+L', 'Loading configurations from file')
        saveConfigItem = configMenu.Append(wx.ID_ANY, 'Save to file\tCtrl+Shift+S',   'Saving configurations to file')
        appsConfigItem = configMenu.Append(wx.ID_ANY, 'Preferences\tCtrl+Shift+I',    'Configurations for application')
        self.Bind(wx.EVT_MENU, self.onConfigApps, id = appsConfigItem.GetId())
        self.Bind(wx.EVT_MENU, self.onConfigLoad, id = loadConfigItem.GetId())
        self.Bind(wx.EVT_MENU, self.onConfigSave, id = saveConfigItem.GetId())
        
        ## Operations menu
        methMenu = wx.Menu()
        showIntItem   = methMenu.Append(wx.ID_ANY, 'Show intensity\tCtrl+Shift+V', 'Monitor intensity')
        showXhistItem = methMenu.Append(wx.ID_ANY, 'Show hist-X\tAlt+X',           'Show histogram along X-axis', kind = wx.ITEM_CHECK)
        showYhistItem = methMenu.Append(wx.ID_ANY, 'Show hist-Y\tAlt+Y',           'Show histogram along Y-axis', kind = wx.ITEM_CHECK)
        autoSaveItem  = methMenu.Append(wx.ID_ANY, 'Auto save\tAlt+S',             'Auto saving data&image')
        self.Bind(wx.EVT_MENU, self.onShowInt,   id =   showIntItem.GetId())
        self.Bind(wx.EVT_MENU, self.onShowXhist, id = showXhistItem.GetId())
        self.Bind(wx.EVT_MENU, self.onShowYhist, id = showYhistItem.GetId())
        self.Bind(wx.EVT_MENU, self.onAutoSave,  id = autoSaveItem.GetId() )

        ## Help menu
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT, '&About\tF1', 'Show about information')
        self.Bind(wx.EVT_MENU, self.onAbout, id = wx.ID_ABOUT)
        
        ## make menu
        self.menubar.Append(fileMenu,   '&File')
        self.menubar.Append(configMenu, '&Configurations')
        self.menubar.Append(methMenu,   '&Operations')
        self.menubar.Append(helpMenu,   '&Help')
        
        ## set menu
        self.SetMenuBar(self.menubar)

    def onOpen(self, event):
        pass

    def onMenuHL(self, event):
        try:
            hltext = event.GetEventObject().GetHelpString(event.GetMenuId())
            self.statusbar.appinfo.SetLabel(hltext)
        except:
            pass

    def onSaveImg(self, event):
        if not os.path.exists(self.save_path_str):
            os.system('mkdir -p' + ' ' + self.save_path_str) # I've not found pure python way (simple) to do that yet.
        filelabel = time.strftime('%H%M%S', time.localtime())
        savetofilename = self.save_path_str + '/' + self.save_img_name_str + filelabel + self.save_img_ext_str
        self.imgpanel.figure.savefig(savetofilename)
        hintText = 'Image Plotting file: ' + savetofilename + ' was saved.'
        self.statusbar.appinfo.SetLabel(hintText)
        #self.statusbar.SetStatusText(hintText)

    def onSaveDat(self, event):
        if not os.path.exists(self.save_path_str):
            os.system('mkdir -p' + ' ' + self.save_path_str) 
        filelabel = time.strftime('%H%M%S', time.localtime())
        savetofilename = self.save_path_str + '/' + self.save_dat_name_str + filelabel + self.save_dat_ext_str
        saveins = funutils.SaveData(self.imgpanel.z, savetofilename, self.save_dat_ext_str)
        hintText = 'Image Data file: ' + savetofilename + ' was saved.'
        #self.statusbar.SetStatusText(hintText)
        self.statusbar.appinfo.SetLabel(hintText)
    
    def onShowInt(self, event):
        self.menuShowInt = ShowIntPanel(self)
        self.menuShowInt.SetTitle('Image Intensity Monitor')
        #self.menuShowInt.SetSize((620,550))
        self.menuShowInt.Show()

    def onShowXhist(self, event):
        flag = not self.imgpanel.linex.get_visible()
        self.imgpanel.linex.set_visible(flag)

    def onShowYhist(self, event):
        flag = not self.imgpanel.liney.get_visible()
        self.imgpanel.liney.set_visible(flag)

    def onAutoSave(self, event):
        self.statusbarcolor = self.statusbar.appinfo.GetForegroundColour()
        self.menuAutoSaveFrame = AutoSavePanel(self)
        self.menuAutoSaveFrame.SetTitle('Automatic Data-Save System')
        self.menuAutoSaveFrame.Show()

    def onSaveTimer(self, event):
        self.saveTimerCounter += 1
        """ for test only
        fmt='%Y-%m-%d %H:%M:%S %Z'
        print self.saveTimerLife, ' SAVE at ', time.strftime(fmt, time.localtime())
        """

        # perform saving task
        #filelabel = time.strftime('%H%M%S', time.localtime())
        filelabel = datetime.now().strftime('%H%M%S.%f')
        savetodatfilebasename = self.savedict['save_path'] + os.sep + self.save_dat_name_str + filelabel
        savetoimgfilebasename = self.savedict['save_path'] + os.sep + self.save_img_name_str + filelabel

        datatosave = self.mypv.get()[0:self.wpx*self.hpx].reshape((self.wpx,self.hpx))[self.roixy[0]:self.roixy[1],self.roixy[2]:self.roixy[3]]
        # save data
        if self.savedict['save_datfmt_hdf5'] == 1: # save hdf5 fmt
            saveins = funutils.SaveData(datatosave, savetodatfilebasename + '.hdf5', '.hdf5')
        if self.savedict['save_datfmt_asc'] == 1: # save asc fmt
            saveins = funutils.SaveData(datatosave, savetodatfilebasename + '.asc', '.asc')
        if self.savedict['save_datfmt_sdds'] == 1: # save sdds fmt
            saveins = funutils.SaveData(datatosave, savetodatfilebasename + '.sdds', '.sdds')

        # save image
        if self.savedict['save_imgfmt_jpg'] == 1: # save jpg fmt
            self.imgpanel.figure.savefig(savetoimgfilebasename + '.jpg')
        if self.savedict['save_imgfmt_eps'] == 1: # save eps fmt
            self.imgpanel.figure.savefig(savetoimgfilebasename + '.eps')
        if self.savedict['save_imgfmt_png'] == 1: # save png fmt
            self.imgpanel.figure.savefig(savetoimgfilebasename + '.png')
 
        # show hint at statusbar
        hintText = 'Data file Record: %d was saved.' % self.saveTimerCounter
        self.statusbar.appinfo.SetLabel(hintText)
        self.statusbar.appinfo.SetForegroundColour('red')

        if self.saveTimerCounter == self.saveTimerLife:
            self.savetimer.Stop()
            hintText = 'Total %d records are saved to directory %s.' % (self.saveTimerCounter, self.savedict['save_path'])
            self.statusbar.appinfo.SetLabel(hintText)
            self.statusbar.appinfo.SetForegroundColour(self.statusbarcolor)
        

    def onConfigApps(self, event):
        self.menuAppConfig = AppConfigPanel(self)
        self.menuAppConfig.SetTitle('Application Preferences')
        self.menuAppConfig.Show()

    def onConfigLoad(self, event):
        try:
            xmlfile = funutils.getFileToLoad(self, ext = 'xml')
            self.loadConfig(xmlfile)
            self.onUpdateUIInit()
            self.onUpdateUI()
        except:
            return

    def onConfigSave(self, event):
        try:
            savetofilename = funutils.getFileToSave(self, ext = 'xml')
            self.xmlconfig.updateConfigs(self.configdict, savetofilename)
            self.statusbar.appinfo.SetLabel('Present configurations were just saved to ' + savetofilename + '.')
            #self.statusbar.SetStatusText('Present configurations were just saved to ' + savetofilename + '.')
        except:
            return

    def onExit(self, event):
        dial = wx.MessageDialog(self, message = "Are you sure to exit this application?",
                                caption = "Exit Warning",
                                style = wx.YES_NO | wx.NO_DEFAULT | wx.CENTRE | wx.ICON_QUESTION)
        if dial.ShowModal() == wx.ID_YES:
            self.Destroy()

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
        info.Name = "Image Viewer"
        info.Version = self.appversion
        info.Copyright = "(C) 2014-2015 Tong Zhang, SINAP, CAS"
        info.Description = wordwrap(
            "This application is created for being an profile/image monitor and image data processing.\n"

            "It is designed by Python language, using GUI module of wxPython.",
            350, wx.ClientDC(self))
        info.WebSite = ("http://everyfame.me", "Image Viewer home page")
        info.Developers = [ "Tong Zhang <zhangtong@sinap.ac.cn>"]
        licenseText = "Image Viewer is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.\n" + "\nImage Viewer is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.\n" + "\nYou should have received a copy of the GNU General Public License along with Image Viewer; if not, write to the Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA"
        info.License = wordwrap(licenseText, 500, wx.ClientDC(self))
        wx.AboutBox(info)


    def onUpdateUIInit(self):
        self.imgpanel.func = self.imginifunc
        self.imgpanel.onGetData()
        self.imgpanel.doPlot()

    def onUpdateUI(self):
        self.updateFont()
        
        self.imgsrc_tc.SetValue(self.imgsrcPV)
        self.panel.SetBackgroundColour(self.bkgdcolor)
        #self.imgpanel.func = self.imginifunc
        #self.imgpanel.onGetData()
        #self.imgpanel.doPlot()
        self.imgpanel.setColor(self.bkgdcolor) # make color as private var
        self.imgpanel.setHratio(self.heightRatio)
        self.imgpanel.repaint() # rewrite repaint func
        self.imgcm.setColor(self.bkgdcolor)
        self.imgcm.repaint()

    def updateFont(self):
        objs_large  = [self.title_st]
        objs_big    = [self.timenow_st]
        objs_small  = [self.min_st, self.max_st, self.min_value_st, self.max_value_st]
        objs_normal = [self.imgsrc_st, self.cm_st, self.cr_st, self.inten_st, self.inten_val,
                       self.imgcr_st, self.pos_st, self.pos_val, self.imgsrc_tc, 
                       self.imgcr_min_tc, self.imgcr_max_tc, self.rcmchkbox,
                       self.cmlist_cb, self.cm_cb,
                       self.daqtgl_btn, self.roi_btn, self.reset_roi_btn]
        objs = objs_large + objs_big + objs_small + objs_normal
        [iobj.setFont(self.font) for iobj in objs]
        [iobj.setFontSize(self.fontptsize_large)  for iobj in objs_large ]
        [iobj.setFontSize(self.fontptsize_big)    for iobj in objs_big   ]
        [iobj.setFontSize(self.fontptsize_normal) for iobj in objs_normal]
        [iobj.setFontSize(self.fontptsize_small)  for iobj in objs_small ]
        
    def createStatusbar(self):
        """
        self.statusbar = self.CreateStatusBar(2)
        self.statusbar.SetStatusWidths([-4, -1])
        self.statusbar.SetStatusText(u'ImageViewer powered by Python' ,0)
        versionfield =  15*' ' + time.strftime('%Y-%m-%d', time.localtime()) + ' ' + '(Version: ' + self.appversion + ')'
        self.statusbar.SetStatusText(versionfield, 1)
        """
        self.statusbar = funutils.ESB.EnhancedStatusBar(self)
        self.statusbar.SetFieldsCount(2)
        self.SetStatusBar(self.statusbar)
        self.statusbar.SetStatusWidths([-4,-1])
        self.statusbar.appinfo= wx.StaticText(self.statusbar, wx.ID_ANY, 
                                 label = 'ImageViewer powered by Python')
        versionfield = wx.StaticText(self.statusbar, wx.ID_ANY, 
                                     label = time.strftime('%Y-%m-%d', time.localtime()) + ' ' + ' (Version: ' + self.appversion + ')')
        self.statusbar.AddWidget(self.statusbar.appinfo, funutils.ESB.ESB_ALIGN_LEFT )
        self.statusbar.AddWidget(versionfield,  funutils.ESB.ESB_ALIGN_RIGHT)

    def createPanel(self):
        self.panel = wx.Panel(self, id = wx.ID_ANY)
        self.panel.SetBackgroundColour(self.bkgdcolor)

        vbox = wx.BoxSizer(wx.VERTICAL)
        ## title and horizontal line
        self.title_st = funutils.MyStaticText(self.panel,
                label = u'Image Viewer', style = wx.ALIGN_CENTER,
                font = self.font, fontsize = self.fontptsize_large, fontweight = wx.FONTWEIGHT_NORMAL,
                fontcolor = 'blue')
        vbox.Add(self.title_st, flag = wx.LEFT | wx.RIGHT | wx.TOP | wx.ALIGN_CENTER, border = 10)
        hline = wx.StaticLine(self.panel, style = wx.LI_HORIZONTAL)
        vbox.Add((-1, 10))
        vbox.Add(hline, proportion = 0, flag = wx.EXPAND | wx.LEFT | wx.RIGHT, border = 28)

        ## hbox to put left and right panels
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        ## left panel
        vboxleft  = wx.BoxSizer(wx.VERTICAL)
        
        ## StaticText for time indication
        self.timenow_st = funutils.MyStaticText(self.panel,
                label = time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime()),
                style = wx.ALIGN_CENTER,
                font = self.font, fontsize = self.fontptsize_big, fontweight = wx.FONTWEIGHT_NORMAL,
                fontcolor = 'black')

        self.imgpanel = ImagePanel(self.panel, figsize = (12,12), dpi = 75, bgcolor = self.bkgdcolor, heightratio = self.heightRatio, func = self.imginifunc)
        
        vboxleft.Add(self.timenow_st, proportion = 0, flag = wx.ALIGN_CENTER | wx.TOP, border = 10)
        vboxleft.Add(self.imgpanel, proportion = 1, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT | wx.BOTTOM, border = 10)

        hbox.Add(vboxleft, proportion = 8, flag = wx.EXPAND | wx.LEFT, border = 8)

        ## separation line
        vline = wx.StaticLine(self.panel, style = wx.LI_VERTICAL)
        hbox.Add(vline, proportion = 0, flag = wx.EXPAND | wx.TOP | wx.BOTTOM, border = 20)
        
        ## right panel
        vboxright = wx.BoxSizer(wx.VERTICAL)

        self.imgsrc_st = funutils.MyStaticText(self.panel,
                label = u'Image Source:', style = wx.ALIGN_LEFT,
                font = self.font, fontsize = self.fontptsize_normal, fontweight = wx.FONTWEIGHT_NORMAL,
                fontcolor = 'black')
        ## define pv value here!
        self.imgsrc_tc = funutils.MyTextCtrl(self.panel, value = self.imgsrcPV, style=wx.TE_PROCESS_ENTER, 
                font = self.font, fontsize = self.fontptsize_normal)
        
        ## add/remove pv from imgsrcPVlist
        self.addpvbtn = wx.BitmapButton(self.panel, bitmap = resutils.addicon.GetBitmap())
        self.rmpvbtn  = wx.BitmapButton(self.panel, bitmap = resutils.delicon.GetBitmap())

        pvbox = wx.BoxSizer(wx.HORIZONTAL)
        pvbox.Add(self.imgsrc_tc, proportion = 1, flag = wx.EXPAND | wx.ALIGN_LEFT | wx.RIGHT, border = 8)
        pvbox.Add(self.addpvbtn,  flag = wx.ALIGN_CENTER_VERTICAL)
        pvbox.Add(self.rmpvbtn,   flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 6)
        
        ## color map
        self.cm_st = funutils.MyStaticText(self.panel,
                label = u'Color Map:', style = wx.ALIGN_LEFT,
                font = self.font, fontsize = self.fontptsize_normal, fontweight = wx.FONTWEIGHT_NORMAL,
                fontcolor = 'black')
        ## combobox for color maps
        self.cmlist_cb = funutils.MyComboBox(self.panel, value = 'Favorites', choices = sorted(self.cmlist.keys()), style = wx.CB_READONLY, 
                font = self.font, fontsize = self.fontptsize_normal, fontweight = wx.FONTWEIGHT_NORMAL, fontcolor = 'black')
        ## list one of classified color map 
        self.cm_cb = funutils.MyComboBox(self.panel, value = self.cmlist['Favorites'][0], choices = self.cmlist['Favorites'], style = wx.CB_READONLY,
                font = self.font, fontsize = self.fontptsize_normal, fontweight = wx.FONTWEIGHT_NORMAL, fontcolor = 'black')
        ## book and unbook btn
        #self.bookbtn   = wx.BitmapButton(self.panel, bitmap = wx.BitmapFromImage(wx.Image('add.png')))
        #self.unbookbtn = wx.BitmapButton(self.panel, bitmap = wx.BitmapFromImage(wx.Image('remove.png')))
        self.bookbtn   = wx.BitmapButton(self.panel, bitmap = resutils.addicon.GetBitmap())
        self.unbookbtn = wx.BitmapButton(self.panel, bitmap = resutils.delicon.GetBitmap())
        ## color range box
        self.cr_st = funutils.MyStaticText(self.panel,
                label = u'Color Range:', style = wx.ALIGN_LEFT,
                font = self.font, fontsize = self.fontptsize_normal, fontweight = wx.FONTWEIGHT_NORMAL,
                fontcolor = 'black')
        self.min_st = funutils.MyStaticText(self.panel,
                label = u'min:', style = wx.ALIGN_LEFT, font = self.font,
                fontsize = self.fontptsize_small, fontweight = wx.FONTWEIGHT_NORMAL,
                fontcolor = 'black')
        self.max_st = funutils.MyStaticText(self.panel,
                label = u'max:', style = wx.ALIGN_LEFT, font = self.font,
                fontsize = self.fontptsize_small, fontweight = wx.FONTWEIGHT_NORMAL,
                fontcolor = 'black')
        ### get the cmin and cmax from imgpanel object
        cmin_now = self.imgpanel.cmin
        cmax_now = self.imgpanel.cmax
        ### initial values for min&max sliders
        self.min_value_st = funutils.MyStaticText(self.panel,
                label = ('%.1f' % (cmin_now)), style = wx.ALIGN_RIGHT,
                font = self.font,
                fontsize = self.fontptsize_small, fontweight = wx.FONTWEIGHT_NORMAL,
                fontcolor = 'blue')
        self.max_value_st = funutils.MyStaticText(self.panel,
                label = ('%.1f' % (cmax_now)), style = wx.ALIGN_RIGHT,
                fontsize = self.fontptsize_small, fontweight = wx.FONTWEIGHT_NORMAL,
                fontcolor = 'blue')
        self.min_slider = funutils.FloatSlider(self.panel, value = cmin_now, minValue = cmin_now, maxValue = cmax_now, increment = 0.1)
        self.max_slider = funutils.FloatSlider(self.panel, value = cmax_now, minValue = cmin_now, maxValue = cmax_now, increment = 0.1)
        
        ## colormap line: st + combox for cm categories
        cmstbox = wx.BoxSizer(wx.HORIZONTAL)
        cmstbox.Add(self.cm_st, flag = wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border = 10)
        cmstbox.Add(self.cmlist_cb, proportion = 1, flag = wx.ALIGN_RIGHT)

        ## selected colormap + add/remove to/from bookmarks btn
        cbbookbox = wx.BoxSizer(wx.HORIZONTAL)
        cbbookbox.Add(self.cm_cb, proportion = 1, flag = wx.EXPAND | wx.ALIGN_LEFT | wx.RIGHT, border = 8)
        cbbookbox.Add(self.bookbtn,   flag = wx.ALIGN_CENTER_VERTICAL)
        cbbookbox.Add(self.unbookbtn, flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 6)

        ## show the selected colormap image
        self.imgcm = ImageColorMap(self.panel, figsize = (0.8,0.2),  dpi = 75, bgcolor = self.bkgdcolor)
        
        ## checkbox for reverse colormap
        self.rcmchkbox = funutils.MyCheckBox(self.panel, label = u'Reverse Colormap', font = self.font, fontsize = self.fontptsize_normal)

        ## colorrange box
        crbox = wx.FlexGridSizer(2, 3, 6, 6)
        crbox.Add(self.min_st,       proportion = 0, flag = wx.LEFT | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        crbox.Add(self.min_slider,   proportion = 1, flag = wx.EXPAND | wx.ALIGN_LEFT)
        crbox.Add(self.min_value_st, proportion = 0, flag = wx.ALIGN_RIGHT)
        crbox.Add(self.max_st,       proportion = 0, flag = wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        crbox.Add(self.max_slider,   proportion = 1, flag = wx.EXPAND | wx.ALIGN_LEFT)
        crbox.Add(self.max_value_st, proportion = 0, flag = wx.ALIGN_RIGHT)
        crbox.AddGrowableCol(1)
        ##
        vboxright.Add(self.imgsrc_st, flag = wx.TOP, border = 25)
        vboxright.Add(pvbox, flag = wx.EXPAND | wx.TOP, border = 10)
        ##
        vboxright.Add((-1,25))
        vboxright.Add(cmstbox,   flag = wx.EXPAND)
        vboxright.Add(cbbookbox, flag = wx.EXPAND | wx.TOP, border = 10)
        """
        ## put rcmchkbox and imgcm into hbox3
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3.Add(self.imgcm, flag = wx.ALIGN_LEFT)
        hbox3.Add(self.rcmchkbox, flag = wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.LEFT, border = 5)
        vboxright.Add(hbox3, flag = wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.EXPAND | wx.TOP, border = 10)
        """
        vboxright.Add(self.rcmchkbox, flag = wx.ALIGN_LEFT | wx.EXPAND | wx.TOP, border = 10)
        vboxright.Add(self.imgcm,     flag = wx.ALIGN_CENTER | wx.EXPAND | wx.TOP, border = 10)
        ##
        vboxright.Add(self.cr_st, flag = wx.TOP, border = 25)
        vboxright.Add(crbox, flag = wx.EXPAND | wx.TOP, border = 10)

        ## for debug: add a statictext and button to vboxright sizer 2015.Feb.11
        self.inten_st   = funutils.MyStaticText(self.panel, label = 'Intensity:', font = self.font, fontsize = self.fontptsize_normal)
        self.inten_val  = funutils.MyStaticText(self.panel, label = '0',          font = self.font, fontsize = self.fontptsize_normal)
        self.daqtgl_btn = funutils.MyButton(self.panel,     label = 'DAQ START',  font = self.font, fontsize = self.fontptsize_normal)
        hbox_int = wx.BoxSizer(wx.HORIZONTAL)
        hbox_int.Add(self.inten_st,  proportion = 0, flag = wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        hbox_int.Add(self.inten_val, proportion = 1, flag = wx.EXPAND | wx.ALIGN_RIGHT | wx.LEFT, border = 10)

        ## add color range for imgsrc
        self.imgcr_st     = funutils.MyStaticText(self.panel, label = 'CR of Image:', 
                                            font = self.font, fontsize = self.fontptsize_normal)
        self.imgcr_min_tc = funutils.MyTextCtrl(self.panel, value = '0',   font = self.font, fontsize = self.fontptsize_normal)
        self.imgcr_max_tc = funutils.MyTextCtrl(self.panel, value = '200', font = self.font, fontsize = self.fontptsize_normal)
        hbox_imgcr = wx.BoxSizer(wx.HORIZONTAL)
        hbox_imgcr.Add(self.imgcr_st,     proportion = 0, flag = wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        hbox_imgcr.Add(self.imgcr_min_tc, proportion = 1, flag = wx.EXPAND | wx.ALIGN_RIGHT | wx.RIGHT | wx.LEFT, border = 5)
        hbox_imgcr.Add(self.imgcr_max_tc, proportion = 1, flag = wx.EXPAND | wx.ALIGN_RIGHT)

        vboxright.Add(hbox_imgcr, proportion = 0, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.TOP, border = 20)
        vboxright.Add(hbox_int,   proportion = 0, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.TOP, border = 20)
        vboxright.Add(self.daqtgl_btn, flag = wx.ALIGN_RIGHT | wx.TOP, border = 20)

        ### information display from image
        ## mouse position tracker
        self.pos_st  = funutils.MyStaticText(self.panel, label = 'Current pos (x,y):', font = self.font, fontsize = self.fontptsize_normal)
        self.pos_val = funutils.MyStaticText(self.panel, label = '',                   font = self.font, fontsize = self.fontptsize_normal)
        hbox_pos = wx.BoxSizer(wx.HORIZONTAL)
        hbox_pos.Add(self.pos_st,  proportion = 0, flag = wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        hbox_pos.Add(self.pos_val, proportion = 1, flag = wx.EXPAND | wx.ALIGN_RIGHT | wx.LEFT, border = 10)

        self.roi_btn       = funutils.MyButton(self.panel, label = 'Choose ROI', font = self.font, fontsize = self.fontptsize_normal)
        self.reset_roi_btn = funutils.MyButton(self.panel, label = 'Reset ROI',  font = self.font, fontsize = self.fontptsize_normal)
        hbox_roi = wx.BoxSizer(wx.HORIZONTAL)
        hbox_roi.Add(self.roi_btn,       proportion = 0, flag = wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        hbox_roi.Add(self.reset_roi_btn, proportion = 1, flag = wx.EXPAND | wx.ALIGN_RIGHT | wx.LEFT, border = 10)

        vboxright.Add(hbox_pos, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.TOP, border = 20)
        vboxright.Add(hbox_roi, flag = wx.ALIGN_RIGHT | wx.TOP, border = 20)

        ##
        hbox.Add(vboxright, proportion = 3, flag = wx.EXPAND | wx.LEFT | wx.RIGHT, border = 10)
       
        ## set sizer
        vbox.Add(hbox, proportion = 1, flag = wx.EXPAND | wx.ALIGN_CENTER)
        self.panel.SetSizer(vbox)
        osizer = wx.BoxSizer(wx.HORIZONTAL)
        osizer.Add(self.panel, proportion = 1, flag = wx.EXPAND)
        self.SetSizerAndFit(osizer)

        ### event bindings

        ## ROI callback
        self.Bind(wx.EVT_BUTTON, self.onChooseROI, self.roi_btn      )
        self.Bind(wx.EVT_BUTTON, self.onResetROI,  self.reset_roi_btn)

        ## add input pv namestring to imgsrcPVlist or not
        self.Bind(wx.EVT_BUTTON, self.onAddPV, self.addpvbtn)
        self.Bind(wx.EVT_BUTTON, self.onRmPV,  self.rmpvbtn )

        ## colormap categories
        self.Bind(wx.EVT_COMBOBOX, self.onSetCmclass, self.cmlist_cb)

        ## color map value from specific category
        self.Bind(wx.EVT_COMBOBOX, self.onSetColormap, self.cm_cb)

        ## add selected colormap to favorites or not
        self.Bind(wx.EVT_BUTTON, self.onBookmark,   self.bookbtn  )
        self.Bind(wx.EVT_BUTTON, self.onUnBookmark, self.unbookbtn)

        ## color range min and max sliders
        self.Bind(wx.EVT_SCROLL, self.onSetColorRange, self.min_slider)
        self.Bind(wx.EVT_SCROLL, self.onSetColorRange, self.max_slider)

        ## when reverse color map checked/unchecked
        self.Bind(wx.EVT_CHECKBOX, self.onCheckRCM, self.rcmchkbox, self.cm_cb)

        ## bind self.imgsrc_tc
        self.Bind(wx.EVT_TEXT_ENTER, self.onSetImgSrc, self.imgsrc_tc)

        ## timer for update image
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER,  self.onUpdate, self.timer     )
        self.Bind(wx.EVT_BUTTON, self.onDAQbtn, self.daqtgl_btn)

        ## another timer for showing time now
        self.timernow = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTickTime, self.timernow)

        ## start timernow (clock)
        self.timernow.Start(1000)

    def onResetROI(self, event):
        self.roixy = [0, self.wpx, 0, self.hpx]

    def onChooseROI(self, event):
        self.roiFrame = ChooseROIFrame(self, self.imgpanel)
        self.roiFrame.SetTitle('Choose ROI')
        self.roiFrame.Show()

    def onTickTime(self, event):
        fmt='%Y-%m-%d %H:%M:%S %Z'
        self.timenow_st.SetLabel(time.strftime(fmt, time.localtime()))

    def onDAQbtn(self, event):
        label = event.GetEventObject().GetLabel()
        try:
            isinstance(self.mypv, epics.pv.PV)
        except AttributeError:
            self.mypv = epics.PV(self.imgsrc_tc.GetValue(), auto_monitor = True)

        if self.timer.IsRunning():
            self.timer.Stop()
            self.min_slider.Enable()
            self.max_slider.Enable()
            self.daqtgl_btn.SetLabel('DAQ START')
        else:
            self.timer.Start(self.timer_msec)
            self.min_slider.Disable()
            self.max_slider.Disable()
            self.daqtgl_btn.SetLabel('DAQ STOP')

    def onUpdate(self, event):
        if self.mypv.connected == True:
            self.inten_val.SetLabel("%.5e" % (np.sum(self.mypv.get())))

            self.imgpanel.z = self.mypv.get()[0:self.wpx*self.hpx].reshape((self.wpx,self.hpx))[self.roixy[0]:self.roixy[1],self.roixy[2]:self.roixy[3]]
            try:
                cmin_now = float(self.imgcr_min_tc.GetValue())
                cmax_now = float(self.imgcr_max_tc.GetValue())
            except ValueError:
                cmin_now = None
                cmax_now = None
            self.imgpanel.im.set_clim(vmin = cmin_now, vmax= cmax_now)
            self.imgpanel.im.set_array(self.imgpanel.z)
            self.imgpanel.repaint()
        else:
            dial = wx.MessageDialog(self, message = u"Lost connection, may be caused by network error or the IOC server is down.",
                    caption = u"Lost Connection", 
                    style = wx.OK | wx.ICON_ERROR | wx.CENTRE)
            if dial.ShowModal() == wx.ID_OK:
                self.timer.Stop()
                self.min_slider.Enable()
                self.max_slider.Enable()
                self.daqtgl_btn.SetLabel('DAQ START')
                dial.Destroy()
    
    def onSetImgSrc(self, event):
        """
        set image data source and show in the image panel
        """
        self.mypv = epics.PV(event.GetEventObject().GetValue(), auto_monitor = True)
        
        self.imgpanel.z = self.mypv.get()[0:self.wpx*self.hpx].reshape((self.wpx,self.hpx))[self.roixy[0]:self.roixy[1],self.roixy[2]:self.roixy[3]]
        self.imgpanel.cmin = self.imgpanel.z.min()
        self.imgpanel.cmax = self.imgpanel.z.max()
        cmin_now = self.imgpanel.cmin
        cmax_now = self.imgpanel.cmax
        # update self.min_slider and self.max_slider,
        # as well as self.min_value_st and self.max_value_st
        self.min_value_st.SetLabel('%.1f' % (cmin_now))
        self.max_value_st.SetLabel('%.1f' % (cmax_now))
        self.min_slider.SetMin  (cmin_now)
        self.min_slider.SetMax  (cmax_now)
        self.min_slider.SetValue(cmin_now)
        self.max_slider.SetMin  (cmin_now)
        self.max_slider.SetMax  (cmax_now)
        self.max_slider.SetValue(cmax_now)
        self.imgcr_min_tc.SetValue('%.1f' % cmin_now)
        self.imgcr_max_tc.SetValue('%.1f' % cmax_now)
        self.imgpanel.im.set_clim(vmin = cmin_now, vmax= cmax_now)
        self.imgpanel.im.set_array(self.imgpanel.z)
        self.imgpanel.repaint()

    def onCheckRCM(self, event):
        if event.GetEventObject().IsChecked(): # checked
            self.rcmflag = '_r'
        else:
            self.rcmflag = ''
        cmap = self.cm_cb.GetValue() + self.rcmflag
        self.imgpanel.onSetcm(cmap)
        self.imgcm.onSetcm(cmap)
            
    def onSetColorRange(self, event):
        clickedobj = event.GetEventObject()
        if clickedobj.GetId() == self.min_slider.GetId():
            self.min_value_st.SetLabel('%.1f' % (clickedobj.GetValue()))
        elif clickedobj.GetId() == self.max_slider.GetId():
            self.max_value_st.SetLabel('%.1f' % (clickedobj.GetValue()))

        cmin = self.min_slider.GetValue()
        cmax = self.max_slider.GetValue()
        self.imgpanel.onSetCr(sorted([cmin, cmax]))

    def onBookmark(self, event):
        cmvalue = self.cm_cb.GetValue()
        if cmvalue not in self.cmlist_favo:
            self.cmlist_favo.append(cmvalue)
        ## update self.cm_cb choices field
        cmclass = self.cmlist_cb.GetValue()
        self.cm_cb.Clear()
        self.cm_cb.AppendItems(self.cmlist[cmclass])

    def onUnBookmark(self, event):
        cmvalue = self.cm_cb.GetValue()
        if cmvalue in self.cmlist_favo:
            self.cmlist_favo.remove(cmvalue)
        ## update self.cm_cb choices field
        cmclass = self.cmlist_cb.GetValue()
        self.cm_cb.Clear()
        self.cm_cb.AppendItems(self.cmlist[cmclass])

    def onAddPV(self, event):
        pvstr = self.imgsrc_tc.GetValue()
        if pvstr not in self.imgsrcPVlist:
            self.imgsrcPVlist.append(pvstr)

    def onRmPV(self, event):
        pvstr = self.imgsrc_tc.GetValue()
        if pvstr in self.imgsrcPVlist:
            self.imgsrcPVlist.remove(pvstr)


    def onSetColormap(self, event):
        self.imgpanel.onSetcm(event.GetEventObject().GetValue() + self.rcmflag)
        self.imgcm.onSetcm(event.GetEventObject().GetValue() + self.rcmflag)

    def onSetCmclass(self, event):
        cmclass = event.GetEventObject().GetValue()
        self.cm_cb.Clear()
        self.cm_cb.AppendItems(self.cmlist[cmclass])

class ConfigNoteBook(wx.Notebook):
    def __init__(self, parent, style = wx.NB_LEFT, *args, **kws):
        super(self.__class__, self).__init__(parent = parent, *args, **kws)
        self.parent = parent
        self.MakePages()
        
    def MakePages(self):
        self.imagePage    =    ImageConfigPanel(self)
        self.stylePage    =    StyleConfigPanel(self)
        self.controlPage  =  ControlConfigPanel(self)
        self.histPlotPage = HistPlotConfigPanel(self)

        self.AddPage(self.imagePage,    'Image'   )
        self.AddPage(self.stylePage,    'Style'   )
        self.AddPage(self.controlPage,  'Control' )
        self.AddPage(self.histPlotPage, 'HistPlot')

class AutoSavePanel(wx.Frame):
    def __init__(self, parent, **kwargs):
        super(self.__class__, self).__init__(parent = parent,
                id = wx.ID_ANY, style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX), **kwargs)
        self.parent = parent
        self.InitUI()

    def InitUI(self):
        self.createPanel()
        self.postInit()

    def createPanel(self):
        self.panel = wx.Panel(self)

        # format choosing
        sbox1 = funutils.createwxStaticBox(self.panel, label = 'Choose Saving Format', fontcolor = 'grey')
        sbsizer1 = wx.StaticBoxSizer(sbox1, orient = wx.HORIZONTAL)

        # data format: hdf5, asc, sdds, etc.
        datahbox        = wx.BoxSizer(wx.VERTICAL)
        data_st         = funutils.MyStaticText(self.panel, label = 'Data Format', fontsize = 12, fontcolor = 'blue')
        self.hdf5_chbox = funutils.MyCheckBox(self.panel, label = 'hdf5', fontsize = 12)
        self.asc_chbox  = funutils.MyCheckBox(self.panel, label = 'asc',  fontsize = 12)
        self.sdds_chbox = funutils.MyCheckBox(self.panel, label = 'sdds', fontsize = 12)
        datahbox.Add(data_st,         proportion = 0, flag = wx.ALL | wx.ALIGN_LEFT, border = 10)
        datahbox.Add(self.hdf5_chbox, proportion = 0, flag = wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.BOTTOM, border = 10)
        datahbox.Add(self.asc_chbox,  proportion = 0, flag = wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.BOTTOM, border = 10)
        datahbox.Add(self.sdds_chbox, proportion = 0, flag = wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.BOTTOM, border = 10)

        # image format: jpg, eps, png, etc.
        imagehbox      = wx.BoxSizer(wx.VERTICAL)
        image_st       = funutils.MyStaticText(self.panel, label = 'Image Format', fontsize = 12, fontcolor = 'blue')
        self.jpg_chbox = funutils.MyCheckBox(self.panel, label = 'jpg', fontsize = 12)
        self.eps_chbox = funutils.MyCheckBox(self.panel, label = 'eps', fontsize = 12)
        self.png_chbox = funutils.MyCheckBox(self.panel, label = 'png', fontsize = 12)
        imagehbox.Add(image_st,       proportion = 0, flag = wx.ALL | wx.ALIGN_LEFT, border = 10)
        imagehbox.Add(self.jpg_chbox, proportion = 0, flag = wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.BOTTOM, border = 10)
        imagehbox.Add(self.eps_chbox, proportion = 0, flag = wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.BOTTOM, border = 10)
        imagehbox.Add(self.png_chbox, proportion = 0, flag = wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.BOTTOM, border = 10)
        
        sbsizer1.Add(datahbox,  proportion = 1, flag = wx.EXPAND | wx.ALL, border = 8)
        sbsizer1.Add(wx.StaticLine(self.panel, style = wx.LI_VERTICAL), flag = wx.EXPAND | wx.TOP | wx.BOTTOM, border = 10)
        sbsizer1.Add(imagehbox, proportion = 1, flag = wx.EXPAND | wx.RIGHT | wx.TOP | wx.BOTTOM, border = 8)
        
        # save timer/io setup
        sbox2 = funutils.createwxStaticBox(self.panel, label = 'Options', fontcolor = 'grey')
        sbsizer2 = wx.StaticBoxSizer(sbox2, orient = wx.VERTICAL)

        ## saveto path
        saveto_st          = funutils.MyStaticText(self.panel, label = 'Save to', fontcolor = 'black', style = wx.ALIGN_LEFT)
        self.savetopath_tc = funutils.MyTextCtrl(self.panel, value = os.getcwd(), style = wx.CB_READONLY)
        choosepath_btn     = funutils.MyButton(self.panel, label = 'Browse')

        ## save freq setting
        savefreq_st1 = funutils.MyStaticText(self.panel, label = 'Save',   fontcolor = 'black', style = wx.ALIGN_LEFT) 
        savefreq_st2 = funutils.MyStaticText(self.panel, label = 'frame',  fontcolor = 'black', style = wx.ALIGN_LEFT) 
        savefreq_st3 = funutils.MyStaticText(self.panel, label = 'every',  fontcolor = 'black', style = wx.ALIGN_LEFT) 
        savefreq_st4 = funutils.MyStaticText(self.panel, label = 'second', fontcolor = 'black', style = wx.ALIGN_LEFT) 
        self.savefreqcnt_sp  = wx.SpinCtrl(self.panel, value = '1',  min = 1, max = 10, initial = 1, style = wx.SP_ARROW_KEYS)
        self.savefreqsec_fsp = fs.FloatSpin(self.panel, value = '2.0',  min_val = 1.0, max_val = 10000, increment = 0.5, digits = 1, style = fs.FS_LEFT)
        savefreq_st5 = funutils.MyStaticText(self.panel, label = 'Total Saved Record Number', fontcolor = 'black', style = wx.ALIGN_LEFT) 
        self.savefreqtot_sp  = wx.SpinCtrl(self.panel, value = '10',  min = 1, max = 10000, initial = 10, style = wx.SP_ARROW_KEYS)

        savegsbox = wx.GridBagSizer(10, 5)
        savegsbox.Add(saveto_st,            pos = (0, 0), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        savegsbox.Add(self.savetopath_tc,   pos = (0, 1), span = (1, 4), flag = wx.EXPAND | wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        savegsbox.Add(choosepath_btn,       pos = (0, 5), span = (1, 1), flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        savegsbox.Add(savefreq_st1,         pos = (1, 0), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        savegsbox.Add(self.savefreqcnt_sp,  pos = (1, 1), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        savegsbox.Add(savefreq_st2,         pos = (1, 2), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        savegsbox.Add(savefreq_st3,         pos = (1, 3), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        savegsbox.Add(self.savefreqsec_fsp, pos = (1, 4), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        savegsbox.Add(savefreq_st4,         pos = (1, 5), span = (1, 1), flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER, border = 10)
        savegsbox.Add(savefreq_st5,         pos = (2, 0), span = (1, 2), flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        savegsbox.Add(self.savefreqtot_sp,  pos = (2, 2), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)

        savegsbox.AddGrowableCol(1)
        savegsbox.AddGrowableCol(2)
        savegsbox.AddGrowableCol(3)
        savegsbox.AddGrowableCol(4)
        
        sbsizer2.Add(savegsbox, proportion = 0, flag = wx.EXPAND | wx.ALL, border = 10)
        
        # cmd hbox sizer
        cmdhbox = wx.BoxSizer(wx.HORIZONTAL)
        startsave_btn = funutils.MyButton(self.panel, label = 'Start SAVE', fontcolor = 'red')
        cancel_btn    = funutils.MyButton(self.panel, label = 'Cancel')
        cmdhbox.Add(cancel_btn,    proportion = 0, flag = wx.RIGHT, border = 10)
        cmdhbox.Add(startsave_btn, proportion = 0, flag = wx.TOP | wx.BOTTOM | wx.RIGHT, border = 0)

        # set sizers
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        mainsizer.Add(sbsizer1, proportion = 4, flag = wx.EXPAND | wx.ALL, border = 10)
        mainsizer.Add(sbsizer2, proportion = 3, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border = 10)
        mainsizer.Add(cmdhbox,  proportion = 0, flag = wx.ALIGN_RIGHT | wx.BOTTOM | wx.RIGHT, border = 10)

        self.panel.SetSizer(mainsizer)
        osizer = wx.BoxSizer(wx.VERTICAL)
        osizer.Add(self.panel, proportion = 1, flag = wx.EXPAND)
        self.SetSizerAndFit(osizer)
        
        # event bindings
        self.Bind(wx.EVT_BUTTON, self.onStart,      startsave_btn)
        self.Bind(wx.EVT_BUTTON, self.onCancel,     cancel_btn)
        self.Bind(wx.EVT_BUTTON, self.onChoosePath, choosepath_btn)

    def postInit(self):
        self.hdf5_chbox.SetValue(True)
        self.asc_chbox.SetValue(False)
        self.sdds_chbox.SetValue(False)
        self.jpg_chbox.SetValue(False)
        self.eps_chbox.SetValue(False)
        self.png_chbox.SetValue(False)

        # define a test timer for saving action
        #self.testtimer = wx.Timer(self)
        #self.Bind(wx.EVT_TIMER, self.onTestTimer, self.testtimer)
    #def onTestTimer(self, event):
    #    fmt='%Y-%m-%d %H:%M:%S %Z'
    #    print 'SAVE at ', time.strftime(fmt, time.localtime())

    def onStart(self, event):
        tperiod_setval = self.savefreqsec_fsp.GetValue() # sec
        cntpert_setval = self.savefreqcnt_sp.GetValue()
        total_setval   = self.savefreqtot_sp.GetValue()
        # return parameters
        self.parent.savedict['save_total_record'] = total_setval
        self.parent.savedict['save_tfreq_msec'  ] = tperiod_setval*1000.0/cntpert_setval
        self.parent.savedict['save_path'        ] = self.savetopath_tc.GetValue()
        self.parent.savedict['save_datfmt_hdf5' ] = self.hdf5_chbox.GetValue()
        self.parent.savedict['save_datfmt_asc'  ] = self.asc_chbox.GetValue()
        self.parent.savedict['save_datfmt_sdds' ] = self.sdds_chbox.GetValue()
        self.parent.savedict['save_imgfmt_jpg'  ] = self.jpg_chbox.GetValue()
        self.parent.savedict['save_imgfmt_eps'  ] = self.eps_chbox.GetValue()
        self.parent.savedict['save_imgfmt_png'  ] = self.png_chbox.GetValue()
        self.parent.saveTimerLife = total_setval
        
        #self.testtimer.Start(tperiod_setval/cntpert_setval*1000)
        self.parent.savetimer.Start(self.parent.savedict['save_tfreq_msec'])
        self.Close(True)

    def onCancel(self, event):
        self.Close(True)

    def onChoosePath(self, event):
        dlg = wx.DirDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            dirpath = dlg.GetPath()
            self.savetopath_tc.SetValue(dirpath)
        dlg.Destroy()

class AppConfigPanel(wx.Frame):
    def __init__(self, parent, **kwargs):
        super(self.__class__, self).__init__(parent = parent,
                id = wx.ID_ANY, style = wx.DEFAULT_FRAME_STYLE, **kwargs)
                #style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX), **kwargs)
        self.parent = parent
        self.InitUI()

    def InitUI(self):
        self.createMenu()
        self.createStatusbar()
        self.createNotebooks()

    def createMenu(self):
        pass

    def createStatusbar(self):
        pass

    def createNotebooks(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # config notebook
        self.configNB = ConfigNoteBook(self, style = wx.NB_TOP)

        # btns
        # btn style
        """
        lbtnfont = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        lbtnfont.SetPointSize(12)
        lbtnfont.SetWeight(wx.FONTWEIGHT_NORMAL)
        lbtnfontcolor = '#FF00B0'
        lbtnfacecolor = '#BFD9F0'
        self.applybtn.SetFont(lbtnfont)
        self.applybtn.SetForegroundColour(lbtnfontcolor)
        self.applybtn.SetBackgroundColour(lbtnfacecolor)
        """

        self.cancelbtn = wx.Button(self, label = 'Cancel')
        self.applybtn  = wx.Button(self, label = 'Apply' )
        self.okbtn     = wx.Button(self, label = 'OK'    )

        self.Bind(wx.EVT_BUTTON, self.onCancelData, self.cancelbtn)
        self.Bind(wx.EVT_BUTTON, self.onApplyData,  self.applybtn )
        self.Bind(wx.EVT_BUTTON, self.onUpdateData, self.okbtn    )

        hboxbtn = wx.BoxSizer(wx.HORIZONTAL)
        hboxbtn.Add(self.cancelbtn, proportion = 0, flag = wx.EXPAND |           wx.BOTTOM, border = 10)
        hboxbtn.Add(self.applybtn,  proportion = 0, flag = wx.EXPAND | wx.LEFT | wx.BOTTOM, border = 10)
        hboxbtn.Add(self.okbtn,     proportion = 0, flag = wx.EXPAND | wx.LEFT | wx.BOTTOM, border = 10)
        
        # set sizer
        vbox.Add(self.configNB, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 15)
        vbox.Add(hboxbtn, flag = wx.ALIGN_RIGHT | wx.RIGHT | wx.TOP, border = 15)
        vbox.Add((-1,10))
        self.SetSizerAndFit(vbox)

        # config pages references:
        self.imagePage    = self.configNB.imagePage
        self.stylePage    = self.configNB.stylePage
        self.controlPage  = self.configNB.controlPage
        self.histPlotPage = self.configNB.histPlotPage

        ## update imgsrcPVcb choices field of self.menuAppConfig
        imgsrcPVcb_point = self.controlPage.imgsrcPVcb
        imgsrcPVcb_point.Clear()
        imgsrcPVcb_point.AppendItems(self.parent.imgsrcPVlist)
        
        # main App panel (ImageViewer) reference
        self.thisapp = self.parent

    def onCancelData(self, event):
        self.Close(True)

    def onApplyData(self, event):
        self.setParams()

    def onUpdateData(self, event):
        self.setParams()
        self.Close(True)

    def setParams(self):
        # imagePage
        self.thisapp.imginifunc         = self.imagePage.imginifunccb.GetValue()
        self.thisapp.wpx                = int(self.imagePage.imgwpxtc.GetValue())
        self.thisapp.hpx                = int(self.imagePage.imghpxtc.GetValue())
        self.thisapp.roixy              = [0, self.thisapp.wpx, 0, self.thisapp.hpx]
        self.thisapp.save_path_str_head = os.path.expanduser(self.imagePage.pathtc.GetValue())
        self.thisapp.save_path_str      = os.path.join(self.thisapp.save_path_str_head, time.strftime('%Y%m%d', time.localtime()))
        self.thisapp.save_img_name_str  = self.imagePage.imgnamepretc.GetValue()
        self.thisapp.save_img_ext_str   = self.imagePage.imgnameexttc.GetValue()
        self.thisapp.save_dat_name_str  = self.imagePage.imgdatnamepretc.GetValue()
        self.thisapp.save_dat_ext_str   = self.imagePage.imgdatnameexttc.GetValue()
        self.thisapp.save_int_name_str  = self.imagePage.intnamepretc.GetValue()
        self.thisapp.save_int_ext_str   = self.imagePage.intnameexttc.GetValue()

        # stylePage
        self.thisapp.bkgdcolor    = funutils.hex2rgb(self.stylePage.bkgdcolortc.GetValue())
        self.thisapp.font         = self.stylePage.font
        self.thisapp.fontptsize   = self.stylePage.font.GetPointSize()
        self.thisapp.fontfamily   = self.stylePage.font.GetFamily()
        self.thisapp.fontstyle    = self.stylePage.font.GetStyle()
        self.thisapp.fontweight   = self.stylePage.font.GetWeight()
        self.thisapp.fontfacename = self.stylePage.font.GetFaceName()

        self.thisapp.font              = wx.Font(self.thisapp.fontptsize, self.thisapp.fontfamily, self.thisapp.fontstyle, self.thisapp.fontweight, faceName = self.thisapp.fontfacename)
        self.thisapp.fontptsize_large  = int(self.thisapp.fontptsize * 2.0)
        self.thisapp.fontptsize_big    = int(self.thisapp.fontptsize * 1.2)
        self.thisapp.fontptsize_normal = int(self.thisapp.fontptsize * 1.0)
        self.thisapp.fontptsize_small  = int(self.thisapp.fontptsize * 0.8)
        self.thisapp.fontptsize_tiny   = int(self.thisapp.fontptsize * 0.5)

        # controlPage
        self.thisapp.timer_freq = self.controlPage.freqtc.GetValue()
        self.thisapp.timer_msec = 1.0/self.thisapp.timer_freq * 1000
        self.thisapp.imgsrcPV   = self.controlPage.imgsrcPVcb.GetValue()

        # histPlotPage
        self.thisapp.heightRatio = float(self.histPlotPage.heightratiotc.GetValue())

        # update parameters
        self.thisapp.configdict['imgIniFunc'     ] = str(self.thisapp.imginifunc)
        self.thisapp.configdict['width'          ] = str(self.thisapp.wpx)
        self.thisapp.configdict['height'         ] = str(self.thisapp.hpx)
        self.thisapp.configdict['savePath'       ] = self.thisapp.save_path_str_head
        self.thisapp.configdict['saveImgName'    ] = self.thisapp.save_img_name_str
        self.thisapp.configdict['saveImgExt'     ] = self.thisapp.save_img_ext_str
        self.thisapp.configdict['saveImgDatName' ] = self.thisapp.save_dat_name_str
        self.thisapp.configdict['saveImgDatExt'  ] = self.thisapp.save_dat_ext_str
        self.thisapp.configdict['saveIntName'    ] = self.thisapp.save_int_name_str
        self.thisapp.configdict['saveIntExt'     ] = self.thisapp.save_int_ext_str
        self.thisapp.configdict['frequency'      ] = str(self.thisapp.timer_freq)  
        self.thisapp.configdict['imgsrcPV'       ] = self.thisapp.imgsrcPV
        self.thisapp.configdict['imgsrcPVlist'   ] = ' '.join(str(i) + ' ' for i in self.thisapp.imgsrcPVlist).rstrip()
        self.thisapp.configdict['cmFavor'        ] = ' '.join(str(i) + ' ' for i in self.thisapp.cmlist_favo).rstrip()
        self.thisapp.configdict['backgroundColor'] = self.stylePage.bkgdcolortc.GetValue()
        self.thisapp.configdict['heightRatio'    ] = str(self.thisapp.heightRatio)
        self.thisapp.configdict['fontpointsize'  ] = str(self.thisapp.fontptsize)
        self.thisapp.configdict['fontfamily'     ] = str(self.thisapp.fontfamily)
        self.thisapp.configdict['fontstyle'      ] = str(self.thisapp.fontstyle)
        self.thisapp.configdict['fontweight'     ] = str(self.thisapp.fontweight)
        self.thisapp.configdict['fontfacename'   ] = self.thisapp.fontfacename
        self.thisapp.xmlconfig.updateConfigs(self.thisapp.configdict)
        self.thisapp.onUpdateUI()
        
        # for debug
        #self.thisapp.printConfig()

class ImageConfigPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        super(self.__class__, self).__init__(parent = parent, id = wx.ID_ANY, **kwargs)
        self.parent = parent
        self.thisapp = self.parent.parent.parent
        self.initUI()
    
    def initUI(self):
        self.initConfig()
        self.createPanel()

    def initConfig(self):
        self.bkgdcolor   = wx.BLUE
        self.fontcolor   = wx.BLACK
        self.fontptsize  = 10
        self.fontweight  = wx.FONTWEIGHT_NORMAL

    def createPanel(self):
        #self.SetBackgroundColour(self.bkgdcolor)

        vboxsizer = wx.BoxSizer(wx.VERTICAL)
        
        """
        sbfont.SetPointSize(self.fontptsize)
        sbfont.SetWeight(self.fontweight)
        sbfontcolor = 'GREY'
        sbox.SetFont(sbfont)
        sbox.SetForegroundColour(sbfontcolor)
        sbsizer = wx.StaticBoxSizer(sbox, orient = wx.VERTICAL)
        """

        #### input items
        gs = wx.GridBagSizer(5, 5)
        
        imginifuncst    = wx.StaticText(self, label = u'Initial Image Function',   style = wx.ALIGN_LEFT)

        imgwpxst        = wx.StaticText(self, label = u'Image Width [px]',         style = wx.ALIGN_LEFT)
        imghpxst        = wx.StaticText(self, label = u'Image Height [px]',        style = wx.ALIGN_LEFT)
        pathst          = wx.StaticText(self, label = u'Save Figure to Path',      style = wx.ALIGN_LEFT)
        imgnameprest    = wx.StaticText(self, label = u'Image Name Prefix',        style = wx.ALIGN_LEFT)
        imgnameextst    = wx.StaticText(self, label = u'Image Name Extension',     style = wx.ALIGN_LEFT)
        intnameprest    = wx.StaticText(self, label = u'Intensity Name Prefix',    style = wx.ALIGN_LEFT)
        intnameextst    = wx.StaticText(self, label = u'Intensity Name Extension', style = wx.ALIGN_LEFT)
        imgdatnameprest = wx.StaticText(self, label = u'Image Data Name Prefix',   style = wx.ALIGN_LEFT)
        imgdatnameextst = wx.StaticText(self, label = u'Image Data Name Extension',style = wx.ALIGN_LEFT)

        self.imginifunccb    = wx.ComboBox(self, value = self.thisapp.imginifunc,        style = wx.CB_READONLY, choices = ['peaks', 'sinc'])

        self.imgwpxtc        = wx.TextCtrl(self, value = str(self.thisapp.wpx),          style = wx.TE_PROCESS_ENTER)
        self.imghpxtc        = wx.TextCtrl(self, value = str(self.thisapp.hpx),          style = wx.TE_PROCESS_ENTER)
        self.pathtc          = wx.TextCtrl(self, value = self.thisapp.save_path_str_head,style = wx.CB_READONLY     )
        self.pathtc.SetToolTip(wx.ToolTip('Fullpath (subdired by the date) the config file be saved.'))
        self.pathbtn         = wx.Button(self, label = 'Browse')
        self.imgnamepretc    = wx.TextCtrl(self, value = self.thisapp.save_img_name_str, style = wx.TE_PROCESS_ENTER)
        self.imgnameexttc    = wx.ComboBox(self, value = self.thisapp.save_img_ext_str,  style = wx.CB_READONLY, choices = ['.png','.jpg','.jpeg','.svg','.tiff','.eps','.pdf','.ps'])
        self.imgdatnamepretc = wx.TextCtrl(self, value = self.thisapp.save_dat_name_str, style = wx.TE_PROCESS_ENTER)
        self.imgdatnameexttc = wx.ComboBox(self, value = self.thisapp.save_dat_ext_str,  style = wx.CB_READONLY, choices = ['.asc','.hdf5','.sdds'])
        self.intnamepretc    = wx.TextCtrl(self, value = self.thisapp.save_int_name_str, style = wx.TE_PROCESS_ENTER)
        self.intnameexttc    = wx.ComboBox(self, value = self.thisapp.save_int_ext_str,  style = wx.CB_READONLY, choices = ['.png','.jpg','.jpeg','.svg','.tiff','.eps','.pdf','.ps'])


        gs.Add(imginifuncst,         pos = (0, 0), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gs.Add(self.imginifunccb,    pos = (0, 1), span = (1, 3), flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)

        gs.Add(imgwpxst,             pos = (1, 0), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gs.Add(self.imgwpxtc,        pos = (1, 1), span = (1, 3), flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gs.Add(imghpxst,             pos = (2, 0), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gs.Add(self.imghpxtc,        pos = (2, 1), span = (1, 3), flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gs.Add(pathst,               pos = (3, 0), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gs.Add(self.pathtc,          pos = (3, 1), span = (1, 2), flag = wx.EXPAND | wx.LEFT  | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gs.Add(self.pathbtn,         pos = (3, 3), span = (1, 1), flag = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gs.Add(imgnameprest,         pos = (4, 0), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gs.Add(self.imgnamepretc,    pos = (4, 1), span = (1, 3), flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gs.Add(imgnameextst,         pos = (5, 0), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gs.Add(self.imgnameexttc,    pos = (5, 1), span = (1, 3), flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)

        gs.Add(imgdatnameprest,      pos = (6, 0), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gs.Add(self.imgdatnamepretc, pos = (6, 1), span = (1, 3), flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gs.Add(imgdatnameextst,      pos = (7, 0), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gs.Add(self.imgdatnameexttc, pos = (7, 1), span = (1, 3), flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)

        gs.Add(intnameprest,         pos = (8, 0), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gs.Add(self.intnamepretc,    pos = (8, 1), span = (1, 3), flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gs.Add(intnameextst,         pos = (9, 0), span = (1, 1), flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gs.Add(self.intnameexttc,    pos = (9, 1), span = (1, 3), flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gs.AddGrowableCol(1, 2)
        gs.AddGrowableCol(2, 0)
        vboxsizer.Add(gs, proportion = 0, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT | wx.TOP, border = 15)

        vboxsizer.Add((-1, 10))
        
        ## set boxsizer
        self.SetSizer(vboxsizer)
        
        ## bind events
        self.Bind(wx.EVT_TEXT_ENTER, self.onUpdateParams,  self.imgwpxtc)
        self.Bind(wx.EVT_TEXT_ENTER, self.onUpdateParams,  self.imghpxtc)
        self.Bind(wx.EVT_BUTTON,     self.onChooseDirpath, self.pathbtn )

    def onChooseDirpath(self, event):
        dlg = wx.DirDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            dirpath = dlg.GetPath()
            self.pathtc.SetValue(dirpath)
        dlg.Destroy()

    def onUpdateParams(self, event):
        obj = event.GetEventObject() 
        try:
            int(obj.GetValue())
        except ValueError:
            dial = wx.MessageDialog(self, message = u"Error, please input an integer number!",
                    caption = u"Input Error", 
                    style = wx.OK | wx.CANCEL | wx.ICON_ERROR | wx.CENTRE)
            if dial.ShowModal() == wx.ID_OK:
                obj.SetValue('')
                dial.Destroy()

class StyleConfigPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        super(self.__class__, self).__init__(parent = parent, id = wx.ID_ANY, **kwargs)
        self.parent = parent
        self.thisapp = self.parent.parent.parent
        self.initUI()
    
    def initUI(self):
        self.initConfig()
        self.createPanel()

    def initConfig(self):
        self.bkgdcolor   = wx.BLUE
        self.fontcolor   = wx.BLACK
        self.fontptsize  = 10
        self.fontweight  = wx.FONTWEIGHT_NORMAL
        self.font        = self.thisapp.font

    def createPanel(self):
        vboxsizer = wx.BoxSizer(wx.VERTICAL)
        
        bkgdcolorst  = funutils.MyStaticText(self, label = u'Background Color',  style = wx.ALIGN_LEFT)
        self.bkgdcolortc  = wx.TextCtrl(self, value = funutils.rgb2hex(self.thisapp.bkgdcolor).upper(), style = wx.CB_READONLY)
        self.bkgdcolorbtn = wx.Button(self, label = 'Choose Color', size = (130, -1))

        fontst  = funutils.MyStaticText(self, label = u'Font',  style = wx.ALIGN_LEFT)
        self.chosenfonttc  = funutils.MyTextCtrl(self, value = u'Do it Pythonicly.', style = wx.TE_READONLY, font = self.font)
        self.choosefontbtn = funutils.MyButton(self, label = 'Choose Font', size = (130, -1))

        gsstyle = wx.GridBagSizer(5, 5)
        gsstyle.Add(bkgdcolorst,       pos = (0, 0), span = (1, 1), flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = 10)
        gsstyle.Add(self.bkgdcolortc,  pos = (0, 1), span = (1, 2), flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gsstyle.Add(self.bkgdcolorbtn, pos = (0, 3), span = (1, 1), flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gsstyle.Add(fontst,       pos = (1, 0), span = (1, 1), flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border = 10)
        gsstyle.Add(self.chosenfonttc,  pos = (1, 1), span = (1, 2), flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gsstyle.Add(self.choosefontbtn, pos = (1, 3), span = (1, 1), flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gsstyle.AddGrowableCol(1, 0)

        vboxsizer.Add(gsstyle, flag = wx.EXPAND | wx.ALL, border = 15)

        vboxsizer.Add((-1, 10))
        
        ## set boxsizer
        self.SetSizer(vboxsizer)
        
        ## bind events
        self.Bind(wx.EVT_BUTTON, self.onChooseColor, self.bkgdcolorbtn )
        self.Bind(wx.EVT_BUTTON, self.onChooseFont,  self.choosefontbtn)

    def onChooseColor(self, event):
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True) # only windows
        if dlg.ShowModal() == wx.ID_OK:
            color = dlg.GetColourData().GetColour()
            self.bkgdcolortc.SetValue(color.GetAsString(wx.C2S_HTML_SYNTAX))
        dlg.Destroy()

    def onChooseFont(self, event):
        fontdata = wx.FontData()
        fontdata.EnableEffects(True)
        fontdata.SetInitialFont(self.font)
        dial = wx.FontDialog(self, fontdata)
        if dial.ShowModal() == wx.ID_OK:
            self.font = dial.GetFontData().GetChosenFont()
            self.chosenfonttc.SetFont(self.font)
        else:
            dial.Destroy()

class ControlConfigPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        super(self.__class__, self).__init__(parent = parent, id = wx.ID_ANY, **kwargs)
        self.parent = parent
        self.thisapp = self.parent.parent.parent
        self.initUI()

    def initUI(self):
        self.initConfig()
        self.createPanel()

    def initConfig(self):
        self.bkgdcolor   = wx.BLUE
        self.fontcolor   = wx.BLACK
        self.fontptsize  = 10
        self.fontweight  = wx.FONTWEIGHT_NORMAL

    def createPanel(self):
        vboxsizer = wx.BoxSizer(wx.VERTICAL)
        
        # frequency
        freqst       = wx.StaticText(self, label = u'Monitor Frequency [Hz]',   style = wx.ALIGN_RIGHT)
        #self.freqtc  = wx.SpinCtrl(self, value = str(self.thisapp.timer_freq),  min = 1, max = 50, initial = 1, style = wx.SP_ARROW_KEYS)
        self.freqtc  = fs.FloatSpin(self, value = str(self.thisapp.timer_freq),  min_val = 0.1, max_val = 50, increment = 0.05, digits = 2, style = fs.FS_LEFT)

        # PV list
        imgsrcPVst      = wx.StaticText(self, label = u'Image PV Name', style = wx.ALIGN_RIGHT)
        self.imgsrcPVcb = wx.ComboBox(self, value = self.thisapp.imgsrcPV,  style = wx.CB_READONLY,
                                            choices = sorted(self.thisapp.imgsrcPVlist))

        gsctrl = wx.GridBagSizer(5, 5)
        gsctrl.Add(freqst,          pos = (0, 0), span = (1, 1), flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gsctrl.Add(self.freqtc,     pos = (0, 2), span = (1, 2), flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gsctrl.Add(imgsrcPVst,      pos = (1, 0), span = (1, 1), flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gsctrl.Add(self.imgsrcPVcb, pos = (1, 2), span = (1, 2), flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gsctrl.AddGrowableCol(2, 0)

        vboxsizer.Add(gsctrl, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border = 15)
        
        vboxsizer.Add((-1, 10))
        
        ## set boxsizer
        self.SetSizer(vboxsizer)

class HistPlotConfigPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        super(self.__class__, self).__init__(parent = parent, id = wx.ID_ANY, **kwargs)
        self.parent = parent
        self.thisapp = self.parent.parent.parent
        self.initUI()

    def initUI(self):
        self.initConfig()
        self.createPanel()

    def initConfig(self):
        self.bkgdcolor   = wx.BLUE
        self.fontcolor   = wx.BLACK
        self.fontptsize  = 10
        self.fontweight  = wx.FONTWEIGHT_NORMAL

    def createPanel(self):
        vboxsizer = wx.BoxSizer(wx.VERTICAL)

        # height ratio
        heightratiost       = wx.StaticText(self, label = u'Height Ratio',   style = wx.ALIGN_RIGHT)
        self.heightratiotc  = fs.FloatSpin(self, value = str(self.thisapp.heightRatio),  min_val = 0.0, max_val = 0.95, increment = 0.05, digits = 2, style = fs.FS_LEFT)

        gshist = wx.GridBagSizer(5, 5)
        gshist.Add(heightratiost,      pos = (0, 0), span = (1, 1), flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gshist.Add(self.heightratiotc, pos = (0, 2), span = (1, 2), flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        gshist.AddGrowableCol(2, 0)

        vboxsizer.Add(gshist, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border = 15 )

        vboxsizer.Add((-1, 10))

        ## set boxsizer
        self.SetSizer(vboxsizer)

class ShowIntPanel(wx.Frame):
    def __init__(self, parent, **kwargs):
        super(self.__class__, self).__init__(parent = parent,
                id = wx.ID_ANY, style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX), **kwargs)
        self.parent = parent
        self.x = []
        self.y = []
        self.cnt = 0
        self.InitUI()
    
    def InitUI(self):
        self.createMenu()
        self.createPanel()
        self.createStatusbar()

    def createMenu(self):
        pass

    def createStatusbar(self):
        pass

    def createPanel(self):
        self.panel = wx.Panel(self, id = wx.ID_ANY)
        self.panel.SetBackgroundColour(self.parent.bkgdcolor)

        vbox = wx.BoxSizer(wx.VERTICAL)
        
        sbox = wx.StaticBox(self.panel, id = wx.ID_ANY, 
                label = u'Intensity Monitor', style = wx.ALIGN_LEFT)
        sbfont = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        sbfont.SetPointSize(8)
        sbfont.SetWeight(wx.FONTWEIGHT_NORMAL)
        sbfontcolor = 'GREY'
        sbox.SetFont(sbfont)
        sbox.SetForegroundColour(sbfontcolor)
        sbsizer = wx.StaticBoxSizer(sbox, orient = wx.VERTICAL)

        self.intdisp = ImagePanelxy(self.panel, figsize = (9,7), dpi = 80, bgcolor = self.parent.bkgdcolor)
        sbsizer.Add(self.intdisp, flag = wx.ALIGN_CENTER | wx.ALL, border = 10)

        #### btns
        self.daqbtn  = wx.Button(self.panel, label = 'Start')
        self.savebtn = wx.Button(self.panel, label = 'Save' )
        self.Bind(wx.EVT_BUTTON, self.onTimerControl, self.daqbtn )
        self.Bind(wx.EVT_BUTTON, self.onSaveFigure,   self.savebtn)
        hboxbtn = wx.BoxSizer(orient = wx.HORIZONTAL)
        hboxbtn.Add(self.daqbtn,  proportion = 1, flag = wx.EXPAND | wx.BOTTOM, border = 10)
        hboxbtn.Add(self.savebtn, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.BOTTOM, border = 10)
        sbsizer.Add(hboxbtn, flag = wx.ALIGN_RIGHT | wx.ALL, border = 10)

        vbox.Add(sbsizer, flag = wx.ALL, border = 15)

        self.panel.SetSizer(vbox)
        osizer = wx.BoxSizer(wx.HORIZONTAL)
        osizer.Add(self.panel)
        self.SetSizerAndFit(osizer)

        ## timer for update plotting curve
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onUpdate, self.timer)

    def onTimerControl(self, event):
        label = event.GetEventObject().GetLabel()
        if self.timer.IsRunning():
            self.timer.Stop()
            self.daqbtn.SetLabel('Start')
        else:
            self.timer.Start(self.parent.timer_msec)
            self.daqbtn.SetLabel('Stop')

    def onSaveFigure(self, event):
        if not os.path.exists(self.parent.save_path_str):
            os.system('mkdir -p' + ' ' + self.parent.save_path_str)
        filelabel = time.strftime('%H%m%S', time.localtime())
        savetofilename = self.parent.save_path_str + '/' + self.parent.save_int_name_str + filelabel + self.parent.save_int_ext_str
        self.intdisp.figure.savefig(savetofilename)

    def onUpdate(self, event):
        self.cnt += 1
        self.x.append(self.cnt)
        self.y.append(float(self.parent.inten_val.GetLabel()))
        self.intdisp.x = np.array(self.x)
        self.intdisp.y = np.array(self.y)
        self.intdisp.xyplot.set_marker('o')
        self.intdisp.xyplot.set_markersize(4)
        self.intdisp.xyplot.set_markerfacecolor('b')
        self.intdisp.xyplot.set_markeredgecolor('b')
        self.intdisp.xyplot.set_linestyle('-')
        self.intdisp.xyplot.set_color('r')
        self.intdisp.repaint()

class ImagePanel(wx.Panel):
    def __init__(self, parent, figsize, dpi, bgcolor, heightratio = 0.4, func = 'peaks', **kwargs):
        #super(self.__class__, self).__init__(parent = parent, **kwargs)
        wx.Panel.__init__(self, parent, **kwargs)
        self.parent   = parent
        self.figsize  = figsize
        self.dpi      = dpi
        self.bgcolor  = bgcolor
        self.hratio   = heightratio
        self.func     = func
        self.figure   = Figure(self.figsize, self.dpi)
        self.canvas   = FigureCanvasWxAgg(self, -1, self.figure)
        self.cmaptype = 'jet'
        self.setColor(self.bgcolor)
        self.onGetData()
        self.onConfigPlot()
        self.doPlot()
        wx.CallAfter(self.fitCanvas) # fit canvas size after initialization

        # resize figure when size event trigged
        self.Bind(wx.EVT_SIZE, self.onSize)

        self.canvas.mpl_connect('button_press_event',   self.onPress  )
        self.canvas.mpl_connect('button_release_event', self.onRelease)
        self.canvas.mpl_connect('motion_notify_event',  self.onMotion )

    def onConfigPlot(self):
        pass

    def onPress(self, event):
        pass
        #print("%d,%d" % (event.xdata, event.ydata))

    def onRelease(self, event):
        pass
        #print("%d,%d" % (event.xdata, event.ydata))

    def onMotion(self, event):
        try:
            self.parent.GetParent().pos_val.SetLabel("(%.4f,%.4f)" % (event.xdata, event.ydata))
        except TypeError:
            pass

    def setHratio(self, hratio):
        self.hratio = hratio

    def setColor(self, rgbtuple = None):
        """Set figure and canvas colours to be the same."""
        if rgbtuple is None:
            rgbtuple = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE).Get()
        clr = [c/255. for c in rgbtuple]
        self.figure.set_facecolor(clr)
        self.figure.set_edgecolor(clr)
        self.canvas.SetBackgroundColour(wx.Colour(*rgbtuple))

    def repaint(self):
        self.onSetHist()
        self.figure.canvas.draw_idle()

    def onSetcm(self, cmap):
        self.cmaptype = cmap
        self.im.set_cmap(self.cmaptype)
        self.im.set_array(self.z)
        self.repaint()

    def onSetHist(self):
        self.histx = self.z.sum(axis = 0)
        self.histy = self.z.sum(axis = 1)
        idxmaxx, idxmaxy = np.where(self.histx==self.histx.max()), np.where(self.histy==self.histy.max())
        self.maxidx, self.maxidy = idxmaxx[0][0], idxmaxy[0][0]
        self.xx = np.arange(self.histx.size) + 1
        self.yy = np.arange(self.histy.size) + 1
        self.linex.set_xdata(self.xx)
        self.linex.set_ydata(self.histx/self.histx.max()*self.maxidy*self.hratio)
        self.liney.set_xdata(self.histy/self.histy.max()*self.maxidx*self.hratio)
        self.liney.set_ydata(self.yy)
        self.xyscalar = [self.xx.min(), self.xx.max(), self.yy.min(), self.yy.max()]
        self.im.set_extent(self.xyscalar)

    def onSetCr(self, crange):
        self.im.set_clim(crange)
        self.repaint()

    def doPlot(self):
        if not hasattr(self, 'axes'):
            self.axes = self.figure.add_subplot(111)
        self.linex, = self.axes.plot(self.xx, self.histx/self.histx.max()*self.maxidy*self.hratio, 'w--')
        self.liney, = self.axes.plot(self.histy/self.histy.max()*self.maxidx*self.hratio, self.yy, 'w--')

        #self.axes.set_title(r'$f(x,y)=\sin x + \cos y$')
        self.im = self.axes.imshow(self.z, aspect = 'equal', cmap = plt.get_cmap(self.cmaptype), 
                                   origin = 'lower left', vmin = self.cmin, vmax = self.cmax)
        self.im.set_extent(self.xyscalar)
        self.linex.set_visible(False)
        self.liney.set_visible(False)
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
        
        self.histx = self.z.sum(axis = 0)
        self.histy = self.z.sum(axis = 1)
        self.xx = np.arange(self.histx.size)+1
        self.yy = np.arange(self.histy.size)+1
        idxmaxx, idxmaxy = np.where(self.histx==self.histx.max()), np.where(self.histy==self.histy.max())
        self.maxidx, self.maxidy = idxmaxx[0][0], idxmaxy[0][0]
        self.xyscalar = [self.xx.min(), self.xx.max(), self.yy.min(), self.yy.max()]


    def fitCanvas(self):
        self.canvas.SetSize(self.GetSize())
        self.figure.set_tight_layout(True)
        self.figure.subplots_adjust(top  = 0.9999, bottom = 0.0001, 
                                    left = 0.0001, right  = 0.9999)

    def onSize(self, event):
        self.canvas.SetSize(self.GetSize())
        self.figure.set_tight_layout(True)
        self.figure.subplots_adjust(top  = 0.9999, bottom = 0.0001, 
                                    left = 0.0001, right  = 0.9999)
        #heresize = self.GetSize()
        #self.figure.set_size_inches(float(heresize[0])/self.figure.get_dpi(),
        #                            float(heresize[1])/self.figure.get_dpi())

class ChooseROIFrame(wx.Frame):
    def __init__(self, parent, imgsrcptn, **kwargs):
        super(self.__class__, self).__init__(parent = parent,
                id = wx.ID_ANY, style = wx.DEFAULT_FRAME_STYLE, **kwargs)
                #style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX), **kwargs)
        self.parent = parent
        self.imgpanel = imgsrcptn
        self.InitUI()

    def InitUI(self):
        self.createMenu()
        self.createStatusbar()
        self.createPanel(self.imgpanel)

    def createMenu(self):
        pass

    def createStatusbar(self):
        pass

    def createPanel(self, imgsrcptn):
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.roiPanel = ChooseROIPanel(self, figsize = (7,7), dpi = 80)
        self.roiPanel.doPlot(imgsrcptn)

        self.cancelbtn = wx.Button(self, label = 'Cancel')
        self.okbtn     = wx.Button(self, label = 'OK'    )

        self.Bind(wx.EVT_BUTTON, self.onCancel, self.cancelbtn)
        self.Bind(wx.EVT_BUTTON, self.onGetROI, self.okbtn    )

        hboxbtn = wx.BoxSizer(wx.HORIZONTAL)
        hboxbtn.Add(self.cancelbtn, proportion = 0, flag = wx.EXPAND |           wx.BOTTOM, border = 10)
        hboxbtn.Add(self.okbtn,     proportion = 0, flag = wx.EXPAND | wx.LEFT | wx.BOTTOM, border = 10)
 
        vbox.Add(self.roiPanel, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 15)
        vbox.Add(hboxbtn, flag = wx.ALIGN_RIGHT | wx.RIGHT | wx.TOP, border = 15)
        vbox.Add((-1,10))
        self.SetSizerAndFit(vbox)

        # get and draw ROI box
        self.is_pressed = False
        self.patch = []
        self.x0, self.y0 = None, None
        self.x1, self.y1 = None, None
        self.figure = self.roiPanel.figure
        self.canvas = self.roiPanel.canvas
        self.axes   = self.roiPanel.axes
        self.canvas.mpl_connect('button_press_event',   self.onPress  )
        self.canvas.mpl_connect('button_release_event', self.onRelease)
        #self.canvas.mpl_connect('motion_notify_event',  self.onMotion )

    def onCancel(self, event):
        self.Close(True)

    def onGetROI(self, event):
        try:
            self.parent.roixy = sorted([int(self.y0), int(self.y1)]) + sorted([int(self.x0), int(self.x1)])
        except TypeError:
            dial = wx.MessageDialog(self, message = u"Please simply draw box on image to get ROI, then click OK.",
                    caption = u"Fetch ROI Warning", 
                    style = wx.OK | wx.ICON_QUESTION | wx.CENTRE)
            if dial.ShowModal() == wx.ID_OK:
                dial.Destroy()
                return
        self.Close(True)

    def onPress(self, event):
        #self.is_pressed = True
        self.x0 = event.xdata
        self.y0 = event.ydata

    def onRelease(self, event):
        #self.is_pressed = False
        self.x1 = event.xdata
        self.y1 = event.ydata
        self.rect = Rectangle((self.x0, self.y0), 
                          self.x1 - self.x0, 
                          self.y1 - self.y0,
                          fill = False, color = 'w', linestyle = 'dashed',
                          linewidth = 1)
        self.patch.append(self.rect)
        [self.axes.add_patch(inspatch) for inspatch in self.patch]
        self.figure.canvas.draw()
    """
    def onMotion(self, event):
        if self.is_pressed == True:
            try:
                self.x1 = event.xdata
                self.y1 = event.ydata
                self.rect = Rectangle((self.x0, self.y0), 
                                  self.x1 - self.x0, 
                                  self.y1 - self.y0,
                                  fill = False, color = 'w', linestyle = 'dashed',
                                  linewidth = 1)
                self.patch.pop()
                self.patch.append(self.rect)
                [self.axes.add_patch(inspatch) for inspatch in self.patch]
                self.figure.canvas.draw_idle()
            except:
                pass
    """

class ChooseROIPanel(wx.Panel):
    def __init__(self, parent, figsize, dpi, **kwargs):
        super(self.__class__, self).__init__(parent = parent, **kwargs)
        self.parent  = parent
        self.figsize = figsize
        self.dpi     = dpi
        self.figure  = Figure(self.figsize, self.dpi)
        self.canvas  = FigureCanvasWxAgg(self, -1, self.figure)
        self.Bind(wx.EVT_SIZE, self.onSize)
    
    def doPlot(self, imgsrcptn):
        ## imgsrcptn: object reference for image, from which ROI would be got
        # set background color
        self.setColor(imgsrcptn.bgcolor)

        # set image
        if not hasattr(self, 'axes'):
            self.axes = self.figure.add_subplot(111)
        self.im = self.axes.imshow(imgsrcptn.z, aspect = 'equal', cmap = plt.get_cmap(imgsrcptn.cmaptype), 
                                   origin = 'lower left', vmin = imgsrcptn.cmin, vmax = imgsrcptn.cmax)
        self.im.set_extent(imgsrcptn.xyscalar)
        self.figure.canvas.draw()

    def onSize(self, event):
        self.canvas.SetSize(self.GetSize())
        self.figure.set_tight_layout(True)
        self.figure.subplots_adjust(top  = 0.9999, bottom = 0.0001, 
                                    left = 0.0001, right  = 0.9999)

    def setColor(self, rgbtuple = None):
        """Set figure and canvas colours to be the same."""
        if rgbtuple is None:
            rgbtuple = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE).Get()
        clr = [c/255. for c in rgbtuple]
        self.figure.set_facecolor(clr)
        self.figure.set_edgecolor(clr)
        self.canvas.SetBackgroundColour(wx.Colour(*rgbtuple))

class ImagePanelxy(wx.Panel):
    def __init__(self, parent, figsize, dpi, bgcolor, **kwargs):
        #super(self.__class__, self).__init__(parent = parent, **kwargs)
        wx.Panel.__init__(self, parent, **kwargs)
        self.parent  = parent
        self.figsize = figsize
        self.dpi     = dpi
        self.bgcolor = bgcolor
        self.figure = Figure(self.figsize, self.dpi)
        self.canvas = FigureCanvasWxAgg(self, -1, self.figure)
        self.setColor(self.bgcolor)
        self.onGetData()
        self.onConfigPlot()
        self.doPlot()
        wx.CallAfter(self.fitCanvas) # fit canvas size after initialization

        self.Bind(wx.EVT_SIZE, self.onSize)

        self.canvas.mpl_connect('button_press_event',   self.onPress  )
        self.canvas.mpl_connect('button_release_event', self.onRelease)
        self.canvas.mpl_connect('motion_notify_event',  self.onMotion )

    def onConfigPlot(self):
        pass

    def onUpdatePlot(self):
        pass

    def onPress(self, event):
        pass

    def onRelease(self, event):
        pass

    def onMotion(self, event):
        pass
        """
        try:
            self.parent.GetParent().pos_val.SetLabel("(%.4f,%.4f)" % (event.xdata, event.ydata))
        except TypeError:
            pass
        """

    def setColor(self, rgbtuple = None):
        """Set figure and canvas colours to be the same."""
        if rgbtuple is None:
            rgbtuple = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE).Get()
        clr = [c/255. for c in rgbtuple]
        self.figure.set_facecolor(clr)
        self.figure.set_edgecolor(clr)
        self.canvas.SetBackgroundColour(wx.Colour(*rgbtuple))

    def repaint(self):
        self.xyplot.set_xdata(self.x)
        self.xyplot.set_ydata(self.y)
        self.axes.set_xlim(min(self.x), max(self.x))
        self.axes.set_ylim(min(self.y), max(self.y))
        self.figure.canvas.draw_idle()

    def doPlot(self):
        if not hasattr(self, 'axes'):
            self.axes = self.figure.add_subplot(111)
        self.xyplot, = self.axes.plot(self.x, self.y, '.', markersize = 1)
        self.figure.canvas.draw()

    def onGetData(self):
        #x = np.linspace(-np.pi, np.pi, 100)
        #y = np.sin(x)
        x = y = [] 
        self.x, self.y = x, y

    def fitCanvas(self):
        self.canvas.SetSize(self.GetSize())
        self.figure.set_tight_layout(True)
        self.figure.subplots_adjust(top  = 0.9999, bottom = 0.0001, 
                                    left = 0.0001, right  = 0.9999)

    def onSize(self, event):
        self.canvas.SetSize(self.GetSize())
        self.figure.set_tight_layout(True)
        self.figure.subplots_adjust(top  = 0.9999, bottom = 0.0001, 
                                    left = 0.0001, right  = 0.9999)

class ImageColorMap(wx.Panel):
    def __init__(self, parent, figsize, dpi, bgcolor, **kwargs):
        super(self.__class__, self).__init__(parent = parent, **kwargs)
        self.parent  = parent
        self.figsize = figsize
        self.dpi     = dpi
        self.bgcolor = bgcolor
        self.cmin = 0
        self.cmax = 1
        self.figure = Figure(self.figsize, self.dpi)
        self.canvas = FigureCanvasWxAgg(self, -1, self.figure)
        self.cmaptype = 'jet'
        self.setColor(self.bgcolor)
        self.onGetData()
        self.doPlot()
        wx.CallAfter(self.fitCanvas)

        # resize figure when size event trigged
        self.Bind(wx.EVT_SIZE, self.onSize)

    def setColor(self, rgbtuple = None):
        """Set figure and canvas colours to be the same."""
        if rgbtuple is None:
            rgbtuple = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE).Get()
        clr = [c/255. for c in rgbtuple]
        self.figure.set_facecolor(clr)
        self.figure.set_edgecolor(clr)
        self.canvas.SetBackgroundColour(wx.Colour(*rgbtuple))

    def repaint(self):
        self.figure.canvas.draw_idle()

    def onSetCr(self, crange):
        self.im.set_clim(crange)
        self.repaint()

    def onSetcm(self, cmap):
        self.cmaptype = cmap
        self.im.set_cmap(self.cmaptype)
        self.repaint()

    def doPlot(self):
        if not hasattr(self, 'axes'):
            self.axes = self.figure.add_subplot(111)
        self.im = self.axes.imshow(self.z, cmap = plt.get_cmap(self.cmaptype),
                                   origin = 'lower left', vmin = self.cmin, vmax = self.cmax)
        self.axes.set_axis_off()
        self.figure.canvas.draw()

    def onGetData(self):
        g = np.linspace(self.cmin, self.cmax, 80)
        self.z = np.vstack((g,g))

    def fitCanvas(self):
        self.canvas.SetSize(self.GetSize())
        self.figure.set_tight_layout(True)
        self.figure.subplots_adjust(top  = 0.9999, bottom = 0.0001, 
                                    left = 0.0001, right  = 0.9999)

    def onSize(self, event):
        self.canvas.SetSize(self.GetSize())
        self.figure.set_tight_layout(True)
        self.figure.subplots_adjust(top  = 0.9999, bottom = 0.0001, 
                                    left = 0.0001, right  = 0.9999)

def main():
    app = wx.App(redirect = False)
    myframe = ImageViewer(None, title = 'ImageViewer --- Another Profile Monitor')
    myframe.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
