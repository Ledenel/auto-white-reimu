import ast

import pandas

from mahjong.record.reader import from_file
from mahjong.record.universe.format import GameCommand, PlayerView, Update, norm_value_str
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
    assert len(commands) > 1


def test_game_command_convert():
    command = GameCommand(
        prop=PlayerView.hand,
        update=Update.RESET_DEFAULT,
        sub_scope=2
    )
    record = command.to_record()
    assert GameCommand.from_record(record).to_record() == record


def test_command_serialize():
    df = pandas.DataFrame(
        (x.to_record() for x in command_list),
    )
    df.to_csv("command_test.csv")
    df_new = pandas.read_csv(
        "command_test.csv",
        converters={'value': norm_value_str},
    )
    reconstructed_list = [GameCommand.from_record(x) for x in df_new.itertuples(index=False)]
    for a, b in zip(command_list, reconstructed_list):
        assert a.to_record() == b.to_record()
