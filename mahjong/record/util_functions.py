import xml.etree.ElementTree as ET
import pandas
from typing import Iterable

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


import re

last_num = re.compile(r"^([A-Za-z]+)([0-9]+)$")


def _event_df_iter(events: Iterable[ET.Element]):
    for event in events:
        result = {}
        matched = last_num.match(event.tag)
        if matched:
            result["<tag>"] = matched.group(1)
            result["<tag_extra>"] = matched.group(2)
        else:
            result["<tag>"] = event.tag
        result.update(event.attrib)
        yield result


def light_dataframe_from_file(file_path):
    root_element = next(ET.parse(file_path).iter())
    return pandas.DataFrame(_event_df_iter(root_element))
