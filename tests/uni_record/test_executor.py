import pandas as pd
import pytest

from mahjong.record.universe.executor import GameExecutor, replace_enum_values
from tests.uni_record.paifu_list import test_files
from tests.uni_record.test_event_definition import to_commands_iter, file_to_commands


@pytest.mark.parametrize("file_name", test_files)
def test_execute(file_name):
    commands = file_to_commands(file_name)
    assert len(list(GameExecutor(strict_mode=True).execute(commands))) > 1


@pytest.mark.parametrize("file_name", test_files)
def test_execute_export(file_name):
    commands = file_to_commands(file_name)
    df = pd.DataFrame(x.flatten() for x in GameExecutor().execute(commands))
    df.columns = pd.MultiIndex.from_tuples(df.columns)
    df.to_csv("state_tenhou.csv")
    assert len(df) > 1


@pytest.mark.parametrize("file_name", test_files)
def test_execute_enum_transform(file_name):
    commands = file_to_commands(file_name)
    df = pd.DataFrame(x.flatten() for x in GameExecutor().execute(commands))
    old_columns = df.columns
    df.columns = pd.MultiIndex.from_tuples(df.columns)
    df.to_csv("state_tenhou_2.csv")
    df_new = pd.read_csv("state_tenhou_2.csv", header=[0, 1, 2], skipinitialspace=True)
    df_rename = df_new.rename(columns=replace_enum_values)
    assert set(old_columns).issubset(set(df_rename.columns))


@pytest.mark.parametrize("file_name", test_files)
def test_read_clean_csv(file_name):
    commands = file_to_commands(file_name)
    df = pd.DataFrame(x.flatten() for x in GameExecutor().execute(commands))
    df.columns = pd.MultiIndex.from_tuples(df.columns)
    df.to_csv("state_tenhou_3.csv")
    GameExecutor.read_clean_csv("state_tenhou_3.csv")
