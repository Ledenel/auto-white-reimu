import os

import pandas

from mahjong.record.reader import from_url, log_id_from_url
from mahjong.record.universe.command import GameCommand
from mahjong.record.universe.executor import GameExecutor
from mahjong.record.universe.tenhou import to_commands, to_command_records


def main():
    tenhou_link = input("input your tenhou.net paifu link:").strip()
    log_id = log_id_from_url(tenhou_link)
    record = from_url(tenhou_link, timeout=10)
    command_csv_path = "{}_command.csv".format(log_id)
    pandas.DataFrame(to_command_records(record)).to_csv(command_csv_path)
    print("command and state saved to '{}'".format(command_csv_path))
    os.system("pause")

if __name__ == '__main__':
    main()