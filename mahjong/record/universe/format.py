from abc import ABCMeta, abstractmethod
from collections import namedtuple, defaultdict
from enum import Flag, auto, Enum, IntEnum
from typing import Any, Callable, Iterable, TypeVar, List

from loguru import logger


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


class View:
    @staticmethod
    def registered_view():
        return {
            ViewScope.game: GameView,
            ViewScope.player: PlayerView,
        }

    @staticmethod
    def by_name(name):
        return View.registered_view()[
            ViewScope[name]
        ]


class GameView(View, Flag):
    wind = auto()
    round = auto()
    sub_round = auto()
    dora_indicators = auto()
    richii_remain_scores = auto()
    oya = auto()


class PlayerView(View, Flag):
    name = auto()
    level = auto()
    extra_level = auto()
    hand = auto()
    discard_tiles = auto()
    fixed_meld = auto()
    meld_public_tiles = auto()
    score = auto()


# public_tiles =
# GameView.dora_indicators |
# PlayerView.discard_tiles |
# PlayerView.meld_public_tiles

# visible_tiles =
# public_tiles |
# hand


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
    RESET_DEFAULT = auto()

    def operand_num(self):
        return defaultdict(default_value_func(None), {
            Update.AND: 2,
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
    def __init__(self, *, prop: View, update: Update, sub_scope=None, value=None, timestamp=None):
        self.timestamp = timestamp
        # if value is None and prop.default_ctor is not None and prop.update_method != Update.CLEAR:
        #     self.value = prop.default_ctor()
        # else:
        self.sub_scope_id = sub_scope
        self.value = value
        self.property = prop
        self.update_method = update
        self.prop = GameProperty(self.property, self.update_method)

    # @staticmethod
    # def multi_command(props: Iterable[GameProperty], sub_scope_id=None, value=None, timestamp=None):
    #     return [GameCommand(
    #         prop,
    #         sub_scope_id=sub_scope_id,
    #         value=value,
    #         timestamp=timestamp
    #     ) for prop in props]

    def __str__(self):
        return str(self.to_record())

    def __repr__(self):
        return "{%s}" % str(self)

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
            prop=View.by_name(record.scope)[record.property],
            update=Update[record.update_method],
            sub_scope=record.sub_scope_id,
            value=record.value,
            timestamp=record.timestamp,
        ),


EventT = TypeVar('EventT')
EventTransform = Callable[[EventT], Iterable[GameCommand]]


class CommandTranslator:
    def __init__(self):
        self.defaults = []
        self.defaults: List[EventTransform]

    @staticmethod
    def fallback_call(event, matchers: List[EventTransform]) -> List[GameCommand]:
        for matcher in matchers:
            value = list(matcher(event))
            if value:
                return value

    # TODO: add preprocess and postprocess for event and command list. (to support timestamp attaching in tenhou).

    def default_event(self, func: EventTransform) -> EventTransform:
        self.defaults.append(func)
        return func

    def translate(self, event: EventT) -> List[GameCommand]:
        pass

    def __call__(self, event: EventT) -> List[GameCommand]:
        return_value = self.translate(event)
        if return_value:
            return return_value
        return_value = CommandTranslator.fallback_call(event, self.defaults)
        if return_value:
            return return_value
        else:
            logger.warning("event <{}> is not transformed to game commands.", event)
            return []
