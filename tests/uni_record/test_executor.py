from mahjong.record.universe.executor import GameExecutor
from tests.uni_record.test_event_definition import get_test_commands

commands = get_test_commands()


def test_execute():
    assert len(list(GameExecutor().execute(commands))) > 1


