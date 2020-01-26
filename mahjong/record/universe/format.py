import ast
from collections import namedtuple, defaultdict
from enum import Flag, auto, Enum, IntEnum
from typing import Callable, Iterable, TypeVar, List

from loguru import logger


class PlayerId(Enum):
    first = 0
    second = 1
    third = 2
    forth = 3


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


def assertion(func):
    def _check_assert(x):
        try:
            func(x)
            return True
        except AssertionError:
            return False

    return _check_assert


class ViewType(Flag):
    index = auto()
    score = auto()
    tiles = auto()
    melds = auto()
    str = auto()

    int = index | score
    list = tiles | melds


class PropertyTypeManager:
    def __init__(self):
        self._checker = {}
        self._default_value = {}

    def get_default(self, view: View):
        view_typ = view.type
        for typ, default_ctor in self._default_value.items():
            if view_typ in typ:
                return default_ctor()

    def assertion_check(self, name):
        def _assertion_wrapper(func):
            checker = assertion(func)
            self._checker[name] = checker
            return checker

        return _assertion_wrapper

    def register_default_ctor(self, name):
        def _default_value_wrapper(func):
            self._default_value[name] = func

        return _default_value_wrapper


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
    discard_tiles = auto()
    fixed_meld = auto()
    meld_public_tiles = auto()
    score = auto()

    type__str = name | level | extra_level
    type__score = score
    type__tiles = hand | discard_tiles | meld_public_tiles
    type__melds = fixed_meld


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


def is_empty(x):
    return x is None or x != x


def norm_empty(x):
    return None if is_empty(x) else x


def norm_value_str(x: str):
    return ast.literal_eval(x) if x != "" else None


# default_ctor: Callable[[], Any] = None[]='
class Update(Enum):
    REPLACE = auto()
    CLEAR = auto()
    ADD = auto()
    REMOVE = auto()
    RESET_DEFAULT = auto()

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


class GameProperty:
    def __init__(self, view_property: View, update_method: Update):
        self.view_property = view_property
        self.update_method = update_method
        # self.default_ctor = default_ctor

    @property
    def scope(self):
        return self.view_property.scope


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
            sub_scope=norm_empty(record.sub_scope_id),
            value=norm_empty(record.value),
            timestamp=norm_empty(record.timestamp),
        )


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
