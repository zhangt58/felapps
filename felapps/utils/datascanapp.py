#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" New App for data correlation analysis

Tong Zhang
2016-07-12 10:11:05 AM CST
"""


import wx
import h5py
import time
import numpy as np

from .datascanframe import DataScanFrame
from .funutils import ScanDataFactor, getFileToSave


class MainFrame(DataScanFrame):
    def __init__(self, parent, appversion="0.1"):
        DataScanFrame.__init__(self, parent)

        self.appversion = appversion

        # events:
        self.Bind(wx.EVT_CLOSE, self.on_exit)

    def about_mitemOnMenuSelection(self, event):
        try:
            from wx.lib.wordwrap import wordwrap
        except:
            dial = wx.MessageDialog(self, message = u"Cannot show about information, sorry!",
                    caption = u"Unknow Error", 
                    style = wx.OK | wx.CANCEL | wx.ICON_ERROR | wx.CENTRE)
            if dial.ShowModal() == wx.ID_OK:
                dial.Destroy()
        info = wx.AboutDialogInfo()
        info.Name = "Correlation Analyzer"
        info.Version = self.appversion
        info.Copyright = "(C) 2016 Tong Zhang, SINAP, CAS"
        info.Description = wordwrap(
            "This application is created for correlation analysis of parameters.\n"

            "It is designed by Python language, using GUI module of wxPython.",
            350, wx.ClientDC(self))
        #info.WebSite = ("http://everyfame.me", "Cornalyzer home page")
        info.Developers = [ "Tong Zhang <zhangtong@sinap.ac.cn>"]
        licenseText = "Cornalyzer is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.\n" + "\nCornalyzer is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.\n" + "\nYou should have received a copy of the GNU General Public License along with Cornalyzer; if not, write to the Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA"
        info.License = wordwrap(licenseText, 500, wx.ClientDC(self))
        wx.AboutBox(info)

    def exit_mitemOnMenuSelection(self, event):
        self.exit_app()

    def on_exit(self, event):
        self.exit_app()

    def exit_app(self):
        dial = wx.MessageDialog(self, message = "Are you sure to exit this application?",
                                caption = 'Exit Warning',
                                style = wx.YES_NO | wx.NO_DEFAULT | wx.CENTRE | wx.ICON_QUESTION)
        if dial.ShowModal() == wx.ID_YES:
            self.Destroy()

    def close_btnOnButtonClick(self, event):
        self.exit_app()

    def save_mitemOnMenuSelection(self, event):
        """ 
        """
        save_full_path = getFileToSave(self, ext='hdf5')
        if save_full_path is not None:
            scandata_ins = ScanDataFactor(self.scan_output_all, self.scaniternum_val, self.shotnum_val)
            #idx = scandata_ins.getYavg()
            data_avgx = scandata_ins.getXavg()
            data_avgy = scandata_ins.getYavg()
            data_xerr = scandata_ins.getXerrbar()
            data_yerr = scandata_ins.getYerrbar()
            data_raw  = self.scan_output_all
            data_shape = scandata_ins.scanshape
            data_var1_name = self.var1_get_PV.pvname
            data_var2_name = self.var2_get_PV.pvname
            data_var2_method = self.var2_op_combox.GetStringSelection()

            fl = self.scanfig_panel.get_fit_line()
            data_fit = None
            if fl is not None:
                x, y = fl.get_data()
                x = x.reshape((x.size, 1))
                y = y.reshape((y.size, 1))
                data_fit = np.hstack((x,y))
            
            # save
            f = h5py.File(save_full_path, 'w')
            rg = f.create_group('data')
            rg.attrs['timestamp'] = self.stop_timestamp #time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime())
            rg.attrs['file info'] = 'scan data output'
            rg.attrs['app'] = 'cornalyzer'
            rg.attrs['scan variable'] = data_var1_name
            rg.attrs['scan dependent variable'] = data_var2_name
            rg.attrs['operation on dependent variable'] = data_var2_method
            rg.attrs['raw data shape'] = data_shape

            # fitting data
            if data_fit is not None:
                rg.attrs['fit info'] = self.scanfig_panel.get_fit_model().fit_report() 
                rg.attrs['fit data shape'] = data_fit.shape

            dset_list = [data_avgx, data_avgy, data_xerr, data_yerr, data_raw, data_fit]
            dset_name = ['x_avg', 'y_avg', 'x_errb', 'y_errb', 'raw', 'fit']
            for (data, dsetname) in zip(dset_list, dset_name):
                if data is None: continue
                dset = f.create_dataset('data/' + dsetname, 
                        shape=data.shape, dtype=data.dtype)
                dset[...] = data
            f.close()
            
            dial = wx.MessageDialog(self, message = "Saved Data into" + save_full_path + ".",
                                    caption = 'Save Message',
                                    style = wx.OK | wx.CENTRE | wx.ICON_QUESTION)
            if dial.ShowModal() == wx.ID_OK:
                dial.Destroy()
