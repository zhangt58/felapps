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
        parseutils.ConfigFile.__init__(
            self, infilename=infilename,
            *args, **kwargs)

    def parseConfigs(self):
        tree = ET.parse(self.xmlfile)
        root = tree.getroot()
        self.root = root
        self.tree = tree
        namelist_image = {}
        namelist_control = {}
        namelist_style = {}
        namelist_histplot = {}
        namestring_image = ['width', 'height', 'savePath', 'saveImgName',
                            'saveImgExt', 'saveImgDatName', 'saveImgDatExt',
                            'saveIntName', 'saveIntExt', 'cmFavor',
                            'imgIniFunc']
        namestring_control = ['frequency', 'imgsrcPV', 'imgsrcPVlist',
                              'libcaPath', 'caAddrAuto', 'caAddrList',
                              'caArrayBytes', 'pixelSize']
        namestring_histplot = ['heightRatio']
        namestring_style = ['backgroundColor', 'fontpointsize', 'fontfamily',
                            'fontstyle', 'fontweight', 'fontfacename']
        for group in root.iter('group'):
            if group.get('name') == 'Image':
                namelist_image = {s: group.find('properties').get(s)
                                  for s in namestring_image}
            elif group.get('name') == 'Control':
                namelist_control = {s: group.find('properties').get(s)
                                    for s in namestring_control}
            elif group.get('name') == 'Style':
                namelist_style = {s: group.find('properties').get(s)
                                  for s in namestring_style}
            elif group.get('name') == 'HistPlot':
                namelist_histplot = {s: group.find('properties').get(s)
                                     for s in namestring_histplot}
        self.namelist.update(namelist_image)
        self.namelist.update(namelist_control)
        self.namelist.update(namelist_style)
        self.namelist.update(namelist_histplot)


class ImageViewer(wx.Frame):
    def __init__(self,
                 parent,
                 config='config.xml',
                 size=(800, 600),
                 appversion='1.0',
                 **kwargs):
        super(self.__class__, self).__init__(
            parent=parent, size=size,
            id=wx.ID_ANY,
            **kwargs)  #style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        self.parent = parent
        self.appversion = appversion
        self.cmlist_unis = ['viridis', 'inferno', 'plasma', 'magma']
        self.cmlist_seq1 = ['Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys',
                            'Oranges', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd',
                            'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu',
                            'YlOrBr', 'YlOrRd']
        self.cmlist_seq2 = ['afmhot', 'autumn', 'bone', 'cool', 'copper',
                            'gist_heat', 'gray', 'hot', 'pink', 'spring',
                            'summer', 'winter']
        self.cmlist_dive = ['BrBG', 'bwr', 'coolwarm', 'PiYG', 'PRGn', 'PuOr',
                            'RdBu', 'RdGy', 'RdYlBu', 'RdYlGn', 'Spectral',
                            'seismic']
        self.cmlist_qual = ['Accent', 'Dark2', 'Paired', 'Pastel1', 'Pastel2',
                            'Set1', 'Set2', 'Set3']
        self.cmlist_misc = ['gist_earth', 'terrain', 'ocean', 'gist_stern',
                            'brg', 'CMRmap', 'cubehelix', 'gnuplot',
                            'gnuplot2', 'gist_ncar', 'nipy_spectral', 'jet',
                            'rainbow', 'gist_rainbow', 'hsv', 'flag', 'prism']
        self.cmlist = {'Sequential-NEW': self.cmlist_unis,
                       'Sequential-I': self.cmlist_seq1,
                       'Sequential-II': self.cmlist_seq2,
                       'Diverging': self.cmlist_dive,
                       'Qualitative': self.cmlist_qual,
                       'Miscellaneous': self.cmlist_misc}

        self.rcmflag = ''  # flag for reverse colormap
        self.configlist = {}  # configurations dict
        self.xmlconfig = {}  # xml config class

        self.loadConfig(configfilename=config)
        #self.printConfig() # just for debug

        self.Bind(wx.EVT_CLOSE, self.onExit)
        self.Bind(wx.EVT_MENU_HIGHLIGHT, self.onMenuHL)
        self.InitUI()

        # handle environment variables
        self.setEnvars()

        # initialize curve fitting module
        self._fit_init()

        # save data settings
        self.savedict = {}
        self.saveTimerLife = 0
        self.saveTimerCounter = 0
        self.savetimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onSaveTimer, self.savetimer)

    def _fit_init(self):
        fit_model_x = funutils.FitModels()
        fit_model_y = funutils.FitModels()
        fit_model_x.method = 'leastsq'
        fit_model_y.method = 'leastsq'
        # config p0:
        # 1 auto
        # 2 manual
        self.fit_model_x = fit_model_x
        self.fit_model_y = fit_model_y

    def _fit_update(self, img_panel_obj):
        x, xdata = img_panel_obj.xx, img_panel_obj.histx
        y, ydata = img_panel_obj.yy, img_panel_obj.histy
        x0, y0 = np.sum(x * xdata) / np.sum(xdata), np.sum(
            y * ydata) / np.sum(xdata)
        p0_x = {'a': xdata.max(),
                'x0': x0,
                'xstd': (np.sum((x - x0)**2 * xdata) / np.sum(xdata))**0.5,
                'y0': 0}
        p0_y = {'a': ydata.max(),
                'x0': y0,
                'xstd': (np.sum((y - y0)**2 * ydata) / np.sum(ydata))**0.5,
                'y0': 0}
        self.fit_model_x.set_data(x=x, y=xdata)
        self.fit_model_x.set_params(**p0_x)
        self.fit_model_y.set_data(x=y, y=ydata)
        self.fit_model_y.set_params(**p0_y)
        res_x = self.fit_model_x.fit()
        res_y = self.fit_model_y.fit()

        self.fit_report_tc.SetDefaultStyle(wx.TextAttr("red"))
        self.fit_report_tc.SetValue('[profile X]\n')
        self.fit_report_tc.AppendText(self.fit_model_x.fit_report())
        self.fit_report_tc.SetDefaultStyle(wx.TextAttr("black"))
        self.fit_report_tc.AppendText("\n" + "-" * 28 + "\n")
        self.fit_report_tc.SetDefaultStyle(wx.TextAttr("blue"))
        self.fit_report_tc.AppendText('[profile Y]\n')
        self.fit_report_tc.AppendText(self.fit_model_y.fit_report())

        # update (x0,y0)
        self.pos0_val.SetLabel('({x:.2f},{y:.2f})'.format(
                            x=res_x.params['x0'].value,
                            y=res_y.params['x0'].value))

    def setEnvars(self):
        boolDict = {True: 'YES', False: 'NO'}
        envKeys = ['PYEPICS_LIBCA', 
                   'EPICS_CA_ADDR_LIST',
                   'EPICS_CA_AUTO_ADDR_LIST', 
                   'EPICS_CA_MAX_ARRAY_BYTES']
        envVals = [self.libcaPath,
                   self.caAddrList, 
                   boolDict[self.caAddrAuto],
                   str(self.caArrayBytes)]
        for k, v in zip(envKeys, envVals):
            # debug only
            os.environ[k] = v

    def loadConfig(self, configfilename):
        self.xmlconfig = ImageConfigFile(configfilename)
        namelist = self.xmlconfig.getConfigs()

        # Image
        self.imginifunc = namelist['imgIniFunc']
        self.wpx, self.hpx = int(float(namelist['width'])), int(float(namelist[
            'height']))
        self.roixy = [0, self.wpx, 0, self.hpx]
        dirdate = time.strftime('%Y%m%d', time.localtime())
        self.save_path_str_head = os.path.expanduser(namelist['savePath'])
        self.save_path_str = os.path.join(self.save_path_str_head, dirdate)
        self.save_img_name_str = namelist['saveImgName']
        self.save_img_ext_str = namelist['saveImgExt']
        self.save_dat_name_str = namelist['saveImgDatName']
        self.save_dat_ext_str = namelist['saveImgDatExt']
        self.save_int_name_str = namelist['saveIntName']
        self.save_int_ext_str = namelist['saveIntExt']

        self.cmlist_favo = namelist['cmFavor'].split()
        self.cmlist['Favorites'] = self.cmlist_favo

        # Control
        self.timer_freq = float(namelist['frequency'])
        self.timer_msec = 1. / self.timer_freq * 1000
        self.imgsrcPV = namelist['imgsrcPV']
        self.imgsrcPVlist = namelist['imgsrcPVlist'].split()
        self.libcaPath = namelist['libcaPath']
        self.caAddrAuto = (namelist['caAddrAuto'] == 'True')
        self.caAddrList = namelist['caAddrList']
        self.caArrayBytes = int(namelist['caArrayBytes'])
        self.pixelSize = float(namelist['pixelSize'])

        # Style
        self.bkgdcolor = funutils.hex2rgb(namelist['backgroundColor'])
        self.fontptsize = int(namelist['fontpointsize'])
        self.fontfamily = int(namelist['fontfamily'])
        self.fontstyle = int(namelist['fontstyle'])
        self.fontweight = int(namelist['fontweight'])
        self.fontfacename = namelist['fontfacename']
        self.font = wx.Font(self.fontptsize,
                            self.fontfamily,
                            self.fontstyle,
                            self.fontweight,
                            faceName=self.fontfacename)
        self.fontptsize_large = int(self.fontptsize * 2.0)
        self.fontptsize_big = int(self.fontptsize * 1.2)
        self.fontptsize_normal = int(self.fontptsize * 1.0)
        self.fontptsize_small = int(self.fontptsize * 0.8)
        self.fontptsize_tiny = int(self.fontptsize * 0.5)

        # HistPlot
        self.heightRatio = float(namelist['heightRatio'])

        self.configdict = namelist

    def printConfig(self):
        for (key, value) in sorted(self.configdict.items()):
            print("%s --- %s" % (key, value))

    def InitUI(self):
        self.createMenubar()
        self.createPanel()
        self.createStatusbar()

    def createMenubar(self):
        self.menubar = wx.MenuBar()

        ## File menu
        fileMenu = wx.Menu()
        openItem = fileMenu.Append(wx.ID_OPEN, '&Open file\tCtrl+O',
                                   'Open file to view')
        saveImgItem = fileMenu.Append(wx.ID_SAVE, '&Save Image Plot\tCtrl+S',
                                      'Save figure plotting to file')
        saveDatItem = fileMenu.Append(wx.ID_ANY, '&Save Image Data\tCtrl+D',
                                      'Save figure data to file')
        fileMenu.AppendSeparator()
        exitItem = fileMenu.Append(wx.ID_EXIT, 'E&xit\tCtrl+W',
                                   'Exit application')
        self.Bind(wx.EVT_MENU, self.onOpen, id=openItem.GetId())
        self.Bind(wx.EVT_MENU, self.onSaveImg, id=saveImgItem.GetId())
        self.Bind(wx.EVT_MENU, self.onSaveDat, id=saveDatItem.GetId())
        self.Bind(wx.EVT_MENU, self.onExit, id=exitItem.GetId())

        ## Configurations menu
        configMenu = wx.Menu()
        loadConfigItem = configMenu.Append(wx.ID_ANY,
                                           'Load from file\tCtrl+Shift+L',
                                           'Loading configurations from file')
        saveConfigItem = configMenu.Append(wx.ID_ANY,
                                           'Save to file\tCtrl+Shift+S',
                                           'Saving configurations to file')
        appsConfigItem = configMenu.Append(wx.ID_ANY,
                                           'Preferences\tCtrl+Shift+I',
                                           'Configurations for application')
        self.Bind(wx.EVT_MENU, self.onConfigApps, id=appsConfigItem.GetId())
        self.Bind(wx.EVT_MENU, self.onConfigLoad, id=loadConfigItem.GetId())
        self.Bind(wx.EVT_MENU, self.onConfigSave, id=saveConfigItem.GetId())

        ## Operations menu
        methMenu = wx.Menu()
        showIntItem = methMenu.Append(
            wx.ID_ANY, 'Show intensity\tCtrl+Shift+V', 'Monitor intensity')
        showXhistItem = methMenu.Append(wx.ID_ANY,
                                        'Show hist-X\tAlt+X',
                                        'Show histogram along X-axis',
                                        kind=wx.ITEM_CHECK)
        showYhistItem = methMenu.Append(wx.ID_ANY,
                                        'Show hist-Y\tAlt+Y',
                                        'Show histogram along Y-axis',
                                        kind=wx.ITEM_CHECK)
        autoSaveItem = methMenu.Append(wx.ID_ANY, 'Auto save\tAlt+S',
                                       'Auto saving data&image')
        self.Bind(wx.EVT_MENU, self.onShowInt, id=showIntItem.GetId())
        self.Bind(wx.EVT_MENU, self.onShowXhist, id=showXhistItem.GetId())
        self.Bind(wx.EVT_MENU, self.onShowYhist, id=showYhistItem.GetId())
        self.Bind(wx.EVT_MENU, self.onAutoSave, id=autoSaveItem.GetId())

        ## Help menu
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT, '&About\tF1',
                                    'Show about information')
        debugItem = helpMenu.Append(wx.ID_ANY, '&Debug\tF2', 'Only for debug')
        self.Bind(wx.EVT_MENU, self.onAbout, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.onDebug, debugItem)

        ## make menu
        self.menubar.Append(fileMenu, '&File')
        self.menubar.Append(configMenu, '&Configurations')
        self.menubar.Append(methMenu, '&Operations')
        self.menubar.Append(helpMenu, '&Help')

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
            os.system(
                'mkdir -p' + ' ' + self.
                save_path_str)  # I've not found pure python way (simple) to do that yet.
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
        saveins = funutils.SaveData(self.imgpanel.z, savetofilename,
                                    self.save_dat_ext_str)
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
        savetodatfilebasename = self.savedict[
            'save_path'] + os.sep + self.save_dat_name_str + filelabel
        savetoimgfilebasename = self.savedict[
            'save_path'] + os.sep + self.save_img_name_str + filelabel

        datatosave = self.mypv.get()[0:self.wpx * self.hpx].reshape((
            self.wpx, self.hpx))[self.roixy[0]:self.roixy[1], self.roixy[2]:
                                 self.roixy[3]]
        # save data
        if self.savedict['save_datfmt_hdf5'] == 1:  # save hdf5 fmt
            saveins = funutils.SaveData(
                datatosave, savetodatfilebasename + '.hdf5', '.hdf5')
        if self.savedict['save_datfmt_asc'] == 1:  # save asc fmt
            saveins = funutils.SaveData(datatosave,
                                        savetodatfilebasename + '.asc', '.asc')
        if self.savedict['save_datfmt_sdds'] == 1:  # save sdds fmt
            saveins = funutils.SaveData(
                datatosave, savetodatfilebasename + '.sdds', '.sdds')

        # save image
        if self.savedict['save_imgfmt_jpg'] == 1:  # save jpg fmt
            self.imgpanel.figure.savefig(savetoimgfilebasename + '.jpg')
        if self.savedict['save_imgfmt_eps'] == 1:  # save eps fmt
            self.imgpanel.figure.savefig(savetoimgfilebasename + '.eps')
        if self.savedict['save_imgfmt_png'] == 1:  # save png fmt
            self.imgpanel.figure.savefig(savetoimgfilebasename + '.png')

