from abc import ABCMeta, abstractmethod
from collections import namedtuple

import bitstruct

import struct

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


def bit_struct_from_desc(desc_str):
    reverse_order = desc_str.strip().split()
    reverse_order.reverse()
    return bitstruct.compile(">%s" % "".join(line.split(":")[1] for line in reverse_order))


def named_tuple_from_desc(type_name, desc_str):
    reverse_order = desc_str.strip().split()
    reverse_order.reverse()
    return namedtuple(type_name, [line.split(":")[0] for line in reverse_order])


class Meld(metaclass=ABCMeta):
    @property
    @abstractmethod
    def data_class(self):
        pass

    @property
    @abstractmethod
    def unpacker(self):
        pass

    def unpack(self, value):
        return self.data_class(*self.unpacker.unpack(struct.pack(">H", int(value))))


class Flush(Meld):
    pass



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
