from player import Player
from utils import base36


class Column:

    def content(self, player: Player):
        pass


class ColumnUserID(Column):

    name = 'UserID'

    def content(self, player: Player) -> str:
        return str(player.userid)


class ColumnName(Column):

    name = 'Name'

    def content(self, player: Player) -> str:
        return player.name


class ColumnSteam64(Column):

    name = 'Steam64'

    def content(self, player: Player) -> str:
        return str(player.steamid.as_64)


class ColumnSteam2(Column):

    name = 'Steam2'

    def content(self, player: Player) -> str:
        return player.steamid.as_steam2


class ColumnSteam3(Column):

    name = 'Steam3'

    def content(self, player: Player) -> str:
        return player.steamid.as_steam3


class ColumnConnected(Column):

    name = 'Connected'

    def content(self, player: Player) -> str:
        return player.connected_str


class ColumnProfile(Column):

    name = 'Profile'

    def content(self, player: Player) -> str:
        return player.steamid.community_url


class ColumnProfileShort(Column):

    name = 'Profile'

    def content(self, player: Player) -> str:
        return f'https://steam.pm/{base36(player.steamid.id)}'


class CustomColumn(Column):

    def __init__(self, idx: int, name: str, fmt: str):
        self.idx = idx
        self.name = name
        self.fmt = fmt

    def content(self, player: Player) -> str:
        out = self.fmt
        out = out.replace('${userid}', str(player.userid))
        out = out.replace('${name}', player.name)
        out = out.replace('${steam64}', str(player.steamid.as_64))
        out = out.replace('${steam2}', player.steamid.as_steam2)
        out = out.replace('${steam3}', player.steamid.as_steam3)
        out = out.replace('${connected}', player.connected_str)
        return out


class ColumnManager:

    def __init__(self):
        self.clear()

    def clear(self):
        self.columns = dict()
        self.count = 0
        self.link = dict()

    def register(self, *columns):
        mock_player = Player(1, 'player', '[U:1:111111111]', '11:11')
        for col in columns:
            self.columns[self.count] = col
            self.link[self.count] = False
            mock_out = col.content(mock_player)
            if mock_out.startswith('https://') or mock_out.startswith('http://'):
                self.link[self.count] = True
            self.count += 1

    def get_item(self, player):
        out = list()
        for i in range(self.count):
            out.append(self.columns[i].content(player))
        return out

    def is_link(self, col) -> bool:
        return self.link[col]

    def is_custom(self, col) -> bool:
        column = self.columns[col]
        return isinstance(column, CustomColumn)

    def custom_idx(self, col) -> bool:
        if not self.is_custom(col):
            return - 1
        return self.columns[col].idx

    def get_link_ids(self) -> list:
        ids = list()
        for i, v in self.link.items():
            if v:
                ids.append(i)
        return ids

    def filter_link_items(self, items: list) -> list:
        out = list()
        for i, v in enumerate(items):
            if self.is_link(i):
                out.append('[Link]')
                continue
            out.append(v)
        return out
