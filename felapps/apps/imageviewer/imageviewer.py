#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ImageViewer: universal application for image viewing and data post-processing.

Author: Tong Zhang
Created: Feb. 3rd, 2015
"""

from ...utils import pltutils
from ...utils import miscutils
import wx

__version__ =  miscutils.AppVersions().getVersion('imageviewer')

def run(maximize = True, logon = False):
    """
    function to make imageviewer app run.
    """
    app = wx.App(redirect = logon, filename='log')
    if maximize == True:
        myframe = pltutils.ImageViewer(None, title = u'ImageViewer \u2014 Another Profile Monitor', appversion = __version__, style = wx.DEFAULT_FRAME_STYLE)
    else:
        myframe = pltutils.ImageViewer(None, title = u'ImageViewer \u2014 Another Profile Monitor', appversion = __version__, style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
    myframe.Show()
    #print myframe.GetSize()
    app.MainLoop()

if __name__ == '__main__':
    run()
