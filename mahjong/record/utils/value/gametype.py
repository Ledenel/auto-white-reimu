from ..bit import bit_struct_from_desc, named_tuple_from_desc, unpack_with, repack_to

game_type_desc = """
preserved:u1
no_aka_dora:b1
no_tanyao_open_hand:b1
east_and_south_round:b1
three_players:b1
play_level_high_bit:u1
speed_up:b1
play_level_low_bit:u1
show_discard_shadow:b1
with_tips:b1
is_5tips:b1
padding_:u5
"""

GameTypeData = named_tuple_from_desc("game_type", game_type_desc)

game_type_packer = bit_struct_from_desc(game_type_desc)


def _pick(values, true_left, default=""):
    if true_left:
        return values[0]
    elif len(values) > 1:
        return values[1]
    else:
        return default


class GameType:
    def __init__(self, type_data):
        self.origin = int(type_data)
        self.data = unpack_with(GameTypeData, game_type_packer, type_data)
        listed = list(self.data)
        listed[0] = 0
        listed[-1] = 0
        self.standard_code = repack_to(game_type_packer, listed)

    def player_count(self) -> int:
        return 3 if self.data.three_players else 4

    def has_aka_dora(self) -> bool:
        return not self.data.no_aka_dora

    def play_level(self):
        return (self.data.play_level_high_bit << 1) | self.data.play_level_low_bit

    def speed_up(self) -> int:
        return self.data.speed_up

    def allow_tanyao_open(self) -> int:
        return not self.data.no_tanyao_open_hand

    def play_wind_count(self) -> int:
        return 2 if self.data.east_and_south_round else 1

    def main_game_count(self) -> int:
        return self.play_wind_count() * self.player_count()

    def with_tips(self) -> bool:
        return self.data.with_tips

    def tips_count(self) -> int:
        if self.with_tips():
            if self.data.is_5tips:
                return 5
            else:
                return 2
        return 0

    def show_discard_shadow(self) -> bool:
        return self.data.show_discard_shadow

    def __eq__(self, other):
        return self.standard_code == other.standard_code

    def __str__(self) -> str:
        return "%s%s%s%s%s%s%s%s" % (
            "零一二三四"[self.player_count()],
            _pick(["若銀琥孔", "般上特鳳"], self.with_tips())[self.play_level()],
            "_東南西北"[self.play_wind_count()],
            _pick("喰", self.allow_tanyao_open()),
            _pick("赤", self.has_aka_dora()),
            _pick("速", self.speed_up()),
            _pick("暗", self.show_discard_shadow()),
            _pick(["祝%d" % (self.tips_count())], self.with_tips()),
        )

    def __repr__(self):
        return "<%s>" % str(self)
