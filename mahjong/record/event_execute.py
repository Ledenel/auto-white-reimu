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

    def drop(self, key):
        dict_cpy = self.nested_dict.copy()
        del dict_cpy[key]
        modified = TransferDict(dict_cpy)
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
class CombinedCommandExecutor:
    def __init__(self, executor_with_type):
        self.executor_with_type = executor_with_type

    def execute_value(self, command: GameCommand, origin_value=None):
        for typ, executor in self.executor_with_type:
            if typ is None or isinstance(command.value, typ):
                method = command.prop.update_method
                if method.operand_num() == 2:
                    return executor[method](origin_value, command.value)
                elif method.operand_num() == 1:
                    return executor[method](command.value)
                elif method.operand_num() == 0:
                    return executor[method]()


class GameExecutor:
    def __init__(self):
        self.executor = CombinedCommandExecutor([
            (list, listExecutor),
            (set, setExecutor),
            (None, defaultExecutor),
        ])
        state_dict = {
            enum: {
                "single": {},
            } if multi_value is None else {
                key: {} for key in multi_value
            } for enum, multi_value in ViewScope.scopes_with_multi_value().items(),
        }
        all_dict = {
            "time": {
                "global": {

                },
            },
            **state_dict
        }
        self.states = TransferDict(all_dict)

    @staticmethod
    def state_value(state_dict, command: GameCommand):
        scope_key = command.prop.scope
        multi_values = View.registered_view()[scope_key]
        if multi_values is None:
            return state_dict[scope_key]["single"]
        else:
            return multi_values(command.sub_scope_id)

    def execute(self, commands: Iterable[GameCommand]):
        curr_state = self.states
        for command in commands:
            curr_state = self.execute_update_state(command, curr_state)
            yield curr_state["time"]["global"].set("timestamp", command.timestamp)

    def execute_update_state(self, command, curr_state):
        method = command.prop.update_method
        view = GameExecutor.state_value(curr_state, command)
        if method == Update.REPLACE:
            curr_state = view.set(
                command.prop.view_property,
                command.value
            )
        elif method == Update.CLEAR:
            curr_state = view.drop(command.prop.view_property)
        elif method == Update.ADD or method == Update.REMOVE:
            curr_state = view.set(
                command.prop.view_property,
                self.executor.execute_value(
                    command, view[command.prop.view_property]
                ),
            )
        elif method == Update.FILL_DEFAULT:
            curr_state = view.setdefault(
                command.prop.view_property,
                self.executor.execute_value(
                    command
                ),
            )
        else:
            raise ValueError("unrecognized", method)
        return curr_state