# show hint at statusbar
        hintText = 'Data file Record: %d was saved.' % self.saveTimerCounter
        self.statusbar.appinfo.SetLabel(hintText)
        self.statusbar.appinfo.SetForegroundColour('red')

        if self.saveTimerCounter == self.saveTimerLife:
            self.savetimer.Stop()
            hintText = 'Total %d records are saved to directory %s.' % (
                self.saveTimerCounter, self.savedict['save_path'])
            self.statusbar.appinfo.SetLabel(hintText)
            self.statusbar.appinfo.SetForegroundColour(self.statusbarcolor)

    def onConfigApps(self, event):
        self.menuAppConfig = AppConfigPanel(self)
        self.menuAppConfig.SetTitle('Application Preferences')
        self.menuAppConfig.Show()

    def onConfigLoad(self, event):
        try:
            xmlfile = funutils.getFileToLoad(self, ext='xml')
            self.loadConfig(xmlfile)
            self.onUpdateUIInit()
            self.onUpdateUI()
        except:
            return

    def onConfigSave(self, event):
        try:
            savetofilename = funutils.getFileToSave(self, ext='xml')
            self.xmlconfig.updateConfigs(self.configdict, savetofilename)
            self.statusbar.appinfo.SetLabel(
                'Present configurations were just saved to ' + savetofilename +
                '.')
            #self.statusbar.SetStatusText('Present configurations were just saved to ' + savetofilename + '.')
        except:
            return

    def onExit(self, event):
        dial = wx.MessageDialog(
            self,
            message="Are you sure to exit this application?",
            caption="Exit Warning",
            style=wx.YES_NO | wx.NO_DEFAULT | wx.CENTRE | wx.ICON_QUESTION)
        if dial.ShowModal() == wx.ID_YES:
            self.Destroy()

    def onAbout(self, event):
        try:
            from wx.lib.wordwrap import wordwrap
        except:
            dial = wx.MessageDialog(
                self,
                message=u"Cannot show about information, sorry!",
                caption=u"Unknown Error",
                style=wx.OK | wx.CANCEL | wx.ICON_ERROR | wx.CENTRE)
            if dial.ShowModal() == wx.ID_OK:
                dial.Destroy()
        info = wx.AboutDialogInfo()
        info.Name = "Image Viewer"
        info.Version = self.appversion
        info.Copyright = "(C) 2014-2016 Tong Zhang, SINAP, CAS"
        info.Description = wordwrap(
            "This application is a general-purposed profile/image viewer and image data postprocessor.\n"
            "It is designed by Python language, using GUI module of wxPython.",
            350, wx.ClientDC(self))
        #info.WebSite = ("http://everyfame.me", "Image Viewer home page")
        info.Developers = ["Tong Zhang <zhangtong@sinap.ac.cn>"]
        licenseText = "Image Viewer is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.\n" + "\nImage Viewer is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.\n" + "\nYou should have received a copy of the GNU General Public License along with Image Viewer; if not, write to the Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA"
        info.License = wordwrap(licenseText, 500, wx.ClientDC(self))
        wx.AboutBox(info)

    def onDebug(self, event):
        self.menuDebug = DebugPanel(self)
        self.menuDebug.SetTitle('Debug Information')
        self.menuDebug.SetMinSize((800, 600))
        self.menuDebug.Show()

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
        self.imgpanel.setColor(self.bkgdcolor)  # make color as private var
        self.imgpanel.setHratio(self.heightRatio)
        self.imgpanel.repaint()  # rewrite repaint func
        self.imgcm.setColor(self.bkgdcolor)
        self.imgcm.repaint()

    def updateFont(self):
        objs_large = [self.title_st]
        objs_big = [self.timenow_st]
        objs_small = [self.min_st, self.max_st, self.min_value_st,
                      self.max_value_st, self.inten_st, self.inten_val, 
                      self.pos0_val, self.pos0_st, self.pos_val, self.pos_st,
                      ]
        objs_normal = [self.imgsrc_st, self.cm_st, self.cr_st, 
                       self.imgcr_st, self.imgsrc_tc, self.imgcr_min_tc,
                       self.imgcr_max_tc, self.rcmchkbox, self.cmlist_cb,
                       self.cm_cb, self.daqtgl_btn, self.roi_btn,
                       self.reset_roi_btn, self.fit_model_st, self.fit_model_val,
                       self.fit_report_tc,
                       #self.m1_st, self.m2_st, self.m1_pos_st, self.m2_pos_st,
                       #self.delx_st, self.delx_val_st,
                       #self.dely_st, self.dely_val_st,
                       #self.mark_st, self.mark_st1, self.mark_st2, self.pcc_st
                       ]
        objs = objs_large + objs_big + objs_small + objs_normal
        [iobj.setFont(self.font) for iobj in objs if iobj != self.fit_report_tc]
        [iobj.setFontSize(self.fontptsize_large) for iobj in objs_large]
        [iobj.setFontSize(self.fontptsize_big) for iobj in objs_big]
        [iobj.setFontSize(self.fontptsize_normal) for iobj in objs_normal]
        [iobj.setFontSize(self.fontptsize_small) for iobj in objs_small]

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
        self.statusbar.SetStatusWidths([-4, -1])
        self.statusbar.appinfo = wx.StaticText(
            self.statusbar,
            wx.ID_ANY,
            label='ImageViewer powered by Python')
        versionfield = wx.StaticText(
            self.statusbar,
            wx.ID_ANY,
            label=time.strftime('%Y-%m-%d', time.localtime()) + ' ' +
            ' (Version: ' + self.appversion + ')')
        self.statusbar.AddWidget(self.statusbar.appinfo,
                                 funutils.ESB.ESB_ALIGN_LEFT)
        self.statusbar.AddWidget(versionfield, funutils.ESB.ESB_ALIGN_RIGHT)

    def createPanel(self):
        self.panel = wx.Panel(self, id=wx.ID_ANY)
        self.panel.SetBackgroundColour(self.bkgdcolor)

        vbox = wx.BoxSizer(wx.VERTICAL)
        ## title and horizontal line
        self.title_st = funutils.MyStaticText(self.panel,
                                              label=u'Image Viewer',
                                              style=wx.ALIGN_CENTER,
                                              font=self.font,
                                              fontsize=self.fontptsize_large,
                                              fontweight=wx.FONTWEIGHT_NORMAL,
                                              fontcolor='blue')
        vbox.Add(self.title_st,
                 flag=wx.LEFT | wx.RIGHT | wx.TOP | wx.ALIGN_CENTER,
                 border=2)
        hline = wx.StaticLine(self.panel, style=wx.LI_HORIZONTAL)
        vbox.Add((-1, 10))
        vbox.Add(hline,
                 proportion=0,
                 flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
                 border=28)

        ## hbox to put left and right panels
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        ## left panel
        vboxleft = wx.BoxSizer(wx.VERTICAL)

        ## StaticText for time indication
        self.timenow_st = funutils.MyStaticText(
            self.panel,
            label=time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime()),
            style=wx.ALIGN_CENTER,
            font=self.font,
            fontsize=self.fontptsize_big,
            fontweight=wx.FONTWEIGHT_NORMAL,
            fontcolor='black')

        self.imgpanel = ImagePanel(self.panel,
                                   figsize=(12, 12),
                                   dpi=75,
                                   bgcolor=self.bkgdcolor,
                                   heightratio=self.heightRatio,
                                   func=self.imginifunc)

        vboxleft.Add(self.timenow_st,
                     proportion=0,
                     flag=wx.ALIGN_CENTER | wx.TOP,
                     border=10)
        vboxleft.Add(self.imgpanel,
                     proportion=1,
                     flag=wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT |
                     wx.BOTTOM,
                     border=10)

        hbox.Add(vboxleft, proportion=8, flag=wx.EXPAND | wx.LEFT, border=8)

        ## separation line
        vline = wx.StaticLine(self.panel, style=wx.LI_VERTICAL)
        hbox.Add(vline,
                 proportion=0,
                 flag=wx.EXPAND | wx.TOP | wx.BOTTOM,
                 border=20)

        ## right panel
        vboxright = wx.BoxSizer(wx.VERTICAL)

        self.imgsrc_st = funutils.MyStaticText(self.panel,
                                               label=u'Image Source:',
                                               style=wx.ALIGN_LEFT,
                                               font=self.font,
                                               fontsize=self.fontptsize_normal,
                                               fontweight=wx.FONTWEIGHT_NORMAL,
                                               fontcolor='black')
        ## define pv value here!
        self.imgsrc_tc = funutils.MyTextCtrl(self.panel,
                                             value=self.imgsrcPV,
                                             style=wx.TE_PROCESS_ENTER,
                                             font=self.font,
                                             fontsize=self.fontptsize_normal)

        ## add/remove pv from imgsrcPVlist
        self.addpvbtn = wx.BitmapButton(self.panel,
                                        bitmap=resutils.addicon.GetBitmap())
        self.rmpvbtn = wx.BitmapButton(self.panel,
                                       bitmap=resutils.delicon.GetBitmap())

        pvbox = wx.BoxSizer(wx.HORIZONTAL)
        pvbox.Add(self.imgsrc_tc,
                  proportion=1,
                  flag=wx.EXPAND | wx.ALIGN_LEFT | wx.RIGHT,
                  border=8)
        pvbox.Add(self.addpvbtn, flag=wx.ALIGN_CENTER_VERTICAL)
        pvbox.Add(self.rmpvbtn,
                  flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT,
                  border=6)

        ## color map
        self.cm_st = funutils.MyStaticText(self.panel,
                                           label=u'Color Map:',
                                           style=wx.ALIGN_LEFT,
                                           font=self.font,
                                           fontsize=self.fontptsize_normal,
                                           fontweight=wx.FONTWEIGHT_NORMAL,
                                           fontcolor='black')
        ## combobox for color maps
        self.cmlist_cb = funutils.MyComboBox(
            self.panel,
            value='Favorites',
            choices=sorted(self.cmlist.keys()),
            style=wx.CB_READONLY,
            font=self.font,
            fontsize=self.fontptsize_normal,
            fontweight=wx.FONTWEIGHT_NORMAL,
            fontcolor='black')
        ## list one of classified color map
        self.cm_cb = funutils.MyComboBox(
            self.panel,
            value=self.cmlist['Favorites'][0],
            choices=self.cmlist['Favorites'], style=wx.CB_READONLY,
            font=self.font, fontsize=self.fontptsize_normal,
            fontweight=wx.FONTWEIGHT_NORMAL, fontcolor='black')
        ## book and unbook btn
        #self.bookbtn   = wx.BitmapButton(self.panel, bitmap = wx.BitmapFromImage(wx.Image('add.png')))
        #self.unbookbtn = wx.BitmapButton(self.panel, bitmap = wx.BitmapFromImage(wx.Image('remove.png')))
        self.bookbtn = wx.BitmapButton(self.panel,
                                       bitmap=resutils.addicon.GetBitmap())
        self.unbookbtn = wx.BitmapButton(self.panel,
                                         bitmap=resutils.delicon.GetBitmap())
        ## color range box
        self.cr_st = funutils.MyStaticText(self.panel,
                                           label=u'Color Range:',
                                           style=wx.ALIGN_LEFT,
                                           font=self.font,
                                           fontsize=self.fontptsize_normal,
                                           fontweight=wx.FONTWEIGHT_NORMAL,
                                           fontcolor='black')
        self.min_st = funutils.MyStaticText(self.panel,
                                            label=u'min:',
                                            style=wx.ALIGN_LEFT,
                                            font=self.font,
                                            fontsize=self.fontptsize_small,
                                            fontweight=wx.FONTWEIGHT_NORMAL,
                                            fontcolor='black')
        self.max_st = funutils.MyStaticText(self.panel,
                                            label=u'max:',
                                            style=wx.ALIGN_LEFT,
                                            font=self.font,
                                            fontsize=self.fontptsize_small,
                                            fontweight=wx.FONTWEIGHT_NORMAL,
                                            fontcolor='black')
        ### get the cmin and cmax from imgpanel object
        cmin_now = self.imgpanel.cmin
        cmax_now = self.imgpanel.cmax
        ### initial values for min&max sliders
        self.min_value_st = funutils.MyStaticText(
            self.panel,
            label=('%.1f' % (cmin_now)),
            style=wx.ALIGN_RIGHT,
            font=self.font,
            fontsize=self.fontptsize_small,
            fontweight=wx.FONTWEIGHT_NORMAL,
            fontcolor='blue')
        self.max_value_st = funutils.MyStaticText(
            self.panel,
            label=('%.1f' % (cmax_now)),
            style=wx.ALIGN_RIGHT,
            fontsize=self.fontptsize_small,
            fontweight=wx.FONTWEIGHT_NORMAL,
            fontcolor='blue')
        self.min_slider = funutils.FloatSlider(self.panel,
                                               value=cmin_now,
                                               minValue=cmin_now,
                                               maxValue=cmax_now,
                                               increment=0.1)
        self.max_slider = funutils.FloatSlider(self.panel,
                                               value=cmax_now,
                                               minValue=cmin_now,
                                               maxValue=cmax_now,
                                               increment=0.1)

        ## colormap line: st + combox for cm categories
        cmstbox = wx.BoxSizer(wx.HORIZONTAL)
        cmstbox.Add(self.cm_st,
                    flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT,
                    border=10)
        cmstbox.Add(self.cmlist_cb, proportion=1, flag=wx.ALIGN_RIGHT)

        ## selected colormap + add/remove to/from bookmarks btn
        cbbookbox = wx.BoxSizer(wx.HORIZONTAL)
        cbbookbox.Add(self.cm_cb,
                      proportion=1,
                      flag=wx.EXPAND | wx.ALIGN_LEFT | wx.RIGHT,
                      border=8)
        cbbookbox.Add(self.bookbtn, flag=wx.ALIGN_CENTER_VERTICAL)
        cbbookbox.Add(self.unbookbtn,
                      flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT,
                      border=6)

        ## show the selected colormap image
        self.imgcm = ImageColorMap(self.panel,
                                   figsize=(0.8, 0.2),
                                   dpi=75,
                                   bgcolor=self.bkgdcolor)

        ## checkbox for reverse colormap
        self.rcmchkbox = funutils.MyCheckBox(self.panel,
                                             label=u'Reverse Colormap',
                                             font=self.font,
                                             fontsize=self.fontptsize_normal)

        ## colorrange box
        crbox = wx.FlexGridSizer(2, 3, 6, 6)
        crbox.Add(self.min_st,
                  proportion=0,
                  flag=wx.LEFT | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        crbox.Add(self.min_slider,
                  proportion=1,
                  flag=wx.EXPAND | wx.ALIGN_LEFT)
        crbox.Add(self.min_value_st, proportion=0, flag=wx.ALIGN_RIGHT)
        crbox.Add(self.max_st,
                  proportion=0,
                  flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        crbox.Add(self.max_slider,
                  proportion=1,
                  flag=wx.EXPAND | wx.ALIGN_LEFT)
        crbox.Add(self.max_value_st, proportion=0, flag=wx.ALIGN_RIGHT)
        crbox.AddGrowableCol(1)
        ##
        vboxright.Add(self.imgsrc_st, flag=wx.TOP, border=25)
        vboxright.Add(pvbox, flag=wx.EXPAND | wx.TOP, border=10)
        ##
        vboxright.Add((-1, 25))
        vboxright.Add(cmstbox, flag=wx.EXPAND)
        vboxright.Add(cbbookbox, flag=wx.EXPAND | wx.TOP, border=10)
        """
        ## put rcmchkbox and imgcm into hbox3
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3.Add(self.imgcm, flag = wx.ALIGN_LEFT)
        hbox3.Add(self.rcmchkbox, flag = wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.LEFT, border = 5)
        vboxright.Add(hbox3, flag = wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.EXPAND | wx.TOP, border = 10)
        """
        vboxright.Add(self.rcmchkbox,
                      flag=wx.ALIGN_LEFT | wx.EXPAND | wx.TOP,
                      border=10)
        vboxright.Add(self.imgcm,
                      flag=wx.ALIGN_CENTER | wx.EXPAND | wx.TOP,
                      border=10)
        ##
        vboxright.Add(self.cr_st, flag=wx.TOP, border=25)
        vboxright.Add(crbox, flag=wx.EXPAND | wx.TOP, border=10)

        ## for debug: add a statictext and button to vboxright sizer 2015.Feb.11
        self.inten_st = funutils.MyStaticText(self.panel,
                                              label=u'Intensity:',
                                              font=self.font,
                                              fontsize=self.fontptsize_small)
        self.inten_val = funutils.MyStaticText(self.panel,
                                               label='0',
                                               font=self.font,
                                               fontsize=self.fontptsize_small)
        self.pos0_st = funutils.MyStaticText(self.panel, 
                                             label=u'(x\N{SUBSCRIPT ZERO},y\N{SUBSCRIPT ZERO}):',
                                             font=self.font,
                                             fontsize=self.fontptsize_small)
        self.pos0_val = funutils.MyStaticText(self.panel,
                                              label='',
                                              font=self.font,
                                              fontsize=self.fontptsize_small)
        hbox_int = wx.BoxSizer(wx.HORIZONTAL)
        hbox_int.Add(self.inten_st,
                     proportion=0,
                     flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        hbox_int.Add(self.inten_val,
                     proportion=1,
                     flag=wx.EXPAND | wx.ALIGN_RIGHT | wx.LEFT,
                     border=10)
        hbox_int.Add(self.pos0_st, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        hbox_int.Add(self.pos0_val,1, wx.EXPAND|wx.ALIGN_RIGHT | wx.LEFT, 10)

        ## add color range for imgsrc
        self.imgcr_st = funutils.MyStaticText(self.panel,
                                              label='CR of Image:',
                                              font=self.font,
                                              fontsize=self.fontptsize_normal)
        self.imgcr_min_tc = funutils.MyTextCtrl(
            self.panel,
            value='0',
            font=self.font,
            fontsize=self.fontptsize_normal)
        self.imgcr_max_tc = funutils.MyTextCtrl(
            self.panel,
            value='200',
            font=self.font,
            fontsize=self.fontptsize_normal)
        hbox_imgcr = wx.BoxSizer(wx.HORIZONTAL)
        hbox_imgcr.Add(self.imgcr_st,
                       proportion=0,
                       flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        hbox_imgcr.Add(self.imgcr_min_tc,
                       proportion=1,
                       flag=wx.EXPAND | wx.ALIGN_RIGHT | wx.RIGHT | wx.LEFT,
                       border=5)
        hbox_imgcr.Add(self.imgcr_max_tc,
                       proportion=1,
                       flag=wx.EXPAND | wx.ALIGN_RIGHT)
        # image color range
        vboxright.Add(hbox_imgcr,
                      proportion=0,
                      flag=wx.EXPAND | wx.ALIGN_CENTER | wx.TOP,
                      border=10)

        ### information display from image
        ## mouse position tracker
        self.pos_st = funutils.MyStaticText(self.panel,
                                            label='(x, y) pos:',
                                            font=self.font,
                                            fontsize=self.fontptsize_small)
        self.pos_val = funutils.MyStaticText(self.panel,
                                             label='',
                                             font=self.font,
                                             fontsize=self.fontptsize_small)
        hbox_pos = wx.BoxSizer(wx.HORIZONTAL)
        hbox_pos.Add(self.pos_st,
                     proportion=0,
                     flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        hbox_pos.Add(self.pos_val,
                     proportion=1,
                     flag=wx.EXPAND | wx.ALIGN_RIGHT | wx.LEFT,
                     border=10)

        self.roi_btn = funutils.MyButton(self.panel,
                                         label='SetROI',
                                         font=self.font,
                                         fontsize=self.fontptsize_normal,
                                         size=(105, -1))
        self.reset_roi_btn = funutils.MyButton(self.panel,
                                               label='ResetROI',
                                               font=self.font,
                                               fontsize=self.fontptsize_normal,
                                               size=(105,-1))
        self.daqtgl_btn = funutils.MyButton(self.panel,
                                            label=u'START',
                                            font=self.font,
                                            fontsize=self.fontptsize_normal,
                                            size=(105, -1))
        self.daqtgl_btn.SetForegroundColour('white')
        self.daqtgl_btn.SetBackgroundColour('green')

        # pos marker hbox

        hbox_ctrl_b = wx.BoxSizer( wx.HORIZONTAL )
                        
        self.mark_st = wx.StaticText( self.panel, wx.ID_ANY, u"Pick M", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.mark_st1 = wx.StaticText( self.panel, wx.ID_ANY, u"#1:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.mark_st2 = wx.StaticText( self.panel, wx.ID_ANY, u"#2:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.mark_st.Wrap( -1 )

        self.mkc1_btn = wx.BitmapButton(self.panel, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW)
        w, h = 16, 16
        k_bmp = wx.EmptyBitmap(w, h)
        k_img = wx.ImageFromBitmap(k_bmp)
        k_img.SetRGBRect(wx.Rect(0, 0, w, h), 255, 0, 0)
        self.mkc1_btn.SetBitmap(wx.BitmapFromImage(k_img))

        self.mkc2_btn = wx.BitmapButton(self.panel, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW)
        w, h = 16, 16
        k_bmp = wx.EmptyBitmap(w, h)
        k_img = wx.ImageFromBitmap(k_bmp)
        k_img.SetRGBRect(wx.Rect(0, 0, w, h), 240, 230, 140)
        self.mkc2_btn.SetBitmap(wx.BitmapFromImage(k_img))

        self.pcc_st = wx.StaticText( self.panel, wx.ID_ANY, u"MColor", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.pcc_btn = wx.BitmapButton(self.panel, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW)
        w, h = 16, 16
        k_bmp = wx.EmptyBitmap(w, h)
        k_img = wx.ImageFromBitmap(k_bmp)
        k_img.SetRGBRect(wx.Rect(0, 0, w, h), 0, 0, 0)
        self.pcc_btn.SetBitmap(wx.BitmapFromImage(k_img))

        # markers info box
        fgSizer_info = wx.FlexGridSizer( 0, 4, 0, 0 )
        fgSizer_info.AddGrowableCol( 1 )
        fgSizer_info.AddGrowableCol( 3 )
        fgSizer_info.SetFlexibleDirection( wx.BOTH )
        fgSizer_info.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.m1_st = wx.StaticText( self.panel, wx.ID_ANY, u"M1:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m1_st.Wrap( -1 )
        self.m1_st.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 90, False, "Monospace" ) )
        
        fgSizer_info.Add( self.m1_st, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.m1_pos_st = wx.StaticText( self.panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m1_pos_st.Wrap( -1 )
        self.m1_pos_st.SetFont( wx.Font( wx.SMALL_FONT.GetPointSize(), 70, 90, 90, False, "Monospace" ) )
        
        fgSizer_info.Add( self.m1_pos_st, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.delx_st = wx.StaticText( self.panel, wx.ID_ANY, u"\N{GREEK CAPITAL LETTER DELTA}x:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.delx_st.Wrap( -1 )
        self.delx_st.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 90, False, "Monospace" ) )
        
        fgSizer_info.Add( self.delx_st, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.delx_val_st = wx.StaticText( self.panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.delx_val_st.Wrap( -1 )
        self.delx_val_st.SetFont( wx.Font( wx.SMALL_FONT.GetPointSize(), 70, 90, 90, False, "Monospace" ) )
        
        fgSizer_info.Add( self.delx_val_st, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.m2_st = wx.StaticText( self.panel, wx.ID_ANY, u"M2:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m2_st.Wrap( -1 )
        self.m2_st.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 90, False, "Monospace" ) )
        
        fgSizer_info.Add( self.m2_st, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.m2_pos_st = wx.StaticText( self.panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m2_pos_st.Wrap( -1 )
        self.m2_pos_st.SetFont( wx.Font( wx.SMALL_FONT.GetPointSize(), 70, 90, 90, False, "Monospace" ) )
        
        fgSizer_info.Add( self.m2_pos_st, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.dely_st = wx.StaticText( self.panel, wx.ID_ANY, u"\N{GREEK CAPITAL LETTER DELTA}y:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.dely_st.Wrap( -1 )
        self.dely_st.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 90, False, "Monospace" ) )
        
        fgSizer_info.Add( self.dely_st, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.dely_val_st = wx.StaticText( self.panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.dely_val_st.Wrap( -1 )
        self.dely_val_st.SetFont( wx.Font( wx.SMALL_FONT.GetPointSize(), 70, 90, 90, False, "Monospace" ) )
        
        fgSizer_info.Add( self.dely_val_st, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        #
        hbox_ctrl_b.Add( self.mark_st,  0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        hbox_ctrl_b.Add( self.mark_st1, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 2 )
        hbox_ctrl_b.Add( self.mkc1_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5 )
        hbox_ctrl_b.Add( self.mark_st2, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 2 )
        hbox_ctrl_b.Add( self.mkc2_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5 )
        hbox_ctrl_b.Add( self.pcc_st,   0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 2 )
        hbox_ctrl_b.Add( self.pcc_btn,  0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5 )

        hbox_ctrl = wx.BoxSizer(wx.HORIZONTAL)
        hbox_ctrl.Add(self.roi_btn,       0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        hbox_ctrl.Add(self.reset_roi_btn, 0, wx.ALIGN_CENTER_VERTICAL)
        hbox_ctrl.Add(self.daqtgl_btn,    0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)

        vbox_ctrl = wx.BoxSizer(wx.VERTICAL)
        vbox_ctrl.Add(fgSizer_info, 1, wx.EXPAND)
        vbox_ctrl.Add(hbox_ctrl_b, 0)#, wx.EXPAND | wx.ALIGN_LEFT)
        vbox_ctrl.Add(hbox_ctrl,   0)#, wx.ALIGN_RIGHT)

        # curve fitting output box region
        sbox_fit = funutils.createwxStaticBox(self.panel,
                                              label="Curve Fitting",
                                              fontcolor='grey',
                                              fontsize=8,
                                              style=wx.ALIGN_CENTER)
        self.sbox_fit = sbox_fit
        sbsizer_fit = wx.StaticBoxSizer(sbox_fit, orient=wx.VERTICAL)

        fit_model_st = funutils.MyStaticText(self.panel,
                                             label='Fitting Model:',
                                             font=self.font,
                                             fontsize=self.fontptsize_normal,
                                             style=wx.ALIGN_LEFT)
        fit_model_val = funutils.MyStaticText(self.panel,
                                              label="Gaussian",
                                              font=self.font,
                                              fontsize=self.fontptsize_normal,
                                              style=wx.ALIGN_CENTER)
        fit_model_popup_btn = wx.BitmapButton(
            self.panel, bitmap=resutils.popicon.GetBitmap())
        #bitmap=wx.ArtProvider.GetBitmap(wx.ART_COPY, wx.ART_OTHER))

        self.fit_model_popup_btn = fit_model_popup_btn
        self.fit_model_st = fit_model_st
        self.fit_model_val = fit_model_val
        # add fit config page to configurations panel
        fit_vbox_m = wx.BoxSizer(wx.VERTICAL)
        fit_hbox_u = wx.BoxSizer(wx.HORIZONTAL)
        fit_vbox_d = wx.BoxSizer(wx.VERTICAL)

        tcfont = wx.Font(self.fontptsize_normal,
                         wx.FONTFAMILY_MODERN,
                         wx.FONTSTYLE_NORMAL,
                         wx.FONTWEIGHT_NORMAL,
                         faceName="Monospace")
        fit_report_tc = funutils.MyTextCtrl(self.panel,
                                            value='',
                                            style=wx.TE_READONLY |
                                            wx.TE_MULTILINE | wx.HSCROLL,
                                            font=tcfont,
                                            )
        self.fit_report_tc = fit_report_tc

        fit_hbox_u.Add(fit_model_st, 0, wx.ALIGN_LEFT)
        fit_hbox_u.Add(fit_model_val, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT,
                       10)
        fit_hbox_u.Add(fit_model_popup_btn, 0, wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, 10)

        fit_vbox_d.Add(fit_report_tc, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.RIGHT
                       | wx.BOTTOM | wx.TOP, 1)

        fit_vbox_m.Add(fit_hbox_u, 0, wx.EXPAND)
        fit_vbox_m.Add(fit_vbox_d, 1, wx.EXPAND)

        sbsizer_fit.Add(fit_vbox_m, 1, wx.EXPAND | wx.LEFT, 1)

        ## layout boxes
        # hline
        vboxright.Add(wx.StaticLine(self.panel, wx.HORIZONTAL), 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)
        # image intensity
        vboxright.Add(hbox_int,
                      proportion=0,
                      flag=wx.EXPAND | wx.ALIGN_CENTER | wx.TOP,
                      border=10)
        # xypos
        vboxright.Add(hbox_pos,
                      flag=wx.EXPAND | wx.ALIGN_CENTER | wx.TOP,
                      border=10)
        # fitting info
        vboxright.Add(sbsizer_fit,
                      1,
                      flag=wx.ALIGN_CENTER | wx.EXPAND | wx.TOP | wx.BOTTOM,
                      border=1)
        # control box, roi, DAQ start button, pos marker picker
        vboxright.Add(vbox_ctrl, flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=5)

        ##
        hbox.Add(vboxright,
                 proportion=3,
                 flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
                 border=20)

        ## set sizer
        vbox.Add(hbox, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER)
        self.panel.SetSizer(vbox)
        osizer = wx.BoxSizer(wx.HORIZONTAL)
        osizer.Add(self.panel, proportion=1, flag=wx.EXPAND)
        self.SetSizerAndFit(osizer)

        ### event bindings

        ## pos markers
        self.Bind(wx.EVT_BUTTON, self.onPickMK1c, self.mkc1_btn)
        self.Bind(wx.EVT_BUTTON, self.onPickMK2c, self.mkc2_btn)
        self.Bind(wx.EVT_BUTTON, self.onPickPcc,  self.pcc_btn)

        ## fit model detail popup
        self.Bind(wx.EVT_BUTTON, self.onFitPopup, self.fit_model_popup_btn)

        ## ROI callback
        self.Bind(wx.EVT_BUTTON, self.onChooseROI, self.roi_btn)
        self.Bind(wx.EVT_BUTTON, self.onResetROI, self.reset_roi_btn)

        ## add input pv namestring to imgsrcPVlist or not
        self.Bind(wx.EVT_BUTTON, self.onAddPV, self.addpvbtn)
        self.Bind(wx.EVT_BUTTON, self.onRmPV, self.rmpvbtn)

        ## colormap categories
        self.Bind(wx.EVT_COMBOBOX, self.onSetCmclass, self.cmlist_cb)

        ## color map value from specific category
        self.Bind(wx.EVT_COMBOBOX, self.onSetColormap, self.cm_cb)

        ## add selected colormap to favorites or not
        self.Bind(wx.EVT_BUTTON, self.onBookmark, self.bookbtn)
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
        self.Bind(wx.EVT_TIMER, self.onUpdate, self.timer)
        self.Bind(wx.EVT_BUTTON, self.onDAQbtn, self.daqtgl_btn)

        ## another timer for showing time now
        self.timernow = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTickTime, self.timernow)

        ## start timernow (clock)
        self.timernow.Start(1000)

    def onPickMK1c(self, event):
        color = funutils.pick_color()
        if color is not None:
            c = color.GetAsString(wx.C2S_HTML_SYNTAX)
            self.imgpanel.set_mkc1(c)
            funutils.set_staticbmp_color(self.mkc1_btn, color)
        self.marker_pos1, self.marker_pos2 = True, False
        self.imgpanel.set_markflags(self.marker_pos1, self.marker_pos2)

    def onPickMK2c(self, event):
        color = funutils.pick_color()
        if color is not None:
            c = color.GetAsString(wx.C2S_HTML_SYNTAX)
            self.imgpanel.set_mkc2(c)
            funutils.set_staticbmp_color(self.mkc2_btn, color)
        self.marker_pos1, self.marker_pos2 = False, True
        self.imgpanel.set_markflags(self.marker_pos1, self.marker_pos2)

    def onPickPcc(self, event):
        color = funutils.pick_color()
        if color is not None:
            c = color.GetAsString(wx.C2S_HTML_SYNTAX)
            self.imgpanel.set_pcc(c)
            funutils.set_staticbmp_color(self.pcc_btn, color)

    def onFitPopup(self, event):
        if self.fit_model_x.get_fit_result() is None or self.fit_model_y.get_fit_result() is None:
            return
        self.fit_popframe = FitPlotFrame(self, self.fit_model_x,
                                         self.fit_model_y)
        self.fit_popframe.SetTitle('Curves Fitting')
        self.fit_popframe.SetMinSize((800, 600))
        self.fit_popframe.Show()

    def onResetROI(self, event):
        self.roixy = [0, self.wpx, 0, self.hpx]

    def onChooseROI(self, event):
        self.roiFrame = ChooseROIFrame(self, self.imgpanel)
        self.roiFrame.SetTitle('Select Region of Interest')
        self.roiFrame.Show()

    def onTickTime(self, event):
        fmt = '%Y-%m-%d %H:%M:%S %Z'
        self.timenow_st.SetLabel(time.strftime(fmt, time.localtime()))

    def onDAQbtn(self, event):
        label = event.GetEventObject().GetLabel()
        try:
            isinstance(self.mypv, epics.pv.PV)
        except AttributeError:
            self.mypv = epics.PV(self.imgsrc_tc.GetValue(), auto_monitor=True)

        if self.timer.IsRunning():
            self.timer.Stop()
            self.min_slider.Enable()
            self.max_slider.Enable()
            self.daqtgl_btn.SetLabel('START')
            self.daqtgl_btn.SetBackgroundColour('green')
        else:
            self.timer.Start(self.timer_msec)
            self.min_slider.Disable()
            self.max_slider.Disable()
            self.daqtgl_btn.SetLabel('STOP')
            self.daqtgl_btn.SetBackgroundColour('red')

    def onUpdate(self, event):
        if self.mypv.connected == True:
            self.inten_val.SetLabel("%.4e" % (np.sum(self.mypv.get())))

            self.imgpanel.z = self.mypv.get()[0:self.wpx * self.hpx].reshape((
                self.wpx, self.hpx))[self.roixy[0]:self.roixy[1], self.roixy[
                    2]:self.roixy[3]]
            try:
                cmin_now = float(self.imgcr_min_tc.GetValue())
                cmax_now = float(self.imgcr_max_tc.GetValue())
            except ValueError:
                cmin_now = None
                cmax_now = None
            self.imgpanel.im.set_clim(vmin=cmin_now, vmax=cmax_now)
            self.imgpanel.im.set_array(self.imgpanel.z)
            self.imgpanel.repaint()
            # update fitting report box
            self._fit_update(self.imgpanel)
            try:
                self.fit_popframe.plotpanel.repaint(self.fit_model_x,
                                                    self.fit_model_y)
            except:
                pass
        else:
            dial = wx.MessageDialog(
                self,
                message=u"Lost connection, may be caused by network error or the IOC server is down.",
                caption=u"Lost Connection",
                style=wx.OK | wx.ICON_ERROR | wx.CENTRE)
            if dial.ShowModal() == wx.ID_OK:
                self.timer.Stop()
                self.min_slider.Enable()
                self.max_slider.Enable()
                self.daqtgl_btn.SetLabel('START')
                dial.Destroy()

    def onSetImgSrc(self, event):
        """
        set image data source and show in the image panel
        """
        self.mypv = epics.PV(event.GetEventObject().GetValue(),
                             auto_monitor=True)

        self.imgpanel.z = self.mypv.get()[0:self.wpx * self.hpx].reshape((
            self.wpx, self.hpx))[self.roixy[0]:self.roixy[1], self.roixy[2]:
                                 self.roixy[3]]
        self.imgpanel.cmin = self.imgpanel.z.min()
        self.imgpanel.cmax = self.imgpanel.z.max()
        cmin_now = self.imgpanel.cmin
        cmax_now = self.imgpanel.cmax
        # update self.min_slider and self.max_slider,
        # as well as self.min_value_st and self.max_value_st
        self.min_value_st.SetLabel('%.1f' % (cmin_now))
        self.max_value_st.SetLabel('%.1f' % (cmax_now))
        self.min_slider.SetMin(cmin_now)
        self.min_slider.SetMax(cmax_now)
        self.min_slider.SetValue(cmin_now)
        self.max_slider.SetMin(cmin_now)
        self.max_slider.SetMax(cmax_now)
        self.max_slider.SetValue(cmax_now)
        self.imgcr_min_tc.SetValue('%.1f' % cmin_now)
        self.imgcr_max_tc.SetValue('%.1f' % cmax_now)
        self.imgpanel.im.set_clim(vmin=cmin_now, vmax=cmax_now)
        self.imgpanel.im.set_array(self.imgpanel.z)
        self.imgpanel.repaint()
        self.inten_val.SetLabel("%.4e" % (np.sum(self.mypv.get())))
        self._fit_update(self.imgpanel)

    def onCheckRCM(self, event):
        if event.GetEventObject().IsChecked():  # checked
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
    def __init__(self, parent, style=wx.NB_LEFT, *args, **kws):
        super(self.__class__, self).__init__(parent=parent, *args, **kws)
        self.parent = parent
        self.MakePages()

    def MakePages(self):
        self.imagePage = ImageConfigPanel(self)
        self.stylePage = StyleConfigPanel(self)
        self.controlPage = ControlConfigPanel(self)
        self.histPlotPage = HistPlotConfigPanel(self)

        self.AddPage(self.imagePage, 'Image')
        self.AddPage(self.stylePage, 'Style')
        self.AddPage(self.controlPage, 'Control')
        self.AddPage(self.histPlotPage, 'HistPlot')


class AutoSavePanel(wx.Frame):
    def __init__(self, parent, **kwargs):
        super(self.__class__, self).__init__(
            parent=parent,
            id=wx.ID_ANY,
            style=wx.DEFAULT_FRAME_STYLE &
            ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX),
            **kwargs)
        self.parent = parent
        self.InitUI()

    def InitUI(self):
        self.createPanel()
        self.postInit()

    def createPanel(self):
        self.panel = wx.Panel(self)

        # format choosing
        sbox1 = funutils.createwxStaticBox(self.panel, label='Choose Saving Format', 
                                           fontcolor='grey', fontsize=8)
        #sbox1 = wx.StaticBox(self.panel, label='Choose Saving Format')
        #sfont = sbox1.GetFont()
        #sfont.SetPointSize(8)
        #sbox1.SetFont(sfont)
        #sbox1.SetForegroundColour('grey')
        sbsizer1 = wx.StaticBoxSizer(sbox1, orient=wx.HORIZONTAL)

        # data format: hdf5, asc, sdds, etc.
        datahbox = wx.BoxSizer(wx.VERTICAL)
        data_st = funutils.MyStaticText(self.panel,
                                        label='Data Format',
                                        fontsize=10,
                                        fontcolor='blue')
        self.hdf5_chbox = funutils.MyCheckBox(
            self.panel, label='hdf5', fontsize=10)
        self.asc_chbox = funutils.MyCheckBox(
            self.panel, label='asc', fontsize=10)
        self.sdds_chbox = funutils.MyCheckBox(
            self.panel, label='sdds', fontsize=10)
        datahbox.Add(data_st,
                     proportion=0,
                     flag=wx.ALL | wx.ALIGN_LEFT,
                     border=10)
        datahbox.Add(self.hdf5_chbox,
                     proportion=0,
                     flag=wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                     border=10)
        datahbox.Add(self.asc_chbox,
                     proportion=0,
                     flag=wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                     border=10)
        datahbox.Add(self.sdds_chbox,
                     proportion=0,
                     flag=wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                     border=10)

        # image format: jpg, eps, png, etc.
        imagehbox = wx.BoxSizer(wx.VERTICAL)
        image_st = funutils.MyStaticText(self.panel,
                                         label='Image Format',
                                         fontsize=10,
                                         fontcolor='blue')
        self.jpg_chbox = funutils.MyCheckBox(
            self.panel, label='jpg', fontsize=10)
        self.eps_chbox = funutils.MyCheckBox(
            self.panel, label='eps', fontsize=10)
        self.png_chbox = funutils.MyCheckBox(
            self.panel, label='png', fontsize=10)
        imagehbox.Add(image_st,
                      proportion=0,
                      flag=wx.ALL | wx.ALIGN_LEFT,
                      border=10)
        imagehbox.Add(self.jpg_chbox,
                      proportion=0,
                      flag=wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                      border=10)
        imagehbox.Add(self.eps_chbox,
                      proportion=0,
                      flag=wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                      border=10)
        imagehbox.Add(self.png_chbox,
                      proportion=0,
                      flag=wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                      border=10)

        sbsizer1.Add(datahbox, proportion=1, flag=wx.EXPAND | wx.ALL, border=8)
        sbsizer1.Add(
            wx.StaticLine(self.panel, style=wx.LI_VERTICAL),
            flag=wx.EXPAND | wx.TOP | wx.BOTTOM,
            border=10)
        sbsizer1.Add(imagehbox,
                     proportion=1,
                     flag=wx.EXPAND | wx.RIGHT | wx.TOP | wx.BOTTOM,
                     border=8)

        # save timer/io setup
        sbox2 = funutils.createwxStaticBox(self.panel,
                                           label='Options',
                                           fontcolor='grey',
                                           fontsize=8)
        sbsizer2 = wx.StaticBoxSizer(sbox2, orient=wx.VERTICAL)

        ## saveto path
        saveto_st = funutils.MyStaticText(self.panel,
                                          label='Save to',
                                          fontcolor='black',
                                          style=wx.ALIGN_LEFT)
        self.savetopath_tc = funutils.MyTextCtrl(self.panel,
                                                 value=os.getcwd(),
                                                 style=wx.TE_READONLY)
        choosepath_btn = funutils.MyButton(self.panel, label='Browse')

        ## save freq setting
        savefreq_st1 = funutils.MyStaticText(self.panel,
                                             label='Save',
                                             fontcolor='black',
                                             style=wx.ALIGN_LEFT)
        savefreq_st2 = funutils.MyStaticText(self.panel,
                                             label='frame',
                                             fontcolor='black',
                                             style=wx.ALIGN_LEFT)
        savefreq_st3 = funutils.MyStaticText(self.panel,
                                             label='every',
                                             fontcolor='black',
                                             style=wx.ALIGN_LEFT)
        savefreq_st4 = funutils.MyStaticText(self.panel,
                                             label='second',
                                             fontcolor='black',
                                             style=wx.ALIGN_LEFT)
        self.savefreqcnt_sp = wx.SpinCtrl(self.panel,
                                          value='1',
                                          min=1,
                                          max=10,
                                          initial=1,
                                          style=wx.SP_ARROW_KEYS)
        self.savefreqsec_fsp = fs.FloatSpin(self.panel,
                                            value='2.0',
                                            min_val=1.0,
                                            max_val=10000,
                                            increment=0.5,
                                            digits=1,
                                            style=fs.FS_LEFT)
        savefreq_st5 = funutils.MyStaticText(self.panel,
                                             label='Total Saved Record Number',
                                             fontcolor='black',
                                             style=wx.ALIGN_LEFT)
        self.savefreqtot_sp = wx.SpinCtrl(self.panel,
                                          value='10',
                                          min=1,
                                          max=10000,
                                          initial=10,
                                          style=wx.SP_ARROW_KEYS)

        savegsbox = wx.GridBagSizer(10, 5)
        savegsbox.Add(saveto_st,
                      pos=(0, 0),
                      span=(1, 1),
                      flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL,
                      border=10)
        savegsbox.Add(self.savetopath_tc,
                      pos=(0, 1),
                      span=(1, 4),
                      flag=wx.EXPAND | wx.LEFT | wx.ALIGN_CENTER_VERTICAL,
                      border=10)
        savegsbox.Add(choosepath_btn,
                      pos=(0, 5),
                      span=(1, 1),
                      flag=wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
                      border=10)
        savegsbox.Add(savefreq_st1,
                      pos=(1, 0),
                      span=(1, 1),
                      flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL,
                      border=10)
        savegsbox.Add(self.savefreqcnt_sp,
                      pos=(1, 1),
                      span=(1, 1),
                      flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL,
                      border=10)
        savegsbox.Add(savefreq_st2,
                      pos=(1, 2),
                      span=(1, 1),
                      flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL,
                      border=10)
        savegsbox.Add(savefreq_st3,
                      pos=(1, 3),
                      span=(1, 1),
                      flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL,
                      border=10)
        savegsbox.Add(self.savefreqsec_fsp,
                      pos=(1, 4),
                      span=(1, 1),
                      flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL,
                      border=10)
        savegsbox.Add(savefreq_st4,
                      pos=(1, 5),
                      span=(1, 1),
                      flag=wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER,
                      border=10)
        savegsbox.Add(savefreq_st5,
                      pos=(2, 0),
                      span=(1, 2),
                      flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL,
                      border=10)
        savegsbox.Add(self.savefreqtot_sp,
                      pos=(2, 2),
                      span=(1, 1),
                      flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL,
                      border=10)

        savegsbox.AddGrowableCol(1)
        savegsbox.AddGrowableCol(2)
        savegsbox.AddGrowableCol(3)
        savegsbox.AddGrowableCol(4)

        sbsizer2.Add(savegsbox,
                     proportion=0,
                     flag=wx.EXPAND | wx.ALL,
                     border=10)

        # cmd hbox sizer
        cmdhbox = wx.BoxSizer(wx.HORIZONTAL)
        startsave_btn = funutils.MyButton(self.panel,
                                          label='Start SAVE',
                                          fontcolor='red')
        cancel_btn = funutils.MyButton(self.panel, label='Cancel')
        cmdhbox.Add(cancel_btn, proportion=0, flag=wx.RIGHT, border=10)
        cmdhbox.Add(startsave_btn,
                    proportion=0,
                    flag=wx.TOP | wx.BOTTOM | wx.RIGHT,
                    border=0)

        # set sizers
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        mainsizer.Add(sbsizer1,
                      proportion=4,
                      flag=wx.EXPAND | wx.ALL,
                      border=10)
        mainsizer.Add(sbsizer2,
                      proportion=3,
                      flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                      border=10)
        mainsizer.Add(cmdhbox,
                      proportion=0,
                      flag=wx.ALIGN_RIGHT | wx.BOTTOM | wx.RIGHT,
                      border=10)

        self.panel.SetSizer(mainsizer)
        osizer = wx.BoxSizer(wx.VERTICAL)
        osizer.Add(self.panel, proportion=1, flag=wx.EXPAND)
        self.SetSizerAndFit(osizer)

        # event bindings
        self.Bind(wx.EVT_BUTTON, self.onStart, startsave_btn)
        self.Bind(wx.EVT_BUTTON, self.onCancel, cancel_btn)
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
        tperiod_setval = self.savefreqsec_fsp.GetValue()  # sec
        cntpert_setval = self.savefreqcnt_sp.GetValue()
        total_setval = self.savefreqtot_sp.GetValue()
        # return parameters
        self.parent.savedict['save_total_record'] = total_setval
        self.parent.savedict[
            'save_tfreq_msec'] = tperiod_setval * 1000.0 / cntpert_setval
        self.parent.savedict['save_path'] = self.savetopath_tc.GetValue()
        self.parent.savedict['save_datfmt_hdf5'] = self.hdf5_chbox.GetValue()
        self.parent.savedict['save_datfmt_asc'] = self.asc_chbox.GetValue()
        self.parent.savedict['save_datfmt_sdds'] = self.sdds_chbox.GetValue()
        self.parent.savedict['save_imgfmt_jpg'] = self.jpg_chbox.GetValue()
        self.parent.savedict['save_imgfmt_eps'] = self.eps_chbox.GetValue()
        self.parent.savedict['save_imgfmt_png'] = self.png_chbox.GetValue()
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
        super(self.__class__, self).__init__(parent=parent,
                                             id=wx.ID_ANY,
                                             style=wx.DEFAULT_FRAME_STYLE,
                                             **kwargs)
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
        self.configNB = ConfigNoteBook(self, style=wx.NB_TOP)

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

        self.cancelbtn = wx.Button(self, label='Cancel')
        self.applybtn = wx.Button(self, label='Apply')
        self.okbtn = wx.Button(self, label='OK')

        self.Bind(wx.EVT_BUTTON, self.onCancelData, self.cancelbtn)
        self.Bind(wx.EVT_BUTTON, self.onApplyData, self.applybtn)
        self.Bind(wx.EVT_BUTTON, self.onUpdateData, self.okbtn)

        hboxbtn = wx.BoxSizer(wx.HORIZONTAL)
        hboxbtn.Add(self.cancelbtn,
                    proportion=0,
                    flag=wx.EXPAND | wx.BOTTOM,
                    border=10)
        hboxbtn.Add(self.applybtn,
                    proportion=0,
                    flag=wx.EXPAND | wx.LEFT | wx.BOTTOM,
                    border=10)
        hboxbtn.Add(self.okbtn,
                    proportion=0,
                    flag=wx.EXPAND | wx.LEFT | wx.BOTTOM,
                    border=10)

        # set sizer
        vbox.Add(self.configNB,
                 proportion=1,
                 flag=wx.EXPAND | wx.ALL,
                 border=15)
        vbox.Add(hboxbtn, flag=wx.ALIGN_RIGHT | wx.RIGHT | wx.TOP, border=15)
        vbox.Add((-1, 10))
        self.SetSizerAndFit(vbox)

        # config pages references:
        self.imagePage = self.configNB.imagePage
        self.stylePage = self.configNB.stylePage
        self.controlPage = self.configNB.controlPage
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
        self.thisapp.imginifunc = self.imagePage.imginifunccb.GetValue()
        self.thisapp.wpx = int(self.imagePage.imgwpxtc.GetValue())
        self.thisapp.hpx = int(self.imagePage.imghpxtc.GetValue())
        self.thisapp.roixy = [0, self.thisapp.wpx, 0, self.thisapp.hpx]
        self.thisapp.save_path_str_head = os.path.expanduser(
            self.imagePage.pathtc.GetValue())
        self.thisapp.save_path_str = os.path.join(
            self.thisapp.save_path_str_head, time.strftime('%Y%m%d',
                                                           time.localtime()))
        self.thisapp.save_img_name_str = self.imagePage.imgnamepretc.GetValue()
        self.thisapp.save_img_ext_str = self.imagePage.imgnameexttc.GetValue()
        self.thisapp.save_dat_name_str = self.imagePage.imgdatnamepretc.GetValue(
        )
        self.thisapp.save_dat_ext_str = self.imagePage.imgdatnameexttc.GetValue(
        )
        self.thisapp.save_int_name_str = self.imagePage.intnamepretc.GetValue()
        self.thisapp.save_int_ext_str = self.imagePage.intnameexttc.GetValue()

        # stylePage
        self.thisapp.bkgdcolor = funutils.hex2rgb(
            self.stylePage.bkgdcolortc.GetValue())
        self.thisapp.font = self.stylePage.font
        self.thisapp.fontptsize = self.stylePage.font.GetPointSize()
        self.thisapp.fontfamily = self.stylePage.font.GetFamily()
        self.thisapp.fontstyle = self.stylePage.font.GetStyle()
        self.thisapp.fontweight = self.stylePage.font.GetWeight()
        self.thisapp.fontfacename = self.stylePage.font.GetFaceName()

        self.thisapp.font = wx.Font(self.thisapp.fontptsize,
                                    self.thisapp.fontfamily,
                                    self.thisapp.fontstyle,
                                    self.thisapp.fontweight,
                                    faceName=self.thisapp.fontfacename)
        self.thisapp.fontptsize_large = int(self.thisapp.fontptsize * 2.0)
        self.thisapp.fontptsize_big = int(self.thisapp.fontptsize * 1.2)
        self.thisapp.fontptsize_normal = int(self.thisapp.fontptsize * 1.0)
        self.thisapp.fontptsize_small = int(self.thisapp.fontptsize * 0.8)
        self.thisapp.fontptsize_tiny = int(self.thisapp.fontptsize * 0.5)

        # controlPage
        self.thisapp.timer_freq = self.controlPage.freqtc.GetValue()
        self.thisapp.timer_msec = 1.0 / self.thisapp.timer_freq * 1000
        self.thisapp.imgsrcPV = self.controlPage.imgsrcPVcb.GetValue()
        self.thisapp.libcaPath = self.controlPage.libcaPathtc.GetValue()
        self.thisapp.caAddrList = self.controlPage.caAddrListtc.GetValue()
        self.thisapp.caAddrAuto = self.controlPage.caAddrAutochk.GetValue()
        self.thisapp.caArrayBytes = int(
            self.controlPage.caArrayBytestc.GetValue())
        self.thisapp.pixelSize = float(
            self.controlPage.pixelSizetc.GetValue())

        # histPlotPage
        self.thisapp.heightRatio = float(
            self.histPlotPage.heightratiotc.GetValue())

        # update parameters
        self.thisapp.configdict['imgIniFunc'] = str(self.thisapp.imginifunc)
        self.thisapp.configdict['width'] = str(self.thisapp.wpx)
        self.thisapp.configdict['height'] = str(self.thisapp.hpx)
        self.thisapp.configdict['savePath'] = self.thisapp.save_path_str_head
        self.thisapp.configdict['saveImgName'] = self.thisapp.save_img_name_str
        self.thisapp.configdict['saveImgExt'] = self.thisapp.save_img_ext_str
        self.thisapp.configdict[
            'saveImgDatName'] = self.thisapp.save_dat_name_str
        self.thisapp.configdict[
            'saveImgDatExt'] = self.thisapp.save_dat_ext_str
        self.thisapp.configdict['saveIntName'] = self.thisapp.save_int_name_str
        self.thisapp.configdict['saveIntExt'] = self.thisapp.save_int_ext_str
        self.thisapp.configdict['frequency'] = str(self.thisapp.timer_freq)
        self.thisapp.configdict['imgsrcPV'] = self.thisapp.imgsrcPV
        self.thisapp.configdict['imgsrcPVlist'] = ' '.join(
            str(i) + ' ' for i in self.thisapp.imgsrcPVlist).rstrip()
        self.thisapp.configdict['cmFavor'] = ' '.join(
            str(i) + ' ' for i in self.thisapp.cmlist_favo).rstrip()
        self.thisapp.configdict[
            'backgroundColor'] = self.stylePage.bkgdcolortc.GetValue()
        self.thisapp.configdict['heightRatio'] = str(self.thisapp.heightRatio)
        self.thisapp.configdict['fontpointsize'] = str(self.thisapp.fontptsize)
        self.thisapp.configdict['fontfamily'] = str(self.thisapp.fontfamily)
        self.thisapp.configdict['fontstyle'] = str(self.thisapp.fontstyle)
        self.thisapp.configdict['fontweight'] = str(self.thisapp.fontweight)
        self.thisapp.configdict['fontfacename'] = self.thisapp.fontfacename
        self.thisapp.configdict['libcaPath'] = self.thisapp.libcaPath
        self.thisapp.configdict['caAddrAuto'] = str(self.thisapp.caAddrAuto)
        self.thisapp.configdict['caAddrList'] = self.thisapp.caAddrList
        self.thisapp.configdict['caArrayBytes'] = str(
            self.thisapp.caArrayBytes)
        self.thisapp.configdict['pixelSize'] = str(
            self.thisapp.pixelSize)
        self.thisapp.xmlconfig.updateConfigs(self.thisapp.configdict)
        self.thisapp.onUpdateUI()
        self.thisapp.setEnvars()

        # for debug
        #self.thisapp.printConfig()


class ImageConfigPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        super(self.__class__, self).__init__(
            parent=parent, id=wx.ID_ANY, **kwargs)
        self.parent = parent
        self.thisapp = self.parent.parent.parent
        self.initUI()

    def initUI(self):
        self.initConfig()
        self.createPanel()

    def initConfig(self):
        self.bkgdcolor = wx.BLUE
        self.fontcolor = wx.BLACK
        self.fontptsize = 10
        self.fontweight = wx.FONTWEIGHT_NORMAL

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

        imginifuncst = wx.StaticText(self,
                                     label=u'Initial Image Function',
                                     style=wx.ALIGN_LEFT)

        imgwpxst = wx.StaticText(self,
                                 label=u'Image Width [px]',
                                 style=wx.ALIGN_LEFT)
        imghpxst = wx.StaticText(self,
                                 label=u'Image Height [px]',
                                 style=wx.ALIGN_LEFT)
        pathst = wx.StaticText(self,
                               label=u'Save Figure to Path',
                               style=wx.ALIGN_LEFT)
        imgnameprest = wx.StaticText(self,
                                     label=u'Image Name Prefix',
                                     style=wx.ALIGN_LEFT)
        imgnameextst = wx.StaticText(self,
                                     label=u'Image Name Extension',
                                     style=wx.ALIGN_LEFT)
        intnameprest = wx.StaticText(self,
                                     label=u'Intensity Name Prefix',
                                     style=wx.ALIGN_LEFT)
        intnameextst = wx.StaticText(self,
                                     label=u'Intensity Name Extension',
                                     style=wx.ALIGN_LEFT)
        imgdatnameprest = wx.StaticText(self,
                                        label=u'Image Data Name Prefix',
                                        style=wx.ALIGN_LEFT)
        imgdatnameextst = wx.StaticText(self,
                                        label=u'Image Data Name Extension',
                                        style=wx.ALIGN_LEFT)

        self.imginifunccb = wx.ComboBox(self,
                                        value=self.thisapp.imginifunc,
                                        style=wx.CB_READONLY,
                                        choices=['peaks', 'sinc'])

        self.imgwpxtc = wx.TextCtrl(self,
                                    value=str(self.thisapp.wpx),
                                    style=wx.TE_PROCESS_ENTER)
        self.imghpxtc = wx.TextCtrl(self,
                                    value=str(self.thisapp.hpx),
                                    style=wx.TE_PROCESS_ENTER)
        self.pathtc = wx.TextCtrl(self,
                                  value=self.thisapp.save_path_str_head,
                                  style=wx.TE_READONLY)
        self.pathtc.SetToolTip(wx.ToolTip(
            'Fullpath (subdired by the date) the config file be saved.'))
        self.pathbtn = wx.Button(self, label='Browse')
        self.imgnamepretc = wx.TextCtrl(self,
                                        value=self.thisapp.save_img_name_str,
                                        style=wx.TE_PROCESS_ENTER)
        self.imgnameexttc = wx.ComboBox(self,
                                        value=self.thisapp.save_img_ext_str,
                                        style=wx.CB_READONLY,
                                        choices=['.png', '.jpg', '.jpeg',
                                                 '.svg', '.tiff', '.eps',
                                                 '.pdf', '.ps'])
        self.imgdatnamepretc = wx.TextCtrl(
            self,
            value=self.thisapp.save_dat_name_str,
            style=wx.TE_PROCESS_ENTER)
        self.imgdatnameexttc = wx.ComboBox(self,
                                           value=self.thisapp.save_dat_ext_str,
                                           style=wx.CB_READONLY,
                                           choices=['.asc', '.hdf5', '.sdds'])
        self.intnamepretc = wx.TextCtrl(self,
                                        value=self.thisapp.save_int_name_str,
                                        style=wx.TE_PROCESS_ENTER)
        self.intnameexttc = wx.ComboBox(self,
                                        value=self.thisapp.save_int_ext_str,
                                        style=wx.CB_READONLY,
                                        choices=['.png', '.jpg', '.jpeg',
                                                 '.svg', '.tiff', '.eps',
                                                 '.pdf', '.ps'])

        gs.Add(imginifuncst,
               pos=(0, 0),
               span=(1, 1),
               flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL,
               border=10)
        gs.Add(self.imginifunccb,
               pos=(0, 1),
               span=(1, 3),
               flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
               border=10)

        gs.Add(imgwpxst,
               pos=(1, 0),
               span=(1, 1),
               flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL,
               border=10)
        gs.Add(self.imgwpxtc,
               pos=(1, 1),
               span=(1, 3),
               flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
               border=10)
        gs.Add(imghpxst,
               pos=(2, 0),
               span=(1, 1),
               flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL,
               border=10)
        gs.Add(self.imghpxtc,
               pos=(2, 1),
               span=(1, 3),
               flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
               border=10)
        gs.Add(pathst,
               pos=(3, 0),
               span=(1, 1),
               flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL,
               border=10)
        gs.Add(self.pathtc,
               pos=(3, 1),
               span=(1, 2),
               flag=wx.EXPAND | wx.LEFT | wx.ALIGN_CENTER_VERTICAL,
               border=10)
        gs.Add(self.pathbtn,
               pos=(3, 3),
               span=(1, 1),
               flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
               border=10)
        gs.Add(imgnameprest,
               pos=(4, 0),
               span=(1, 1),
               flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL,
               border=10)
        gs.Add(self.imgnamepretc,
               pos=(4, 1),
               span=(1, 3),
               flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
               border=10)
        gs.Add(imgnameextst,
               pos=(5, 0),
               span=(1, 1),
               flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL,
               border=10)
        gs.Add(self.imgnameexttc,
               pos=(5, 1),
               span=(1, 3),
               flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
               border=10)

        gs.Add(imgdatnameprest,
               pos=(6, 0),
               span=(1, 1),
               flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL,
               border=10)
        gs.Add(self.imgdatnamepretc,
               pos=(6, 1),
               span=(1, 3),
               flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
               border=10)
        gs.Add(imgdatnameextst,
               pos=(7, 0),
               span=(1, 1),
               flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL,
               border=10)
        gs.Add(self.imgdatnameexttc,
               pos=(7, 1),
               span=(1, 3),
               flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
               border=10)

        gs.Add(intnameprest,
               pos=(8, 0),
               span=(1, 1),
               flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL,
               border=10)
        gs.Add(self.intnamepretc,
               pos=(8, 1),
               span=(1, 3),
               flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
               border=10)
        gs.Add(intnameextst,
               pos=(9, 0),
               span=(1, 1),
               flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL,
               border=10)
        gs.Add(self.intnameexttc,
               pos=(9, 1),
               span=(1, 3),
               flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
               border=10)
        gs.AddGrowableCol(1, 2)
        gs.AddGrowableCol(2, 0)
        vboxsizer.Add(gs,
                      proportion=0,
                      flag=wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT |
                      wx.TOP,
                      border=15)

        vboxsizer.Add((-1, 10))

        ## set boxsizer
        self.SetSizer(vboxsizer)

        ## bind events
        self.Bind(wx.EVT_TEXT_ENTER, self.onUpdateParams, self.imgwpxtc)
        self.Bind(wx.EVT_TEXT_ENTER, self.onUpdateParams, self.imghpxtc)
        self.Bind(wx.EVT_BUTTON, self.onChooseDirpath, self.pathbtn)

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
            dial = wx.MessageDialog(
                self,
                message=u"Error, please input an integer number!",
                caption=u"Input Error",
                style=wx.OK | wx.CANCEL | wx.ICON_ERROR | wx.CENTRE)
            if dial.ShowModal() == wx.ID_OK:
                obj.SetValue('')
                dial.Destroy()


class StyleConfigPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        super(self.__class__, self).__init__(
            parent=parent, id=wx.ID_ANY, **kwargs)
        self.parent = parent
        self.thisapp = self.parent.parent.parent
        self.initUI()

    def initUI(self):
        self.initConfig()
        self.createPanel()

    def initConfig(self):
        self.bkgdcolor = wx.BLUE
        self.fontcolor = wx.BLACK
        self.fontptsize = 10
        self.fontweight = wx.FONTWEIGHT_NORMAL
        self.font = self.thisapp.font

    def createPanel(self):
        vboxsizer = wx.BoxSizer(wx.VERTICAL)

        bkgdcolorst = wx.StaticText(self,
                                    label=u'Background Color',
                                    style=wx.ALIGN_LEFT)
        self.bkgdcolortc = wx.TextCtrl(
            self,
            value=funutils.rgb2hex(self.thisapp.bkgdcolor).upper(),
            style=wx.TE_READONLY)
        self.bkgdcolorbtn = wx.Button(self,
                                      label='Choose Color',
                                      size=(140, -1))

        fontst = wx.StaticText(self, label=u'Font', style=wx.ALIGN_LEFT)
        self.chosenfonttc = funutils.MyTextCtrl(self,
                                                value=u'Do it Pythonicly.',
                                                style=wx.TE_READONLY,
                                                font=self.font)
        self.choosefontbtn = wx.Button(self,
                                       label='Choose Font',
                                       size=(140, -1))

        gsstyle = wx.GridBagSizer(5, 5)
        gsstyle.Add(bkgdcolorst,
                    pos=(0, 0),
                    span=(1, 1),
                    flag=wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL,
                    border=10)
        gsstyle.Add(self.bkgdcolortc,
                    pos=(0, 1),
                    span=(1, 2),
                    flag=wx.EXPAND | wx.LEFT | wx.RIGHT |
                    wx.ALIGN_CENTER_VERTICAL,
                    border=10)
        gsstyle.Add(self.bkgdcolorbtn,
                    pos=(0, 3),
                    span=(1, 1),
                    flag=wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
                    border=10)
        gsstyle.Add(fontst,
                    pos=(1, 0),
                    span=(1, 1),
                    flag=wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL,
                    border=10)
        gsstyle.Add(self.chosenfonttc,
                    pos=(1, 1),
                    span=(1, 2),
                    flag=wx.EXPAND | wx.LEFT | wx.RIGHT |
                    wx.ALIGN_CENTER_VERTICAL,
                    border=10)
        gsstyle.Add(self.choosefontbtn,
                    pos=(1, 3),
                    span=(1, 1),
                    flag=wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
                    border=10)
        gsstyle.AddGrowableCol(1, 0)

        vboxsizer.Add(gsstyle, flag=wx.EXPAND | wx.ALL, border=15)

        vboxsizer.Add((-1, 10))

        ## set boxsizer
        self.SetSizer(vboxsizer)

        ## bind events
        self.Bind(wx.EVT_BUTTON, self.onChooseColor, self.bkgdcolorbtn)
        self.Bind(wx.EVT_BUTTON, self.onChooseFont, self.choosefontbtn)

    def onChooseColor(self, event):
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True)  # only windows
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
            #print self.font.GetFaceName(), self.font.GetFamilyString()
            self.chosenfonttc.SetFont(self.font)
        else:
            dial.Destroy()


class ControlConfigPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        super(self.__class__, self).__init__(
            parent=parent, id=wx.ID_ANY, **kwargs)
        self.parent = parent
        self.thisapp = self.parent.parent.parent
        self.initUI()

    def initUI(self):
        self.initConfig()
        self.createPanel()

    def initConfig(self):
        self.bkgdcolor = wx.BLUE
        self.fontcolor = wx.BLACK
        self.fontptsize = 10
        self.fontweight = wx.FONTWEIGHT_NORMAL

    def createPanel(self):
        vboxsizer = wx.BoxSizer(wx.VERTICAL)

        # frequency
        freqst = wx.StaticText(self,
                               label=u'Monitor Frequency [Hz]',
                               style=wx.ALIGN_RIGHT)
        #self.freqtc  = wx.SpinCtrl(self, value = str(self.thisapp.timer_freq),  min = 1, max = 50, initial = 1, style = wx.SP_ARROW_KEYS)
        self.freqtc = fs.FloatSpin(self,
                                   value=str(self.thisapp.timer_freq),
                                   min_val=0.1,
                                   max_val=50,
                                   increment=0.05,
                                   digits=2,
                                   style=fs.FS_LEFT)

        # PV list
        imgsrcPVst = wx.StaticText(self,
                                   label=u'Image PV Name',
                                   style=wx.ALIGN_RIGHT)
        self.imgsrcPVcb = wx.ComboBox(
            self,
            value=self.thisapp.imgsrcPV,
            style=wx.CB_READONLY,
            choices=sorted(self.thisapp.imgsrcPVlist))

        # LIBCA PATH
        libcaPathst = wx.StaticText(self,
                                    label=u'CA Library Path',
                                    style=wx.ALIGN_RIGHT)
        libcaPathtc = wx.TextCtrl(self,
                                  value=self.thisapp.libcaPath,
                                  style=wx.TE_READONLY)
        libcaPathbtn = wx.Button(self, label=u'Browse')
        self.libcaPathtc = libcaPathtc

        # EPICS ENVS
        caAddrAutochk = wx.CheckBox(self, label=u'Auto CA Address')
        caAddrListst = wx.StaticText(self,
                                     label=u'CA Address List',
                                     style=wx.ALIGN_RIGHT)
        caAddrListtc = wx.TextCtrl(self,
                                   value=self.thisapp.caAddrList,
                                   style=wx.TE_PROCESS_ENTER)
        caAddrListtc.SetToolTip(wx.ToolTip(
            "Input IP addresses or hostnames seperated by ';' or ',' or SPACE."))
        caAddrAutochk.SetValue(self.thisapp.caAddrAuto)
        self.caAddrAutochk = caAddrAutochk
        self.caAddrListst = caAddrListst
        self.caAddrListtc = caAddrListtc
        if self.caAddrAutochk.IsChecked():
            caAddrListst.Disable()
            caAddrListtc.Disable()
        else:
            caAddrListst.Enable()
            caAddrListtc.Enable()

        caArrayBytesst = wx.StaticText(self,
                                       label=u'CA Max Array Bytes',
                                       style=wx.ALIGN_RIGHT)
        caArrayBytestc = wx.TextCtrl(self,
                                     value=str(self.thisapp.caArrayBytes),
                                     style=wx.TE_PROCESS_ENTER)
        self.caArrayBytestc = caArrayBytestc

        # pixel unit
        pixelSizest = wx.StaticText(self,
                                    label=u'Pixel Size in \N{GREEK SMALL LETTER MU}m',
                                    style=wx.ALIGN_RIGHT)
        pixelSizetc = wx.TextCtrl(self,
                                  value=str(self.thisapp.pixelSize),
                                  style=wx.TE_PROCESS_ENTER)
        self.pixelSizetc = pixelSizetc

        gsctrl = wx.GridBagSizer(5, 5)
        gsctrl.Add(freqst,
                   pos=(0, 0),
                   span=(1, 1),
                   flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL,
                   border=10)
        gsctrl.Add(self.freqtc,
                   pos=(0, 1),
                   span=(1, 3),
                   flag=wx.EXPAND | wx.LEFT | wx.RIGHT |
                   wx.ALIGN_CENTER_VERTICAL,
                   border=10)

        gsctrl.Add(imgsrcPVst,
                   pos=(1, 0),
                   span=(1, 1),
                   flag=wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
                   border=10)
        gsctrl.Add(self.imgsrcPVcb,
                   pos=(1, 1),
                   span=(1, 3),
                   flag=wx.EXPAND | wx.LEFT | wx.RIGHT |
                   wx.ALIGN_CENTER_VERTICAL,
                   border=10)

        gsctrl.Add(libcaPathst,
                   pos=(2, 0),
                   span=(1, 1),
                   flag=wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
                   border=10)
        gsctrl.Add(libcaPathtc,
                   pos=(2, 1),
                   span=(1, 3),
                   flag=wx.EXPAND | wx.LEFT | wx.RIGHT |
                   wx.ALIGN_CENTER_VERTICAL,
                   border=10)
        gsctrl.Add(libcaPathbtn,
                   pos=(2, 4),
                   span=(1, 1),
                   flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
                   border=10)

        gsctrl.Add(caArrayBytesst,
                   pos=(3, 0),
                   span=(1, 1),
                   flag=wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
                   border=10)
        gsctrl.Add(caArrayBytestc,
                   pos=(3, 1),
                   span=(1, 3),
                   flag=wx.EXPAND | wx.LEFT | wx.RIGHT |
                   wx.ALIGN_CENTER_VERTICAL,
                   border=10)

        gsctrl.Add(caAddrAutochk,
                   pos=(4, 0),
                   span=(1, 4),
                   flag=wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
                   border=10)

        gsctrl.Add(caAddrListst,
                   pos=(5, 0),
                   span=(1, 1),
                   flag=wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
                   border=10)
        gsctrl.Add(caAddrListtc,
                   pos=(5, 1),
                   span=(1, 3),
                   flag=wx.EXPAND | wx.LEFT | wx.RIGHT |
                   wx.ALIGN_CENTER_VERTICAL,
                   border=10)

        gsctrl.Add(pixelSizest,
                   pos=(6, 0),
                   span=(1, 1),
                   flag=wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
                   border=10)
        gsctrl.Add(pixelSizetc,
                   pos=(6, 1),
                   span=(1, 3),
                   flag=wx.EXPAND | wx.LEFT | wx.RIGHT |
                   wx.ALIGN_CENTER_VERTICAL,
                   border=10)

        gsctrl.AddGrowableCol(1)
        gsctrl.AddGrowableCol(2)
        gsctrl.AddGrowableCol(3)

        vboxsizer.Add(gsctrl,
                      flag=wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT |
                      wx.TOP,
                      border=15)

        vboxsizer.Add((-1, 10))

        ## set boxsizer
        self.SetSizer(vboxsizer)

        ## bind events
        self.Bind(wx.EVT_BUTTON, self.onChooseLib, libcaPathbtn)
        self.Bind(wx.EVT_CHECKBOX, self.onCheckAuto, caAddrAutochk)
        self.Bind(wx.EVT_TEXT_ENTER, self.onUpdateParams1, caAddrListtc)
        self.Bind(wx.EVT_TEXT_ENTER, self.onUpdateParams2, caArrayBytestc)
        self.Bind(wx.EVT_TEXT_ENTER, self.onUpdateParams2, pixelSizetc)

    def onChooseLib(self, event):
        sofile = funutils.getFileToLoad(self, ext='so')
        self.libcaPathtc.SetValue(sofile)

    def onCheckAuto(self, event):
        if event.GetEventObject().IsChecked():
            self.caAddrListst.Disable()
            self.caAddrListtc.Disable()
        else:
            self.caAddrListst.Enable()
            self.caAddrListtc.Enable()

    def onUpdateParams1(self, event):
        val = event.GetEventObject().GetValue()
        newval = val.replace(',', ';').replace(';', ' ').split()
        event.GetEventObject().SetValue(' '.join(newval))

    def onUpdateParams2(self, event):
        obj = event.GetEventObject()
        try:
            float(obj.GetValue())
        except ValueError:
            dial = wx.MessageDialog(
                self,
                message=u"Error, please input a positive number!",
                caption=u"Input Error",
                style=wx.OK | wx.CANCEL | wx.ICON_ERROR | wx.CENTRE)
            if dial.ShowModal() == wx.ID_OK:
                obj.SetValue('')
                dial.Destroy()


class HistPlotConfigPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        super(self.__class__, self).__init__(
            parent=parent, id=wx.ID_ANY, **kwargs)
        self.parent = parent
        self.thisapp = self.parent.parent.parent
        self.initUI()

    def initUI(self):
        self.initConfig()
        self.createPanel()

    def initConfig(self):
        self.bkgdcolor = wx.BLUE
        self.fontcolor = wx.BLACK
        self.fontptsize = 10
        self.fontweight = wx.FONTWEIGHT_NORMAL

    def createPanel(self):
        vboxsizer = wx.BoxSizer(wx.VERTICAL)

        # height ratio
        heightratiost = wx.StaticText(self,
                                      label=u'Height Ratio',
                                      style=wx.ALIGN_RIGHT)
        self.heightratiotc = fs.FloatSpin(self,
                                          value=str(self.thisapp.heightRatio),
                                          min_val=0.0,
                                          max_val=0.95,
                                          increment=0.05,
                                          digits=2,
                                          style=fs.FS_LEFT)

        gshist = wx.GridBagSizer(5, 5)
        gshist.Add(heightratiost,
                   pos=(0, 0),
                   span=(1, 1),
                   flag=wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
                   border=10)
        gshist.Add(self.heightratiotc,
                   pos=(0, 2),
                   span=(1, 2),
                   flag=wx.EXPAND | wx.LEFT | wx.RIGHT |
                   wx.ALIGN_CENTER_VERTICAL,
                   border=10)
        gshist.AddGrowableCol(2, 0)

        vboxsizer.Add(gshist,
                      flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                      border=15)

        vboxsizer.Add((-1, 10))

        ## set boxsizer
        self.SetSizer(vboxsizer)


class ShowIntPanel(wx.Frame):
    def __init__(self, parent, **kwargs):
        super(self.__class__, self).__init__(
            parent=parent,
            id=wx.ID_ANY,
            style=wx.DEFAULT_FRAME_STYLE &
            ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX),
            **kwargs)
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
        self.panel = wx.Panel(self, id=wx.ID_ANY)
        self.panel.SetBackgroundColour(self.parent.bkgdcolor)

        vbox = wx.BoxSizer(wx.VERTICAL)

        sbox = wx.StaticBox(self.panel,
                            id=wx.ID_ANY,
                            label=u'Intensity Monitor',
                            style=wx.ALIGN_LEFT)
        sbfont = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        sbfont.SetPointSize(8)
        sbfont.SetWeight(wx.FONTWEIGHT_NORMAL)
        sbfontcolor = 'GREY'
        sbox.SetFont(sbfont)
        sbox.SetForegroundColour(sbfontcolor)
        sbsizer = wx.StaticBoxSizer(sbox, orient=wx.VERTICAL)

        self.intdisp = ImagePanelxy(self.panel,
                                    figsize=(9, 7),
                                    dpi=80,
                                    bgcolor=self.parent.bkgdcolor)
        sbsizer.Add(self.intdisp, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        #### btns
        self.daqbtn = wx.Button(self.panel, label='Start')
        self.savebtn = wx.Button(self.panel, label='Save')
        self.Bind(wx.EVT_BUTTON, self.onTimerControl, self.daqbtn)
        self.Bind(wx.EVT_BUTTON, self.onSaveFigure, self.savebtn)
        hboxbtn = wx.BoxSizer(orient=wx.HORIZONTAL)
        hboxbtn.Add(self.daqbtn,
                    proportion=1,
                    flag=wx.EXPAND | wx.BOTTOM,
                    border=10)
        hboxbtn.Add(self.savebtn,
                    proportion=1,
                    flag=wx.EXPAND | wx.LEFT | wx.BOTTOM,
                    border=10)
        sbsizer.Add(hboxbtn, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)

        vbox.Add(sbsizer, flag=wx.ALL, border=15)

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
    def __init__(self,
                 parent,
                 figsize,
                 dpi,
                 bgcolor,
                 heightratio=0.4,
                 func='peaks',
                 **kwargs):
        #super(self.__class__, self).__init__(parent = parent, **kwargs)
        wx.Panel.__init__(self, parent, **kwargs)
        self.parent = parent
        self.figsize = figsize
        self.dpi = dpi
        self.bgcolor = bgcolor
        self.hratio = heightratio
        self.func = func
        self.figure = Figure(self.figsize, self.dpi)
        self.canvas = FigureCanvasWxAgg(self, -1, self.figure)
        self.cmaptype = 'jet'
        self.setColor(self.bgcolor)
        self.onGetData()
        self.onConfigPlot()
        self.doPlot()
        wx.CallAfter(self.fitCanvas)  # fit canvas size after initialization

        # resize figure when size event trigged
        self.Bind(wx.EVT_SIZE, self.onSize)

        self.canvas.mpl_connect('button_press_event', self.onPress)
        self.canvas.mpl_connect('button_release_event', self.onRelease)
        self.canvas.mpl_connect('motion_notify_event', self.onMotion)

        self.mkc1 = wx.Colour(255, 0, 0).GetAsString(wx.C2S_HTML_SYNTAX)
        self.mkc2 = wx.Colour(240, 230, 140).GetAsString(wx.C2S_HTML_SYNTAX)
        self.pcc = wx.Colour(0, 0, 0).GetAsString(wx.C2S_HTML_SYNTAX)

        self.mk1 = False
        self.mk2 = False

    def onConfigPlot(self):
        pass

    def onRelease(self, event):
        pass
        #print("%d,%d" % (event.xdata, event.ydata))

    def onMotion(self, event):
        if event.inaxes is not None:
            self.parent.GetParent().pos_val.SetLabel("(%.4f,%.4f)" %
                                                     (event.xdata,
                                                      event.ydata))

    def setHratio(self, hratio):
        self.hratio = hratio

    def setColor(self, rgbtuple=None):
        """Set figure and canvas colours to be the same."""
        if rgbtuple is None:
            rgbtuple = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE).Get()
        clr = [c / 255. for c in rgbtuple]
        self.figure.set_facecolor(clr)
        self.figure.set_edgecolor(clr)
        self.canvas.SetBackgroundColour(wx.Colour(*rgbtuple))

    def refresh(self):
        self.canvas.draw_idle()

    def repaint(self):
        self.onSetHist()
        self.figure.canvas.draw_idle()

    def onSetcm(self, cmap):
        self.cmaptype = cmap
        self.im.set_cmap(self.cmaptype)
        self.im.set_array(self.z)
        self.repaint()

    def onSetHist(self):
        self.histx = self.z.sum(axis=0)
        self.histy = self.z.sum(axis=1)
        idxmaxx, idxmaxy = np.where(self.histx == self.histx.max()), np.where(
            self.histy == self.histy.max())
        self.maxidx, self.maxidy = idxmaxx[0][0], idxmaxy[0][0]
        self.xx = np.arange(self.histx.size) + 1
        self.yy = np.arange(self.histy.size) + 1
        self.linex.set_xdata(self.xx)
        self.linex.set_ydata(self.histx / self.histx.max() * self.maxidy *
                             self.hratio)
        self.liney.set_xdata(self.histy / self.histy.max() * self.maxidx *
                             self.hratio)
        self.liney.set_ydata(self.yy)
        self.xyscalar = [self.xx.min(), self.xx.max(), self.yy.min(),
                         self.yy.max()]
        self.im.set_extent(self.xyscalar)
        self.axes.set_xlim(self.xyscalar[0:2])
        self.axes.set_ylim(self.xyscalar[2:4])

    def onSetCr(self, crange):
        self.im.set_clim(crange)
        self.repaint()

    def doPlot(self):
        if not hasattr(self, 'axes'):
            self.axes = self.figure.add_subplot(111)
        self.linex, = self.axes.plot(self.xx, self.histx / self.histx.max() *
                                     self.maxidy * self.hratio, 'w--')
        self.liney, = self.axes.plot(self.histy / self.histy.max() *
                                     self.maxidx * self.hratio, self.yy, 'w--')

        #self.axes.set_title(r'$f(x,y)=\sin x + \cos y$')
        self.im = self.axes.imshow(self.z,
                                   aspect='equal',
                                   cmap=plt.get_cmap(self.cmaptype),
                                   origin='lower left',
                                   vmin=self.cmin,
                                   vmax=self.cmax)
        self.im.set_extent(self.xyscalar)
        self.linex.set_visible(False)
        self.liney.set_visible(False)
        self.axes.set_xlim(self.xyscalar[0:2])
        self.axes.set_ylim(self.xyscalar[2:4])
        self.figure.canvas.draw()

    def onGetData(self):

        if self.func == 'peaks':
            x = np.linspace(-np.pi, np.pi, 100)
            y = np.linspace(-np.pi, np.pi, 100)
            self.x, self.y = np.meshgrid(x, y)
            self.z = funutils.func_peaks(self.x, self.y)
        elif self.func == 'sinc':
            x = np.linspace(-2 * np.pi, 2 * np.pi, 100)
            y = np.linspace(-2 * np.pi, 2 * np.pi, 100)
            self.x, self.y = np.meshgrid(x, y)
            self.z = funutils.func_sinc(self.x, self.y)

        self.cmin = self.z.min()
        self.cmax = self.z.max()

        self.histx = self.z.sum(axis=0)
        self.histy = self.z.sum(axis=1)
        self.xx = np.arange(self.histx.size) + 1
        self.yy = np.arange(self.histy.size) + 1
        idxmaxx, idxmaxy = np.where(self.histx == self.histx.max()), np.where(
            self.histy == self.histy.max())
        self.maxidx, self.maxidy = idxmaxx[0][0], idxmaxy[0][0]
        self.xyscalar = [self.xx.min(), self.xx.max(), self.yy.min(),
                         self.yy.max()]

    def fitCanvas(self):
        self.canvas.SetSize(self.GetSize())
        self.figure.set_tight_layout(True)
        self.figure.subplots_adjust(
            top=0.9999, bottom=0.0001,
            left=0.0001, right=0.9999)

    def onSize(self, event):
        self.canvas.SetSize(self.GetSize())
        self.figure.set_tight_layout(True)
        self.figure.subplots_adjust(
            top=0.9999, bottom=0.0001,
            left=0.0001, right=0.9999)

    def onPress(self, event):
        if event.inaxes:
            x0, y0 = event.xdata, event.ydata
            self.draw_hvlines(x0, y0)

    def set_markflags(self, mk1=False, mk2=False):
        self.mk1, self.mk2 = mk1, mk2
        try:
            if self.mk1 == True:
                self._draw_hvlines1(self.x_pos1, self.y_pos1)
            elif self.mk2 == True:
                self._draw_hvlines2(self.x_pos2, self.y_pos2)
        except:
            return

    def set_mkc1(self, color):
        self.mkc1 = color

    def set_mkc2(self, color):
        self.mkc2 = color

    def set_pcc(self, color):
        self.pcc = color
        if hasattr(self, 'pc1'):
            self.pc1.set_mec(color)
            self.pc1.set_mfc(color)
        if hasattr(self, 'pc2'):
            self.pc2.set_mec(color)
            self.pc2.set_mfc(color)
        if hasattr(self, 'plbl1'):
            self.plbl1.set_color(color)
        if hasattr(self, 'plbl2'):
            self.plbl2.set_color(color)
        self.refresh()

    def draw_hvlines(self, x0, y0):
        if self.mk1 == True:
            self._draw_hvlines1(x0, y0)
        elif self.mk2 == True:
            self._draw_hvlines2(x0, y0)
        self.update_deltxy()

    def _draw_hvlines1(self, x0, y0):
        if hasattr(self, 'plbl1'):
            self.plbl1.set_position((x0, y0))
        else:
            self.plbl1 = self.axes.text(x0, y0, r'$\mathsf{M1}$', fontsize=16, alpha=0.5)
        self.plbl1.set_color(self.pcc)

        if hasattr(self, 'hl1'):
            self.hl1.set_ydata([y0, y0])
        else:
            self.hl1 = self.axes.axhline(y0, ls='--')
        self.hl1.set_color(self.mkc1)

        if hasattr(self, 'vl1'):
            self.vl1.set_xdata([x0, x0])
        else:
            self.vl1 = self.axes.axvline(x0, ls='--')
        self.vl1.set_color(self.mkc1)

        if hasattr(self, 'pc1'):
            self.pc1.set_data(x0, y0)
        else:
            self.pc1, = self.axes.plot(x0, y0, 'ko', ms=6, mfc='k', mec='k')
        self.pc1.set_mec(self.pcc)
        self.pc1.set_mfc(self.pcc)

        self.x_pos1, self.y_pos1 = x0, y0

        self.parent.GetParent().m1_pos_st.SetLabel('{0:.1f},{1:.1f}'.format(x0, y0))

        self.refresh()

    def _draw_hvlines2(self, x0, y0):
        if hasattr(self, 'plbl2'):
            self.plbl2.set_position((x0, y0))
        else:
            self.plbl2 = self.axes.text(x0, y0, r'$\mathsf{M2}$', fontsize=16, alpha=0.5)
        self.plbl2.set_color(self.pcc)

        if hasattr(self, 'hl2'):
            self.hl2.set_ydata([y0, y0])
        else:
            self.hl2 = self.axes.axhline(y0, color='r', ls='--')
        self.hl2.set_color(self.mkc2)

        if hasattr(self, 'vl2'):
            self.vl2.set_xdata([x0, x0])
        else:
            self.vl2 = self.axes.axvline(x0, color='r', ls='--')
        self.vl2.set_color(self.mkc2)

        if hasattr(self, 'pc2'):
            self.pc2.set_data(x0, y0)
        else:
            self.pc2, = self.axes.plot(x0, y0, 'ko', ms=6, mfc='k', mec='k')
        self.pc2.set_mec(self.pcc)
        self.pc2.set_mfc(self.pcc)

        self.x_pos2, self.y_pos2 = x0, y0

        self.parent.GetParent().m2_pos_st.SetLabel('{0:.1f},{1:.1f}'.format(x0, y0))
        self.refresh()

    def update_deltxy(self):
        ps = self.parent.GetParent().pixelSize
        m1_pos_val = self.parent.GetParent().m1_pos_st.GetLabel()
        m2_pos_val = self.parent.GetParent().m2_pos_st.GetLabel()
        if m1_pos_val != '' and m2_pos_val != '':
            x1, y1 = [float(i) for i in m1_pos_val.split(',')]
            x2, y2 = [float(i) for i in m2_pos_val.split(',')]
            dx = abs(x1 - x2)
            dy = abs(y1 - y2)
            self.parent.GetParent().delx_val_st.SetLabel("{0:.1f}|{1:.1f}".format(dx,dx*ps) + u'\N{GREEK SMALL LETTER MU}m')
            self.parent.GetParent().dely_val_st.SetLabel("{0:.1f}|{1:.1f}".format(dy,dy*ps) + u'\N{GREEK SMALL LETTER MU}m')

class FitPlotFrame(wx.Frame):
    def __init__(self, parent, model_x, model_y, **kwargs):
        super(self.__class__, self).__init__(parent=parent,
                                             style=wx.DEFAULT_FRAME_STYLE,
                                             **kwargs)
        self._parent = parent
        self._model_x = model_x
        self._model_y = model_y

        self._font = self._parent.font
        self._fontsize = self._parent.fontptsize_normal

        self._init()

    def _init(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox_l = wx.BoxSizer(wx.HORIZONTAL)
        hbox_r = wx.BoxSizer(wx.HORIZONTAL)
        panel = wx.Panel(self)
        plotpanel = FitPlotPanel(panel,
                                 figsize=(9, 7),
                                 dpi=80,
                                 bgcolor=self._parent.bkgdcolor,
                                 fitmodel_x=self._model_x,
                                 fitmodel_y=self._model_y)
        self.plotpanel = plotpanel

        # left hbox, x,y ranges
        auto_scale_ckb = funutils.MyCheckBox(panel,
                                             label=u'Auto',
                                             font=self._font,
                                             fontsize=self._fontsize)

        x1range_st = funutils.MyStaticText(panel,
                                           label=u'X1',
                                           style=wx.ALIGN_LEFT,
                                           font=self._font,
                                           fontsize=self._fontsize,
                                           fontcolor='black')
        x2range_st = funutils.MyStaticText(panel,
                                           label=u'X2',
                                           style=wx.ALIGN_LEFT,
                                           font=self._font,
                                           fontsize=self._fontsize,
                                           fontcolor='black')
        y1range_st = funutils.MyStaticText(panel,
                                           label=u'Y1',
                                           style=wx.ALIGN_LEFT,
                                           font=self._font,
                                           fontsize=self._fontsize,
                                           fontcolor='black')
        y2range_st = funutils.MyStaticText(panel,
                                           label=u'Y2',
                                           style=wx.ALIGN_LEFT,
                                           font=self._font,
                                           fontsize=self._fontsize,
                                           fontcolor='black')
        x1range_tc = funutils.MyTextCtrl(panel,
                                         name='x1',
                                         value="",
                                         style=wx.TE_PROCESS_ENTER,
                                         font=self._font,
                                         fontsize=self._fontsize)
        x2range_tc = funutils.MyTextCtrl(panel,
                                         name='x2',
                                         value="",
                                         style=wx.TE_PROCESS_ENTER,
                                         font=self._font,
                                         fontsize=self._fontsize)
        y1range_tc = funutils.MyTextCtrl(panel,
                                         name='y1',
                                         value="",
                                         style=wx.TE_PROCESS_ENTER,
                                         font=self._font,
                                         fontsize=self._fontsize)
        y2range_tc = funutils.MyTextCtrl(panel,
                                         name='y2',
                                         value="",
                                         style=wx.TE_PROCESS_ENTER,
                                         font=self._font,
                                         fontsize=self._fontsize)
        self.x1range_st = x1range_st
        self.x2range_st = x2range_st
        self.x1range_tc = x1range_tc
        self.x2range_tc = x2range_tc
        self.y1range_st = y1range_st
        self.y2range_st = y2range_st
        self.y1range_tc = y1range_tc
        self.y2range_tc = y2range_tc
        # set tc values
        x1range = self.plotpanel.ax1.get_xlim()
        x2range = self.plotpanel.ax2.get_xlim()
        y1range = self.plotpanel.ax1.get_ylim()
        y2range = self.plotpanel.ax2.get_ylim()
        x1range_tc.SetValue("{0:.1f}:{1:.1f}".format(x1range[0], x1range[1]))
        x2range_tc.SetValue("{0:.1f}:{1:.1f}".format(x2range[0], x2range[1]))
        y1range_tc.SetValue("{0:.1f}:{1:.1f}".format(y1range[0], y1range[1]))
        y2range_tc.SetValue("{0:.1f}:{1:.1f}".format(y2range[0], y2range[1]))

        # right hbox, control buttons
        export_btn = funutils.MyButton(panel,
                                       label='&Export',
                                       font=self._parent.font,
                                       fontsize=self._parent.fontptsize_normal)
        exit_btn = funutils.MyButton(panel,
                                     label='E&xit',
                                     font=self._parent.font,
                                     fontsize=self._parent.fontptsize_normal)

        #
        hbox_l.Add(x1range_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        hbox_l.Add(x1range_tc, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        hbox_l.Add(y1range_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        hbox_l.Add(y1range_tc, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        hbox_l.Add(x2range_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        hbox_l.Add(x2range_tc, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        hbox_l.Add(y2range_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        hbox_l.Add(y2range_tc, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        hbox_l.Add(auto_scale_ckb, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)

        hbox_r.Add(export_btn, 0, wx.LEFT, 5)
        hbox_r.Add(exit_btn, 0, wx.LEFT, 5)
        hbox.Add(hbox_l, 1, wx.EXPAND)
        hbox.Add(hbox_r, 0, wx.EXPAND)

        #
        vbox.Add(plotpanel, 1, wx.EXPAND | wx.ALL, 10)
        vbox.Add(
            wx.StaticLine(panel, wx.LI_HORIZONTAL), 0, wx.EXPAND | wx.LEFT |
            wx.RIGHT, 10)
        vbox.Add(hbox, 0, wx.EXPAND | wx.ALL, 10)

        panel.SetSizer(vbox)

        # events
        self.Bind(wx.EVT_BUTTON, self.onExit, exit_btn)
        self.Bind(wx.EVT_BUTTON, self.onExport, export_btn)
        self.Bind(wx.EVT_TEXT_ENTER, self.onSetRange)
        self.Bind(wx.EVT_CHECKBOX, self.onAutoScale, auto_scale_ckb)

    def onAutoScale(self, event):
        if event.GetEventObject().IsChecked():
            self.plotpanel.ax1.autoscale()
            self.plotpanel.ax2.autoscale()
            self.plotpanel.refresh_draw()
            for obj in (self.x1range_st, self.x1range_tc, self.y1range_st,
                        self.y1range_tc, self.x2range_st, self.x2range_tc,
                        self.y2range_st, self.y2range_tc):
                obj.Disable()
        else:
            for obj in (self.x1range_tc, self.y1range_tc, self.x2range_tc,
                        self.y2range_tc):
                obj.Enable()
                range_list = [float(i) for i in obj.GetValue().split(':')]
                self.set_datalim(obj.GetName(), range_list)
            for obj in (self.x1range_st, self.y1range_st, self.x2range_st,
                        self.y2range_st):
                obj.Enable()

    def set_datalim(self, nid, range_list):
        if nid == 'x1':
            self.plotpanel.ax1.set_xlim(range_list)
        elif nid == 'y1':
            self.plotpanel.ax1.set_ylim(range_list)
        elif nid == 'x2':
            self.plotpanel.ax2.set_xlim(range_list)
        elif nid == 'y2':
            self.plotpanel.ax2.set_ylim(range_list)
        self.plotpanel.refresh_draw()

    def onExit(self, event):
        self.Close(True)

    def onExport(self, event):
        data_raw = self.plotpanel.data_raw
        data_fit = self.plotpanel.data_fit
        if not os.path.exists(self._parent.save_path_str):
            os.system('mkdir -p' + ' ' + self._parent.save_path_str)
        filelabel = time.strftime('%H%M%S', time.localtime())
        savetofilename = self._parent.save_path_str + '/' + 'fitdata' + filelabel + '.hdf5'
        try:
            funutils.ExportData(data_raw, data_fit, self._model_x, self._model_y, savetofilename)
            dial = wx.MessageDialog(self,
                                    message=u"Data saved into " + savetofilename + ".",
                                    caption=u"Successfully Saved Data",
                                    style=wx.OK | wx.ICON_WARNING | wx.CENTRE)
            if dial.ShowModal() == wx.ID_OK:
                dial.Destroy()
        except:
            dial = wx.MessageDialog(self,
                                    message=u"Data cannot saved into " + savetofilename + ".",
                                    caption=u"Saved Data Failure",
                                    style=wx.OK | wx.ICON_WARNING | wx.CENTRE)
            if dial.ShowModal() == wx.ID_OK:
                dial.Destroy()
    
    def onSetRange(self, event):
        obj = event.GetEventObject()
        nid = obj.GetName()
        try:
            range_list = [float(i) for i in obj.GetValue().split(':')]
        except:
            dial = wx.MessageDialog(
                self,
                message="Invalid data range, format required: 'min:max'.",
                caption="Input ERROR",
                style=wx.OK | wx.CENTRE | wx.ICON_ERROR)
            if dial.ShowModal() == wx.ID_OK:
                obj.SetValue(':')
                dial.Destroy()
            return
        if len(range_list) == 1:
            dial = wx.MessageDialog(
                self,
                message="Full range should have two numbers, format required: 'min:max'.",
                caption="Input ERROR",
                style=wx.OK | wx.CENTRE | wx.ICON_ERROR)
            if dial.ShowModal() == wx.ID_OK:
                obj.SetValue(':')
                dial.Destroy()
            return
        if range_list[0] >= range_list[1]:
            dial = wx.MessageDialog(
                self,
                message="Invalid range, format required: 'min:max', min<max.",
                caption="Input Warning",
                style=wx.OK | wx.CENTRE | wx.ICON_INFORMATION)
            if dial.ShowModal() == wx.ID_OK:
                dial.Destroy()
            return
        self.set_datalim(nid, range_list)


class ChooseROIFrame(wx.Frame):
    def __init__(self, parent, imgsrcptn, **kwargs):
        super(self.__class__, self).__init__(parent=parent,
                                             id=wx.ID_ANY,
                                             style=wx.DEFAULT_FRAME_STYLE,
                                             **kwargs)
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
        self.roiPanel = ChooseROIPanel(self, figsize=(7, 7), dpi=80)
        self.roiPanel.doPlot(imgsrcptn)

        self.cancelbtn = wx.Button(self, label='Cancel')
        self.okbtn = wx.Button(self, label='OK')

        self.Bind(wx.EVT_BUTTON, self.onCancel, self.cancelbtn)
        self.Bind(wx.EVT_BUTTON, self.onGetROI, self.okbtn)

        hboxbtn = wx.BoxSizer(wx.HORIZONTAL)
        hboxbtn.Add(self.cancelbtn, proportion=0, flag=wx.EXPAND)
        hboxbtn.Add(self.okbtn,
                    proportion=0,
                    flag=wx.EXPAND | wx.LEFT,
                    border=20)

        vbox.Add(self.roiPanel,
                 proportion=1,
                 flag=wx.EXPAND | wx.ALL,
                 border=5)
        vbox.Add(hboxbtn, flag=wx.ALIGN_CENTER, border=5)
        vbox.Add((-1, 10))
        self.SetSizerAndFit(vbox)

        # get and draw ROI box
        self.is_pressed = False
        self.patch = []
        self.x0, self.y0 = None, None
        self.x1, self.y1 = None, None
        self.figure = self.roiPanel.figure
        self.canvas = self.roiPanel.canvas
        self.axes = self.roiPanel.axes
        self.canvas.mpl_connect('button_press_event', self.onPress)
        self.canvas.mpl_connect('button_release_event', self.onRelease)
        self.canvas.mpl_connect('motion_notify_event', self.onMotion)

    def onCancel(self, event):
        self.Close(True)

    def onGetROI(self, event):
        try:
            self.parent.roixy = sorted([int(self.y0), int(self.y1)]) + sorted(
                [int(self.x0), int(self.x1)])
        except TypeError:
            dial = wx.MessageDialog(
                self,
                message=u"Please simply drag a box on image to get ROI, then click OK.",
                caption=u"Fetch ROI Warning",
                style=wx.OK | wx.ICON_QUESTION | wx.CENTRE)
            if dial.ShowModal() == wx.ID_OK:
                dial.Destroy()
                return
        self.Close(True)

    def onPress(self, event):
        self.is_pressed = True
        self.x0 = event.xdata
        self.y0 = event.ydata

    def onRelease(self, event):
        self.is_pressed = False

    def onMotion(self, event):
        if self.is_pressed and event.inaxes:
            self.x1 = event.xdata
            self.y1 = event.ydata
            if self.x1 == self.x0 or self.y1 == self.y0: return
            self.rect = Rectangle(
                (self.x0, self.y0),
                self.x1 - self.x0,
                self.y1 - self.y0,
                fill=False,
                color='w',
                linestyle='dashed',
                linewidth=2)
            self.patch.append(self.rect)
            [self.axes.add_patch(inspatch) for inspatch in self.patch]
            if len(self.patch) > 0:
                [x.set_visible(False) for x in self.patch[:-1]]
            self.figure.canvas.draw()


class ChooseROIPanel(wx.Panel):
    def __init__(self, parent, figsize, dpi, **kwargs):
        super(self.__class__, self).__init__(parent=parent, **kwargs)
        self.parent = parent
        self.figsize = figsize
        self.dpi = dpi
        self.figure = Figure(self.figsize, self.dpi)
        self.canvas = FigureCanvasWxAgg(self, -1, self.figure)
        self.Bind(wx.EVT_SIZE, self.onSize)

    def doPlot(self, imgsrcptn):
        ## imgsrcptn: object reference for image, from which ROI would be got
        # set background color
        self.setColor(imgsrcptn.bgcolor)

        # set image
        if not hasattr(self, 'axes'):
            self.axes = self.figure.add_subplot(111)
        self.im = self.axes.imshow(imgsrcptn.z,
                                   aspect='equal',
                                   cmap=plt.get_cmap(imgsrcptn.cmaptype),
                                   origin='lower left',
                                   vmin=imgsrcptn.cmin,
                                   vmax=imgsrcptn.cmax)
        self.im.set_extent(imgsrcptn.xyscalar)
        self.figure.canvas.draw()

    def onSize(self, event):
        self.canvas.SetSize(self.GetSize())
        self.figure.set_tight_layout(True)
        self.figure.subplots_adjust(
            top=0.9999, bottom=0.0001,
            left=0.0001, right=0.9999)

    def setColor(self, rgbtuple=None):
        """Set figure and canvas colours to be the same."""
        if rgbtuple is None:
            rgbtuple = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE).Get()
        clr = [c / 255. for c in rgbtuple]
        self.figure.set_facecolor(clr)
        self.figure.set_edgecolor(clr)
        self.canvas.SetBackgroundColour(wx.Colour(*rgbtuple))


class ImagePanelxy(wx.Panel):
    def __init__(self, parent, figsize, dpi, bgcolor, **kwargs):
        #super(self.__class__, self).__init__(parent = parent, **kwargs)
        wx.Panel.__init__(self, parent, **kwargs)
        self.parent = parent
        self.figsize = figsize
        self.dpi = dpi
        self.bgcolor = bgcolor
        self.figure = Figure(self.figsize, self.dpi)
        self.canvas = FigureCanvasWxAgg(self, -1, self.figure)
        self.setColor(self.bgcolor)
        self.onGetData()
        self.onConfigPlot()
        self.doPlot()
        wx.CallAfter(self.fitCanvas)  # fit canvas size after initialization

        self.Bind(wx.EVT_SIZE, self.onSize)

        self.canvas.mpl_connect('button_press_event', self.onPress)
        self.canvas.mpl_connect('button_release_event', self.onRelease)
        self.canvas.mpl_connect('motion_notify_event', self.onMotion)

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

    def setColor(self, rgbtuple=None):
        """Set figure and canvas colours to be the same."""
        if rgbtuple is None:
            rgbtuple = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE).Get()
        clr = [c / 255. for c in rgbtuple]
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
        self.xyplot, = self.axes.plot(self.x, self.y, '.', markersize=1)
        self.figure.canvas.draw()

    def onGetData(self):
        #x = np.linspace(-np.pi, np.pi, 100)
        #y = np.sin(x)
        x = y = []
        self.x, self.y = x, y

    def fitCanvas(self):
        self.canvas.SetSize(self.GetSize())
        self.figure.set_tight_layout(True)
        self.figure.subplots_adjust(
            top=0.9999, bottom=0.0001,
            left=0.0001, right=0.9999)

    def onSize(self, event):
        self.canvas.SetSize(self.GetSize())
        self.figure.set_tight_layout(True)
        self.figure.subplots_adjust(
            top=0.9999, bottom=0.0001,
            left=0.0001, right=0.9999)


class FitPlotPanel(ImagePanelxy):
    def __init__(self, parent, figsize, dpi, bgcolor, fitmodel_x, fitmodel_y,
                 **kwargs):
        self.fitmodel_x = fitmodel_x
        self.fitmodel_y = fitmodel_y
        ImagePanelxy.__init__(self, parent, figsize, dpi, bgcolor, **kwargs)

    def update_fit_modules(self, new_fitmodel_x, new_fitmodel_y):
        self.fitmodel_x = new_fitmodel_x
        self.fitmodel_y = new_fitmodel_y
        self.onGetData()

    def update_figure(self):
        self.linex_raw.set_xdata(self.data_raw['x'])
        self.linex_raw.set_ydata(self.data_raw['xdata'])
        self.linex_fit.set_xdata(self.data_fit['x'])
        self.linex_fit.set_ydata(self.data_fit['xdata'])

        self.liney_raw.set_xdata(self.data_raw['y'])
        self.liney_raw.set_ydata(self.data_raw['ydata'])
        self.liney_fit.set_xdata(self.data_fit['y'])
        self.liney_fit.set_ydata(self.data_fit['ydata'])
        self.canvas.draw_idle()

    def onGetData(self):
        x_raw, xdata_raw = self.fitmodel_x.get_data()
        y_raw, ydata_raw = self.fitmodel_y.get_data()

        x_fit = np.linspace(x_raw.min(), x_raw.max(), 200)
        y_fit = np.linspace(y_raw.min(), y_raw.max(), 200)

        self._x_fit = x_fit
        self._y_fit = y_fit

        fit_res_x = self.fitmodel_x.get_fit_result()
        fit_res_y = self.fitmodel_y.get_fit_result()

        fx, tx = self.fitmodel_x.get_fitfunc(fit_res_x.params)
        fy, ty = self.fitmodel_y.get_fitfunc(fit_res_y.params)

        xdata_fit, ydata_fit = fx(fit_res_x.params, x_fit), fy(
            fit_res_y.params, y_fit)
        self.data_raw = {'x': x_raw,
                         'xdata': xdata_raw,
                         'y': y_raw,
                         'ydata': ydata_raw}
        self.data_fit = {'x': x_fit,
                         'xdata': xdata_fit,
                         'y': y_fit,
                         'ydata': ydata_fit}

    def repaint(self, new_fitmodel_x, new_fitmodel_y):
        self.update_fit_modules(new_fitmodel_x, new_fitmodel_y)
        self.update_figure()

    def refresh_draw(self):
        self.canvas.draw_idle()

    def doPlot(self):
        if not hasattr(self, 'ax1'):
            self.ax1 = self.figure.add_subplot(121)
        if not hasattr(self, 'ax2'):
            self.ax2 = self.figure.add_subplot(122)
        self.linex_raw, = self.ax1.plot(self.data_raw['x'],
                                        self.data_raw['xdata'],
                                        'o',
                                        mec='r',
                                        mfc='r',
                                        ms=6)
        self.linex_fit, = self.ax1.plot(self.data_fit['x'],
                                        self.data_fit['xdata'],
                                        'r--',
                                        lw=2)
        self.liney_raw, = self.ax2.plot(self.data_raw['y'],
                                        self.data_raw['ydata'],
                                        'o',
                                        mec='b',
                                        mfc='b',
                                        ms=6)
        self.liney_fit, = self.ax2.plot(self.data_fit['y'],
                                        self.data_fit['ydata'],
                                        'b--',
                                        lw=2)
        self.ax1.set_title('$\mathrm{Profile}\,x$')
        self.ax2.set_title('$\mathrm{Profile}\,y$')

        self.ax1.autoscale()
        self.ax2.autoscale()
        #self.ax1.set_aspect('auto','datalim')
        #self.ax2.set_aspect('auto','datalim')
        self.canvas.draw()


class ImageColorMap(wx.Panel):
    def __init__(self, parent, figsize, dpi, bgcolor, **kwargs):
        super(self.__class__, self).__init__(parent=parent, **kwargs)
        self.parent = parent
        self.figsize = figsize
        self.dpi = dpi
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

    def setColor(self, rgbtuple=None):
        """Set figure and canvas colours to be the same."""
        if rgbtuple is None:
            rgbtuple = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE).Get()
        clr = [c / 255. for c in rgbtuple]
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
        self.im = self.axes.imshow(self.z,
                                   cmap=plt.get_cmap(self.cmaptype),
                                   origin='lower left',
                                   vmin=self.cmin,
                                   vmax=self.cmax)
        self.axes.set_axis_off()
        self.figure.canvas.draw()

    def onGetData(self):
        g = np.linspace(self.cmin, self.cmax, 80)
        self.z = np.vstack((g, g))

    def fitCanvas(self):
        self.canvas.SetSize(self.GetSize())
        self.figure.set_tight_layout(True)
        self.figure.subplots_adjust(
            top=0.9999, bottom=0.0001,
            left=0.0001, right=0.9999)

    def onSize(self, event):
        self.canvas.SetSize(self.GetSize())
        self.figure.set_tight_layout(True)
        self.figure.subplots_adjust(
            top=0.9999, bottom=0.0001,
            left=0.0001, right=0.9999)


class DebugPanel(wx.Frame):
    def __init__(self, parent, **kwargs):
        super(self.__class__, self).__init__(parent=parent,
                                             id=wx.ID_ANY,
                                             style=wx.DEFAULT_FRAME_STYLE,
                                             **kwargs)
        #style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX), **kwargs)
        self.parent = parent
        self.InitUI()

    def InitUI(self):
        self.createPanel()

    def createPanel(self):
        panel = wx.Panel(self)
        envs = os.environ
        tcfont = wx.Font(8,
                         wx.FONTFAMILY_MODERN,
                         wx.FONTSTYLE_NORMAL,
                         wx.FONTWEIGHT_NORMAL,
                         faceName="Monospace")
        tc = funutils.MyTextCtrl(panel,
                                 value=u'',
                                 style=wx.TE_READONLY | wx.TE_MULTILINE,
                                 font=tcfont)
        tc.AppendText("DEBUG INFORMATION:")
        for k, v in envs.items():
            tc.AppendText("\n{k:>30s}: {v:<10s}".format(k=k, v=v))
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(tc, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        panel.SetSizer(vbox)


def main():
    app = wx.App(redirect=False)
    myframe = ImageViewer(None,
                          title='ImageViewer --- Another Profile Monitor')
    myframe.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
