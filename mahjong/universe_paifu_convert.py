import os

from mahjong.record.reader import from_url, log_id_from_url
from mahjong.record.universe.command import GameCommand
from mahjong.record.universe.executor import GameExecutor
from mahjong.record.universe.tenhou import to_commands


def main():
    tenhou_link = input("input your tenhou.net paifu link:").strip()
    log_id = log_id_from_url(tenhou_link)
    record = from_url(tenhou_link, timeout=10)
    commands = to_commands(record)
    command_csv_path = "{}_command.csv".format(log_id)
    GameCommand.to_dataframe(commands).to_csv(command_csv_path)
    state_csv_format = "{}_states.csv".format(log_id)
    GameExecutor().execute_as_dataframe(commands).to_csv(state_csv_format)
    print("command and execute state saved to '{}' and '{}'".format(command_csv_path, state_csv_format))
    os.system("pause")

if __name__ == '__main__':
    main()