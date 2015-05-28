#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
cornalyzer: correlation analyzer, study the relation between parameters

Author: Tong Zhang
Created: May. 27, 2015
"""

from ...utils import felutils
from ...utils import miscutils
import wx

__version__ =  miscutils.AppVersions().getVersion('cornalyzer')

def run(maximize = True, logon = False):
    """
    function to call cornalyzer
    """
    app = wx.App(redirect = logon, filename = 'log')
    if maximize == True:
        myframe = felutils.ScanAnalyzer(None, title = u'Cornalyzer \u2014 Another correlation analyzer', appversion = __version__, style = wx.DEFAULT_FRAME_STYLE)
    else:
        myframe = felutils.ScanAnalyzer(None, title = u'Cornalyzer \u2014 Another correlation analyzer', appversion = __version__, style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
    myframe.Show()
    app.MainLoop()

if __name__ == '__main__':
    run()


