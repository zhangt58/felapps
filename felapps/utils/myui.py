# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Jul 11 2016)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
from . import resutils
from . import funutils

###########################################################################
## Class PlotFrame
###########################################################################


class PlotFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self,
                          parent,
                          id=wx.ID_ANY,
                          title=wx.EmptyString,
                          pos=wx.DefaultPosition,
                          size=wx.Size(1024, 768),
                          style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        vbox_m = wx.BoxSizer(wx.VERTICAL)

        self.m_splitter = wx.SplitterWindow(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D)
        self.m_splitter.SetSashGravity(0.7)
        self.m_splitter.Bind(wx.EVT_IDLE, self.m_splitterOnIdle)

        self.splitter_left = wx.Panel(self.m_splitter, wx.ID_ANY,
                                      wx.DefaultPosition, wx.DefaultSize,
                                      wx.TAB_TRAVERSAL)
        vbox_left = wx.BoxSizer(wx.VERTICAL)

        hbox_ctrl_t = wx.BoxSizer(wx.HORIZONTAL)

        self.imhide_tgbtn = wx.ToggleButton(self.splitter_left, wx.ID_ANY,
                                            u"Hide Image", wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        hbox_ctrl_t.Add(self.imhide_tgbtn, 0, wx.ALIGN_CENTER_VERTICAL |
                        wx.ALL, 5)

        self.inc_font_btn = wx.BitmapButton(self.splitter_left, wx.ID_ANY,
                                            wx.NullBitmap, wx.DefaultPosition,
                                            wx.DefaultSize, wx.BU_AUTODRAW)
        self.inc_font_btn.SetBitmap(resutils.incrfsicon.GetBitmap())
        #self.inc_font_btn.Bind(wx.EVT_BUTTON, self.onIncFontSize)
        hbox_ctrl_t.Add(self.inc_font_btn, 0, wx.ALIGN_CENTER_VERTICAL |
                        wx.ALL, 5)

        self.dec_font_btn = wx.BitmapButton(self.splitter_left, wx.ID_ANY,
                                            wx.NullBitmap, wx.DefaultPosition,
                                            wx.DefaultSize, wx.BU_AUTODRAW)
        self.dec_font_btn.SetBitmap(resutils.decrfsicon.GetBitmap())
        #self.dec_font_btn.Bind(wx.EVT_BUTTON, self.onDecFontSize)
        hbox_ctrl_t.Add(self.dec_font_btn, 0, wx.ALIGN_CENTER_VERTICAL |
                        wx.ALL, 5)

        self.ll_origin = wx.RadioButton(self.splitter_left, wx.ID_ANY, u"SW",
                                        wx.DefaultPosition, wx.DefaultSize, 0)
        hbox_ctrl_t.Add(self.ll_origin, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                        5)

        self.ul_origin = wx.RadioButton(self.splitter_left, wx.ID_ANY, u"NW",
                                        wx.DefaultPosition, wx.DefaultSize, 0)
        hbox_ctrl_t.Add(self.ul_origin, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                        5)

        self.ur_origin = wx.RadioButton(self.splitter_left, wx.ID_ANY, u"NE",
                                        wx.DefaultPosition, wx.DefaultSize, 0)
        hbox_ctrl_t.Add(self.ur_origin, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                        5)

        self.lr_origin = wx.RadioButton(self.splitter_left, wx.ID_ANY, u"SE",
                                        wx.DefaultPosition, wx.DefaultSize, 0)
        hbox_ctrl_t.Add(self.lr_origin, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                        5)

        self.grid_ckb = wx.CheckBox(self.splitter_left, wx.ID_ANY, u"grid",
                                    wx.DefaultPosition, wx.DefaultSize, 0)
        hbox_ctrl_t.Add(self.grid_ckb, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.gridc_btn = wx.BitmapButton(self.splitter_left, wx.ID_ANY,
                                         wx.NullBitmap, wx.DefaultPosition,
                                         wx.DefaultSize, wx.BU_AUTODRAW)
        w, h = 16, 16
        k_bmp = wx.EmptyBitmap(w, h)
        k_img = wx.ImageFromBitmap(k_bmp)
        k_img.SetRGBRect(wx.Rect(0, 0, w, h), 0, 0, 0)
        self.gridc_btn.SetBitmap(wx.BitmapFromImage(k_img))
        hbox_ctrl_t.Add(self.gridc_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                        5)

        self.mticks_ckb = wx.CheckBox(self.splitter_left, wx.ID_ANY, u"mticks",
                                      wx.DefaultPosition, wx.DefaultSize, 0)
        hbox_ctrl_t.Add(self.mticks_ckb, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                        5)

        vbox_left.Add(hbox_ctrl_t, 0, wx.EXPAND, 2)

        self.plotpanel = funutils.AnalysisPlotPanel(self.splitter_left,
                                                    toolbar=True)
        vbox_left.Add(self.plotpanel, 1, wx.ALL | wx.EXPAND, 2)

        hbox_ctrl_b = wx.BoxSizer(wx.HORIZONTAL)

        self.mark_st = wx.StaticText(self.splitter_left, wx.ID_ANY,
                                     u"Pos Markers:", wx.DefaultPosition,
                                     wx.DefaultSize, 0)
        self.mark_st.Wrap(-1)
        hbox_ctrl_b.Add(self.mark_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.pos1_st = wx.StaticText(self.splitter_left, wx.ID_ANY, u"#1",
                                     wx.DefaultPosition, wx.DefaultSize, 0)
        self.pos1_st.Wrap(-1)
        hbox_ctrl_b.Add(self.pos1_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.mkc1_btn = wx.BitmapButton(self.splitter_left, wx.ID_ANY,
                                        wx.NullBitmap, wx.DefaultPosition,
                                        wx.DefaultSize, wx.BU_AUTODRAW)
        w, h = 16, 16
        k_bmp = wx.EmptyBitmap(w, h)
        k_img = wx.ImageFromBitmap(k_bmp)
        k_img.SetRGBRect(wx.Rect(0, 0, w, h), 255, 0, 0)
        self.mkc1_btn.SetBitmap(wx.BitmapFromImage(k_img))
        hbox_ctrl_b.Add(self.mkc1_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.pos2_st = wx.StaticText(self.splitter_left, wx.ID_ANY, u"#2",
                                     wx.DefaultPosition, wx.DefaultSize, 0)
        self.pos2_st.Wrap(-1)
        hbox_ctrl_b.Add(self.pos2_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.mkc2_btn = wx.BitmapButton(self.splitter_left, wx.ID_ANY,
                                        wx.NullBitmap, wx.DefaultPosition,
                                        wx.DefaultSize, wx.BU_AUTODRAW)
        w, h = 16, 16
        k_bmp = wx.EmptyBitmap(w, h)
        k_img = wx.ImageFromBitmap(k_bmp)
        k_img.SetRGBRect(wx.Rect(0, 0, w, h), 240, 230, 140)
        self.mkc2_btn.SetBitmap(wx.BitmapFromImage(k_img))
        hbox_ctrl_b.Add(self.mkc2_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.pcc_st = wx.StaticText(self.splitter_left, wx.ID_ANY, u"M Color",
                                    wx.DefaultPosition, wx.DefaultSize, 0)
        self.pcc_st.Wrap(-1)
        hbox_ctrl_b.Add(self.pcc_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.pcc_btn = wx.BitmapButton(self.splitter_left, wx.ID_ANY,
                                       wx.NullBitmap, wx.DefaultPosition,
                                       wx.DefaultSize, wx.BU_AUTODRAW)
        w, h = 16, 16
        k_bmp = wx.EmptyBitmap(w, h)
        k_img = wx.ImageFromBitmap(k_bmp)
        k_img.SetRGBRect(wx.Rect(0, 0, w, h), 0, 0, 0)
        self.pcc_btn.SetBitmap(wx.BitmapFromImage(k_img))
        hbox_ctrl_b.Add(self.pcc_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        fgSizer_info = wx.FlexGridSizer(0, 4, 0, 0)
        fgSizer_info.AddGrowableCol(1)
        fgSizer_info.AddGrowableCol(3)
        fgSizer_info.SetFlexibleDirection(wx.BOTH)
        fgSizer_info.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m1_st = wx.StaticText(self.splitter_left, wx.ID_ANY, u"M1:",
                                   wx.DefaultPosition, wx.Size(-1, 12), 0)
        self.m1_st.Wrap(-1)
        self.m1_st.SetFont(wx.Font(8, 70, 90, 90, False, "Monospace"))

        fgSizer_info.Add(self.m1_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        self.m1_pos_st = wx.StaticText(self.splitter_left, wx.ID_ANY,
                                       wx.EmptyString, wx.DefaultPosition,
                                       wx.DefaultSize, 0)
        self.m1_pos_st.Wrap(-1)
        self.m1_pos_st.SetFont(wx.Font(8, 70, 90, 90, False, "Monospace"))

        fgSizer_info.Add(self.m1_pos_st, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL |
                         wx.EXPAND, 0)

        self.delx_st = wx.StaticText(self.splitter_left, wx.ID_ANY, u"\N{GREEK CAPITAL LETTER DELTA}x:",
                                     wx.DefaultPosition, wx.DefaultSize, 0)
        self.delx_st.Wrap(-1)
        self.delx_st.SetFont(wx.Font(8, 70, 90, 90, False, "Monospace"))

        fgSizer_info.Add(self.delx_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        self.delx_val_st = wx.StaticText(self.splitter_left, wx.ID_ANY,
                                         wx.EmptyString, wx.DefaultPosition,
                                         wx.DefaultSize, 0)
        self.delx_val_st.Wrap(-1)
        self.delx_val_st.SetFont(wx.Font(8, 70, 90, 90, False, "Monospace"))

        fgSizer_info.Add(self.delx_val_st, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL
                         | wx.EXPAND, 0)

        self.m2_st = wx.StaticText(self.splitter_left, wx.ID_ANY, u"M2:",
                                   wx.DefaultPosition, wx.DefaultSize, 0)
        self.m2_st.Wrap(-1)
        self.m2_st.SetFont(wx.Font(8, 70, 90, 90, False, "Monospace"))

        fgSizer_info.Add(self.m2_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        self.m2_pos_st = wx.StaticText(self.splitter_left, wx.ID_ANY,
                                       wx.EmptyString, wx.DefaultPosition,
                                       wx.DefaultSize, 0)
        self.m2_pos_st.Wrap(-1)
        self.m2_pos_st.SetFont(wx.Font(8, 70, 90, 90, False, "Monospace"))

        fgSizer_info.Add(self.m2_pos_st, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL |
                         wx.EXPAND, 0)

        self.dely_st = wx.StaticText(self.splitter_left, wx.ID_ANY, u"\N{GREEK CAPITAL LETTER DELTA}y:",
                                     wx.DefaultPosition, wx.DefaultSize, 0)
        self.dely_st.Wrap(-1)
        self.dely_st.SetFont(wx.Font(8, 70, 90, 90, False, "Monospace"))

        fgSizer_info.Add(self.dely_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        self.dely_val_st = wx.StaticText(self.splitter_left, wx.ID_ANY,
                                         wx.EmptyString, wx.DefaultPosition,
                                         wx.DefaultSize, 0)
        self.dely_val_st.Wrap(-1)
        self.dely_val_st.SetFont(wx.Font(8, 70, 90, 90, False, "Monospace"))

        fgSizer_info.Add(self.dely_val_st, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL
                         | wx.EXPAND, 0)

        hbox_ctrl_b.Add(fgSizer_info, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL |
                        wx.EXPAND, 5)

        vbox_left.Add(hbox_ctrl_b, 0, wx.EXPAND, 2)

        self.splitter_left.SetSizer(vbox_left)
        self.splitter_left.Layout()
        vbox_left.Fit(self.splitter_left)
        self.splitter_right = wx.Panel(self.m_splitter, wx.ID_ANY,
                                       wx.DefaultPosition, wx.DefaultSize,
                                       wx.TAB_TRAVERSAL)
        vbox_right = wx.BoxSizer(wx.VERTICAL)

        self.style_panel = wx.Panel(self.splitter_right, wx.ID_ANY,
                                    wx.DefaultPosition, wx.DefaultSize,
                                    wx.TAB_TRAVERSAL)
        self.style_panel.SetBackgroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWFRAME))

        fgsizer_style = wx.FlexGridSizer(0, 2, 0, 4)
        fgsizer_style.SetFlexibleDirection(wx.BOTH)
        fgsizer_style.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.cmap_st = wx.StaticText(self.style_panel, wx.ID_ANY, u"Color Map",
                                     wx.DefaultPosition, wx.DefaultSize, 0)
        self.cmap_st.Wrap(-1)
        fgsizer_style.Add(self.cmap_st, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                          5)

        cmap_cbChoices = [u"jet"]
        self.cmap_cb = wx.ComboBox(self.style_panel, wx.ID_ANY, wx.EmptyString,
                                   wx.DefaultPosition, wx.Size(130, -1),
                                   cmap_cbChoices, wx.CB_READONLY)
        self.cmap_cb.SetSelection(0)
        fgsizer_style.Add(self.cmap_cb, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                          5)

        self.crange_st = wx.StaticText(self.style_panel, wx.ID_ANY,
                                       u"Color Range", wx.DefaultPosition,
                                       wx.DefaultSize, 0)
        self.crange_st.Wrap(-1)
        fgsizer_style.Add(self.crange_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                          5)

        self.crange_tc = wx.TextCtrl(self.style_panel, wx.ID_ANY,
                                     wx.EmptyString, wx.DefaultPosition,
                                     wx.Size(130, -1), wx.TE_PROCESS_ENTER)
        fgsizer_style.Add(self.crange_tc, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                          5)

        self.lineid_st = wx.StaticText(self.style_panel, wx.ID_ANY,
                                       u"Set Line ID", wx.DefaultPosition,
                                       wx.DefaultSize, 0)
        self.lineid_st.Wrap(-1)
        fgsizer_style.Add(self.lineid_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                          5)

        lineid_choiceChoices = []
        self.lineid_choice = wx.Choice(self.style_panel, wx.ID_ANY,
                                       wx.DefaultPosition, wx.Size(130, -1),
                                       lineid_choiceChoices, 0)
        self.lineid_choice.SetSelection(0)
        fgsizer_style.Add(self.lineid_choice, 0, wx.ALIGN_CENTER_VERTICAL |
                          wx.ALL, 5)

        self.lc_st = wx.StaticText(self.style_panel, wx.ID_ANY, u"Line Color",
                                   wx.DefaultPosition, wx.DefaultSize, 0)
        self.lc_st.Wrap(-1)
        fgsizer_style.Add(self.lc_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        lc_hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.lc_bmp = wx.StaticBitmap(self.style_panel, wx.ID_ANY,
                                      wx.NullBitmap, wx.DefaultPosition,
                                      wx.Size(16, 16), 0)
        lc_hbox.Add(self.lc_bmp, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT |
                    wx.RIGHT, 5)

        self.lc_btn = wx.Button(self.style_panel, wx.ID_ANY, u"Pick Color",
                                wx.DefaultPosition, wx.Size(-1, -1), 0)
        lc_hbox.Add(self.lc_btn, 1, wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM |
                    wx.RIGHT | wx.TOP, 5)

        fgsizer_style.Add(lc_hbox, 1, wx.EXPAND, 5)

        self.ls_st = wx.StaticText(self.style_panel, wx.ID_ANY, u"Line Style",
                                   wx.DefaultPosition, wx.DefaultSize, 0)
        self.ls_st.Wrap(-1)
        fgsizer_style.Add(self.ls_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        ls_cbChoices = [u"solid"]
        self.ls_cb = wx.ComboBox(self.style_panel, wx.ID_ANY, wx.EmptyString,
                                 wx.DefaultPosition, wx.Size(130, -1),
                                 ls_cbChoices, wx.CB_READONLY)
        self.ls_cb.SetSelection(0)
        fgsizer_style.Add(self.ls_cb, 0, wx.ALL, 5)

        self.lw_st = wx.StaticText(self.style_panel, wx.ID_ANY, u"Line Width",
                                   wx.DefaultPosition, wx.DefaultSize, 0)
        self.lw_st.Wrap(-1)
        fgsizer_style.Add(self.lw_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.lw_tc = wx.TextCtrl(self.style_panel, wx.ID_ANY, u"1",
                                 wx.DefaultPosition, wx.Size(130, -1),
                                 wx.TE_PROCESS_ENTER)
        fgsizer_style.Add(self.lw_tc, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.mk_st = wx.StaticText(self.style_panel, wx.ID_ANY,
                                   u"Marker Style", wx.DefaultPosition,
                                   wx.DefaultSize, 0)
        self.mk_st.Wrap(-1)
        fgsizer_style.Add(self.mk_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        mk_cbChoices = [u"circle"]
        self.mk_cb = wx.ComboBox(self.style_panel, wx.ID_ANY, wx.EmptyString,
                                 wx.DefaultPosition, wx.Size(130, -1),
                                 mk_cbChoices, wx.CB_READONLY)
        self.mk_cb.SetSelection(0)
        fgsizer_style.Add(self.mk_cb, 0, wx.ALL, 5)

        self.ms_st = wx.StaticText(self.style_panel, wx.ID_ANY, u"Marker Size",
                                   wx.DefaultPosition, wx.DefaultSize, 0)
        self.ms_st.Wrap(-1)
        fgsizer_style.Add(self.ms_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.ms_tc = wx.TextCtrl(self.style_panel, wx.ID_ANY, u"5",
                                 wx.DefaultPosition, wx.Size(130, -1),
                                 wx.TE_PROCESS_ENTER)
        fgsizer_style.Add(self.ms_tc, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.mec_st = wx.StaticText(self.style_panel, wx.ID_ANY,
                                    u"MK EdgeColor", wx.DefaultPosition,
                                    wx.DefaultSize, 0)
        self.mec_st.Wrap(-1)
        fgsizer_style.Add(self.mec_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        mec_hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.mec_bmp = wx.StaticBitmap(self.style_panel, wx.ID_ANY,
                                       wx.NullBitmap, wx.DefaultPosition,
                                       wx.Size(16, 16), 0)
        mec_hbox.Add(self.mec_bmp, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT |
                     wx.RIGHT, 5)

        self.mec_btn = wx.Button(self.style_panel, wx.ID_ANY, u"Pick Color",
                                 wx.DefaultPosition, wx.Size(-1, -1), 0)
        mec_hbox.Add(self.mec_btn, 1, wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM |
                     wx.RIGHT | wx.TOP, 5)

        fgsizer_style.Add(mec_hbox, 1, wx.EXPAND, 5)

        self.mfc_st = wx.StaticText(self.style_panel, wx.ID_ANY,
                                    u"MK FaceColor", wx.DefaultPosition,
                                    wx.DefaultSize, 0)
        self.mfc_st.Wrap(-1)
        fgsizer_style.Add(self.mfc_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        mfc_hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.mfc_bmp = wx.StaticBitmap(self.style_panel, wx.ID_ANY,
                                       wx.NullBitmap, wx.DefaultPosition,
                                       wx.Size(16, 16), 0)
        mfc_hbox.Add(self.mfc_bmp, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT |
                     wx.RIGHT, 5)

        self.mfc_btn = wx.Button(self.style_panel, wx.ID_ANY, u"Pick Color",
                                 wx.DefaultPosition, wx.Size(-1, -1), 0)
        mfc_hbox.Add(self.mfc_btn, 1, wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM |
                     wx.RIGHT | wx.TOP, 5)

        fgsizer_style.Add(mfc_hbox, 1, wx.EXPAND, 5)

        self.style_panel.SetSizer(fgsizer_style)
        self.style_panel.Layout()
        fgsizer_style.Fit(self.style_panel)
        vbox_right.Add(self.style_panel, 1, wx.EXPAND | wx.LEFT | wx.RIGHT |
                       wx.TOP, 5)

        self.m_staticline1 = wx.StaticLine(self.splitter_right, wx.ID_ANY,
                                           wx.DefaultPosition, wx.DefaultSize,
                                           wx.LI_HORIZONTAL)
        vbox_right.Add(self.m_staticline1, 0, wx.ALL | wx.EXPAND, 5)

        self.result_panel = wx.Panel(self.splitter_right, wx.ID_ANY,
                                     wx.DefaultPosition, wx.DefaultSize,
                                     wx.TAB_TRAVERSAL)
        self.result_panel.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOW))
        self.result_panel.SetBackgroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWFRAME))

        vbox_res = wx.BoxSizer(wx.VERTICAL)

        self.output_st = wx.StaticText(self.result_panel, wx.ID_ANY,
                                       u"Fitting Output:", wx.DefaultPosition,
                                       wx.DefaultSize, 0)
        self.output_st.Wrap(-1)
        self.output_st.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), 70, 90,
                                       90, False, wx.EmptyString))
        self.output_st.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))

        vbox_res.Add(self.output_st, 0, wx.ALL, 5)

        self.output_tc = wx.TextCtrl(
            self.result_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
            wx.DefaultSize, wx.TE_MULTILINE | wx.TE_READONLY)
        self.output_tc.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), 70, 90,
                                       90, False, "Monospace"))
        self.output_tc.SetBackgroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWFRAME))

        vbox_res.Add(self.output_tc, 1, wx.ALL | wx.EXPAND, 1)

        self.result_panel.SetSizer(vbox_res)
        self.result_panel.Layout()
        vbox_res.Fit(self.result_panel)
        vbox_right.Add(self.result_panel, 1, wx.BOTTOM | wx.EXPAND | wx.LEFT |
                       wx.RIGHT, 5)

        hbox_ctrl1 = wx.BoxSizer(wx.HORIZONTAL)

        self.exit_btn = wx.Button(self.splitter_right, wx.ID_ANY, u"E&xit",
                                  wx.DefaultPosition, wx.DefaultSize, 0)
        hbox_ctrl1.Add(self.exit_btn, 0, 0, 5)

        vbox_right.Add(hbox_ctrl1, 0, wx.ALIGN_RIGHT | wx.RIGHT, 5)

        self.splitter_right.SetSizer(vbox_right)
        self.splitter_right.Layout()
        vbox_right.Fit(self.splitter_right)
        self.m_splitter.SplitVertically(self.splitter_left,
                                        self.splitter_right, 700)
        vbox_m.Add(self.m_splitter, 1, wx.EXPAND, 5)

        self.SetSizer(vbox_m)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.imhide_tgbtn.Bind(wx.EVT_TOGGLEBUTTON,
                               self.imhide_tgbtnOnToggleButton)
        self.ll_origin.Bind(wx.EVT_RADIOBUTTON, self.ll_originOnRadioButton)
        self.ul_origin.Bind(wx.EVT_RADIOBUTTON, self.ul_originOnRadioButton)
        self.ur_origin.Bind(wx.EVT_RADIOBUTTON, self.ur_originOnRadioButton)
        self.lr_origin.Bind(wx.EVT_RADIOBUTTON, self.lr_originOnRadioButton)
        self.grid_ckb.Bind(wx.EVT_CHECKBOX, self.grid_ckbOnCheckBox)
        self.mticks_ckb.Bind(wx.EVT_CHECKBOX, self.mticks_ckbOnCheckBox)
        self.cmap_cb.Bind(wx.EVT_COMBOBOX, self.cmap_cbOnCombobox)
        self.crange_tc.Bind(wx.EVT_TEXT_ENTER, self.crange_tcOnTextEnter)
        self.lineid_choice.Bind(wx.EVT_CHOICE, self.lineid_choiceOnChoice)
        self.lc_btn.Bind(wx.EVT_BUTTON, self.lc_btnOnButtonClick)
        self.ls_cb.Bind(wx.EVT_COMBOBOX, self.ls_cbOnCombobox)
        self.lw_tc.Bind(wx.EVT_TEXT_ENTER, self.lw_tcOnTextEnter)
        self.mk_cb.Bind(wx.EVT_COMBOBOX, self.mk_cbOnCombobox)
        self.ms_tc.Bind(wx.EVT_TEXT_ENTER, self.ms_tcOnTextEnter)
        self.mec_btn.Bind(wx.EVT_BUTTON, self.mec_btnOnButtonClick)
        self.mfc_btn.Bind(wx.EVT_BUTTON, self.mfc_btnOnButtonClick)
        self.exit_btn.Bind(wx.EVT_BUTTON, self.exit_btnOnButtonClick)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def imhide_tgbtnOnToggleButton(self, event):
        event.Skip()

    def ll_originOnRadioButton(self, event):
        event.Skip()

    def ul_originOnRadioButton(self, event):
        event.Skip()

    def ur_originOnRadioButton(self, event):
        event.Skip()

    def lr_originOnRadioButton(self, event):
        event.Skip()

    def grid_ckbOnCheckBox(self, event):
        event.Skip()

    def mticks_ckbOnCheckBox(self, event):
        event.Skip()

    def cmap_cbOnCombobox(self, event):
        event.Skip()

    def crange_tcOnTextEnter(self, event):
        event.Skip()

    def lineid_choiceOnChoice(self, event):
        event.Skip()

    def lc_btnOnButtonClick(self, event):
        event.Skip()

    def ls_cbOnCombobox(self, event):
        event.Skip()

    def lw_tcOnTextEnter(self, event):
        event.Skip()

    def mk_cbOnCombobox(self, event):
        event.Skip()

    def ms_tcOnTextEnter(self, event):
        event.Skip()

    def mec_btnOnButtonClick(self, event):
        event.Skip()

    def mfc_btnOnButtonClick(self, event):
        event.Skip()

    def exit_btnOnButtonClick(self, event):
        event.Skip()

    def m_splitterOnIdle(self, event):
        self.m_splitter.SetSashPosition(700)
        self.m_splitter.Unbind(wx.EVT_IDLE)
