from collections import OrderedDict

from mahjong.record.universe.command import GameCommand
from mahjong.record.universe.format import Update
from mahjong.record.universe.property_manager import prop_manager


class GameInterpreter:
    def __init__(self):
        self.state = OrderedDict()

    def interpret(self, command: GameCommand):
        key = (command.sub_scope_id, command.prop.view_property)
        old = self.state.get(key, None)
        new = execute_new_value(command, old_value=old)
        self.state[key] = new
        return new


def execute_new_value(command, old_value):
    method = command.prop.update_method
    view_property = command.prop.view_property
    new_value = command.value
    if method == Update.REPLACE:
        pass
    # elif method == Update.CLEAR:
    #     result_state = view.drop(view_property)
    elif method == Update.ADD or method == Update.REMOVE:
        new_value = prop_manager.call(old_value, command.value, prop=view_property, method=method)
    elif method == Update.RESET_DEFAULT:
        new_value = prop_manager.default_value(prop=view_property)
    elif method == Update.ASSERT_EQUAL_OR_SET:
        pass
    else:
        raise ValueError("unrecognized", method)
    return new_value
