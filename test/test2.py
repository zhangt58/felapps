#!/usr/bin/env python

import wx

class MyFrame(wx.Frame):
    def __init__(self, *args, **kws):
        super(self.__class__,self).__init__(*args, **kws)
        
        nb1 = MyNB(self)

        self.Show()

class MyNB(wx.Notebook):
    def __init__(self, parent, *args, **kws):
        super(self.__class__, self).__init__(parent=parent, style = wx.NB_LEFT, *args, **kws)

        # panel #1
        self.panel1 = MyPanel(self)
        self.panel1.SetBackgroundColour(wx.Colour(0, 0, 255))
        self.btn1 = wx.Button(self.panel1, label = 'choose color')

        # panel #2
        self.panel2 = MyPanel(self)
        self.panel2.SetBackgroundColour(wx.Colour(0, 255, 255))
        self.btn2 = wx.Button(self.panel2, label = 'Hello')

        # #1 Tab
        self.AddPage(self.panel1, 'First Tab')
        # #2 Tab
        self.AddPage(self.panel2, 'Second Tab')

        # events
        self.Bind(wx.EVT_BUTTON, self.onChooseColor, self.btn1)

    def onChooseColor(self, event):
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            color = dlg.GetColourData().GetColour()
            self.panel1.SetBackgroundColour(color)
            print color.GetAsString(wx.C2S_HTML_SYNTAX)
        dlg.Destroy()


 

class MyPanel(wx.Panel):
    def __init__(self, parent, *args, **kws):
        super(self.__class__, self).__init__(parent=parent, *args, **kws)

def main():
    app = wx.App()
    myframe = MyFrame(None)
    app.MainLoop()

main()

