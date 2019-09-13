import webbrowser
from bisect import bisect

import pyperclip
import wx

import add_column
import column
import icon
import option
import player

__version__ = '1.0.0'
TIP0 = 'How to use:'
TIP1 = '1. Execute "status" command in TF2 developer console,'
TIP2 = '2. Copy the user list part,'
TIP3 = '3. Click "Load from clipboard" button.'


class frameMain(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(
            self, parent, id=wx.ID_ANY, title='TF2 Status Enhancer', pos=wx.DefaultPosition,
            size=wx.Size(720, 540), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL
        )

        self.SetSizeHints(wx.Size(640, 480), wx.DefaultSize)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))

        self.SizerMain = wx.BoxSizer(wx.VERTICAL)
        self.SizerTip = wx.BoxSizer(wx.VERTICAL)
        self.SizerTop = wx.BoxSizer(wx.HORIZONTAL)
        self.SizerBottom = wx.BoxSizer(wx.HORIZONTAL)

        self.StaticTip0 = wx.StaticText(self, wx.ID_ANY, TIP0, wx.DefaultPosition, wx.DefaultSize, 0)
        self.StaticTip1 = wx.StaticText(self, wx.ID_ANY, TIP1, wx.DefaultPosition, wx.DefaultSize, 0)
        self.StaticTip2 = wx.StaticText(self, wx.ID_ANY, TIP2, wx.DefaultPosition, wx.DefaultSize, 0)
        self.StaticTip3 = wx.StaticText(self, wx.ID_ANY, TIP3, wx.DefaultPosition, wx.DefaultSize, 0)
        self.SizerTip.Add(self.StaticTip0, 1, wx.ALL | wx.EXPAND, 0)
        self.SizerTip.Add(self.StaticTip1, 1, wx.ALL | wx.EXPAND, 0)
        self.SizerTip.Add(self.StaticTip2, 1, wx.ALL | wx.EXPAND, 0)
        self.SizerTip.Add(self.StaticTip3, 1, wx.ALL | wx.EXPAND, 0)

        self.ListCtrl = wx.ListCtrl(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES)
        self.SizerTop.Add(self.ListCtrl, 1, wx.ALL | wx.EXPAND, 5)

        self.ButtonLoad = wx.Button(self, wx.ID_ANY, '&Load from clipboard', wx.DefaultPosition, wx.Size(-1, 35), 0)
        self.ButtonClear = wx.Button(self, wx.ID_ANY, '&Clear', wx.DefaultPosition, wx.Size(-1, 35), 0)
        self.SizerBottom.Add(self.ButtonLoad, 3, wx.ALIGN_CENTER | wx.LEFT | wx.EXPAND, 5)
        self.SizerBottom.Add(self.ButtonClear, 2, wx.ALIGN_CENTER | wx.RIGHT | wx.EXPAND, 5)

        self.SizerMain.Add(self.SizerTip, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 5)
        self.SizerMain.Add(self.SizerTop, 1, wx.EXPAND, 5)
        self.SizerMain.Add(self.SizerBottom, 0, wx.BOTTOM | wx.EXPAND, 5)

        self.SetSizer(self.SizerMain)
        self.Layout()
        self.Centre(wx.BOTH)

        self.StatusMenu = wx.Menu()
        self.StatusMenu.Append(0, '&Copy')
        self.StatusMenu.Append(1, 'Copy vote&kick command')

        self.ColMenu = wx.Menu()

        self.ButtonLoad.Bind(wx.EVT_BUTTON, self.OnLoad)
        self.ButtonClear.Bind(wx.EVT_BUTTON, self.OnClear)
        self.ListCtrl.Bind(wx.EVT_LEFT_DCLICK, self.OnListClick)
        self.ListCtrl.Bind(wx.EVT_RIGHT_DOWN, self.OnListRightClick)
        self.ListCtrl.Bind(wx.EVT_LIST_COL_RIGHT_CLICK, self.OnColRightClick)
        self.StatusMenu.Bind(wx.EVT_MENU, self.OnStatusMenu)
        self.ColMenu.Bind(wx.EVT_MENU, self.OnColMenu)

        self.AccTable = wx.AcceleratorTable([
            (wx.ACCEL_CTRL, ord('V'), self.ButtonLoad.GetId())
        ])
        self.SetAcceleratorTable(self.AccTable)

        self.options = option.load_options()

        self.players = list()
        self.columns = column.ColumnManager()
        self.reload_columns()

    def OnLoad(self, event):
        clip = pyperclip.paste()
        players = player.parse_status(clip)
        if players:
            self.players = players
            self.reload_players()

    def OnClear(self, event):
        self.players = list()
        self.reload_players()

    def OnListClick(self, event):
        lc = self.ListCtrl
        x, y = event.GetPosition()
        row, col = self.pos_to_cell(x, y)
        if row == -1 or col == -1:
            return

        lc.SetFocus()
        lc.Focus(row)
        lc.Select(row)

        if self.columns.is_link(col):
            webbrowser.open(self.real_data[row][col], new=2, autoraise=False)

    def OnListRightClick(self, event):
        lc = self.ListCtrl

        x, y = event.GetPosition()
        row, col = self.pos_to_cell(x, y)
        if row == -1 or col == -1:
            return

        lc.SetFocus()
        lc.Focus(row)
        lc.Select(row)

        self.StatusMenu.attached_row = row
        self.StatusMenu.attached_col = col
        if self.columns.is_link(col):
            self.StatusMenu.SetLabel(0, '&Copy URL')
        else:
            self.StatusMenu.SetLabel(0, '&Copy')
        lc.PopupMenu(self.StatusMenu)

    def OnColRightClick(self, event):
        lc = self.ListCtrl
        col = event.GetColumn()
        self.ColMenu.attached_col = col
        self.build_col_menu(col)
        lc.PopupMenu(self.ColMenu)

    def OnStatusMenu(self, event):
        row, col = self.StatusMenu.attached_row, self.StatusMenu.attached_col
        sel = event.GetId()
        if sel == 0:
            pyperclip.copy(self.real_data[row][col])
        if sel == 1:
            pyperclip.copy(self.players[self.StatusMenu.attached_row].kick_cmd())

    def OnColMenu(self, event):
        opt = self.options['columns']
        col = self.ColMenu.attached_col
        sel = event.GetId()
        if sel == 0:
            opt['steam64'] = not opt['steam64']
        if sel == 1:
            opt['steam2'] = not opt['steam2']
        if sel == 2:
            opt['steam3'] = not opt['steam3']
        if sel == 3:
            opt['connected'] = not opt['connected']
        if sel == 4:
            opt['profile'] = not opt['profile']
        if sel == 5:
            dialog = add_column.dialogCustom(self)
            dialog.SetIcon(self.app_icon)
            ret = dialog.ShowModal()
            if ret == wx.OK:
                opt['custom'].append(dialog.get_custom())
                dialog.Destroy()
            else:
                dialog.Destroy()
                return
        if sel == 6:
            idx = self.columns.custom_idx(col)
            if idx < 0:
                return
            opt['custom'].pop(idx)
        self.reload_columns()

    def reload_columns(self):
        lc = self.ListCtrl
        col_map = {
            'steam64': column.ColumnSteam64(),
            'steam2': column.ColumnSteam2(),
            'steam3': column.ColumnSteam3(),
            'connected': column.ColumnConnected(),
            'profile': column.ColumnProfile()
        }
        self.columns.clear()
        col_objs = [
            column.ColumnUserID(),
            column.ColumnName()
        ]
        for k, v in col_map.items():
            if self.options['columns'][k]:
                col_objs.append(v)
        for i, custom in enumerate(self.options['columns']['custom']):
            col_objs.append(column.CustomColumn(i, custom['name'], custom['format']))
        self.columns.register(*col_objs)
        lc.ClearAll()
        for i in range(self.columns.count):
            col = self.columns.columns[i]
            lc.InsertColumn(i, col.name)
        option.save_options(self.options)
        self.reload_players()

    def reload_players(self):
        lc = self.ListCtrl
        lc.DeleteAllItems()
        self.real_data = list()
        for i, p in enumerate(self.players):
            items = self.columns.get_item(p)
            self.real_data.append(items)
            lc.Append(self.columns.filter_link_items(items))
        self.adjust()

    def adjust(self):
        lc = self.ListCtrl
        col_count = lc.GetColumnCount()
        if col_count <= 0:
            return
        for col in range(col_count):
            lc.SetColumnWidth(col, wx.LIST_AUTOSIZE_USEHEADER)

    def pos_to_cell(self, x, y):
        lc = self.ListCtrl
        row, _ = lc.HitTest((x, y))
        col_locs = [0]
        loc = 0
        for n in range(lc.GetColumnCount()):
            loc = loc + lc.GetColumnWidth(lc.GetColumnIndexFromOrder(n))
            col_locs.append(loc)
        col = bisect(col_locs, x + lc.GetScrollPos(wx.HORIZONTAL)) - 1
        if row < 0 or col < 0:
            return -1, -1
        col = lc.GetColumnIndexFromOrder(col)
        return row, col

    def build_col_menu(self, col):
        menu = self.ColMenu
        items = menu.GetMenuItems()
        for i in items:
            menu.Remove(i.GetId())
        menu.AppendCheckItem(0, 'Steam64')
        menu.AppendCheckItem(1, 'Steam2')
        menu.AppendCheckItem(2, 'Steam3')
        menu.AppendCheckItem(3, 'Connected')
        menu.AppendCheckItem(4, 'Profile')
        menu.Append(wx.ID_SEPARATOR)
        menu.Append(5, '&Add custom column...')
        if self.columns.is_custom(col):
            menu.Append(wx.ID_SEPARATOR)
            menu.Append(6, '&Remove column')
        opt = self.options['columns']
        if opt['steam64']:
            menu.FindItemById(0).Check()
        if opt['steam2']:
            menu.FindItemById(1).Check()
        if opt['steam3']:
            menu.FindItemById(2).Check()
        if opt['connected']:
            menu.FindItemById(3).Check()
        if opt['profile']:
            menu.FindItemById(4).Check()


if __name__ == '__main__':
    app = wx.App(False)
    frame = frameMain(None)
    frame.app_icon = wx.Icon()
    frame.app_icon.CopyFromBitmap(icon.icon.GetBitmap())
    frame.SetIcon(frame.app_icon)
    frame.SetTitle('{} {}'.format(frame.GetTitle(), __version__))
    frame.Show(True)
    app.MainLoop()
