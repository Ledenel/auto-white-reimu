import mahjong.record.universe.tenhou.event_definition as _event_def
from mahjong.record.universe.tenhou.xml_macher import tenhou_command


def to_command_iter(record):
    for event in record.events:
        yield from tenhou_command(event)


def to_commands(record):
    return list(to_command_iter(record))
