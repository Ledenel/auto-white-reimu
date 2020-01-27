from mahjong.record.universe.command import PropertyTypeManager
from mahjong.record.universe.format import ViewType

prop_manager = PropertyTypeManager()


@prop_manager.register_default_ctor(ViewType.list)
def empty_list():
    return []