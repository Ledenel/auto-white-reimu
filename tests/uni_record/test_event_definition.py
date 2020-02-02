import pandas
import pytest

from mahjong.record.reader import from_file
from mahjong.record.universe.format import PlayerView, Update
from mahjong.record.universe.command import GameCommand
from mahjong.record.universe.tenhou import to_commands
from tests.uni_record.paifu_list import test_files


def to_commands_iter(files):
    for file in files:
        with open(file, "r") as f:
            record = from_file(f)
            commands = to_commands(record)
            yield commands


@pytest.mark.parametrize("file_name", test_files)
def test_command_convert(file_name):
    with open(file_name, "r") as f:
        record = from_file(f)
    commands = to_commands(record, strict=True)
    assert len(commands) > 1


def test_game_command_convert():
    command = GameCommand(
        prop=PlayerView.hand,
        update=Update.RESET_DEFAULT,
        sub_scope=2
    )
    record = command.to_record()
    assert GameCommand.from_record(record).to_record() == record


@pytest.mark.parametrize("command_list", to_commands_iter(test_files), ids=test_files)
def test_command_serialize(command_list):
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


@pytest.mark.parametrize("command_list", to_commands_iter(test_files), ids=test_files)
def test_command_clean(command_list):
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


@pytest.mark.parametrize("command_list", to_commands_iter(test_files), ids=test_files)
def test_command_state_expand(command_list):
    df = pandas.DataFrame(
        (x.to_record() for x in command_list),
    )
    df.to_csv("command_test_expand.csv")
    df = pandas.read_csv(
        "command_test_expand.csv",
        # converters={'value': norm_value_str},
    )
    # clean up df
    df = df.apply(GameCommand.pandas_columns_clean, axis="columns")
    # extract all states to columns

    column_props = ["sub_scope_id", "property"]
    df_state = df[column_props + ["state"]]
    df_state = df_state.set_index(column_props, append=True)
    df_state = df_state.unstack(level=column_props)
    df_state = df_state.ffill()
    df_state.to_csv("state_fill.csv")
