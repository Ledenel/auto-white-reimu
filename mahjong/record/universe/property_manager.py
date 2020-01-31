import json
from collections import OrderedDict, Counter
from enum import Enum, auto

from mahjong.record.universe.format import ViewType, View


class PropertyMethod(Enum):
    default_value = auto()
    is_type = auto()
    check_equal = auto()
    to_str = auto()
    from_str = auto()


class PropertyTypeManager:
    def __init__(self):
        self._func_mapper = OrderedDict()
        self._checker = OrderedDict()
        self._default_value_ctor = OrderedDict()
        self._equality_check = OrderedDict()
        self._value_to_str = OrderedDict()
        self._str_to_value = OrderedDict()

    def register(self, typ, method):
        def _register_func(func):
            self._func_mapper[(typ, method)] = func
            return func

        return _register_func

    def call(self, method, typ, *values):
        return lookup_func_table(self._func_mapper, method, typ, *values)

    def register_equal_check(self, name):
        return self.register(name, PropertyMethod.check_equal)

    def equal_value(self, expected, actual, view: View = None):
        return self.call(PropertyMethod.check_equal, view, expected, actual)
        # return lookup_enum_table(self._equality_check, view, expected, actual)

    def register_to_str(self, name):
        def _to_str_wrapper(func):
            self._value_to_str[name] = func
            return func

        return _to_str_wrapper

    def to_str(self, value, view: View = None):
        return lookup_enum_table(self._value_to_str, view, value)

    def register_from_str(self, name):
        def _from_str_wrapper(func):
            self._str_to_value[name] = func
            return func

        return _from_str_wrapper

    def from_str(self, str_value, view: View = None):
        return lookup_enum_table(self._str_to_value, view, str_value)

    def get_default(self, view: View):
        return lookup_enum_table(self._default_value_ctor, view)

    def register_assertion_check(self, name):
        def _assertion_wrapper(func):
            checker = assertion(func)
            self._checker[name] = checker
            return checker

        return _assertion_wrapper

    def register_default_ctor(self, name):
        def _default_value_wrapper(func):
            self._default_value_ctor[name] = func
            return func

        return _default_value_wrapper


prop_manager = PropertyTypeManager()


@prop_manager.register_default_ctor(ViewType.list)
def empty_list():
    return []


@prop_manager.register_equal_check(ViewType.tiles)
def tiles_equal(expected, actual):
    return Counter(expected) == Counter(actual)


@prop_manager.register_equal_check(None)
def general_equal(expceted, actual):
    return expceted == actual


@prop_manager.register_to_str(None)
def json_dump(x):
    return json.dumps(x)


@prop_manager.register_from_str(None)
def json_load_any(x):
    if x != x:
        return None
    str_rep = str(x)
    if isinstance(x, bool):
        str_rep = str_rep.lower()
    return json.loads(str_rep)


def assertion(func):
    def _check_assert(x):
        try:
            func(x)
            return True
        except AssertionError:
            return False

    return _check_assert


def lookup_enum_table(call_table, view, *args):
    for typ, func in call_table.items():
        if typ is None or (view is not None and view.type in typ):
            return func(*args)
    raise ValueError("no '{}' found in table {}.".format(view.type, call_table))


def lookup_func_table(call_table, method, view, *args):
    for (typ, mthd), func in call_table.items():
        if method == mthd and typ is None or (view is not None and view.type in typ):
            return func(*args)
    raise ValueError("no '{},{}' found in table {}.".format(view.type, method, call_table))
