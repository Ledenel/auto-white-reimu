import operator

from typing import Iterable

from mahjong.record.uni_format import *


def null():
    return None


defaultExecutor = {
    Update.FILL_DEFAULT: null,
    Update.ADD: operator.add,
    Update.REMOVE: operator.sub,
}


def fill_value_executor(value):
    def default_val():
        return value

    return {
        Update.FILL_DEFAULT: default_val,
        Update.ADD: operator.add,
        Update.REMOVE: operator.sub,
    }


def remove_all(lst: list, values: list):
    lst_r = lst.copy()
    for val in values:
        lst_r.remove(val)
    return lst_r


listExecutor = {
    Update.FILL_DEFAULT: list,
    Update.ADD: operator.add,
    Update.REMOVE: remove_all,
}

setExecutor = {
    Update.FILL_DEFAULT: set,
    Update.ADD: operator.or_,
    Update.REMOVE: operator.sub,
}


class TransferDict:
    def __init__(self, nested_dict, parent=None, parent_key=None):
        self.parent: TransferDict = parent
        self.parent_key = parent_key
        self.nested_dict = {
            k: TransferDict(v, self, k) if isinstance(v, dict) else v
            for k, v in nested_dict.items()
        }

    def __getattr__(self, item):
        return getattr(self.nested_dict, item)

    def _readonly(self, *args, **kwards):
        raise NotImplemented

    __setattr__ = __setitem__ = __delattr__ = pop = update = popitem = _readonly

    def set(self, key, value):
        modified = TransferDict({
            **self,
            key: value
        })
        return self.parent.set(
            self.parent_key, modified
        ) if self.parent is not None else modified

    def setdefault(self, key, default):
        if key not in self:
            return self.set(key, default)
        else:
            return self


# def setdefault(self, k, default):
#     if k in self:
#         return self
#     self


class GameExecutor:
    def __init__(self):
        self.executors = [
            listExecutor,
            setExecutor,
            defaultExecutor,
        ]
        state_dict = {
            enum: {} for enum in ViewScope.enum_members,
        }
        all_dict = {
            "timestamp": {

            },
            **state_dict
        }
        self.states = TransferDict(all_dict)

    def execute(self, commands: Iterable[GameCommand]):
        curr_state = self.states
        for command in commands:
            method = command.prop.update_method
            if method == Update.REPLACE:
                curr_state = curr_state[command.prop.scope].set(
                    command.prop.view_property,
                    command.value
                )
            elif method == Update.CLEAR:
                raise NotImplemented  # TODO
            elif method == Update.ADD:
                raise NotImplemented
            elif method == Update.REMOVE:
                raise NotImplemented
            elif method == Update.FILL_DEFAULT:
                raise NotImplemented
            else:
                raise ValueError("unrecognized", method)
            yield curr_state["timestamp"].set("global", command.timestamp)
