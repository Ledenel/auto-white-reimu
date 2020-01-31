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
        new_value = executor.execute_value(command, old_value)
    elif method == Update.RESET_DEFAULT:
        new_value = prop_manager.get_default(view_property)
    elif method == Update.ASSERT_EQUAL_OR_SET:
        pass
    else:
        raise ValueError("unrecognized", method)
    return new_value, view_property