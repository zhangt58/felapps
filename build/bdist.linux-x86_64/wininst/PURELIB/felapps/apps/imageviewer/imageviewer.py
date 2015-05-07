#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ImageViewer: universal application for image viewing and data post-processing.

Author: Tong Zhang
Created: Feb. 3rd, 2015
"""

from ...utils import pltutils
import wx

def run():
    """
    function to make imageviewer app run.
    """
    app = wx.App(redirect = True, filename='log')
    myframe = pltutils.ImageViewer(None, title = 'ImageViewer --- Another Profile Monitor', 
            style = wx.DEFAULT_FRAME_STYLE)
            #style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
    myframe.Show()
    app.MainLoop()

if __name__ == '__main__':
    run()
