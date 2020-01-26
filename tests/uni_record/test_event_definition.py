from mahjong.record.reader import from_file
from mahjong.record.universe.tenhou import to_commands

test_file = "tests/2009060321gm-00b9-0000-75b25bcf.xml"

command_list = None

def command_setup():
    global command_list
    with open(test_file, "r") as f:
        record = from_file(f)
    command_list = to_commands(record)

command_setup()

def test_command_convert():
    with open(test_file, "r") as f:
        record = from_file(f)
    commands = to_commands(record)
    print(commands)
    assert len(commands) > 0
