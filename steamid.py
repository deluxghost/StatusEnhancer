import re
from enum import IntEnum


class SteamIntEnum(IntEnum):
    pass


class EUniverse(SteamIntEnum):
    Invalid = 0
    Public = 1
    Beta = 2
    Internal = 3
    Dev = 4
#   RC = 5  #: doesn't exit anymore
    Max = 6


class EType(SteamIntEnum):
    Invalid = 0
    Individual = 1      #: single user account
    Multiseat = 2       #: multiseat (e.g. cybercafe) account
    GameServer = 3      #: game server account
    AnonGameServer = 4  #: anonymous game server account
    Pending = 5         #: pending
    ContentServer = 6   #: content server
    Clan = 7
    Chat = 8
    ConsoleUser = 9     #: Fake SteamID for local PSN account on PS3 or Live account on 360, etc.
    AnonUser = 10
    Max = 11


class EInstanceFlag(SteamIntEnum):
    MMSLobby = 0x20000
    Lobby = 0x40000
    Clan = 0x80000


class ETypeChar(SteamIntEnum):
    I = EType.Invalid
    U = EType.Individual
    M = EType.Multiseat
    G = EType.GameServer
    A = EType.AnonGameServer
    P = EType.Pending
    C = EType.ContentServer
    g = EType.Clan
    T = EType.Chat
    L = EType.Chat  # lobby chat, 'c' for clan chat
    c = EType.Chat  # clan chat
    a = EType.AnonUser

    def __str__(self):
        return self.name


ETypeChars = ''.join(ETypeChar.__members__.keys())


class SteamID(int):
    """
    Object for converting steamID to its' various representations
    .. code:: python
        SteamID()  # invalid steamid
        SteamID(12345)  # accountid
        SteamID('12345')
        SteamID(id=12345, type='Invalid', universe='Invalid', instance=0)
        SteamID(103582791429521412)  # steam64
        SteamID('103582791429521412')
        SteamID('STEAM_1:0:2')  # steam2
        SteamID('[g:1:4]')  # steam3
    """
    EType = EType                  #: reference to EType
    EUniverse = EUniverse          #: reference to EUniverse
    EInstanceFlag = EInstanceFlag  #: reference to EInstanceFlag

    def __new__(cls, *args, **kwargs):
        steam64 = make_steam64(*args, **kwargs)
        return super(SteamID, cls).__new__(cls, steam64)

    def __init__(self, *args, **kwargs):
        pass

    def __repr__(self):
        return "%s(id=%s, type=%s, universe=%s, instance=%s)" % (
            self.__class__.__name__,
            self.id,
            repr(self.type.name),
            repr(self.universe.name),
            self.instance,
            )

    @property
    def id(self):
        """
        :return: account id
        :rtype: :class:`int`
        """
        return int(self) & 0xFFffFFff

    @property
    def instance(self):
        """
        :rtype: :class:`int`
        """
        return (int(self) >> 32) & 0xFFffF

    @property
    def type(self):
        """
        :rtype: :py:class:`steam.enum.EType`
        """
        return EType((int(self) >> 52) & 0xF)

    @property
    def universe(self):
        """
        :rtype: :py:class:`steam.enum.EUniverse`
        """
        return EUniverse((int(self) >> 56) & 0xFF)

    @property
    def as_32(self):
        """
        :return: account id
        :rtype: :class:`int`
        """
        return self.id

    @property
    def as_64(self):
        """
        :return: steam64 format
        :rtype: :class:`int`
        """
        return int(self)

    @property
    def as_steam2(self):
        """
        :return: steam2 format (e.g ``STEAM_1:0:1234``)
        :rtype: :class:`str`
        .. note::
            ``STEAM_X:Y:Z``. The value of ``X`` should represent the universe, or ``1``
            for ``Public``. However, there was a bug in GoldSrc and Orange Box games
            and ``X`` was ``0``. If you need that format use :attr:`SteamID.as_steam2_zero`
        """
        return "STEAM_%d:%d:%d" % (
            int(self.universe),
            self.id % 2,
            self.id >> 1,
            )

    @property
    def as_steam2_zero(self):
        """
        For GoldSrc and Orange Box games.
        See :attr:`SteamID.as_steam2`
        :return: steam2 format (e.g ``STEAM_0:0:1234``)
        :rtype: :class:`str`
        """
        return self.as_steam2.replace("_1", "_0")

    @property
    def as_steam3(self):
        """
        :return: steam3 format (e.g ``[U:1:1234]``)
        :rtype: :class:`str`
        """
        typechar = str(ETypeChar(self.type))
        instance = None

        if self.type in (EType.AnonGameServer, EType.Multiseat):
            instance = self.instance
        elif self.type == EType.Individual:
            if self.instance != 1:
                instance = self.instance
        elif self.type == EType.Chat:
            if self.instance & EInstanceFlag.Clan:
                typechar = 'c'
            elif self.instance & EInstanceFlag.Lobby:
                typechar = 'L'
            else:
                typechar = 'T'

        parts = [typechar, int(self.universe), self.id]

        if instance is not None:
            parts.append(instance)

        return '[%s]' % (':'.join(map(str, parts)))

    @property
    def community_url(self):
        """
        :return: e.g https://steamcommunity.com/profiles/123456789
        :rtype: :class:`str`
        """
        suffix = {
            EType.Individual: "profiles/%s",
            EType.Clan: "gid/%s",
        }
        if self.type in suffix:
            url = "https://steamcommunity.com/%s" % suffix[self.type]
            return url % self.as_64

        return None

    def is_valid(self):
        """
        Check whether this SteamID is valid
        :rtype: :py:class:`bool`
        """
        if self.type == EType.Invalid or self.type >= EType.Max:
            return False

        if self.universe == EUniverse.Invalid or self.universe >= EUniverse.Max:
            return False

        if self.type == EType.Individual:
            if self.id == 0 or self.instance > 4:
                return False

        if self.type == EType.Clan:
            if self.id == 0 or self.instance != 0:
                return False

        if self.type == EType.GameServer:
            if self.id == 0:
                return False

        if self.type == EType.AnonGameServer:
            if self.id == 0 and self.instance == 0:
                return False

        return True


