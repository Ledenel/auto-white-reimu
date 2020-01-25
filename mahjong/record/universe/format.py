from abc import ABCMeta, abstractmethod
from collections import namedtuple, defaultdict
from enum import Flag, auto, Enum, IntEnum
from typing import Any, Callable


class PlayerId(IntEnum):
    first = 0,
    second = 1,
    third = 2,
    forth = 3,


class ViewScope(Flag):
    game = auto()
    player = auto()

    @staticmethod
    def scopes_with_multi_value():
        return {
            ViewScope.game: None,
            ViewScope.player: PlayerId,
        }


class View(Flag, metaclass=ABCMeta):

    @staticmethod
    def registered_view():
        return {
            ViewScope.game: GameView,
            ViewScope.player: PlayerView,
        }

    @staticmethod
    def by_name(name):
        for registered in View.registered_view().values():
            if hasattr(registered, name):
                return registered[name]
        return None


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


def default_value_func(value):
    def _default():
        return value

    return _default


# default_ctor: Callable[[], Any] = None[]='
class Update(Enum):
    REPLACE = auto()
    CLEAR = auto()
    ADD = auto()
    REMOVE = auto()
    FILL_DEFAULT = auto()

    def operand_num(self):
        return defaultdict(default_value_func(None), {
            Update.AND: 2,
            Update.REMOVE: 2,
            Update.FILL_DEFAULT: 0,
        })[self]


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
        "sub_scope_id",
        "property",
        "update_method",
        "value",
    ]
)


class GameCommand:
    def __init__(self, prop: GameProperty, sub_scope_id=None, value=None, timestamp=None):
        self.timestamp = timestamp
        # if value is None and prop.default_ctor is not None and prop.update_method != Update.CLEAR:
        #     self.value = prop.default_ctor()
        # else:
        self.sub_scope_id = sub_scope_id
        self.value = value
        self.prop = prop

    def to_record(self):
        return _Game_command(
            timestamp=self.timestamp,
            scope=self.prop.scope.name,
            sub_scope_id=self.sub_scope_id,
            property=self.prop.view_property.name,
            update_method=self.prop.update_method.name,
            value=self.value,
        )

    @staticmethod
    def from_record(record: _Game_command):
        return GameCommand(
            GameProperty(
                View.by_name(record.scope),
                Update[record.update_method],
            ),
            sub_scope_id=record.sub_scope_id,
            value=record.value,
            timestamp=record.timestamp,
        ),
