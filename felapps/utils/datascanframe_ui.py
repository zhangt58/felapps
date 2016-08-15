# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Feb 16 2016)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
from . import funutils

###########################################################################
## Class DataScanFrame
###########################################################################


class DataScanFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self,
                          parent,
                          id=wx.ID_ANY,
                          title=wx.EmptyString,
                          pos=wx.DefaultPosition,
                          size=wx.Size(1280, 1024),
                          style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        main_vbox = wx.BoxSizer(wx.VERTICAL)

        self.m_splitter = wx.SplitterWindow(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D)
        self.m_splitter.SetSashGravity(0)
        self.m_splitter.Bind(wx.EVT_IDLE, self.m_splitterOnIdle)
        self.m_splitter.SetMinimumPaneSize(300)

        self.m_panel_up = wx.Panel(self.m_splitter, wx.ID_ANY,
                                   wx.DefaultPosition, wx.DefaultSize,
                                   wx.TAB_TRAVERSAL)
        self.m_panel_up.SetFont(wx.Font(10, 70, 90, 90, False, wx.EmptyString))
        self.m_panel_up.SetForegroundColour(wx.Colour(176, 176, 176))

        up_vbox = wx.BoxSizer(wx.VERTICAL)

        up_sbox_ctrl = wx.StaticBoxSizer(
            wx.StaticBox(self.m_panel_up, wx.ID_ANY, u"Control Panel"),
            wx.HORIZONTAL)

        self.panel1 = wx.Panel(up_sbox_ctrl.GetStaticBox(), wx.ID_ANY,
                               wx.DefaultPosition, wx.DefaultSize,
                               wx.TAB_TRAVERSAL)
        self.panel1.SetFont(wx.Font(8, 70, 90, 90, False, wx.EmptyString))
        self.panel1.SetForegroundColour(wx.Colour(176, 176, 176))

        panel1_hbox = wx.BoxSizer(wx.HORIZONTAL)

        sbsizer_l = wx.StaticBoxSizer(
            wx.StaticBox(self.panel1, wx.ID_ANY, u"Set Variables"),
            wx.VERTICAL)

        gbSizer1 = wx.GridBagSizer(0, 0)
        gbSizer1.SetFlexibleDirection(wx.BOTH)
        gbSizer1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.var1_pv_set_st = wx.StaticText(
            sbsizer_l.GetStaticBox(), wx.ID_ANY, u"Var-I (set)",
            wx.DefaultPosition, wx.DefaultSize, 0)
        self.var1_pv_set_st.Wrap(-1)
        self.var1_pv_set_st.SetFont(wx.Font(10, 70, 90, 90, False,
                                            wx.EmptyString))
        self.var1_pv_set_st.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        gbSizer1.Add(self.var1_pv_set_st, wx.GBPosition(0, 0), wx.GBSpan(1, 1),
                     wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.var1_pv_set_tc = wx.TextCtrl(
            sbsizer_l.GetStaticBox(), wx.ID_ANY, u"UN-PS:Q-13:SETI",
            wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER)
        self.var1_pv_set_tc.SetFont(wx.Font(10, 70, 90, 90, False,
                                            wx.EmptyString))
        self.var1_pv_set_tc.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))
        self.var1_pv_set_tc.SetToolTipString(
            u"Input variable data source (set), usually a PV string.")

        gbSizer1.Add(self.var1_pv_set_tc, wx.GBPosition(0, 1), wx.GBSpan(1, 2),
                     wx.ALL | wx.EXPAND, 5)

        self.var1_pv_read_st = wx.StaticText(
            sbsizer_l.GetStaticBox(), wx.ID_ANY, u"(read)", wx.DefaultPosition,
            wx.DefaultSize, 0)
        self.var1_pv_read_st.Wrap(-1)
        self.var1_pv_read_st.SetFont(wx.Font(10, 70, 90, 90, False,
                                             wx.EmptyString))
        self.var1_pv_read_st.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        gbSizer1.Add(self.var1_pv_read_st, wx.GBPosition(0, 3), wx.GBSpan(
            1, 1), wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.var1_pv_read_tc = wx.TextCtrl(sbsizer_l.GetStaticBox(), wx.ID_ANY,
                                           u"UN-PS:Q-13:I", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.var1_pv_read_tc.SetFont(wx.Font(10, 70, 90, 90, False,
                                             wx.EmptyString))
        self.var1_pv_read_tc.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))
        self.var1_pv_read_tc.SetToolTipString(
            u"Input variable data source (read), usually a PV string.")

        gbSizer1.Add(self.var1_pv_read_tc, wx.GBPosition(0, 4), wx.GBSpan(
            1, 2), wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 5)

        self.var1_pv_flag_ckb = wx.CheckBox(
            sbsizer_l.GetStaticBox(), wx.ID_ANY, u"Copy", wx.DefaultPosition,
            wx.DefaultSize, 0)
        self.var1_pv_flag_ckb.SetFont(wx.Font(10, 70, 90, 90, False,
                                              wx.EmptyString))
        self.var1_pv_flag_ckb.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        gbSizer1.Add(self.var1_pv_flag_ckb, wx.GBPosition(0, 6), wx.GBSpan(
            1, 1), wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.var1_from_st = wx.StaticText(
            sbsizer_l.GetStaticBox(), wx.ID_ANY, u"Set Var-I From",
            wx.DefaultPosition, wx.DefaultSize, 0)
        self.var1_from_st.Wrap(-1)
        self.var1_from_st.SetFont(wx.Font(10, 70, 90, 90, False,
                                          wx.EmptyString))
        self.var1_from_st.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        gbSizer1.Add(self.var1_from_st, wx.GBPosition(1, 0), wx.GBSpan(1, 1),
                     wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.var1_from_tc = wx.TextCtrl(sbsizer_l.GetStaticBox(), wx.ID_ANY,
                                        u"-10", wx.DefaultPosition,
                                        wx.DefaultSize, wx.TE_PROCESS_ENTER)
        self.var1_from_tc.SetFont(wx.Font(10, 70, 90, 90, False,
                                          wx.EmptyString))
        self.var1_from_tc.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))
        self.var1_from_tc.SetToolTipString(
            u"Variable varying range start point, a float number.")

        gbSizer1.Add(self.var1_from_tc, wx.GBPosition(1, 1), wx.GBSpan(1, 2),
                     wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 5)

        self.var1_to_st = wx.StaticText(sbsizer_l.GetStaticBox(), wx.ID_ANY,
                                        u"To", wx.DefaultPosition,
                                        wx.DefaultSize, 0)
        self.var1_to_st.Wrap(-1)
        self.var1_to_st.SetFont(wx.Font(10, 70, 90, 90, False, wx.EmptyString))
        self.var1_to_st.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        gbSizer1.Add(self.var1_to_st, wx.GBPosition(1, 3), wx.GBSpan(1, 1),
                     wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.var1_to_tc = wx.TextCtrl(sbsizer_l.GetStaticBox(), wx.ID_ANY,
                                      u"10", wx.DefaultPosition,
                                      wx.DefaultSize, wx.TE_PROCESS_ENTER)
        self.var1_to_tc.SetFont(wx.Font(10, 70, 90, 90, False, wx.EmptyString))
        self.var1_to_tc.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))
        self.var1_to_tc.SetToolTipString(
            u"Variable varying range end point, a float number.")

        gbSizer1.Add(self.var1_to_tc, wx.GBPosition(1, 4), wx.GBSpan(1, 2),
                     wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 5)

        self.m_staticText17 = wx.StaticText(
            sbsizer_l.GetStaticBox(), wx.ID_ANY, wx.EmptyString,
            wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText17.Wrap(-1)
        gbSizer1.Add(self.m_staticText17, wx.GBPosition(1, 6), wx.GBSpan(1, 1),
                     wx.ALL, 5)

        self.var2_pv_st = wx.StaticText(sbsizer_l.GetStaticBox(), wx.ID_ANY,
                                        u"Var-II (read)", wx.DefaultPosition,
                                        wx.DefaultSize, 0)
        self.var2_pv_st.Wrap(-1)
        self.var2_pv_st.SetFont(wx.Font(10, 70, 90, 90, False, wx.EmptyString))
        self.var2_pv_st.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        gbSizer1.Add(self.var2_pv_st, wx.GBPosition(2, 0), wx.GBSpan(1, 1),
                     wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.var2_pv_tc = wx.TextCtrl(sbsizer_l.GetStaticBox(), wx.ID_ANY,
                                      u"UN-UN:MOD-1:GAP", wx.DefaultPosition,
                                      wx.DefaultSize, wx.TE_PROCESS_ENTER)
        self.var2_pv_tc.SetFont(wx.Font(10, 70, 90, 90, False, wx.EmptyString))
        self.var2_pv_tc.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))
        self.var2_pv_tc.SetToolTipString(
            u"Input dependent variable data source (read), usually a PV string.")

        gbSizer1.Add(self.var2_pv_tc, wx.GBPosition(2, 1), wx.GBSpan(1, 3),
                     wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 5)

        var2_op_comboxChoices = [u"none", u"sum", u"max", u"min",
                                 u"user-defined"]
        self.var2_op_combox = wx.ComboBox(
            sbsizer_l.GetStaticBox(), wx.ID_ANY, u"none", wx.DefaultPosition,
            wx.DefaultSize, var2_op_comboxChoices, wx.CB_READONLY)
        self.var2_op_combox.SetFont(wx.Font(10, 70, 90, 90, False,
                                            wx.EmptyString))
        self.var2_op_combox.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))
        self.var2_op_combox.SetToolTipString(
            u"Choose functional operation to Var-II.")

        gbSizer1.Add(self.var2_op_combox, wx.GBPosition(2, 4), wx.GBSpan(1, 1),
                     wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.var2_op_st = wx.StaticText(sbsizer_l.GetStaticBox(), wx.ID_ANY,
                                        u"Raw data.", wx.DefaultPosition,
                                        wx.DefaultSize, wx.ALIGN_LEFT)
        self.var2_op_st.Wrap(-1)
        self.var2_op_st.SetFont(wx.Font(8, 70, 90, 90, False, wx.EmptyString))
        self.var2_op_st.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        gbSizer1.Add(self.var2_op_st, wx.GBPosition(2, 5), wx.GBSpan(1, 2),
                     wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        gbSizer1.AddGrowableCol(1)
        gbSizer1.AddGrowableCol(2)
        gbSizer1.AddGrowableCol(4)
        gbSizer1.AddGrowableCol(5)

        sbsizer_l.Add(gbSizer1, 1, wx.EXPAND, 5)

        bSizer26 = wx.BoxSizer(wx.HORIZONTAL)

        self.mode_st = wx.StaticText(sbsizer_l.GetStaticBox(), wx.ID_ANY,
                                     u"Mode", wx.DefaultPosition,
                                     wx.DefaultSize, 0)
        self.mode_st.Wrap(-1)
        self.mode_st.SetFont(wx.Font(10, 70, 90, 90, False, wx.EmptyString))
        self.mode_st.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        bSizer26.Add(self.mode_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.ds_flag_rb = wx.RadioButton(sbsizer_l.GetStaticBox(), wx.ID_ANY,
                                         u"Data Scan", wx.DefaultPosition,
                                         wx.DefaultSize, 0)
        self.ds_flag_rb.SetFont(wx.Font(10, 70, 90, 90, False, wx.EmptyString))
        self.ds_flag_rb.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))
        self.ds_flag_rb.SetToolTipString(
            u"Check to enable parameters scan mode.")

        bSizer26.Add(self.ds_flag_rb, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.daq_flag_rb = wx.RadioButton(sbsizer_l.GetStaticBox(), wx.ID_ANY,
                                          u"DAQ", wx.DefaultPosition,
                                          wx.DefaultSize, 0)
        self.daq_flag_rb.SetFont(wx.Font(10, 70, 90, 90, False,
                                         wx.EmptyString))
        self.daq_flag_rb.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))
        self.daq_flag_rb.SetToolTipString(
            u"Check to enable data correlation analysis mode.")

        bSizer26.Add(self.daq_flag_rb, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.daq_pv_list_st = wx.StaticText(
            sbsizer_l.GetStaticBox(), wx.ID_ANY, u"PV List",
            wx.DefaultPosition, wx.DefaultSize, 0)
        self.daq_pv_list_st.Wrap(-1)
        self.daq_pv_list_st.SetFont(wx.Font(10, 70, 90, 90, False,
                                            wx.EmptyString))
        self.daq_pv_list_st.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        bSizer26.Add(self.daq_pv_list_st, 0, wx.ALIGN_CENTER_VERTICAL |
                     wx.LEFT, 30)

        self.daq_pv_list_tc = wx.TextCtrl(sbsizer_l.GetStaticBox(), wx.ID_ANY,
                                          wx.EmptyString, wx.DefaultPosition,
                                          wx.DefaultSize, 0)
        self.daq_pv_list_tc.SetFont(wx.Font(10, 70, 90, 90, False,
                                            wx.EmptyString))
        self.daq_pv_list_tc.SetToolTipString(u"Input PVs seperated by ';'")

        bSizer26.Add(self.daq_pv_list_tc, 1, wx.ALIGN_CENTER_VERTICAL |
                     wx.LEFT, 5)

        self.daq_pv_list_btn = wx.Button(sbsizer_l.GetStaticBox(), wx.ID_ANY,
                                         u"...", wx.DefaultPosition, wx.Size(
                                             40, -1), 0)
        self.daq_pv_list_btn.SetFont(wx.Font(10, 70, 90, 90, False,
                                             wx.EmptyString))

        bSizer26.Add(self.daq_pv_list_btn, 0, wx.ALIGN_CENTER_VERTICAL |
                     wx.ALL, 5)

        sbsizer_l.Add(bSizer26, 0, wx.EXPAND, 5)

        bSizer27 = wx.BoxSizer(wx.VERTICAL)

        self.mode_tc = wx.TextCtrl(sbsizer_l.GetStaticBox(), wx.ID_ANY,
                                   u"Parameters scan mode is activated.",
                                   wx.DefaultPosition, wx.DefaultSize,
                                   wx.TE_MULTILINE | wx.TE_READONLY)
        self.mode_tc.SetFont(wx.Font(8, 70, 90, 90, False, wx.EmptyString))

        bSizer27.Add(self.mode_tc, 1, wx.ALL | wx.EXPAND, 5)

        sbsizer_l.Add(bSizer27, 1, wx.EXPAND, 5)

        bSizer25 = wx.BoxSizer(wx.HORIZONTAL)

        self.adv_mode_ckb = wx.CheckBox(sbsizer_l.GetStaticBox(), wx.ID_ANY,
                                        u"Advanced Mode", wx.DefaultPosition,
                                        wx.DefaultSize, 0)
        self.adv_mode_ckb.SetFont(wx.Font(10, 70, 90, 90, False,
                                          wx.EmptyString))
        self.adv_mode_ckb.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))
        self.adv_mode_ckb.Enable(False)
        self.adv_mode_ckb.SetToolTipString(
            u"Check to active advanced mode, click 'Configure' button for details.")

        bSizer25.Add(self.adv_mode_ckb, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                     5)

        self.adv_mode_btn = wx.Button(sbsizer_l.GetStaticBox(), wx.ID_ANY,
                                      u"Configure", wx.DefaultPosition,
                                      wx.DefaultSize, 0)
        self.adv_mode_btn.SetFont(wx.Font(10, 70, 90, 90, False,
                                          wx.EmptyString))
        self.adv_mode_btn.Enable(False)

        bSizer25.Add(self.adv_mode_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                     5)

        sbsizer_l.Add(bSizer25, 0, wx.EXPAND, 5)

        panel1_hbox.Add(sbsizer_l, 3, wx.BOTTOM | wx.EXPAND | wx.LEFT |
                        wx.RIGHT, 5)

        sbsizer_m = wx.StaticBoxSizer(
            wx.StaticBox(self.panel1, wx.ID_ANY, u"DAQ Configurations"),
            wx.VERTICAL)

        bSizer21 = wx.BoxSizer(wx.VERTICAL)

        fgSizer5 = wx.FlexGridSizer(0, 3, 0, 0)
        fgSizer5.AddGrowableCol(1)
        fgSizer5.SetFlexibleDirection(wx.BOTH)
        fgSizer5.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.iternum_st = wx.StaticText(sbsizer_m.GetStaticBox(), wx.ID_ANY,
                                        u"Iteration Number",
                                        wx.DefaultPosition, wx.DefaultSize, 0)
        self.iternum_st.Wrap(-1)
        self.iternum_st.SetFont(wx.Font(10, 70, 90, 90, False, wx.EmptyString))
        self.iternum_st.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        fgSizer5.Add(self.iternum_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.iternum_sc = wx.SpinCtrl(
            sbsizer_m.GetStaticBox(), wx.ID_ANY, u"10", wx.DefaultPosition,
            wx.DefaultSize, wx.SP_ARROW_KEYS, 1, 1000, 10)
        self.iternum_sc.SetFont(wx.Font(10, 70, 90, 90, False, wx.EmptyString))
        self.iternum_sc.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))
        self.iternum_sc.SetToolTipString(u"Total number of scan iteration.")

        fgSizer5.Add(self.iternum_sc, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL |
                     wx.EXPAND, 5)

        self.m_staticText45 = wx.StaticText(
            sbsizer_m.GetStaticBox(), wx.ID_ANY, wx.EmptyString,
            wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText45.Wrap(-1)
        fgSizer5.Add(self.m_staticText45, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                     5)

        self.shotperiter_st = wx.StaticText(
            sbsizer_m.GetStaticBox(), wx.ID_ANY, u"Shot Number",
            wx.DefaultPosition, wx.DefaultSize, 0)
        self.shotperiter_st.Wrap(-1)
        self.shotperiter_st.SetFont(wx.Font(10, 70, 90, 90, False,
                                            wx.EmptyString))
        self.shotperiter_st.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        fgSizer5.Add(self.shotperiter_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                     5)

        self.shotperiter_sc = wx.SpinCtrl(
            sbsizer_m.GetStaticBox(), wx.ID_ANY, u"5", wx.DefaultPosition,
            wx.DefaultSize, wx.SP_ARROW_KEYS, 1, 1000, 5)
        self.shotperiter_sc.SetFont(wx.Font(10, 70, 90, 90, False,
                                            wx.EmptyString))
        self.shotperiter_sc.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))
        self.shotperiter_sc.SetToolTipString(
            u"Shot number to record per iteration.")

        fgSizer5.Add(self.shotperiter_sc, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL
                     | wx.EXPAND, 5)

        self.m_staticText39 = wx.StaticText(
            sbsizer_m.GetStaticBox(), wx.ID_ANY, u"per iteration",
            wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText39.Wrap(-1)
        self.m_staticText39.SetFont(wx.Font(10, 70, 90, 90, False,
                                            wx.EmptyString))
        self.m_staticText39.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        fgSizer5.Add(self.m_staticText39, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                     5)

        self.waittime_st = wx.StaticText(sbsizer_m.GetStaticBox(), wx.ID_ANY,
                                         u"Wait Time", wx.DefaultPosition,
                                         wx.DefaultSize, 0)
        self.waittime_st.Wrap(-1)
        self.waittime_st.SetFont(wx.Font(10, 70, 90, 90, False,
                                         wx.EmptyString))
        self.waittime_st.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        fgSizer5.Add(self.waittime_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.waittime_sc = wx.SpinCtrlDouble(sbsizer_m.GetStaticBox(),
                                             wx.ID_ANY,
                                             value='0.5',
                                             min=0.1,
                                             max=100,
                                             inc=0.1,
                                             style=wx.SP_ARROW_KEYS |
                                             wx.ALIGN_LEFT)
        self.waittime_sc.SetDigits(2)
        self.waittime_sc.Bind(wx.EVT_SPINCTRLDOUBLE,
                              self.waittime_scOnSpinCtrl)

        self.waittime_sc.SetFont(wx.Font(10, 70, 90, 90, False,
                                         wx.EmptyString))
        self.waittime_sc.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))
        self.waittime_sc.SetToolTipString(
            u"Pause time after each iteration setup.")

        fgSizer5.Add(self.waittime_sc, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL |
                     wx.EXPAND, 5)

        self.m_staticText41 = wx.StaticText(
            sbsizer_m.GetStaticBox(), wx.ID_ANY, u"second", wx.DefaultPosition,
            wx.DefaultSize, 0)
        self.m_staticText41.Wrap(-1)
        self.m_staticText41.SetFont(wx.Font(10, 70, 90, 90, False,
                                            wx.EmptyString))
        self.m_staticText41.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        fgSizer5.Add(self.m_staticText41, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                     5)

        self.m_staticText42 = wx.StaticText(
            sbsizer_m.GetStaticBox(), wx.ID_ANY, u"Scan DAQ rate",
            wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText42.Wrap(-1)
        self.m_staticText42.SetFont(wx.Font(10, 70, 90, 90, False,
                                            wx.EmptyString))
        self.m_staticText42.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        fgSizer5.Add(self.m_staticText42, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                     5)

        self.daqrate_sc = wx.SpinCtrl(sbsizer_m.GetStaticBox(), wx.ID_ANY,
                                      u"5", wx.DefaultPosition, wx.DefaultSize,
                                      wx.SP_ARROW_KEYS, 1, 50, 5)
        self.daqrate_sc.SetFont(wx.Font(10, 70, 90, 90, False, wx.EmptyString))
        self.daqrate_sc.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))
        self.daqrate_sc.SetToolTipString(u"Record to be taken per second.")

        fgSizer5.Add(self.daqrate_sc, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL |
                     wx.EXPAND, 5)

        self.m_staticText43 = wx.StaticText(
            sbsizer_m.GetStaticBox(), wx.ID_ANY, u"Hz", wx.DefaultPosition,
            wx.DefaultSize, 0)
        self.m_staticText43.Wrap(-1)
        self.m_staticText43.SetFont(wx.Font(10, 70, 90, 90, False,
                                            wx.EmptyString))
        self.m_staticText43.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        fgSizer5.Add(self.m_staticText43, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                     5)

        bSizer21.Add(fgSizer5, 0, wx.EXPAND, 5)

        self.m_staticline21 = wx.StaticLine(sbsizer_m.GetStaticBox(),
                                            wx.ID_ANY, wx.DefaultPosition,
                                            wx.DefaultSize, wx.LI_HORIZONTAL)
        bSizer21.Add(self.m_staticline21, 0, wx.EXPAND | wx.ALL, 10)

        gSizer1 = wx.GridSizer(0, 4, 0, 0)

        self.start_btn = wx.Button(sbsizer_m.GetStaticBox(), wx.ID_ANY,
                                   u"START", wx.DefaultPosition,
                                   wx.DefaultSize, 0)
        self.start_btn.SetFont(wx.Font(10, 70, 90, 90, False, wx.EmptyString))
        self.start_btn.SetMinSize(wx.Size(100, -1))

        gSizer1.Add(self.start_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.stop_btn = wx.Button(sbsizer_m.GetStaticBox(), wx.ID_ANY, u"STOP",
                                  wx.DefaultPosition, wx.DefaultSize, 0)
        self.stop_btn.SetFont(wx.Font(10, 70, 90, 90, False, wx.EmptyString))
        self.stop_btn.SetMinSize(wx.Size(100, -1))

        gSizer1.Add(self.stop_btn, 0, wx.ALL, 5)

        self.retake_btn = wx.Button(sbsizer_m.GetStaticBox(), wx.ID_ANY,
                                    u"RETAKE", wx.DefaultPosition,
                                    wx.DefaultSize, 0)
        self.retake_btn.SetFont(wx.Font(10, 70, 90, 90, False, wx.EmptyString))
        self.retake_btn.SetMinSize(wx.Size(100, -1))

        gSizer1.Add(self.retake_btn, 0, wx.ALL, 5)

        self.close_btn = wx.Button(sbsizer_m.GetStaticBox(), wx.ID_ANY,
                                   u"CLOSE", wx.DefaultPosition,
                                   wx.DefaultSize, 0)
        self.close_btn.SetFont(wx.Font(10, 70, 90, 90, False, wx.EmptyString))
        self.close_btn.SetMinSize(wx.Size(100, -1))

        gSizer1.Add(self.close_btn, 0, wx.ALL, 5)

        bSizer21.Add(gSizer1, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        bSizer14 = wx.BoxSizer(wx.HORIZONTAL)

        self.timenow_st = wx.StaticText(sbsizer_m.GetStaticBox(), wx.ID_ANY,
                                        wx.EmptyString, wx.DefaultPosition,
                                        wx.DefaultSize, 0)
        self.timenow_st.Wrap(-1)
        bSizer14.Add(self.timenow_st, 0, wx.ALL, 5)

        bSizer21.Add(bSizer14, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        sbsizer_m.Add(bSizer21, 1, wx.EXPAND, 5)

        panel1_hbox.Add(sbsizer_m, 2, wx.BOTTOM | wx.EXPAND | wx.RIGHT, 5)

        self.panel1.SetSizer(panel1_hbox)
        self.panel1.Layout()
        panel1_hbox.Fit(self.panel1)
        up_sbox_ctrl.Add(self.panel1, 2, wx.ALL | wx.EXPAND, 1)

        up_vbox.Add(up_sbox_ctrl, 1, wx.ALL | wx.EXPAND, 5)

        self.m_panel_up.SetSizer(up_vbox)
        self.m_panel_up.Layout()
        up_vbox.Fit(self.m_panel_up)
        self.m_panel_down = wx.Panel(self.m_splitter, wx.ID_ANY,
                                     wx.DefaultPosition, wx.DefaultSize,
                                     wx.TAB_TRAVERSAL)
        self.m_panel_down.SetFont(wx.Font(10, 70, 90, 90, False,
                                          wx.EmptyString))
        self.m_panel_down.SetForegroundColour(wx.Colour(176, 176, 176))

        bottom_vbox = wx.BoxSizer(wx.VERTICAL)

        down_sbox_scan = wx.StaticBoxSizer(
            wx.StaticBox(self.m_panel_down, wx.ID_ANY,
                         u"Correlation Analysis Panel"), wx.VERTICAL)

        bSizer19 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_splitter_down = wx.SplitterWindow(down_sbox_scan.GetStaticBox(),
                                                 wx.ID_ANY, wx.DefaultPosition,
                                                 wx.DefaultSize, wx.SP_3D)
        self.m_splitter_down.SetSashGravity(0)
        self.m_splitter_down.Bind(wx.EVT_IDLE, self.m_splitter_downOnIdle)
        self.m_splitter_down.SetMinimumPaneSize(400)

        self.m_splitter_l = wx.Panel(self.m_splitter_down, wx.ID_ANY,
                                     wx.DefaultPosition, wx.DefaultSize,
                                     wx.TAB_TRAVERSAL)
        bSizer23 = wx.BoxSizer(wx.VERTICAL)

        self.scanfig_panel = funutils.ScanPlotPanel(self.m_splitter_l,
                                                    toolbar=True)
        bSizer23.Add(self.scanfig_panel, 1, wx.ALL | wx.EXPAND, 2)

        self.m_splitter_l.SetSizer(bSizer23)
        self.m_splitter_l.Layout()
        bSizer23.Fit(self.m_splitter_l)
        self.m_splitter_r = wx.Panel(self.m_splitter_down, wx.ID_ANY,
                                     wx.DefaultPosition, wx.DefaultSize,
                                     wx.TAB_TRAVERSAL)
        self.m_splitter_r.SetFont(wx.Font(10, 70, 90, 90, False,
                                          wx.EmptyString))
        self.m_splitter_r.SetForegroundColour(wx.Colour(176, 176, 176))

        bSizer24 = wx.BoxSizer(wx.VERTICAL)

        sbSizer13 = wx.StaticBoxSizer(
            wx.StaticBox(self.m_splitter_r, wx.ID_ANY, u"Curve"), wx.VERTICAL)

        bSizer17 = wx.BoxSizer(wx.HORIZONTAL)

        self.fit_model_st = wx.StaticText(sbSizer13.GetStaticBox(), wx.ID_ANY,
                                          u"Model", wx.DefaultPosition,
                                          wx.DefaultSize, 0)
        self.fit_model_st.Wrap(-1)
        self.fit_model_st.SetFont(wx.Font(10, 70, 90, 90, False,
                                          wx.EmptyString))
        self.fit_model_st.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        bSizer17.Add(self.fit_model_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                     5)

        fit_model_cbChoices = []
        self.fit_model_cb = wx.ComboBox(sbSizer13.GetStaticBox(), wx.ID_ANY,
                                        u"gaussian", wx.DefaultPosition,
                                        wx.DefaultSize, fit_model_cbChoices,
                                        wx.CB_READONLY)
        bSizer17.Add(self.fit_model_cb, 0, wx.ALL, 5)

        self.fit_config_ckb = wx.CheckBox(sbSizer13.GetStaticBox(), wx.ID_ANY,
                                          u"Add Config", wx.DefaultPosition,
                                          wx.DefaultSize, 0)
        self.fit_config_ckb.SetFont(wx.Font(10, 70, 90, 90, False,
                                            wx.EmptyString))
        self.fit_config_ckb.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        bSizer17.Add(self.fit_config_ckb, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                     5)

        self.fit_config_btn = wx.BitmapButton(
            sbSizer13.GetStaticBox(), wx.ID_ANY, wx.ArtProvider.GetBitmap(
                wx.ART_ADD_BOOKMARK, ), wx.DefaultPosition, wx.DefaultSize,
            wx.BU_AUTODRAW)
        self.fit_config_btn.Enable(False)
        self.fit_config_btn.SetToolTipString(
            u"Additional parameters for curve fitting, input format: k=v.\nAvailable 'k':\n    'n': highest order for polynomial fit;\n    'xmin': fitting window, min of x;\n    'xmax': fitting window, max of x;")

        bSizer17.Add(self.fit_config_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                     5)

        self.fit_refresh_btn = wx.BitmapButton(
            sbSizer13.GetStaticBox(), wx.ID_ANY, wx.ArtProvider.GetBitmap(
                u"gtk-refresh", ), wx.DefaultPosition, wx.Size(-1, -1),
            wx.BU_AUTODRAW)
        self.fit_refresh_btn.SetToolTipString(u"Refresh fitting curve.")

        bSizer17.Add(self.fit_refresh_btn, 0, wx.ALIGN_CENTER_VERTICAL |
                     wx.ALL, 5)

        sbSizer13.Add(bSizer17, 0, wx.EXPAND, 5)

        bSizer18 = wx.BoxSizer(wx.VERTICAL)

        bSizer22 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText23 = wx.StaticText(
            sbSizer13.GetStaticBox(), wx.ID_ANY, u"Fitting report:",
            wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText23.Wrap(-1)
        self.m_staticText23.SetFont(wx.Font(10, 70, 90, 90, False,
                                            wx.EmptyString))
        self.m_staticText23.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        bSizer22.Add(self.m_staticText23, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                     5)

        self.fit_to_fig_btn = wx.Button(sbSizer13.GetStaticBox(), wx.ID_ANY,
                                        u"Stick To Figure", wx.DefaultPosition,
                                        wx.DefaultSize, 0)
        self.fit_to_fig_btn.SetToolTipString(
            u"Put fitting result to scan figure.")

        bSizer22.Add(self.fit_to_fig_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                     5)

        self.stick_pos_tc = wx.TextCtrl(sbSizer13.GetStaticBox(), wx.ID_ANY,
                                        wx.EmptyString, wx.DefaultPosition,
                                        wx.DefaultSize, wx.TE_PROCESS_ENTER)
        self.stick_pos_tc.SetToolTipString(
            u"Label options: key = val, multi-keys should be separated by ';', available keys:\n    'x': x position;\n    'y': y position;\n    'fontsize': text fontsize;")

        bSizer22.Add(self.stick_pos_tc, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                     5)

        bSizer18.Add(bSizer22, 0, wx.EXPAND, 5)

        self.fit_report_tc = wx.TextCtrl(sbSizer13.GetStaticBox(), wx.ID_ANY,
                                         wx.EmptyString, wx.DefaultPosition,
                                         wx.DefaultSize, wx.TE_MULTILINE)
        self.fit_report_tc.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), 70,
                                           90, 90, False, wx.EmptyString))

        bSizer18.Add(self.fit_report_tc, 1, wx.ALL | wx.EXPAND, 5)

        sbSizer13.Add(bSizer18, 1, wx.EXPAND, 5)

        bSizer24.Add(sbSizer13, 1, wx.ALL | wx.EXPAND, 5)

        sbSizer14 = wx.StaticBoxSizer(
            wx.StaticBox(self.m_splitter_r, wx.ID_ANY, u"Style"), wx.VERTICAL)

        gbSizer2 = wx.GridBagSizer(0, 0)
        gbSizer2.SetFlexibleDirection(wx.BOTH)
        gbSizer2.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.lineid_st = wx.StaticText(sbSizer14.GetStaticBox(), wx.ID_ANY,
                                       u"Edit Line", wx.DefaultPosition,
                                       wx.DefaultSize, 0)
        self.lineid_st.Wrap(-1)
        self.lineid_st.SetFont(wx.Font(10, 70, 90, 90, False, wx.EmptyString))
        self.lineid_st.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        gbSizer2.Add(self.lineid_st, wx.GBPosition(0, 0), wx.GBSpan(1, 1),
                     wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        lineid_cbChoices = [u"Average", u"Errorbar", u"Fitting"]
        self.lineid_cb = wx.ComboBox(sbSizer14.GetStaticBox(), wx.ID_ANY,
                                     u"Average", wx.DefaultPosition,
                                     wx.DefaultSize, lineid_cbChoices, 0)
        gbSizer2.Add(self.lineid_cb, wx.GBPosition(0, 1), wx.GBSpan(1, 3),
                     wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 5)

        self.mark_style_st = wx.StaticText(sbSizer14.GetStaticBox(), wx.ID_ANY,
                                           u"Marker", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.mark_style_st.Wrap(-1)
        self.mark_style_st.SetFont(wx.Font(10, 70, 90, 90, False,
                                           wx.EmptyString))
        self.mark_style_st.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        gbSizer2.Add(self.mark_style_st, wx.GBPosition(1, 0), wx.GBSpan(1, 1),
                     wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        mksize_hbox = wx.BoxSizer(wx.HORIZONTAL)

        mksize_hbox.SetMinSize(wx.Size(120, -1))
        self.mks_sc = wx.SpinCtrlDouble(sbSizer14.GetStaticBox(),
                                        wx.ID_ANY,
                                        value='5',
                                        min=1,
                                        max=20,
                                        inc=0.5,
                                        style=wx.SP_ARROW_KEYS | wx.ALIGN_LEFT,
                                        size=(50, -1))
        self.mks_sc.SetDigits(1)
        self.mks_sc.Bind(wx.EVT_SPINCTRLDOUBLE, self.mks_scOnSpinCtrl)
        self.mks_sc.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))
        self.mks_sc.SetToolTipString(u"size")

        mksize_hbox.Add(self.mks_sc, 1, wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM |
                        wx.EXPAND | wx.LEFT | wx.TOP, 5)

        self.mew_sc = wx.SpinCtrlDouble(sbSizer14.GetStaticBox(),
                                        wx.ID_ANY,
                                        value='1',
                                        min=0.5,
                                        max=10,
                                        inc=0.5,
                                        style=wx.SP_ARROW_KEYS | wx.ALIGN_LEFT,
                                        size=(50, -1))
        self.mew_sc.SetDigits(1)
        self.mew_sc.Bind(wx.EVT_SPINCTRLDOUBLE, self.mew_scOnSpinCtrl)
        self.mew_sc.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))
        self.mew_sc.SetToolTipString(u"thickness")

        mksize_hbox.Add(self.mew_sc, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL |
                        wx.BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)

        gbSizer2.Add(mksize_hbox, wx.GBPosition(1, 1), wx.GBSpan(1, 1),
                     wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 5)

        mkcolor_hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.mec_btn = wx.BitmapButton(sbSizer14.GetStaticBox(), wx.ID_ANY,
                                       wx.NullBitmap, wx.DefaultPosition,
                                       wx.DefaultSize, wx.BU_AUTODRAW)
        w, h = 16, 16
        k_bmp = wx.EmptyBitmap(w, h)
        k_img = wx.ImageFromBitmap(k_bmp)
        k_img.SetRGBRect(wx.Rect(0, 0, w, h), 0, 0, 0)
        self.mec_btn.SetBitmap(wx.BitmapFromImage(k_img))

        self.mec_btn.Bind(wx.EVT_BUTTON, self.mec_btnOnButtonClick)
        self.mec_btn.SetToolTipString(u"edgecolor")

        mkcolor_hbox.Add(self.mec_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.mfc_btn = wx.BitmapButton(sbSizer14.GetStaticBox(), wx.ID_ANY,
                                       wx.NullBitmap, wx.DefaultPosition,
                                       wx.DefaultSize, wx.BU_AUTODRAW)
        w, h = 16, 16
        k_bmp = wx.EmptyBitmap(w, h)
        k_img = wx.ImageFromBitmap(k_bmp)
        k_img.SetRGBRect(wx.Rect(0, 0, w, h), 0, 0, 0)
        self.mfc_btn.SetBitmap(wx.BitmapFromImage(k_img))

        self.mfc_btn.Bind(wx.EVT_BUTTON, self.mfc_btnOnButtonClick)
        self.mfc_btn.SetToolTipString(u"facecolor")

        mkcolor_hbox.Add(self.mfc_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        gbSizer2.Add(mkcolor_hbox, wx.GBPosition(1, 2), wx.GBSpan(1, 1),
                     wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 5)

        mkstyle_cbChoices = []
        self.mkstyle_cb = wx.ComboBox(sbSizer14.GetStaticBox(), wx.ID_ANY,
                                      wx.EmptyString, wx.DefaultPosition,
                                      wx.Size(100, -1), mkstyle_cbChoices, 0)
        self.mkstyle_cb.SetToolTipString(u"style")

        gbSizer2.Add(self.mkstyle_cb, wx.GBPosition(1, 3), wx.GBSpan(1, 1),
                     wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 5)

        self.line_style_st = wx.StaticText(sbSizer14.GetStaticBox(), wx.ID_ANY,
                                           u"Line", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.line_style_st.Wrap(-1)
        self.line_style_st.SetFont(wx.Font(10, 70, 90, 90, False,
                                           wx.EmptyString))
        self.line_style_st.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        gbSizer2.Add(self.line_style_st, wx.GBPosition(2, 0), wx.GBSpan(1, 1),
                     wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        lw_hbox = wx.BoxSizer(wx.HORIZONTAL)

        lw_hbox.SetMinSize(wx.Size(120, -1))
        self.lw_sc = wx.SpinCtrlDouble(sbSizer14.GetStaticBox(),
                                       wx.ID_ANY,
                                       value='1',
                                       min=0,
                                       max=20,
                                       inc=0.5,
                                       style=wx.SP_ARROW_KEYS | wx.ALIGN_LEFT)
        self.lw_sc.SetDigits(1)
        self.lw_sc.Bind(wx.EVT_SPINCTRLDOUBLE, self.lw_scOnSpinCtrl)
        self.lw_sc.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))
        self.lw_sc.SetToolTipString(u"width")

        lw_hbox.Add(self.lw_sc, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        gbSizer2.Add(lw_hbox, wx.GBPosition(2, 1), wx.GBSpan(1, 1),
                     wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 5)

        lc_hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.lc_btn = wx.BitmapButton(sbSizer14.GetStaticBox(), wx.ID_ANY,
                                      wx.NullBitmap, wx.DefaultPosition,
                                      wx.DefaultSize, wx.BU_AUTODRAW)
        w, h = 16, 16
        k_bmp = wx.EmptyBitmap(w, h)
        k_img = wx.ImageFromBitmap(k_bmp)
        k_img.SetRGBRect(wx.Rect(0, 0, w, h), 0, 0, 0)
        self.lc_btn.SetBitmap(wx.BitmapFromImage(k_img))

        self.lc_btn.Bind(wx.EVT_BUTTON, self.lc_btnOnButtonClick)
        self.lc_btn.SetToolTipString(u"color")

        lc_hbox.Add(self.lc_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        gbSizer2.Add(lc_hbox, wx.GBPosition(2, 2), wx.GBSpan(1, 1),
                     wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 5)

        ls_cbChoices = []
        self.ls_cb = wx.ComboBox(sbSizer14.GetStaticBox(), wx.ID_ANY,
                                 wx.EmptyString, wx.DefaultPosition, wx.Size(
                                     100, -1), ls_cbChoices, 0)
        self.ls_cb.SetToolTipString(u"style")

        gbSizer2.Add(self.ls_cb, wx.GBPosition(2, 3), wx.GBSpan(1, 1),
                     wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 5)

        self.grid_ckb = wx.CheckBox(sbSizer14.GetStaticBox(), wx.ID_ANY,
                                    u"Grid", wx.DefaultPosition,
                                    wx.DefaultSize, 0)
        self.grid_ckb.SetFont(wx.Font(10, 70, 90, 90, False, wx.EmptyString))
        self.grid_ckb.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        gbSizer2.Add(self.grid_ckb, wx.GBPosition(3, 0), wx.GBSpan(1, 1),
                     wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.legend_ckb = wx.CheckBox(sbSizer14.GetStaticBox(), wx.ID_ANY,
                                      u"Legend", wx.DefaultPosition,
                                      wx.DefaultSize, 0)
        self.legend_ckb.SetFont(wx.Font(10, 70, 90, 90, False, wx.EmptyString))
        self.legend_ckb.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        gbSizer2.Add(self.legend_ckb, wx.GBPosition(3, 1), wx.GBSpan(1, 1),
                     wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.clr_retake_btn = wx.Button(sbSizer14.GetStaticBox(), wx.ID_ANY,
                                        u"Clear RETAKE", wx.DefaultPosition,
                                        wx.DefaultSize, 0)
        self.clr_retake_btn.SetToolTipString(
            u"Clear all picked points for re-scan operation.")

        gbSizer2.Add(self.clr_retake_btn, wx.GBPosition(3, 2), wx.GBSpan(1, 2),
                     wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.auto_xlabel_ckb = wx.CheckBox(sbSizer14.GetStaticBox(), wx.ID_ANY,
                                           u"Auto xlabel", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.auto_xlabel_ckb.SetFont(wx.Font(10, 70, 90, 90, False,
                                             wx.EmptyString))
        self.auto_xlabel_ckb.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        gbSizer2.Add(self.auto_xlabel_ckb, wx.GBPosition(4, 0), wx.GBSpan(
            1, 1), wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.user_xlabel_ckb = wx.CheckBox(sbSizer14.GetStaticBox(), wx.ID_ANY,
                                           u"Define", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.user_xlabel_ckb.SetFont(wx.Font(10, 70, 90, 90, False,
                                             wx.EmptyString))
        self.user_xlabel_ckb.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        gbSizer2.Add(self.user_xlabel_ckb, wx.GBPosition(4, 1), wx.GBSpan(
            1, 1), wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.user_xlabel_tc = wx.TextCtrl(sbSizer14.GetStaticBox(), wx.ID_ANY,
                                          wx.EmptyString, wx.DefaultPosition,
                                          wx.DefaultSize, 0)
        self.user_xlabel_tc.SetFont(wx.Font(10, 70, 90, 90, False,
                                            wx.EmptyString))
        self.user_xlabel_tc.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))
        self.user_xlabel_tc.Enable(False)

        gbSizer2.Add(self.user_xlabel_tc, wx.GBPosition(4, 2), wx.GBSpan(1, 2),
                     wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 5)

        self.auto_title_ckb = wx.CheckBox(sbSizer14.GetStaticBox(), wx.ID_ANY,
                                          u"Auto Title", wx.DefaultPosition,
                                          wx.DefaultSize, 0)
        self.auto_title_ckb.SetFont(wx.Font(10, 70, 90, 90, False,
                                            wx.EmptyString))
        self.auto_title_ckb.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        gbSizer2.Add(self.auto_title_ckb, wx.GBPosition(5, 0), wx.GBSpan(1, 1),
                     wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.user_title_ckb = wx.CheckBox(sbSizer14.GetStaticBox(), wx.ID_ANY,
                                          u"Define", wx.DefaultPosition,
                                          wx.DefaultSize, 0)
        self.user_title_ckb.SetFont(wx.Font(10, 70, 90, 90, False,
                                            wx.EmptyString))
        self.user_title_ckb.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        gbSizer2.Add(self.user_title_ckb, wx.GBPosition(5, 1), wx.GBSpan(1, 1),
                     wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.user_title_tc = wx.TextCtrl(sbSizer14.GetStaticBox(), wx.ID_ANY,
                                         wx.EmptyString, wx.DefaultPosition,
                                         wx.DefaultSize, 0)
        self.user_title_tc.SetFont(wx.Font(10, 70, 90, 90, False,
                                           wx.EmptyString))
        self.user_title_tc.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))
        self.user_title_tc.Enable(False)
        self.user_title_tc.SetToolTipString(
            u"Macro: $TITLE could be used to represent the default title string.")

        gbSizer2.Add(self.user_title_tc, wx.GBPosition(5, 2), wx.GBSpan(1, 2),
                     wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 5)

        sbSizer14.Add(gbSizer2, 1, wx.EXPAND, 5)

        bSizer24.Add(sbSizer14, 1, wx.ALL | wx.EXPAND, 5)

        self.m_splitter_r.SetSizer(bSizer24)
        self.m_splitter_r.Layout()
        bSizer24.Fit(self.m_splitter_r)
        self.m_splitter_down.SplitVertically(self.m_splitter_l,
                                             self.m_splitter_r, 760)
        bSizer19.Add(self.m_splitter_down, 1, wx.EXPAND, 5)

        down_sbox_scan.Add(bSizer19, 1, wx.EXPAND, 5)

        bottom_vbox.Add(down_sbox_scan, 1, wx.ALL | wx.EXPAND, 5)

        self.m_panel_down.SetSizer(bottom_vbox)
        self.m_panel_down.Layout()
        bottom_vbox.Fit(self.m_panel_down)
        self.m_splitter.SplitHorizontally(self.m_panel_up, self.m_panel_down,
                                          400)
        main_vbox.Add(self.m_splitter, 1, wx.EXPAND, 5)

        self.SetSizer(main_vbox)
        self.Layout()
        self.m_menubar2 = wx.MenuBar(0)
        self.file_menu = wx.Menu()
        self.save_mitem = wx.MenuItem(self.file_menu, wx.ID_SAVE,
                                      u"&Save" + u"\t" + u"Ctrl+S",
                                      wx.EmptyString, wx.ITEM_NORMAL)
        self.file_menu.AppendItem(self.save_mitem)

        self.file_menu.AppendSeparator()

        self.exit_mitem = wx.MenuItem(self.file_menu, wx.ID_EXIT,
                                      u"E&xit" + u"\t" + u"Ctrl+W",
                                      wx.EmptyString, wx.ITEM_NORMAL)
        self.file_menu.AppendItem(self.exit_mitem)

        self.m_menubar2.Append(self.file_menu, u"&File")

        self.help_menu = wx.Menu()
        self.about_mitem = wx.MenuItem(self.help_menu, wx.ID_ABOUT,
                                       u"&About" + u"\t" + u"F1",
                                       wx.EmptyString, wx.ITEM_NORMAL)
        self.help_menu.AppendItem(self.about_mitem)

        self.m_menubar2.Append(self.help_menu, u"&Help")

        self.SetMenuBar(self.m_menubar2)

        self.Centre(wx.BOTH)

        # Connect Events
        self.var1_pv_set_tc.Bind(wx.EVT_TEXT_ENTER, self.var1_pv_tcOnTextEnter)
        self.var1_pv_flag_ckb.Bind(wx.EVT_CHECKBOX,
                                   self.var1_pv_flag_ckbOnCheckBox)
        self.var1_from_tc.Bind(wx.EVT_TEXT_ENTER, self.var1_from_tcOnTextEnter)
        self.var1_to_tc.Bind(wx.EVT_TEXT_ENTER, self.var1_to_tcOnTextEnter)
        self.var2_pv_tc.Bind(wx.EVT_TEXT_ENTER, self.var2_pv_tcOnTextEnter)
        self.var2_op_combox.Bind(wx.EVT_COMBOBOX,
                                 self.var2_op_comboxOnCombobox)
        self.ds_flag_rb.Bind(wx.EVT_RADIOBUTTON, self.ds_flag_rbOnRadioButton)
        self.daq_flag_rb.Bind(wx.EVT_RADIOBUTTON,
                              self.daq_flag_rbOnRadioButton)
        self.daq_pv_list_btn.Bind(wx.EVT_BUTTON,
                                  self.daq_pv_list_btnOnButtonClick)
        self.adv_mode_ckb.Bind(wx.EVT_CHECKBOX, self.adv_mode_ckbOnCheckBox)
        self.adv_mode_btn.Bind(wx.EVT_BUTTON, self.adv_mode_btnOnButtonClick)
        self.iternum_sc.Bind(wx.EVT_SPINCTRL, self.iternum_scOnSpinCtrl)
        self.shotperiter_sc.Bind(wx.EVT_SPINCTRL,
                                 self.shotperiter_scOnSpinCtrl)
        self.daqrate_sc.Bind(wx.EVT_SPINCTRL, self.daqrate_scOnSpinCtrl)
        self.start_btn.Bind(wx.EVT_BUTTON, self.start_btnOnButtonClick)
        self.stop_btn.Bind(wx.EVT_BUTTON, self.stop_btnOnButtonClick)
        self.retake_btn.Bind(wx.EVT_BUTTON, self.retake_btnOnButtonClick)
        self.close_btn.Bind(wx.EVT_BUTTON, self.close_btnOnButtonClick)
        self.fit_model_cb.Bind(wx.EVT_COMBOBOX, self.fit_model_cbOnCombobox)
        self.fit_config_ckb.Bind(wx.EVT_CHECKBOX,
                                 self.fit_config_ckbOnCheckBox)
        self.fit_config_btn.Bind(wx.EVT_BUTTON,
                                 self.fit_config_btnOnButtonClick)
        self.fit_refresh_btn.Bind(wx.EVT_BUTTON,
                                  self.fit_refresh_btnOnButtonClick)
        self.fit_to_fig_btn.Bind(wx.EVT_BUTTON,
                                 self.fit_to_fig_btnOnButtonClick)
        self.stick_pos_tc.Bind(wx.EVT_TEXT_ENTER, self.stick_pos_tcOnTextEnter)
        self.lineid_cb.Bind(wx.EVT_COMBOBOX, self.lineid_cbOnCombobox)
        self.mkstyle_cb.Bind(wx.EVT_COMBOBOX, self.mkstyle_cbOnCombobox)
        self.ls_cb.Bind(wx.EVT_COMBOBOX, self.ls_cbOnCombobox)
        self.grid_ckb.Bind(wx.EVT_CHECKBOX, self.grid_ckbOnCheckBox)
        self.legend_ckb.Bind(wx.EVT_CHECKBOX, self.legend_ckbOnCheckBox)
        self.clr_retake_btn.Bind(wx.EVT_BUTTON,
                                 self.clr_retake_btnOnButtonClick)
        self.auto_xlabel_ckb.Bind(wx.EVT_CHECKBOX,
                                  self.auto_xlabel_ckbOnCheckBox)
        self.user_xlabel_ckb.Bind(wx.EVT_CHECKBOX,
                                  self.user_xlabel_ckbOnCheckBox)
        self.auto_title_ckb.Bind(wx.EVT_CHECKBOX,
                                 self.auto_title_ckbOnCheckBox)
        self.user_title_ckb.Bind(wx.EVT_CHECKBOX,
                                 self.user_title_ckbOnCheckBox)
        self.Bind(wx.EVT_MENU,
                  self.save_mitemOnMenuSelection,
                  id=self.save_mitem.GetId())
        self.Bind(wx.EVT_MENU,
                  self.exit_mitemOnMenuSelection,
                  id=self.exit_mitem.GetId())
        self.Bind(wx.EVT_MENU,
                  self.about_mitemOnMenuSelection,
                  id=self.about_mitem.GetId())

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def var1_pv_tcOnTextEnter(self, event):
        event.Skip()

    def var1_pv_flag_ckbOnCheckBox(self, event):
        event.Skip()

    def var1_from_tcOnTextEnter(self, event):
        event.Skip()

    def var1_to_tcOnTextEnter(self, event):
        event.Skip()

    def var2_pv_tcOnTextEnter(self, event):
        event.Skip()

    def var2_op_comboxOnCombobox(self, event):
        event.Skip()

    def ds_flag_rbOnRadioButton(self, event):
        event.Skip()

    def daq_flag_rbOnRadioButton(self, event):
        event.Skip()

    def daq_pv_list_btnOnButtonClick(self, event):
        event.Skip()

    def adv_mode_ckbOnCheckBox(self, event):
        event.Skip()

    def adv_mode_btnOnButtonClick(self, event):
        event.Skip()

    def iternum_scOnSpinCtrl(self, event):
        event.Skip()

    def shotperiter_scOnSpinCtrl(self, event):
        event.Skip()

    def daqrate_scOnSpinCtrl(self, event):
        event.Skip()

    def start_btnOnButtonClick(self, event):
        event.Skip()

    def stop_btnOnButtonClick(self, event):
        event.Skip()

    def retake_btnOnButtonClick(self, event):
        event.Skip()

    def close_btnOnButtonClick(self, event):
        event.Skip()

    def fit_model_cbOnCombobox(self, event):
        event.Skip()

    def fit_config_ckbOnCheckBox(self, event):
        event.Skip()

    def fit_config_btnOnButtonClick(self, event):
        event.Skip()

    def fit_refresh_btnOnButtonClick(self, event):
        event.Skip()

    def fit_to_fig_btnOnButtonClick(self, event):
        event.Skip()

    def stick_pos_tcOnTextEnter(self, event):
        event.Skip()

    def lineid_cbOnCombobox(self, event):
        event.Skip()

    def mkstyle_cbOnCombobox(self, event):
        event.Skip()

    def ls_cbOnCombobox(self, event):
        event.Skip()

    def grid_ckbOnCheckBox(self, event):
        event.Skip()

    def legend_ckbOnCheckBox(self, event):
        event.Skip()

    def clr_retake_btnOnButtonClick(self, event):
        event.Skip()

    def auto_xlabel_ckbOnCheckBox(self, event):
        event.Skip()

    def user_xlabel_ckbOnCheckBox(self, event):
        event.Skip()

    def auto_title_ckbOnCheckBox(self, event):
        event.Skip()

    def user_title_ckbOnCheckBox(self, event):
        event.Skip()

    def save_mitemOnMenuSelection(self, event):
        event.Skip()

    def exit_mitemOnMenuSelection(self, event):
        event.Skip()

    def about_mitemOnMenuSelection(self, event):
        event.Skip()

    def m_splitterOnIdle(self, event):
        self.m_splitter.SetSashPosition(400)
        self.m_splitter.Unbind(wx.EVT_IDLE)

    def m_splitter_downOnIdle(self, event):
        self.m_splitter_down.SetSashPosition(760)
        self.m_splitter_down.Unbind(wx.EVT_IDLE)

    ###########################################################################
    ## Class FuncListFrame
    ###########################################################################


class FuncListFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self,
                          parent,
                          id=wx.ID_ANY,
                          title=wx.EmptyString,
                          pos=wx.DefaultPosition,
                          size=wx.Size(500, 400),
                          style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer16 = wx.BoxSizer(wx.VERTICAL)

        self.m_staticText21 = wx.StaticText(
            self, wx.ID_ANY, u"Fullpath of the user-defined functions:",
            wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText21.Wrap(-1)
        bSizer16.Add(self.m_staticText21, 0, wx.ALL, 5)

        bSizer17 = wx.BoxSizer(wx.HORIZONTAL)

        self.path_tc = wx.TextCtrl(
            self, wx.ID_ANY,
            u"/home/tong/Programming/projects/felapps/felapps/configs/udefs.py",
            wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY)
        self.path_tc.SetToolTipString(u"Fullpath of user-defined functions.")

        bSizer17.Add(self.path_tc, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.path_btn = wx.Button(self, wx.ID_ANY, u"Browse",
                                  wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer17.Add(self.path_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.reload_btn = wx.Button(self, wx.ID_ANY, u"Reload",
                                    wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer17.Add(self.reload_btn, 0, wx.ALL, 5)

        bSizer16.Add(bSizer17, 0, wx.EXPAND, 5)

        self.udefs_lc = wx.ListCtrl(self, wx.ID_ANY, wx.DefaultPosition,
                                    wx.DefaultSize, wx.LC_REPORT)
        bSizer16.Add(self.udefs_lc, 1, wx.ALL | wx.EXPAND, 5)

        bSizer18 = wx.BoxSizer(wx.HORIZONTAL)

        self.cancel_btn = wx.Button(self, wx.ID_ANY, u"Cancel",
                                    wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer18.Add(self.cancel_btn, 0, wx.ALL, 5)

        self.ok_btn = wx.Button(self, wx.ID_ANY, u"OK", wx.DefaultPosition,
                                wx.DefaultSize, 0)
        bSizer18.Add(self.ok_btn, 0, wx.ALL, 5)

        bSizer16.Add(bSizer18, 0, wx.ALIGN_CENTER, 5)

        self.SetSizer(bSizer16)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.path_btn.Bind(wx.EVT_BUTTON, self.path_btnOnButtonClick)
        self.reload_btn.Bind(wx.EVT_BUTTON, self.reload_btnOnButtonClick)
        self.udefs_lc.Bind(wx.EVT_LIST_ITEM_SELECTED,
                           self.udefs_lcOnListItemSelected)
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.cancel_btnOnButtonClick)
        self.ok_btn.Bind(wx.EVT_BUTTON, self.ok_btnOnButtonClick)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def path_btnOnButtonClick(self, event):
        event.Skip()

    def reload_btnOnButtonClick(self, event):
        event.Skip()

    def udefs_lcOnListItemSelected(self, event):
        event.Skip()

    def cancel_btnOnButtonClick(self, event):
        event.Skip()

    def ok_btnOnButtonClick(self, event):
        event.Skip()
