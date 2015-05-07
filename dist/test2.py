#!/usr/bin/env python

import wx

class MyFrame(wx.Frame):
    def __init__(self, *args, **kws):
        super(self.__class__,self).__init__(*args, **kws)

        self.panel = wx.Panel(self)
        btn = wx.Button(self.panel, label = 'choose color') 
        self.Bind(wx.EVT_BUTTON, self.onChooseColor, btn)
        self.Show()

    def onChooseColor(self, event):
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            color = dlg.GetColourData().GetColour()
            self.panel.SetBackgroundColour(color)
            print color.GetAsString(wx.C2S_HTML_SYNTAX)
            
        dlg.Destroy()

def main():
    app = wx.App()
    myframe = MyFrame(None)
    app.MainLoop()

main()

