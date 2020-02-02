import mahjong.record.universe.tenhou.event_definition as _event_def
from mahjong.record.universe.tenhou.xml_macher import tenhou_command


def to_command_iter(record, strict):
    tenhou_command.clear()
    for event in record.events:
        yield from tenhou_command(event, strict)


def to_command_records(record, raw=False, strict=False):
    for cmd in to_command_iter(record, strict):
        if raw:
            yield cmd.to_raw_record()
        else:
            yield cmd.to_record()


def to_commands(record, strict=False):
    return list(to_command_iter(record, strict))
