import wx
import pcbnew


class PanelizerDialog(wx.Dialog):
    def __init__(self, parent=None):
        super(PanelizerDialog, self).__init__(
            parent,
            title="PCB Panelizer",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.Bind(wx.EVT_CLOSE, self.on_close)

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        grid = wx.FlexGridSizer(rows=5, cols=2, vgap=10, hgap=10)

        # --- Array size ---
        grid.Add(wx.StaticText(panel, label="Columns (X):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_cols = wx.TextCtrl(panel, value="2")
        grid.Add(self.txt_cols, 1, wx.EXPAND)

        grid.Add(wx.StaticText(panel, label="Rows (Y):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_rows = wx.TextCtrl(panel, value="2")
        grid.Add(self.txt_rows, 1, wx.EXPAND)

        # --- Method ---
        grid.Add(wx.StaticText(panel, label="Method:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.cb_method = wx.Choice(panel, choices=["V-Cut", "Mousebites"])
        self.cb_method.SetSelection(0)
        grid.Add(self.cb_method, 1, wx.EXPAND)

        # --- Gap / mousebite size ---
        grid.Add(wx.StaticText(panel, label="Gap / Mousebite (mm):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.cb_gap = wx.Choice(panel, choices=["1.0", "1.5", "2.0", "2.5", "5.0"])
        self.cb_gap.SetSelection(2)  # default 2.0 mm
        grid.Add(self.cb_gap, 1, wx.EXPAND)

        # --- Panel size ---
        grid.Add(wx.StaticText(panel, label="Panel Width (mm):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_width = wx.TextCtrl(panel, value="100")
        grid.Add(self.txt_width, 1, wx.EXPAND)

        grid.Add(wx.StaticText(panel, label="Panel Height (mm):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_height = wx.TextCtrl(panel, value="100")
        grid.Add(self.txt_height, 1, wx.EXPAND)

        vbox.Add(grid, 1, wx.ALL | wx.EXPAND, 15)



        panel.SetSizer(vbox)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(panel, 1, wx.EXPAND)
        
        btns = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        main_sizer.Add(btns, 0, wx.ALL | wx.CENTER, 10)
        
        self.SetSizer(main_sizer)
        main_sizer.Fit(self)
        self.Layout()
        self.Center()

    def on_close(self, event):
        self.EndModal(wx.ID_CANCEL)

    def GetSettings(self):
        try:
            return {
                "cols": int(self.txt_cols.GetValue()),
                "rows": int(self.txt_rows.GetValue()),
                "gap_mm": float(self.cb_gap.GetString(self.cb_gap.GetSelection())),
                "method": self.cb_method.GetString(self.cb_method.GetSelection()),
                "panel_w_mm": float(self.txt_width.GetValue()),
                "panel_h_mm": float(self.txt_height.GetValue()),
            }
        except ValueError:
            return None
