import wx

TEXT = 'https://steamcommunity.com/profile/${steam64}'
TIP0 = 'You can use following variables in format string:'
TIP1 = '${userid}, ${name}, ${steam64}, ${steam2}, ${steam3}, ${connected}'
TIP2 = 'They will be replaced by player\'s info.'
TIP3 = 'Example: https://steamcommunity.com/profile/${steam64}'


class dialogCustom(wx.Dialog):

    def __init__(self, parent):
        wx.Frame.__init__(
            self, parent, id=wx.ID_ANY, title='Add custom column', pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE | wx.TAB_TRAVERSAL
        )
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))

        self.SizerMain = wx.BoxSizer(wx.VERTICAL)
        self.SizerTip = wx.BoxSizer(wx.VERTICAL)
        self.SizerButton = wx.BoxSizer(wx.HORIZONTAL)

        self.StaticTip0 = wx.StaticText(self, wx.ID_ANY, TIP0, wx.DefaultPosition, wx.DefaultSize, 0)
        self.StaticTip1 = wx.StaticText(self, wx.ID_ANY, TIP1, wx.DefaultPosition, wx.DefaultSize, 0)
        self.StaticTip2 = wx.StaticText(self, wx.ID_ANY, TIP2, wx.DefaultPosition, wx.DefaultSize, 0)
        self.StaticTip3 = wx.StaticText(self, wx.ID_ANY, TIP3, wx.DefaultPosition, wx.DefaultSize, 0)
        self.SizerTip.Add(self.StaticTip0, 1, wx.ALL | wx.EXPAND, 0)
        self.SizerTip.Add(self.StaticTip1, 1, wx.ALL | wx.EXPAND, 0)
        self.SizerTip.Add(self.StaticTip2, 1, wx.ALL | wx.EXPAND, 0)
        self.SizerTip.Add(self.StaticTip3, 1, wx.ALL | wx.EXPAND, 0)

        self.StaticName = wx.StaticText(self, wx.ID_ANY, 'Column name:', wx.DefaultPosition, wx.DefaultSize, 0)
        self.StaticFmt = wx.StaticText(self, wx.ID_ANY, 'Format string:', wx.DefaultPosition, wx.DefaultSize, 0)

        self.EditName = wx.TextCtrl(self, wx.ID_OK, '', wx.DefaultPosition, wx.DefaultSize, 0)
        self.EditFmt = wx.TextCtrl(self, wx.ID_CANCEL, '', wx.DefaultPosition, wx.DefaultSize, 0)

        self.ButtonYes = wx.Button(self, wx.ID_ANY, '&Save', wx.DefaultPosition, wx.DefaultSize, 0)
        self.ButtonNo = wx.Button(self, wx.ID_ANY, '&Cancel', wx.DefaultPosition, wx.DefaultSize, 0)

        self.ButtonYes.SetDefault()

        self.SizerButton.Add((0, 0), 1, wx.EXPAND, 5)
        self.SizerButton.Add(self.ButtonYes, 0, wx.EXPAND, 5)
        self.SizerButton.Add(self.ButtonNo, 0, wx.EXPAND, 5)

        self.SizerMain.Add(self.StaticName, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 5)
        self.SizerMain.Add(self.EditName, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 5)
        self.SizerMain.Add(self.StaticFmt, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 5)
        self.SizerMain.Add(self.EditFmt, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 5)
        self.SizerMain.Add(self.SizerTip, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 5)
        self.SizerMain.Add((0, 0), 1, wx.EXPAND, 5)
        self.SizerMain.Add(self.SizerButton, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 5)

        self.SetSizer(self.SizerMain)
        self.Layout()
        self.Centre(wx.BOTH)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.ButtonYes.Bind(wx.EVT_BUTTON, self.OnSave)
        self.ButtonNo.Bind(wx.EVT_BUTTON, self.OnCancel)

    def OnClose(self, event):
        self.EndModal(wx.CANCEL)

    def OnSave(self, event):
        name = self.EditName.GetLineText(0).strip()
        if not name:
            wx.MessageBox('You must enter a column name!', 'Warning', parent=self)
            return
        self.EndModal(wx.OK)

    def OnCancel(self, event):
        self.EndModal(wx.CANCEL)

    def get_custom(self):
        name = self.EditName.GetLineText(0).strip()
        fmt = self.EditFmt.GetLineText(0).strip()
        return {
            'name': name,
            'format': fmt
        }
