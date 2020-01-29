import ast

import pandas

from mahjong.record.reader import from_file
from mahjong.record.universe.format import PlayerView, Update
from mahjong.record.universe.command import norm_value_str, GameCommand
from mahjong.record.universe.tenhou import to_commands

test_file = "tests/2009060321gm-00b9-0000-75b25bcf.xml"

command_list = None


def command_setup():
    global command_list
    commands = get_test_commands()
    command_list = commands


def get_test_commands():
    with open(test_file, "r") as f:
        record = from_file(f)
    commands = to_commands(record)
    return commands


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
        # converters={'value': norm_value_str},
    )
    reconstructed_list = [GameCommand.from_record(x) for x in df_new.itertuples()]
    for a, b in zip(command_list, reconstructed_list):
        assert a.to_record() == b.to_record()

def test_command_clean():
    df = pandas.DataFrame(
        (x.to_record() for x in command_list),
    )
    df.to_csv("command_test.csv")
    df_new = pandas.read_csv(
        "command_test.csv",
        # converters={'value': norm_value_str},
    )
    df_clean = df_new.apply(GameCommand.pandas_columns_clean, axis="columns")
    reconstructed_list = [GameCommand.from_raw_record(x) for x in df_clean.itertuples()]
    for a, b in zip(command_list, reconstructed_list):
        assert a.to_record() == b.to_record()
