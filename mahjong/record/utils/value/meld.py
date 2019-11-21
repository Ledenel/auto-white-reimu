from abc import ABCMeta, abstractmethod
from typing import Set, Iterable

from mahjong.container.set import TileSet
from ..bit import bit_struct_from_desc, named_tuple_from_desc, unpack_with
from ..constant import TENHOU_TILE_CATEGORY
from ..value.tile import tile_from_tenhou
from ...category import SubCategory

flush_desc = """
kui:u2
syuntsu:b1
hai0:u2
hai1:u2
hai2:u2
padding__:u1
type6:u6
"""

triplet_desc = """
kui:u2
syuntsu:b1
koutsu:b1
chakan:b1
hai_unused:u2
padding__:u2
type7:u7
"""

kan_desc = """
kui:u2
syuntsu:b1
koutsu:b1
chakan:b1
nuki:b1
padding__:u2
type8:u8
"""

added_kan_desc = """
kui:u2
syuntsu:b1
koutsu:b1
chakan:b1
hai_added:u2
padding__:u2
type7:u7
"""

kita_desc = """
kui:u2
syuntsu:b1
koutsu:b1
chakan:b1
nuki:b1
padding__:u2
type8:u8
"""

FROM_MAP = [0, 1, 2, 3]


def init_from_basic(tiles_basic, which_first):
    first_tile = tiles_basic[which_first]
    self_tiles = set(tiles_basic) - {first_tile}
    return {first_tile}, self_tiles


def tile_set_from_tenhou(tenhou_ints: Iterable[int]):
    return TileSet(tile_from_tenhou(x) for x in tenhou_ints)


class Meld(metaclass=ABCMeta):
    @property
    @abstractmethod
    def borrowed_tiles(self) -> Set[int]:
        pass

    @property
    @abstractmethod
    def self_tiles(self) -> Set[int]:
        pass

    @property
    @abstractmethod
    def from_who(self):
        pass

    def is_opened(self) -> bool:
        if self.borrowed_tiles:
            return True
        else:
            return False

    def __repr__(self):
        return "<{}>".format(self)

    def __str__(self):
        return "'{type}' using '{self_tile}' to get '{borrow}' from player {player}".format(
            type=type(self).__name__,
            self_tile=tile_set_from_tenhou(self.self_tiles),
            borrow=tile_set_from_tenhou(self.borrowed_tiles),
            player=self.from_who,
        )


class TenhouMeld(Meld, metaclass=ABCMeta):
    @property
    @abstractmethod
    def data_class(self):
        pass

    @property
    @abstractmethod
    def unpacker(self):
        pass

    @property
    def data(self):
        return self._data

    @property
    def borrowed_index(self):
        return 3 - self.data.kui

    @property
    def from_who(self):
        return (self.who_index + FROM_MAP[self.data.kui]) % 4

    def unpack(self, value):
        unpacker = self.unpacker
        data_class = self.data_class
        return unpack_with(data_class, unpacker, value)

    def __init__(self, who_index, value) -> None:
        super().__init__()
        self.who_index = who_index
        self._data = self.unpack(value)


class Flush(TenhouMeld):
    def __init__(self, who_index, value) -> None:
        super().__init__(who_index, value)
        data = self.data
        flush_kinds = SubCategory(3, 7, 3)
        flush_color, flush_start_number, which_first = flush_kinds.category(data.type6)
        hais = [data.hai0, data.hai1, data.hai2]
        tiles_basic = [
            TENHOU_TILE_CATEGORY.index((flush_color, flush_start_number + i, hai))
            for i, hai in enumerate(hais)
        ]
        borrowed_tiles, self_tiles = init_from_basic(tiles_basic, which_first)
        self._self_tiles = self_tiles
        self._borrowed_tiles = borrowed_tiles

    @property
    def self_tiles(self):
        return self._self_tiles

    @property
    def borrowed_tiles(self):
        return self._borrowed_tiles

    @property
    def data_class(self):
        return FlushData

    @property
    def unpacker(self):
        return flush_packer


class Triplet(TenhouMeld):
    @property
    def data_class(self):
        return TripletData

    def __init__(self, who_index, value) -> None:
        super().__init__(who_index, value)
        triplet_kinds = SubCategory(34, 3)
        triplet_color_number = SubCategory(4, 9)
        tile_type, which_first = triplet_kinds.category(self.data.type7)
        color, number = triplet_color_number.category(tile_type)
        hais = sorted(list(set(range(4)) - {self.data.hai_unused}))
        tiles_basic = [
            TENHOU_TILE_CATEGORY.index((color, number, hai))
            for i, hai in enumerate(hais)
        ]
        borrowed_tiles, self_tiles = init_from_basic(tiles_basic, which_first)
        self._self_tiles = self_tiles
        self._borrowed_tiles = borrowed_tiles

    @property
    def unpacker(self):
        return triplet_packer

    @property
    def self_tiles(self):
        return self._self_tiles

    @property
    def borrowed_tiles(self):
        return self._borrowed_tiles


