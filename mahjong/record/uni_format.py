from abc import ABCMeta, abstractmethod
from collections import namedtuple
from enum import Flag, auto, Enum, IntEnum
from typing import Any, Callable


class PlayerId(IntEnum):
    first = 0,
    second = 1,
    third = 2,
    forth = 3,
    all = -1,


class ViewScope(Enum):
    game = auto()
    player = auto()


class View(Flag, metaclass=ABCMeta):
    pass


class GameView(View):
    wind = auto()
    round = auto()
    sub_round = auto()
    dora_indicators = auto()
    richii_remain_scores = auto()


class PlayerView(View):
    name = auto()
    level = auto()
    extra_level = auto()
    hand = auto()
    discard_tiles = auto()
    fixed_meld = auto()
    meld_public_tiles = auto()
    score = auto()

    # public_tiles = discard_tiles | meld_public_tiles
    # visible_tiles = public_tiles | hand


# default_ctor: Callable[[], Any] = None
class Update(Enum):
    REPLACE = auto()
    CLEAR = auto()
    ADD = auto()
    REMOVE = auto()
    FILL_DEFAULT = auto()


# _Game_property = namedtuple(
#     "GameProperty_",
#     field_names=[
#         "view_property",
#         "update_method",
#     ]
# )


class GameProperty:
    def __init__(self, view_property: View, update_method: Update):
        self.view_property = view_property
        self.update_method = update_method
        # self.default_ctor = default_ctor

    @property
    def scope(self):
        if isinstance(self.view_property, GameView):
            return ViewScope.game
        elif isinstance(self.view_property, PlayerView):
            return ViewScope.player


_Game_command = namedtuple(
    "GameCommand_",
    field_names=[
        "timestamp",
        "scope",
        "property",
        "update_method",
        "value",
    ]
)


class GameCommand:
    def __init__(self, prop: GameProperty, value=None, timestamp=None):
        self.timestamp = timestamp
        # if value is None and prop.default_ctor is not None and prop.update_method != Update.CLEAR:
        #     self.value = prop.default_ctor()
        # else:
        self.value = value
        self.prop = prop

    def to_record(self):
        return _Game_command(
            timestamp=self.timestamp,
            scope=self.prop.scope.name,
            property=self.prop.view_property.name,
            update_method=self.prop.update_method.name,
            value=self.value,
        )
