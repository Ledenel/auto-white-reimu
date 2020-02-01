import json
from collections import OrderedDict, Counter
from enum import Enum, auto

from mahjong.record.universe.format import ViewType, View, Update


class PropertyMethod(Enum):
    default_value = auto()
    is_type = auto()
    check_equal = auto()
    to_str = auto()
    from_str = auto()


class PropertyTypeManager:
    def __init__(self):
        self._func_mapper = OrderedDict()

    def register(self, typ, method):
        def _register_func(func):
            self._func_mapper[(typ, method)] = func
            return func

        return _register_func

    def call(self, *values, prop, method):
        return lookup_func_table(self._func_mapper, method, prop, *values)

    def __getattr__(self, item):
        if item in PropertyMethod.__members__:
            mthd = PropertyMethod[item]

            def _call_wrapper(*args, prop: View = None):
                return self.call(*args, prop=prop, method=mthd)

            return _call_wrapper
        else:
            return getattr(super(), item)

    def register_assertion_check(self, name):
        def _assertion_wrapper(func):
            checker = assertion(func)
            self.register(name, PropertyMethod.is_type)()
            return checker

        return _assertion_wrapper


prop_manager = PropertyTypeManager()


@prop_manager.register(ViewType.index, PropertyMethod.default_value)
def default_index():
    return 0


@prop_manager.register(ViewType.list, PropertyMethod.default_value)
def empty_list():
    return []


@prop_manager.register(ViewType.tiles, PropertyMethod.check_equal)
def tiles_equal(expected, actual):
    return Counter(expected) == Counter(actual)


@prop_manager.register(None, PropertyMethod.check_equal)
def general_equal(expceted, actual):
    return expceted == actual


@prop_manager.register(ViewType.str, PropertyMethod.to_str)
@prop_manager.register(ViewType.str, PropertyMethod.from_str)
def plain_str(x):
    return str(x)


@prop_manager.register(None, PropertyMethod.to_str)
def json_dump(x):
    return json.dumps(x)


@prop_manager.register(None, PropertyMethod.from_str)
def json_load_any(x):
    if x != x:
        return None
    str_rep = str(x)
    if isinstance(x, bool):
        str_rep = str_rep.lower()
    return json.loads(str_rep)


@prop_manager.register(ViewType.list, Update.REMOVE)
def remove_all(lst: list, values: list):
    lst_r = lst.copy()
    for val in values:
        lst_r.remove(val)
    return lst_r


@prop_manager.register(None, Update.ADD)
def add_general(a, b):
    return a + b


@prop_manager.register(None, Update.REMOVE)
def remove_general(a, b):
    return a - b


def assertion(func):
    def _check_assert(x):
        try:
            func(x)
            return True
        except AssertionError:
            return False

    return _check_assert


def lookup_func_table(call_table, method, view, *args):
    for (typ, mthd), func in call_table.items():
        if method == mthd and (typ is None or (view is not None and hasattr(view, "type") and view.type in typ)):
            return func(*args)
    raise ValueError("no '{},{}' found in table {}.".format(view.type, method, call_table))
