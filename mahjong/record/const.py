from collections import Counter
from itertools import product

_all_tiles = [''.join(str(x) for x in item) for item in
              list((n, t) for t in "mps" for n in range(1, 9 + 1)) + list(product(range(1, 7 + 1), "z"))]
_dora_suit_num = list(range(2, 9 + 1)) + [1]
_dora_honor_num = [2, 3, 4, 1, 6, 7, 5]
_dora_tiles = [[''.join(str(x) for x in item)] for item in
               list((n, t) for t in "mps" for n in _dora_suit_num) + list(product(_dora_honor_num, "z"))]
_dora_map = dict(zip(_all_tiles, _dora_tiles))
for suit in "mps":
    _dora_map["0%s" % suit] = ["6%s" % suit]
    _dora_map["4%s" % suit].append("0%s" % suit)


def doras(indicators):
    dora_list = []
    for ind in indicators:
        dora_list.extend(_dora_map[ind])
    return dora_list


_player_4_tiles = Counter(_all_tiles * 4)
_player_3_tiles = _player_4_tiles - Counter(["%dm" % i for i in range(2, 8 + 1)] * 4)


def initial_tiles(player_num, has_aka):
    initials = _player_4_tiles
    akas = Counter(["0m", "0s", "0p"])
    if player_num == 3:
        initials = _player_3_tiles
        akas = akas - Counter(["0m"])
    if has_aka:
        initials = initials - Counter(["5m", "5s", "5p"]) + akas
    return list(initials)
