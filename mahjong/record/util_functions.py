import os
import xml.etree.ElementTree as ET
import pandas
from typing import Iterable

from mahjong.record.reader import from_file, from_url, log_id_from_url
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


def _event_df_iter(events: Iterable[ET.Element], abstract=True):
    for i, event in enumerate(events):
        result = {}
        matched = last_num.match(event.tag)
        if matched:
            tag = matched.group(1)
            result["<tag_extra>"] = matched.group(2)
        else:
            tag = event.tag
        result["<tag>"] = tag
        if matched and abstract:
            pass
        else:
            result.update(event.attrib)
            for k, v in result.items():
                yield {"index": i, "tag": tag, "attr": k, "value": v}


def light_dataframe_from_file(file_path, abstract=True):
    root_element = next(ET.parse(file_path).iter())
    log_file = os.path.split(file_path)[-1]
    log_id, _ = os.path.splitext(log_file)
    df = pandas.DataFrame(_event_df_iter(root_element, abstract))
    df["log_id"] = log_id
    return df
