from urllib.parse import unquote

from .utils.constant import DRAW_REGEX, DISCARD_REGEX, RANKS
from .utils.value.meld import meld_from


def is_event_triggered_by_player(event, player_index, tag_name):
    return event.tag == tag_name and int(event.attrib["who"]) == player_index


class TenhouPlayer:
    def __init__(self, index, name_encoded, level, rate, sex):
        self.sex = sex

        self.rate = rate
        self.level = level
        self.name = unquote(name_encoded)
        self.index = index

    def __str__(self):
        return "%s %s R%.2f" % (
            self.name,
            RANKS[self.level],
            self.rate
        )

    def clear(self):
        pass

    def is_draw(self, event):
        regex = DRAW_REGEX[self.index]
        return regex.match(event.tag)

    def draw_tile_index(self, draw_event):
        regex = DRAW_REGEX[self.index]
        return int(regex.match(draw_event.tag).group(1))

    def is_discard(self, event):
        regex = DISCARD_REGEX[self.index]
        return regex.match(event.tag)

    def discard_tile_index(self, discard_event):
        regex = DISCARD_REGEX[self.index]
        return int(regex.match(discard_event.tag).group(1))

    def is_open_hand(self, event):
        return is_event_triggered_by_player(event, self.index, "N")

    def is_player_choice(self, event):
        return self.is_discard(event) or self.is_open_hand(event) or self.is_win(event)

    def opened_hand_type(self, event):
        return meld_from(event)

    def is_reach(self, event):
        return is_event_triggered_by_player(event, self.index, "REACH")

    def is_win(self, event):
        return is_event_triggered_by_player(event, self.index, "AGARI")
