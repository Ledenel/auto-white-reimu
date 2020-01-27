from mahjong.record.universe.executor import GameExecutor
from tests.uni_record.test_event_definition import get_test_commands
import pandas as pd

commands = get_test_commands()


def test_execute():
    assert len(list(GameExecutor().execute(commands))) > 1

# TODO: add export execute to csv (flatten for TransferDict).

def test_execute_export():
    df = pd.DataFrame(x.flatten() for x in GameExecutor().execute(commands))
    df.columns = pd.MultiIndex.from_tuples(df.columns)
    df.to_csv("state_tenhou.csv")
    assert len(df) > 1