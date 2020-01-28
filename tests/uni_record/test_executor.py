import pandas as pd

from mahjong.record.universe.executor import GameExecutor, replace_enum_values
from tests.uni_record.test_event_definition import get_test_commands

commands = get_test_commands()


def test_execute():
    assert len(list(GameExecutor().execute(commands))) > 1


# TODO: add export execute to csv (flatten for TransferDict).

def test_execute_export():
    df = pd.DataFrame(x.flatten() for x in GameExecutor().execute(commands))
    df.columns = pd.MultiIndex.from_tuples(df.columns)
    df.to_csv("state_tenhou.csv")
    assert len(df) > 1


def test_execute_enum_transform():
    df = pd.DataFrame(x.flatten() for x in GameExecutor().execute(commands))
    old_columns = df.columns
    df.columns = pd.MultiIndex.from_tuples(df.columns)
    df.to_csv("state_tenhou_2.csv")
    df_new = pd.read_csv("state_tenhou_2.csv", header=[0,1,2])
    df_rename = df_new.rename(columns=replace_enum_values)
    assert set(old_columns).issubset(set(df_rename.columns))