def make_steam64(id=0, *args, **kwargs):
    """
    Returns steam64 from various other representations.
    .. code:: python
        make_steam64()  # invalid steamid
        make_steam64(12345)  # accountid
        make_steam64('12345')
        make_steam64(id=12345, type='Invalid', universe='Invalid', instance=0)
        make_steam64(103582791429521412)  # steam64
        make_steam64('103582791429521412')
        make_steam64('STEAM_1:0:2')  # steam2
        make_steam64('[g:1:4]')  # steam3
    """

    accountid = id
    etype = EType.Invalid
    universe = EUniverse.Invalid
    instance = None

    if len(args) == 0 and len(kwargs) == 0:
        value = str(accountid)

        # numeric input
        if value.isdigit():
            value = int(value)

            # 32 bit account id
            if 0 < value < 2**32:
                accountid = value
                etype = EType.Individual
                universe = EUniverse.Public
            # 64 bit
            elif value < 2**64:
                return value

        # textual input e.g. [g:1:4]
        else:
            result = steam2_to_tuple(value) or steam3_to_tuple(value)

            if result:
                (accountid,
                 etype,
                 universe,
                 instance,
                 ) = result
            else:
                accountid = 0

    elif len(args) > 0:
        length = len(args)
        if length == 1:
            etype, = args
        elif length == 2:
            etype, universe = args
        elif length == 3:
            etype, universe, instance = args
        else:
            raise TypeError("Takes at most 4 arguments (%d given)" % length)

    if len(kwargs) > 0:
        etype = kwargs.get('type', etype)
        universe = kwargs.get('universe', universe)
        instance = kwargs.get('instance', instance)

    etype = (EType(etype)
             if isinstance(etype, (int, EType))
             else EType[etype]
             )

    universe = (EUniverse(universe)
                if isinstance(universe, (int, EUniverse))
                else EUniverse[universe]
                )

    if instance is None:
        instance = 1 if etype in (EType.Individual, EType.GameServer) else 0

    assert instance <= 0xffffF, "instance larger than 20bits"

    return (universe << 56) | (etype << 52) | (instance << 32) | accountid


def steam2_to_tuple(value):
    """
    :param value: steam2 (e.g. ``STEAM_1:0:1234``)
    :type value: :class:`str`
    :return: (accountid, type, universe, instance)
    :rtype: :class:`tuple` or :class:`None`
    .. note::
        The universe will be always set to ``1``. See :attr:`SteamID.as_steam2`
    """
    match = re.match(r"^STEAM_(?P<universe>\d+)"
                     r":(?P<reminder>[0-1])"
                     r":(?P<id>\d+)$", value
                     )

    if not match:
        return None

    steam32 = (int(match.group('id')) << 1) | int(match.group('reminder'))
    universe = int(match.group('universe'))

    # Games before orange box used to incorrectly display universe as 0, we support that
    if universe == 0:
        universe = 1

    return (steam32, EType(1), EUniverse(universe), 1)


def steam3_to_tuple(value):
    """
    :param value: steam3 (e.g. ``[U:1:1234]``)
    :type value: :class:`str`
    :return: (accountid, type, universe, instance)
    :rtype: :class:`tuple` or :class:`None`
    """
    match = re.match(r"^\["
                     r"(?P<type>[i%s]):"        # type char
                     r"(?P<universe>[0-4]):"     # universe
                     r"(?P<id>\d{1,10})"            # accountid
                     r"(:(?P<instance>\d+))?"  # instance
                     r"\]$" % ETypeChars,
                     value
                     )
    if not match:
        return None

    steam32 = int(match.group('id'))
    universe = EUniverse(int(match.group('universe')))
    typechar = match.group('type').replace('i', 'I')
    etype = EType(ETypeChar[typechar])
    instance = match.group('instance')

    if typechar in 'gT':
        instance = 0
    elif instance is not None:
        instance = int(instance)
    elif typechar == 'L':
        instance = EInstanceFlag.Lobby
    elif typechar == 'c':
        instance = EInstanceFlag.Clan
    elif etype in (EType.Individual, EType.GameServer):
        instance = 1
    else:
        instance = 0

    instance = int(instance)

    return (steam32, etype, universe, instance)
