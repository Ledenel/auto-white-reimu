from collections import defaultdict
from enum import Flag, auto, Enum


class PlayerId(Enum):
    first = 0
    second = 1
    third = 2
    forth = 3


class ViewScope(Flag):
    game = auto()
    player = auto()
    record = auto()

    @staticmethod
    def scopes_with_multi_value():
        return {
            ViewScope.game: None,
            ViewScope.player: PlayerId,
            ViewScope.record: None,
        }


class View:
    @staticmethod
    def registered_view():
        return {
            ViewScope.record: RecordView,
            ViewScope.game: GameView,
            ViewScope.player: PlayerView,
        }

    @property
    def scope(self):
        for k, v in View.registered_view().items():
            if isinstance(self, v):
                return k

    @classmethod
    def all_types(cls):
        prefix = cls.get_type_prefix()
        return [(name, item) for name, item in cls.__members__.items() if name.startswith(prefix)]

    @staticmethod
    def get_type_prefix():
        prefix = "type__"
        return prefix

    @classmethod
    def all_properties(cls):
        prefix = cls.get_type_prefix()
        return [item for name, item in cls.__members__.items() if not name.startswith(prefix)]

    @property
    def type(self):
        view_type = View.registered_view()[self.scope]
        typs = view_type.all_types()
        prefix = self.get_type_prefix()
        for name, typ in typs:
            if self in typ:
                typ_name = name[len(prefix):]
                try:
                    return ViewType[typ_name]
                except KeyError:
                    raise ValueError("{self}'s type <{typ}> is not in the ViewType {members}".format(
                        typ=typ_name,
                        self=self,
                        members=list(ViewType.__members__)
                    ))
        raise ValueError("No type registered to {}".format(self))

    @staticmethod
    def by_name(name):
        return View.registered_view()[
            ViewScope[name]
        ]


class ViewType(Flag):
    index = auto()
    score = auto()
    tiles = auto()
    melds = auto()
    str = auto()
    bool = auto()

    int = index | score
    list = tiles | melds


class RecordView(View, Flag):
    player_count = auto()
    play_level = auto()
    has_aka_dora = auto()
    speed_up = auto()
    allow_tanyao_open = auto()
    play_wind_count = auto()
    show_discard_shadow = auto()
    seed = auto()

    type__index = player_count | play_wind_count
    type__str = play_level | seed
    type__bool = has_aka_dora | speed_up | allow_tanyao_open | show_discard_shadow


class GameView(View, Flag):
    wind = auto()
    round = auto()
    sub_round = auto()
    dora_indicators = auto()
    richii_remain_scores = auto()
    oya = auto()

    type__index = wind | round | sub_round | oya
    type__score = richii_remain_scores
    type__tiles = dora_indicators


class PlayerView(View, Flag):
    name = auto()
    level = auto()
    extra_level = auto()
    hand = auto()
    in_richii = auto()
    discard_tiles = auto()
    fixed_meld = auto()
    meld_public_tiles = auto()
    score = auto()
    bonus_tiles = auto()
    round = auto()

    type__str = name | level | extra_level
    type__index = round
    type__bool = in_richii
    type__score = score
    type__tiles = hand | discard_tiles | meld_public_tiles | bonus_tiles
    type__melds = fixed_meld


# public_tiles =
# GameView.dora_indicators |
# PlayerView.discard_tiles |
# PlayerView.meld_public_tiles

# visible_tiles =
# public_tiles |
# hand


# default_ctor: Callable[[], Any] = None[]='
class Update(Enum):
    REPLACE = auto()
    CLEAR = auto()
    ADD = auto()
    REMOVE = auto()
    RESET_DEFAULT = auto()
    ASSERT_EQUAL_OR_SET = auto()

    def operand_num(self):
        return defaultdict(default_value_func(None), {
            Update.ADD: 2,
            Update.REMOVE: 2,
            Update.RESET_DEFAULT: 0,
        })[self]


# _Game_property = namedtuple(
#     "GameProperty_",
#     field_names=[
#         "view_property",
#         "update_method",
#     ]
# )


def default_value_func(value):
    def _default():
        return value

    return _default
