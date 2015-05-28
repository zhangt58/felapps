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

__version__ = miscutils.AppVersions().getVersion('felformula')

def run(maximize = True, logon = False):
    """
    function to call felformula GUI
    """
    app = wx.App(redirect = logon, filename = 'log')
    if maximize == True:
        myframe = felcalc.MainFrame(None, title = u'FEL Formula \u2014 FEL Calculation App', appversion = __version__, style = wx.DEFAULT_FRAME_STYLE)
    else:
        myframe = felcalc.MainFrame(None, title = u'FEL Formula \u2014 FEL Calculation App', appversion = __version__, style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
    myframe.Show()
    app.MainLoop()

if __name__ == '__main__':
    run()



