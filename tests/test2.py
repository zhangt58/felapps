#!/usr/bin/env python

import wx
from wx.lib.agw import floatspin as fs
import numpy as np

class MyFrame(wx.Frame):
    def __init__(self, *args, **kws):
        super(self.__class__,self).__init__(*args, **kws)
        
        nb1 = MyNB(self)

        self.Show()

class MyFrame1(wx.Frame):
    def __init__(self, *args, **kws):
        super(self.__class__,self).__init__(*args, **kws)

        self.curvalue = 2.3 
        self.minValue = 0.2
        self.maxValue = 9.1
        self.incValue = 0.1
        self.facValue = 10

        self.slider_min = self.minValue*self.facValue
        self.slider_max = self.maxValue*self.facValue
        self.slider_cur = self.curvalue*self.facValue

        self.slider_num = int((self.slider_max - self.slider_min)/(self.incValue*self.facValue) + 1)

        self.sliderTicRange = np.linspace(self.slider_min, self.slider_max, self.slider_num)
        self.sliderValRange = np.linspace(self.minValue, self.maxValue, self.slider_num) 

        self.iniUI1()
        #self.iniUI()
        self.Show()
    
    def iniUI1(self):
        self.panel = wx.Panel(self)
        self.slider = FloatSlider(self.panel, value = 1.0, minValue = 1, maxValue = 100)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.slider, proportion = 0, flag = wx.EXPAND)
        self.panel.SetSizer(vbox)

        self.Bind(wx.EVT_SLIDER, self.onSlider, self.slider)

    def onSlider(self, event):
        obj = event.GetEventObject()
        print obj.GetValue()

    def iniUI(self):

        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour((170, 238, 170))

        self._slider = wx.Slider(self.panel, value = self.slider_cur, 
                minValue = self.slider_min, maxValue = self.slider_max, 
                style = wx.SL_HORIZONTAL)
        self._min_label = wx.StaticText(self.panel, label = str(self.minValue))
        self._max_label = wx.StaticText(self.panel, label = str(self.maxValue))
        self._val_label = wx.StaticText(self.panel, label = str(self.curvalue))

        self.hbox_top  = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_top.Add(self._val_label, proportion = 0, flag = wx.ALIGN_CENTER)

        self.hbox_down = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_down.Add(self._min_label, proportion = 0, flag = wx.EXPAND | wx.ALIGN_CENTRE)
        self.hbox_down.Add(self._slider,    proportion = 2, flag = wx.EXPAND | wx.ALIGN_CENTRE | wx.LEFT | wx.RIGHT, border = 10)
        self.hbox_down.Add(self._max_label, proportion = 0, flag = wx.EXPAND | wx.ALIGN_CENTRE)

        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self.vbox.Add(self.hbox_top,  proportion = 0, flag = wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, border = 10)
        self.vbox.Add(self.hbox_down, proportion = 0, flag = wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, border = 10)
        
        self.panel.SetSizer(self.vbox)

        self.Bind(wx.EVT_SLIDER, self.onFSlider, self._slider)

    def onFSlider(self, event):
        obj = event.GetEventObject()
        ticValue = obj.GetValue() - obj.GetMin()
        curVal = self.sliderValRange[ticValue]
        print ticValue, curVal
        self._val_label.SetLabel(str(curVal))

