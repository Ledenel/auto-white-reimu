from .constant import DRAW_ALL_REGEX, DISCARD_ALL_REGEX


def is_game_init(event):
    return event.tag == "INIT"


def is_open_hand(event):
    return event.tag == "N"


def is_dora_indicator_event(event):
    return event.tag == "DORA"


def is_somebody_win_game(event):
    return event.tag == "AGARI"


def is_nobody_win_game(event):
    return event.tag == "RYUUKYOKU"


def draw_value(event):
    matched = DRAW_ALL_REGEX.match(event.tag)
    if matched:
        return int(matched.group(1))


def discard_value(event):
    matched = DISCARD_ALL_REGEX.match(event.tag)
    if matched:
        return int(matched.group(1))
