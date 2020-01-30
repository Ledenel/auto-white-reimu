import pandas

from mahjong.record.reader import from_file, from_url
from mahjong.record.universe.command import GameCommand
from mahjong.record.universe.executor import GameExecutor
from mahjong.record.universe.tenhou import to_commands


def command_to_raw_dataframe(commands):
    return pandas.DataFrame(
        (x.to_raw_record() for x in commands),
    )


tenhou_record_from_file = from_file
tenhou_record_from_url = from_url


def parse_dataframe_from_tenhou_record(record, return_state=True, for_serialize=True):
    commands = to_commands(record)
    command_df = GameCommand.to_dataframe(commands, raw=not for_serialize)
    if not return_state:
        return command_df
    state_df = GameExecutor().execute_as_dataframe(commands)
    return command_df, state_df