class MyNB(wx.Notebook):
    def __init__(self, parent, *args, **kws):
        super(self.__class__, self).__init__(parent=parent, style = wx.NB_TOP, *args, **kws)

        # panel #1
        self.panel1 = MyPanel(self)
        self.panel1.SetBackgroundColour(wx.Colour(0, 0, 255))

        self.spinctrl = fs.FloatSpin(self.panel1, value = '0.1', min_val = 0.1, max_val = 0.9, digits = 2, increment = 0.01)#, agwStyle = fs.FS_READONLY)
        # panel #2
        self.panel2 = MyPanel(self)
        self.panel2.SetBackgroundColour(wx.Colour(0, 255, 255))
        self.btn2 = wx.Button(self.panel2, label = 'choose color')

        # panel #3
        self.panel3 = MyPanel(self)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        
        p1 = FloatSlider(self.panel3, value = 1.0, minValue = 0.1, maxValue = 9.1)
        print p1.GetSize()
        #p1 = wx.Panel(self.panel3)
        #p1 = wx.Button(self.panel3, label = 'btn1')
        #p1.SetBackgroundColour('red')

        p2 = wx.Panel(self.panel3)
        #p2 = wx.Button(self.panel3, label = 'btn2')
        p2.SetBackgroundColour('blue')

        p3 = wx.Panel(self.panel3)
        #p3 = wx.Button(self.panel3, label = 'btn3')
        p3.SetBackgroundColour('yellow')

        p4 = wx.Panel(self.panel3)
        #p4 = wx.Button(self.panel3, label = 'btn4')
        p4.SetBackgroundColour('green')

        hbox1.Add(p1, proportion = 1, flag = wx.EXPAND)
        hbox1.Add(p2, proportion = 1, flag = wx.EXPAND)

        hbox2.Add(p3, proportion = 1, flag = wx.EXPAND)
        hbox2.Add(p4, proportion = 1, flag = wx.EXPAND)
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox1, proportion = 1, flag = wx.EXPAND)
        vbox.Add(hbox2, proportion = 1, flag = wx.EXPAND)

        self.panel3.SetSizer(vbox)


        # #1 Tab
        self.AddPage(self.panel1, 'First Tab')
        # #2 Tab
        self.AddPage(self.panel2, 'Second Tab')
        # #3 Tab
        self.AddPage(self.panel3, 'Third Tab')

        # events
        self.Bind(wx.EVT_BUTTON, self.onChooseColor, self.btn2)

    def onChooseColor(self, event):
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            color = dlg.GetColourData().GetColour()
            self.panel2.SetBackgroundColour(color)
            print color.GetAsString(wx.C2S_HTML_SYNTAX)
        dlg.Destroy()

class MyFrame2(wx.Frame):
    def __init__(self, *args, **kws):
        super(self.__class__,self).__init__(*args, **kws)
        slide = FloatSlider(self,0.2,0.1,1.0,0.01)
        self.Show()

class MyPanel(wx.Panel):
    def __init__(self, parent, *args, **kws):
        super(self.__class__, self).__init__(parent=parent, *args, **kws)

"""
class FloatSlider(wx.Slider):
    #def __init__(self, parent, *args, **kws):
    #    super(self.__class__, self).__init__(parent, *args, **kws)
    
    def GetValue(self):
        return float(wx.Slider.GetValue(self))/self.GetMax()
"""

class FloatSlider(wx.Slider):

    def __init__(self, parent, id = wx.ID_ANY, value = 0, minvValue = 0, maxValue = 10, increment = 0.1, 
                 size = wx.DefaultSize, style = wx.SL_HORIZONTAL, *args, **kws):
        self._value = value
        self._min = minValue
        self._max = maxValue
        self._inc = increment
        ival, imin, imax = [round(v/res) for v in (value, minValue, maxValue)]
        self._islider = super(FloatSlider, self)
        self._islider.__init__(parent = parent, value = ival, minValue = imin, maxValue = imax, id = id, size = size, style = style, *args, **kws)
        self.Bind(wx.EVT_SCROLL, self._OnScroll, self._islider)

    def _OnScroll(self, event):
        ival = self._islider.GetValue()
        imin = self._islider.GetMin()
        imax = self._islider.GetMax()
        if ival == imin:
            self._value = self._min
        elif ival == imax:
            self._value = self._max
        else:
            self._value = ival * self._inc
        event.Skip()
        print 'OnScroll: value=%f, ival=%d' % (self._value, ival)

    def GetValue(self):
        return self._value

    def GetMin(self):
        return self._min

    def GetMax(self):
        return self._max

    def GetInc(self):
        return self._inc

    def SetValue(self, value):
        self._islider.SetValue(round(value/self._res))
        self._value = value

    def SetMin(self, minval):
        self._islider.SetMin(round(minval/self._res))
        self._min = minval

    def SetMax(self, maxval):
        self._islider.SetMax(round(maxval/self._res))
        self._max = maxval

    def SetInc(self, inc):
        self._islider.SetRange(round(self._min/inc), round(self._max/inc))
        self._islider.SetValue(round(self._value/inc))
        self._inc = inc

    def SetRange(self, minval, maxval):
        self._islider.SetRange(round(minval/self._res), round(maxval/self._res))
        self._min = minval
        self._max = maxval

def main():
    app = wx.App()
    #myframe = MyFrame(None)
    #myframe = MyFrame1(None)
    myframe = MyFrame2(None)
    app.MainLoop()

if __name__ == '__main__':
    main()

