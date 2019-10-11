import re
from typing import List

from steamid import SteamID

from utils import parse_time

line_pat = re.compile(r'^#\s+(?P<userid>\d+)\s+"(?P<name>.+)"\s+(?P<steamid>\S+)\s+(?P<other>.+)$')


class Player:

    def __init__(self, userid: int, name: str, steamid: str, connected: str):
        self.userid = userid
        self.name = name
        self.steamid = SteamID(steamid)
        self.connected_str = connected
        self.connected = parse_time(connected)

    def kick_cmd(self) -> str:
        return f'callvote kick {self.userid}'


def parse_player(line: str) -> Player:
    if not line.startswith('#'):
        return
    match = line_pat.match(line)
    if not match:
        return
    userid = int(match.group('userid'))
    name = match.group('name')
    steamid = match.group('steamid')
    other = match.group('other')
    if steamid == 'BOT':
        return
    connected = ''
    other_parts = other.split()
    if other_parts:
        connected = other_parts[0]
    player = Player(userid, name, steamid, connected)
    return player


def parse_status(status_str: str) -> List[Player]:
    lines = status_str.split('\n')
    players = list()
    for line in lines:
        player = parse_player(line)
        if player is not None:
            players.append(player)
    players.sort(key=lambda p: p.userid)
    return players
