#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
General matplotlib plot panel developed by wxPython (UI) and Python

Author : Tong Zhang
Created: 2016-07-05 21:20:05 PM CST
"""


import wx
import os
import time
import numpy as np
import h5py

import wx.lib.mixins.inspection as wit
from wx.lib.wordwrap import wordwrap
from ...utils import analysisframe
from ...utils import miscutils
from ...utils import funutils
from ...utils import resutils


__version__ =  miscutils.AppVersions().getVersion('wxmpv')
__author__  = "Tong Zhang"

class MainFrame(analysisframe.AnalysisFrame):
    def __init__(self, parent, appversion=__version__):
        analysisframe.AnalysisFrame.__init__(self, parent, datasrc=None)
        self._appversion = appversion
        self._init_ui()

    def _init_ui(self):
        ## 
        file_menu = wx.Menu()
        open_mitem = wx.MenuItem(file_menu, wx.ID_OPEN, u"&Open\tCtrl+O")
        save_mitem = wx.MenuItem(file_menu, wx.ID_SAVE, u"&Save\tCtrl+S")
        exit_mitem = wx.MenuItem(file_menu, wx.ID_EXIT, u"E&xit\tCtrl+W")
        file_menu.AppendItem(open_mitem)
        file_menu.AppendItem(save_mitem)
        file_menu.AppendSeparator()
        file_menu.AppendItem(exit_mitem)

        ## 
        help_menu = wx.Menu()
        info_mitem = help_menu.Append(wx.ID_HELP, '&Contents\tF1', 'Show help contents')
        about_mitem = help_menu.Append(wx.ID_ABOUT, '&About', 'Show about information')

        ##
        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, u"&File") 
        menu_bar.Append(help_menu, u"&Help") 
        self.SetMenuBar(menu_bar)
        
        # 
        self.Bind(wx.EVT_CLOSE, self.on_exit)
        self.Bind(wx.EVT_MENU, self.onExit,   exit_mitem)
        self.Bind(wx.EVT_MENU, self.on_open,  open_mitem)
        self.Bind(wx.EVT_MENU, self.on_save,  save_mitem)
        self.Bind(wx.EVT_MENU, self.on_about, about_mitem)
        self.Bind(wx.EVT_MENU, self.on_info,  info_mitem)

    def on_info(self, event):
        pass

    def on_exit(self, event):
        dial = wx.MessageDialog(
            self,
            message="Are you sure to exit this application?",
            caption="Exit Warning",
            style=wx.YES_NO | wx.NO_DEFAULT | wx.CENTRE | wx.ICON_QUESTION)
        if dial.ShowModal() == wx.ID_YES:
            self.Destroy()

    def on_about(self, event):
        info = wx.AboutDialogInfo()
        info.Name = "wxMatPlotViewer\n wxmpv "
        info.Version = self._appversion
        info.Copyright = "(C) 2016 Tong Zhang, SINAP, CAS"
        info.Description = wordwrap(
            "Figure plot application build with matplotlib package.\n"
            "It is designed by Python language, using GUI module of wxPython.",
            350, wx.ClientDC(self))
        #info.WebSite = ("http://everyfame.me", "Image Viewer home page")
        info.Developers = ["Tong Zhang <zhangtong@sinap.ac.cn>"]
        licenseText = "wxMatPlotViewer is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.\n" + "\nwxMatPlotViewer is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.\n" + "\nYou should have received a copy of the GNU General Public License along with Image Viewer; if not, write to the Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA"
        info.License = wordwrap(licenseText, 500, wx.ClientDC(self))
        wx.AboutBox(info)

    def on_open(self, event):
        openfile_name = funutils.getFileToLoad(self, ext=['hdf5','h5', 'txt','asc','dat','jpg','jpeg','png','bmp'])
        data, typ = self._get_image_data(openfile_name)
        if data is not None:
            self.plotpanel.clear()
            self.plotpanel.set_figure_data(data, fit=(typ not in ['JPG', 'PNG', 'BMP']))
            self.set_fit_output()
            clim = self.plotpanel.get_clim()
            self.crange_tc.SetValue(clim)

    def on_save(self, event):
        data = self.plotpanel.get_data()
        savefile_name = funutils.getFileToSave(self, ext=['hdf5'])
        if savefile_name is not None:
            self.save_data(savefile_name, data)

    def save_data(self, fname, data):
        try:
            f = h5py.File(fname, 'w')

            rg = f.create_group('data')
            rg.attrs['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime())
            for k, v in data['attr'].items():
                rg.attrs[k] = v

            raw_x = np.stack([data['raw']['prof_x'][0], data['raw']['prof_x'][1]], 1)
            dset = f.create_dataset('data/raw/x', shape=raw_x.shape, dtype=raw_x.dtype)
            dset[...] = raw_x
            raw_y = np.stack([data['raw']['prof_y'][0], data['raw']['prof_y'][1]], 1)
            dset = f.create_dataset('data/raw/y', shape=raw_y.shape, dtype=raw_y.dtype)
            dset[...] = raw_y

            fit_x = np.stack([data['fit']['prof_x'][0], data['fit']['prof_x'][1]], 1)
            dset = f.create_dataset('data/fit/x', shape=fit_x.shape, dtype=fit_x.dtype)
            dset[...] = fit_x

            fit_y = np.stack([data['fit']['prof_y'][0], data['fit']['prof_y'][1]], 1)
            dset = f.create_dataset('data/fit/y', shape=fit_y.shape, dtype=fit_y.dtype)
            dset[...] = fit_y
            
            im_data = data['image']
            dset = f.create_dataset('data/image', shape=im_data.shape, dtype=im_data.dtype)
            dset[...] = im_data
            f.close()

            dial = wx.MessageDialog(
                self,
                message="Saved data into \n" + fname + ".",
                caption="Save Done",
                style=wx.OK | wx.CENTRE | wx.ICON_WARNING)
            if dial.ShowModal() == wx.ID_OK:
                self.Destroy()
        except:
            dial = wx.MessageDialog(
                self,
                message="Saving data into \n" + fname + " fails.",
                caption="Save Warning",
                style=wx.OK | wx.CENTRE | wx.ICON_WARNING)
            if dial.ShowModal() == wx.ID_OK:
                self.Destroy()

    def _get_image_data(self, datafile):
        """ read datafile (hdf5, txt, asc, jpg, etc.) into array
        """
        if datafile is None:
            return None
        else:
            ext = os.path.basename(datafile).split('.')[-1]
            if ext.upper() in ['HDF5', 'H5']:
                data = self._get_data_hdf5(datafile)
            elif ext.upper() in ['TXT', 'ASC', 'DAT']:
                data = self._get_data_txt(datafile)
            elif ext.upper() in ['JPG', 'PNG', 'BMP']:
                data = self._get_data_pic(datafile)
            return data, ext.upper()

    def _get_data_hdf5(self, fname):
        f = h5py.File(fname, 'r')
        data = f['image']['data'][...]
        return data
    
    def _get_data_txt(self, fname):
        data = np.loadtxt(fname)
        return data
    
    def _get_data_pic(self, fname):
        from scipy import misc
        f_rgb = misc.imread(fname)
        if len(f_rgb.shape) == 3:
            f_lum = f_rgb.sum(axis=2)/3.0
            return f_lum
        else:
            return f_rgb

        
class InspectApp(wx.App, wit.InspectionMixin):
    def OnInit(self):
        self.Init()
        frame = MainFrame(None)
        frame.SetTitle(u"wxmpv \u2014 wxMatPlotViewer (debug mode, CTRL+ALT+I)")
        frame.Show()
        frame.SetIcon(resutils.wicon_s.GetIcon())
        self.SetTopWindow(frame)
        return True

def run(logon=False, debug=False):
    """
    function to make app run.
    """
    if debug == True:
        app = InspectApp()
    else:
        app = wx.App(redirect=logon, filename = 'log')
        frame = MainFrame(None)
        frame.SetTitle(u"wxmpv \u2014 wxMatPlotViewer")
        frame.Show()
        frame.SetIcon(resutils.wicon_s.GetIcon())
    app.MainLoop()

if __name__ == '__main__':
    run()