class Kan(Meld, metaclass=ABCMeta):
    @property
    @abstractmethod
    def is_opened_kan(self) -> bool:
        pass


class TenhouAddedKan(TenhouMeld):
    @property
    def data_class(self):
        return AddedKanData

    def __init__(self, who_index, value) -> None:
        super().__init__(who_index, value)
        triplet_kinds = SubCategory(34, 3)
        triplet_color_number = SubCategory(4, 9)
        tile_type, which_first = triplet_kinds.category(self.data.type7)
        color, number = triplet_color_number.category(tile_type)
        self._self_tiles = {TENHOU_TILE_CATEGORY.index((color, number, self.data.hai_added))}
        self._borrowed_tiles = set()

    @property
    def unpacker(self):
        return added_kan_packer

    @property
    def self_tiles(self):
        return self._self_tiles

    @property
    def borrowed_tiles(self):
        return self._borrowed_tiles


class TenhouKan(TenhouMeld, Kan):
    @property
    def is_opened_kan(self) -> bool:
        return self.data.kui != 0

    @property
    def data_class(self):
        return KanData

    def __init__(self, who_index, value) -> None:
        super().__init__(who_index, value)
        color, number, hai_index = TENHOU_TILE_CATEGORY.category(self.data.type8)
        hais = list(range(4))
        tiles_basic = [
            TENHOU_TILE_CATEGORY.index((color, number, hai))
            for i, hai in enumerate(hais)
        ]
        if self.data.kui == 0:
            self._self_tiles = set(tiles_basic)
            self._borrowed_tiles = set()
        else:
            borrowed_tiles, self_tiles = init_from_basic(tiles_basic, hai_index)
            self._self_tiles = self_tiles
            self._borrowed_tiles = borrowed_tiles

    @property
    def unpacker(self):
        return kan_packer

    @property
    def self_tiles(self):
        return self._self_tiles

    @property
    def borrowed_tiles(self):
        return self._borrowed_tiles


class KanFromTriplet(Kan):
    @property
    def is_opened_kan(self) -> bool:
        return True

    def __init__(self, triplet_meld: Triplet, added_meld: TenhouAddedKan) -> None:
        super().__init__()
        self._self_tiles = triplet_meld.self_tiles | added_meld.self_tiles
        self._borrowed_tiles = triplet_meld.borrowed_tiles
        self._from_who = triplet_meld.from_who

    @property
    def borrowed_tiles(self):
        return self._borrowed_tiles

    @property
    def self_tiles(self):
        return self._self_tiles

    @property
    def from_who(self):
        return self._from_who


class Kita(TenhouMeld):
    @property
    def data_class(self):
        return KitaData

    def __init__(self, who_index, value) -> None:
        super().__init__(who_index, value)
        self._self_tiles = {self.data.type8}
        self._borrowed_tiles = set()

    @property
    def unpacker(self):
        return kita_packer

    @property
    def self_tiles(self):
        return self._self_tiles

    @property
    def borrowed_tiles(self):
        return self._borrowed_tiles


FlushData = named_tuple_from_desc("flush_data", flush_desc)
flush_packer = bit_struct_from_desc(flush_desc)

TripletData = named_tuple_from_desc("triplet_data", triplet_desc)
triplet_packer = bit_struct_from_desc(triplet_desc)

KanData = named_tuple_from_desc("kan_data", kan_desc)
kan_packer = bit_struct_from_desc(kan_desc)

AddedKanData = named_tuple_from_desc("added_kan_data", added_kan_desc)
added_kan_packer = bit_struct_from_desc(added_kan_desc)

KitaData = named_tuple_from_desc("kita_data", kita_desc)
kita_packer = bit_struct_from_desc(kita_desc)

meld_type_desc = kita_desc
meld_type_unpacker = bit_struct_from_desc(meld_type_desc)
MeldTypeData = named_tuple_from_desc("meld_type", meld_type_desc)


def meld_type(data):
    type_of = unpack_with(MeldTypeData, meld_type_unpacker, data)
    if type_of.syuntsu:
        return "flush"
    elif type_of.koutsu:
        return "triplet"
    elif type_of.chakan:
        return "add_kan"
    elif type_of.nuki:
        return "kita"
    else:
        return "kan"


def meld_from(event) -> Meld:
    who = int(event.attrib['who'])
    data = event.attrib['m']
    type_of = unpack_with(MeldTypeData, meld_type_unpacker, data)

    if type_of.syuntsu:
        return Flush(who, data)
    elif type_of.koutsu:
        return Triplet(who, data)
    elif type_of.chakan:
        return TenhouAddedKan(who, data)
    elif type_of.nuki:
        return Kita(who, data)
    else:
        return TenhouKan(who, data)


def is_triplet_of_added_kan(item: Triplet, added: TenhouAddedKan):
    added_tile = tile_from_tenhou(list(added.self_tiles)[0])
    triplet_representative = tile_from_tenhou(list(item.self_tiles)[0])
    return added_tile == triplet_representative
