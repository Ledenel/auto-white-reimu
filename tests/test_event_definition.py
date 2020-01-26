from mahjong.record.reader import from_file
from mahjong.record.universe.tenhou import to_commands

test_file = "2009060321gm-00b9-0000-75b25bcf.xml"


def test_command_convert():
    with open(test_file, "r") as f:
        record = from_file(f)
    commands = to_commands(record)
    print(commands)
    assert len(commands) > 0
