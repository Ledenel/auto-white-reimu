from mahjong.record.universe.command import GameCommand
from mahjong.record.universe.format import Update
from mahjong.record.universe.property_manager import prop_manager


class GameInterpreter:
    pass


def execute_new_value(executor, command, old_value):
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
    return new_value, view_property


class CombinedCommandExecutor:
    def __init__(self, executor_with_type):
        self.executor_with_type = executor_with_type

    def has_function(self, value, method: Update):
        for typ, executor in self.executor_with_type:
            if typ is None or isinstance(value, typ):
                if method in executor:
                    return True
        return False

    def execute_value(self, command: GameCommand, origin_value=None):
        for typ, executor in self.executor_with_type:
            if typ is None or isinstance(command.value, typ):
                method = command.prop.update_method
                if method.operand_num() == 2:
                    return executor[method](origin_value, command.value)
                elif method.operand_num() == 1:
                    return executor[method](command.value)
                elif method.operand_num() == 0:
                    raise ValueError("Zero operand is not supported. Type of None value may be ambiguous.")
