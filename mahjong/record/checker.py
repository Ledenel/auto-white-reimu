import os

from mahjong.record.reader import from_url, TenhouRecord
from mahjong.tenhou_record_check import template_env, render_template


class TenhouChecker:
    def __init__(self):
        self.env = template_env("mahjong")
        self.template = self.env.get_template("record_checker_template.html")

    def parse(self, record_or_url, player_index, timeout=10, generate_filename=False):
        url = None
        if isinstance(record_or_url, str):
            record = from_url(record_or_url, timeout)
            url = record_or_url
        elif isinstance(record_or_url, TenhouRecord):
            record = record_or_url
        else:
            raise TypeError("unknown type of {}".format(record_or_url))
        player = record.players[player_index]
        return render_template(player, record, self.template, log_url=url,
                               generate_filename=generate_filename)
