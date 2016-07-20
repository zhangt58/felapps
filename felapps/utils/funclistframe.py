#!/usr/bin/env python
# -*- coding: utf-8 -*-


import wx
from . import datascanframe_ui as dsfui
from .funutils import getFileToLoad

import imp
import os
from inspect import getmembers, isfunction

class FuncListFrame(dsfui.FuncListFrame):
    def __init__(self, parent, fullpath='.'):
        dsfui.FuncListFrame.__init__(self, parent)
        self.parent = parent

        self.path_tc.SetValue(os.path.abspath(fullpath))
        self._init_udefs_lc()
        self._init_items()
        
        self.select_idx = None

    def _init_items(self):
        full_path = os.path.expanduser(self.path_tc.GetValue())
        if not os.path.isfile(full_path):
            self.full_path = None
            return
        else:
            self.full_path = full_path
            self.parent.func_path = full_path
            self._load_items(full_path)

    def _init_udefs_lc(self):
        """ initialize udefs_lc
        """
        self.udefs_lc.InsertColumn(0, "ID",   wx.LIST_FORMAT_LEFT)
        self.udefs_lc.InsertColumn(1, "Name", wx.LIST_FORMAT_LEFT)
        self.udefs_lc.InsertColumn(2, "Note", wx.LIST_FORMAT_LEFT)
        self.udefs_lc.SetColumnWidth(0,  50)
        self.udefs_lc.SetColumnWidth(1, 150)
        self.udefs_lc.SetColumnWidth(2, 300)

    def _load_items(self, fullpath):
        """ load fullpath file and fill up udefs_lc
        """
        mm = imp.load_source('myfunc', fullpath)
        func_list = getmembers(mm, isfunction)
        lc = self.udefs_lc
        lc.DeleteAllItems()
        for i, ft in enumerate(func_list):
            f = ft[1]
            fn, fd = f.func_name.strip(), f.func_doc
            fd = fd.strip() if fd is not None else ''
            idx = lc.InsertStringItem(65536, str(i))
            lc.SetStringItem(idx, 1, fn)
            lc.SetStringItem(idx, 2, fd)
        self.func_list = func_list

    def udefs_lcOnListItemSelected(self, event):
        self.select_idx = event.Index
    
    def reload_btnOnButtonClick(self, event):
        self._load_items(self.full_path)

    def cancel_btnOnButtonClick(self, event):
        self.Close()

    def ok_btnOnButtonClick(self, event):
        if self.select_idx is not None:
            self.parent.var2_op_func = self.func_list[self.select_idx][1]
        self.Close()

    def path_btnOnButtonClick(self, event):
        full_path = getFileToLoad(self, ext=['py','*'])
        if full_path is not None:
            self.path_tc.SetValue(full_path)
            self.full_path = full_path
            self.parent.func_path = full_path
            self._load_items(full_path)
