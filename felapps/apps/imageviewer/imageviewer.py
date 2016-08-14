#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ImageViewer: universal application for image viewing and data post-processing.

Author: Tong Zhang
Created: Feb. 3rd, 2015
"""

from ...utils import pltutils
from ...utils import miscutils
from ...utils import funutils
from ...utils import resutils
import wx
import wx.lib.mixins.inspection as wit
import os

__version__ =  miscutils.AppVersions().getVersion('imageviewer')
__author__  = "Tong Zhang"

class InspectApp(wx.App, wit.InspectionMixin):
    def OnInit(self):
        self.Init()
        configFile = funutils.handleConfig(config_name = 'imageviewer.xml')
        myframe = pltutils.ImageViewer(None, config = configFile, title = u"ImageViewer" + ' ' + "Another Profile Monitor (debug mode, CTRL+ALT+I)", appversion = __version__, style = wx.DEFAULT_FRAME_STYLE)
        myframe.Show()
        myframe.SetIcon(resutils.iicon_s.GetIcon())
        self.SetTopWindow(myframe)
        return True

def run(maximize=True, logon=False, debug=False):
    """
    function to make imageviewer app run.
    """
    if debug == True:
        app = InspectApp()
        app.MainLoop()
    else:
        app = wx.App(redirect=logon, filename = 'log')

        configFile = funutils.handleConfig(config_name = 'imageviewer.xml')
        if maximize == True:
            myframe = pltutils.ImageViewer(None, config = configFile, title = u'ImageViewer \u2014 Another Profile Monitor', appversion = __version__, style = wx.DEFAULT_FRAME_STYLE)
        else:
            myframe = pltutils.ImageViewer(None, config = configFile, title = u'ImageViewer \u2014 Another Profile Monitor', appversion = __version__, style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        myframe.Show()
        myframe.SetIcon(resutils.iicon_s.GetIcon())
        app.MainLoop()

if __name__ == '__main__':
    run()
