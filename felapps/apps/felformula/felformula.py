#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FelFormula: calculation cheat sheet for free-electron laser physics

Author: Tong Zhang
Created: May. 28, 2015 (re-organized)
"""

from ...physics import felcalc
from ...utils   import miscutils
import wx
import wx.lib.mixins.inspection as wit

__version__ = miscutils.AppVersions().getVersion('felformula')
__author__  = "Tong Zhang"

class InspectApp(wx.App, wit.InspectionMixin):
    def OnInit(self):
        self.Init()
        myframe = felcalc.MainFrame(None, title = u'FEL Formula \u2014 Calculator for FEL physics (debug mode, CTRL+ALT+I)', appversion = __version__, style = wx.DEFAULT_FRAME_STYLE)
        myframe.Show()
        self.SetTopWindow(myframe)
        return True

def run(maximize = True, logon = False, debug = False):
    """
    function to call felformula GUI
    """
    if debug == True:
        app = InspectApp()
        app.MainLoop()
    else:
        app = wx.App(redirect = logon, filename = 'log')
        if maximize == True:
            myframe = felcalc.MainFrame(None, title = u'FEL Formula \u2014 Calculator for FEL physics', appversion = __version__, style = wx.DEFAULT_FRAME_STYLE)
        else:
            myframe = felcalc.MainFrame(None, title = u'FEL Formula \u2014 FEL Calculation App', appversion = __version__, style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        myframe.Show()
        app.MainLoop()

if __name__ == '__main__':
    run()



