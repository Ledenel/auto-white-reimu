import struct
from collections import namedtuple

import bitstruct


def bit_struct_from_desc(desc_str):
    reverse_order = desc_str.strip().split()
    reverse_order.reverse()
    return bitstruct.compile(">%s" % "".join(line.split(":")[1] for line in reverse_order))


def named_tuple_from_desc(type_name, desc_str):
    reverse_order = desc_str.strip().split()
    reverse_order.reverse()
    return namedtuple(type_name, [line.split(":")[0] for line in reverse_order])


def unpack_with(data_class, unpacker, value):
    return data_class(*unpacker.unpack(to_bit_bytes(value)))


def repack_to(unpacker, value_list):
    return struct.unpack(">H", unpacker.pack(*value_list))


def to_bit_bytes(value):
    packed_bytes = struct.pack(">H", int(value))
    return packed_bytes
