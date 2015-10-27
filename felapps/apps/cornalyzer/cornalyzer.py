#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
cornalyzer: correlation analyzer, study the relation between parameters

Author: Tong Zhang
Created: May. 27, 2015
"""

from ...utils import scanutils
from ...utils import miscutils
import wx
import wx.lib.mixins.inspection as wit

__version__ =  miscutils.AppVersions().getVersion('cornalyzer')
__author__  = "Tong Zhang"

class InspectApp(wx.App, wit.InspectionMixin):
    def OnInit(self):
        self.Init()
        myframe = scanutils.ScanAnalyzer(None, title = u'Cornalyzer \u2014 Another Correlation Analyzer', appversion = __version__, style = wx.DEFAULT_FRAME_STYLE)
        myframe.Show()
        self.SetTopWindow(myframe)
        return True

def run(maximize = True, logon = False, debug = True):
    """
    function to call cornalyzer
    """
    if debug == True:
        app = InspectApp()
        app.MainLoop()
    else:
        app = wx.App(redirect = logon, filename = 'log')
        if maximize == True:
            myframe = scanutils.ScanAnalyzer(None, title = u'Cornalyzer \u2014 Another Correlation Analyzer', appversion = __version__, style = wx.DEFAULT_FRAME_STYLE)
        else:
            myframe = scanutils.ScanAnalyzer(None, title = u'Cornalyzer \u2014 Another Correlation Analyzer', appversion = __version__, style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        myframe.Show()
        app.MainLoop()

if __name__ == '__main__':
    run()
