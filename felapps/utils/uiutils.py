#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
custom GUI controls

Tong Zhang
2016-06-19 12:37:40 PM CST
"""

import wx
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as Toolbar
from matplotlib.figure import Figure
import numpy as np
from bisect import bisect

import wx.gizmos as gizmos

class MyPlotPanel(wx.Panel):
    def __init__(self, parent, figsize=None, dpi=None,
                 bgcolor=None, type=None, toolbar=None, aspect='auto',
                 **kwargs):
        """ construction method of MyPlotPanel class
        :param parent: parent object
        :param figsize: plot figure size, (w, h)
        :param dpi: figure dpi,
        :parma bgcolor: background color of figure and canvas
        :param type: type of initial figure, 'image' or 'line'
        :param toolbar: show toolbar if not set None
        :param aspect: axes aspect, float number or 'auto' by default
        """
        wx.Panel.__init__(self, parent, **kwargs)
        self.parent = parent
        self.figsize = figsize
        self.dpi = dpi
        self.bgcolor = bgcolor
        self.type = type
        self.toolbar = toolbar
        self.aspect = aspect
        self.figure = Figure(self.figsize, self.dpi)
        self.canvas = FigureCanvas(self, -1, self.figure)

        # figure background color
        self.set_color(self.bgcolor)

        # initialize plot
        self._init_plot()

        # set layout
        self.set_layout()

        # post-initialization
        self._post_init()

        # binding events
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas.mpl_connect('pick_event', self.on_pick)
        self.Bind(wx.EVT_SIZE, self.on_size)

        self.xylim_choice.Bind(wx.EVT_CHOICE,  self.xylim_choiceOnChoice)
        self.minlim_tc.Bind(wx.EVT_TEXT_ENTER, self.minlim_tcOnTextEnter)
        self.maxlim_tc.Bind(wx.EVT_TEXT_ENTER, self.maxlim_tcOnTextEnter)

    def set_layout(self):
        """ set panel layout
        """
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # set toolbar if defined
        if self.toolbar is not None:
            self.toobar = MyToolbar(self.canvas)
            self.toobar.Realize()
            hbox.Add(self.toobar, 0, wx.EXPAND | wx.RIGHT, 5)

        # add x[y]lim control
        xylim_hbox = wx.BoxSizer( wx.HORIZONTAL )

        xy_vbox = wx.BoxSizer( wx.VERTICAL )

        xylim_choiceChoices = [ u"X-Limit", u"Y-Limit", u"Auto" ]
        self.xylim_choice = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, xylim_choiceChoices, 0 )
        self.xylim_choice.SetSelection( 0 )
        xy_vbox.Add( self.xylim_choice, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 3 )

        xylim_hbox.Add( xy_vbox, 0, wx.ALIGN_CENTER_VERTICAL, 1 )

        lim_vbox = wx.BoxSizer( wx.VERTICAL )

        min_hbox = wx.BoxSizer( wx.HORIZONTAL )

        self.minlim_st = wx.StaticText( self, wx.ID_ANY, u"Min", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.minlim_st.Wrap( -1 )
        self.minlim_st.SetFont( wx.Font( 6, 70, 90, 90, False, "Monospace" ) )

        min_hbox.Add( self.minlim_st, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 1 )

        self.minlim_tc = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
        self.minlim_tc.SetFont( wx.Font( 6, 70, 90, 90, False, "Monospace" ) )
        self.minlim_tc.SetToolTipString( u"Min of Limit" )

        min_hbox.Add( self.minlim_tc, 0, wx.ALIGN_CENTER_VERTICAL|wx.TOP, 1 )

        lim_vbox.Add( min_hbox, 1, wx.EXPAND, 1 )

        max_hbox = wx.BoxSizer( wx.HORIZONTAL )

        self.maxlim_st = wx.StaticText( self, wx.ID_ANY, u"Max", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.maxlim_st.Wrap( -1 )
        self.maxlim_st.SetFont( wx.Font( 6, 70, 90, 90, False, "Monospace" ) )

        max_hbox.Add( self.maxlim_st, 0, wx.ALIGN_CENTER_VERTICAL|wx.BOTTOM|wx.RIGHT|wx.TOP, 1 )

        self.maxlim_tc = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
        self.maxlim_tc.SetFont( wx.Font( 6, 70, 90, 90, False, "Monospace" ) )
        self.maxlim_tc.SetToolTipString( u"Max of Limit" )

        max_hbox.Add( self.maxlim_tc, 0, wx.ALIGN_CENTER_VERTICAL|wx.BOTTOM|wx.TOP, 1 )
        lim_vbox.Add( max_hbox, 1, wx.EXPAND, 1 )
        xylim_hbox.Add( lim_vbox, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 1 )

        hbox.Add(xylim_hbox, 0, wx.EXPAND | wx.RIGHT, 5)

        # (x, y) pos label
        self.pos_st = wx.StaticText(self, label='')
        hbox.Add(self.pos_st, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(hbox, 0, wx.EXPAND | wx.BOTTOM, 0)
        self.SetSizerAndFit(sizer)

    def _init_plot(self):
        if not hasattr(self, 'axes'):
            self.axes = self.figure.add_subplot(111, aspect=self.aspect)
        if self.type == 'image':  # draw image
            x = y = np.linspace(-np.pi, np.pi, 100)
            self.x, self.y = np.meshgrid(x, y)
            self.z = self._func_peaks(self.x, self.y)
            self.image = self.axes.imshow(self.z)
        else: # draw line
            self.x = np.linspace(-10, 10, 200)
            self.y = np.sin(self.x)
            self.line, = self.axes.plot(self.x, self.y)

    def _post_init(self):
        self._set_xylim_flag(self.xylim_choice.GetStringSelection())

    def set_color(self, rgb_tuple):
        """ set figure and canvas with the same color.
        :param rgb_tuple: rgb color tuple,
                          e.g. (255, 255, 255) for white color
        """
        if rgb_tuple is None:
            #rgb_tuple = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE).Get()
            rgb_tuple = wx.SystemSettings.GetColour(wx.SYS_COLOUR_DESKTOP).Get()
        clr = [c/255.0 for c in rgb_tuple]
        self.figure.set_facecolor(clr)
        self.figure.set_edgecolor(clr)
        self.canvas.SetBackgroundColour(wx.Colour(*rgb_tuple))

    def on_size(self, event):
        self.fit_canvas()
        self.canvas.draw_idle()
        event.Skip()

    def on_press(self, event):
        pass

    def on_release(self, event):
        pass

    def on_pick(self, event):
        pass

    def on_motion(self, event):
        if event.inaxes is not None:
            self.pos_st.SetLabel("({x:<.4f}, {y:<.4f})".format(x=event.xdata, y=event.ydata))

    def fit_canvas(self):
        """ tight fit canvas layout
        """
        #self.canvas.SetSize(self.GetSize())
        self.figure.set_tight_layout(True)

    def _func_peaks(self, x, y):
        return 3.0 * (1.0 - x)**2.0 * np.exp(-(x**2) - (y+1)**2) \
             - 10*(x/5 - x**3 - y**5) * np.exp(-x**2-y**2) \
             - 1.0/3.0*np.exp(-(x+1)**2 - y**2)

    def refresh(self):
        self.canvas.draw_idle()

    def xylim_choiceOnChoice(self, event):
        sel_str = self.xylim_choice.GetStringSelection()
        self._set_xylim_flag(sel_str)
        if sel_str == 'Auto':
            self.minlim_tc.Disable()
            self.maxlim_tc.Disable()
            self.minlim_st.Disable()
            self.maxlim_st.Disable()

            # auto set xy limit
            min_list = [np.vstack(line.get_data()).min(axis=1).tolist() 
                            for line in self.axes.get_lines()]
            max_list = [np.vstack(line.get_data()).max(axis=1).tolist()
                            for line in self.axes.get_lines()]
            xmin, ymin = np.array(min_list).min(axis=0)
            xmax, ymax = np.array(max_list).max(axis=0)
            x0, xhw = (xmin + xmax) * 0.5, (xmax - xmin) * 0.5
            y0, yhw = (ymin + ymax) * 0.5, (ymax - ymin) * 0.5
            _xmin, _xmax = x0 - xhw * 1.1, x0 + xhw * 1.1
            _ymin, _ymax = y0 - yhw * 1.1, y0 + yhw * 1.1
            self.axes.set_xlim([_xmin, _xmax])
            self.axes.set_ylim([_ymin, _ymax])

            self.refresh()
        else:
            self.minlim_tc.Enable()
            self.maxlim_tc.Enable()
            self.minlim_st.Enable()
            self.maxlim_st.Enable()

            try:
                _xlim = self.axes.get_xlim()
                _ylim = self.axes.get_ylim()
            except:
                _xlim = [0, 100]
                _ylim = [0, 100]
            self._set_default_minlim(_xlim, _ylim)
            self._set_default_maxlim(_xlim, _ylim)
        
    
    def _set_default_minlim(self, xlim_array, ylim_array):
        if self._xylim == 'X-Limit':
            self.minlim_tc.SetValue("{xmin:.3g}".format(xmin=xlim_array[0]))
        elif self._xylim == 'Y-Limit':
            self.minlim_tc.SetValue("{ymin:.3g}".format(ymin=ylim_array[0]))

    def _set_default_maxlim(self, xlim_array, ylim_array):
        if self._xylim == 'X-Limit':
            self.maxlim_tc.SetValue("{xmax:.3g}".format(xmax=xlim_array[1]))
        elif self._xylim == 'Y-Limit':
            self.maxlim_tc.SetValue("{ymax:.3g}".format(ymax=ylim_array[1]))

    def minlim_tcOnTextEnter(self, event):
        xymin = float(self.minlim_tc.GetValue())
        xymax = float(self.maxlim_tc.GetValue())
        self._set_xylim_range(xymin, xymax)

    def maxlim_tcOnTextEnter(self, event):
        xymin = float(self.minlim_tc.GetValue())
        xymax = float(self.maxlim_tc.GetValue())
        self._set_xylim_range(xymin, xymax)

    def _set_xylim_flag(self, flag='X-Limit'):
        """ control x/y limit to be set
            :param flag: 'X-Limit' or 'Y-Limit'
        """
        self._xylim = flag

    def _set_xylim_range(self, vmin, vmax):
        """ set x/y limit according to _xylim value
            :param vmin: min of limit
            :param vmax: max of limit
        """
        if self._xylim == 'X-Limit':
            self.axes.set_xlim([vmin, vmax])
        elif self._xylim == 'Y-Limit':
            self.axes.set_ylim([vmin, vmax])
        self.refresh()
            

class MyToolbar(Toolbar):
    def __init__(self, canvas):
        Toolbar.__init__(self, canvas)

        #self.AddTool(wx.ID_ANY, '')

class LatticePlotPanel(MyPlotPanel):
    def __init__(self, parent, **kwargs):
        MyPlotPanel.__init__(self, parent, **kwargs)

        #self.canvas.mpl_connect('pick_event', self.on_pick)

    #def on_pick(self, event):
    #    print event.mouseevent.xdata, event.mouseevent.ydata
    #    obj = event.artist
    #    if hasattr(self, 'anote_list'):
    #        for i in self.anote_list:

    def on_motion(self, event):
        if event.inaxes is not None:
            name, type = self.identify_obj(event.xdata)
            if name is not None:
                self.pos_st.SetLabel("({x:<.4f}, {y:<.4f}) --- [{name} : {type}]".format(
                    x=event.xdata, y=event.ydata,
                    name=name,type=type))
            else:
                self.pos_st.SetLabel("({x:<.4f}, {y:<.4f})".format(
                    x=event.xdata, y=event.ydata))

    def identify_obj(self, x):
        if self.x_pos_list is None: return None,None
        else:
            try:
                idx = bisect(self.x_pos_list, x)
                name = self.anote_list[idx]['name']
                type = self.anote_list[idx]['type']
            except IndexError:
                name, type = None, None
            return name, type

class EditListFrame(wx.Frame):
    def __init__(self, parent, string_list=None, label=None):
        wx.Frame.__init__(self, parent)

        self.parent = parent
        self.string_list = string_list
        self.label = label if label is not None else ''
        self._init_ui()

    def _init_ui(self):
        self.panel = wx.Panel(self)
        msizer = wx.BoxSizer(wx.VERTICAL)
        self.elb = gizmos.EditableListBox(self.panel, -1, label=self.label, size=(250, 250))
        if self.string_list is None:
            self.string_list = []
        self.elb.SetStrings(self.string_list)

        msizer.Add(self.elb, 1, wx.EXPAND | wx.ALL, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        cancel_btn = wx.Button(self.panel, label='Cancel')
        ok_btn     = wx.Button(self.panel, label='OK')
        hbox.Add(cancel_btn, 0)
        hbox.Add(ok_btn, 0, wx.LEFT, 10)

        msizer.Add(hbox, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.panel.SetSizer(msizer)

        self.Bind(wx.EVT_BUTTON, self.on_cancel, cancel_btn)
        self.Bind(wx.EVT_BUTTON, self.on_ok,     ok_btn)

    def on_cancel(self, event):
        self.Close()

    def on_ok(self, event):
        self.Close()

class EditFrame(wx.Frame):
    def __init__(self, parent, init_string=None):
        wx.Frame.__init__(self, parent)

        self.parent = parent
        self.init_string = init_string

        self._init_ui()

    def _init_ui(self):
        self.panel = wx.Panel(self)
        msizer = wx.BoxSizer(wx.VERTICAL)
        self.tc = wx.TextCtrl(self.panel, -1, value='', size=(250, 250), style=wx.TE_MULTILINE)
        if self.init_string is None:
            self.init_string = ''
        self.tc.SetValue(self.init_string)

        msizer.Add(self.tc, 1, wx.EXPAND | wx.ALL, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        cancel_btn = wx.Button(self.panel, label='Cancel')
        ok_btn     = wx.Button(self.panel, label='OK')
        hbox.Add(cancel_btn, 0)
        hbox.Add(ok_btn, 0, wx.LEFT, 10)

        msizer.Add(hbox, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.panel.SetSizer(msizer)

        self.Bind(wx.EVT_BUTTON, self.on_cancel, cancel_btn)
        self.Bind(wx.EVT_BUTTON, self.on_ok,     ok_btn)

    def on_cancel(self, event):
        self.Close()

    def on_ok(self, event):
        self.Close()

from wx.lib.mixins.listctrl import CheckListCtrlMixin
class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin):
    def __init__(self, parent, log):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        CheckListCtrlMixin.__init__(self)
        self.log = log
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)

    def OnItemActivated(self, event):
        pass

class TestFrame(wx.Frame):
    def __init__(self, parent, **kwargs):
        wx.Frame.__init__(self, parent, **kwargs)

        sizer = wx.BoxSizer(wx.VERTICAL)
        m_panel = MyPlotPanel(self, figsize=None,
                               type='line', toolbar=True)
        sizer.Add(m_panel, 1, wx.ALIGN_CENTER | wx.EXPAND, 10)
        self.SetSizerAndFit(sizer)

def test():
    app = wx.App()
    frame = TestFrame(None, title="Matplotlib Panel Test")
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    test()
