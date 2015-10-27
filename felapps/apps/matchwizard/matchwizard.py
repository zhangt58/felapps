#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MatchWizard: application to do lattice matching

Author: Tong Zhang
Created: Sep. 23rd, 2015
"""

from ...utils import matchutils
from ...utils import miscutils
from ...utils import funutils
import wx
import wx.lib.mixins.inspection as wit
import os

__version__ =  miscutils.AppVersions().getVersion('matchwizard')
__author__  = "Tong Zhang"

class InspectApp(wx.App, wit.InspectionMixin):
    def OnInit(self):
        self.Init()

        configFile = os.path.expanduser("~/.felapps/config/imageviewer.xml")
        if not os.path.isfile(configFile):
            configFile = funutils.getFileToLoad(None, ext = 'xml')

        myframe = matchutils.MatchWizard(None, config = configFile, title = u'MatchWizard \u2014 (debug mode, CTRL+ALT+I)', appversion = __version__, style = wx.DEFAULT_FRAME_STYLE)
        myframe.Show()
        self.SetTopWindow(myframe)
        return True

def run(maximize = True, logon = False, debug=True):
    """
    function to make matchwizard app run.
    """
    if debug == True:
        app = InspectApp()
        app.MainLoop()
    else:
        app = wx.App(redirect = logon, filename='log')

        configFile = os.path.expanduser("~/.felapps/config/imageviewer.xml")
        if not os.path.isfile(configFile):
            configFile = funutils.getFileToLoad(None, ext = 'xml')

        if maximize == True:
            myframe = matchutils.MatchWizard(None, config = configFile, title = u'MatchWizard \u2014', appversion = __version__, style = wx.DEFAULT_FRAME_STYLE)
        else:
            myframe = matchutils.MatchWizard(None, config = configFile, title = u'MatchWizard \u2014', appversion = __version__, style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        myframe.Show()
        app.MainLoop()

if __name__ == '__main__':
    run()
