#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
cornalyzer: correlation analyzer, study the relation between parameters

Author: Tong Zhang
Created: May. 27, 2015
"""

from ...utils import datascanapp
from ...utils import miscutils
from ...utils import resutils
import wx
import wx.lib.mixins.inspection as wit

__version__ =  miscutils.AppVersions().getVersion('cornalyzer')
__author__  = "Tong Zhang"

class InspectApp(wx.App, wit.InspectionMixin):
    def OnInit(self):
        self.Init()
        myframe = datascanapp.MainFrame(None, __version__)
        myframe.SetTitle(u'Cornalyzer \u2014 Data Correlation Analyzer (debug mode, CTRL+ALT+I)')
        #appversion = __version__, style = wx.DEFAULT_FRAME_STYLE)
        myframe.Show()
        myframe.SetMinSize((1024, 768))
        myframe.SetIcon(resutils.cicon_s.GetIcon())
        self.SetTopWindow(myframe)
        return True

def run(maximize=True, logon=False, debug=True):
    """
    function to call cornalyzer
    """
    if debug == True:
        app = InspectApp()
        app.MainLoop()
    else:
        app = wx.App(redirect=logon, filename='log')
        if maximize == True:
            myframe = datascanapp.MainFrame(None, __version__)
            myframe.SetTitle(u'Cornalyzer \u2014 Data Correlation Analyzer')
            #, appversion = __version__, style = wx.DEFAULT_FRAME_STYLE)
        else:
            myframe = datascanapp.MainFrame(None, __version__)
            myframe.SetTitle(u'Cornalyzer \u2014 Data Correlation Analyzer')
            #, appversion = __version__, style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        myframe.Show()
        myframe.SetMinSize((1024, 768))
        myframe.SetIcon(resutils.cicon_s.GetIcon())
        app.MainLoop()

if __name__ == '__main__':
    run()
