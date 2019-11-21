import re

from ..category import SubCategory, MixedCategory

DRAW_INDICATOR = ['T', 'U', 'V', 'W']
DRAW_ALL_REGEX = re.compile(r"^[%s]([0-9]+)$" % ("".join(DRAW_INDICATOR)))
DRAW_GROUPED_REGEX = re.compile(r"^([%s])([0-9]+)$" % ("".join(DRAW_INDICATOR)))
DISCARD_INDICATOR = ['D', 'E', 'F', 'G']
DISCARD_ALL_REGEX = re.compile(r"^[%s]([0-9]+)$" % ("".join(DISCARD_INDICATOR)))
DISCARD_GROUPED_REGEX = re.compile(r"^([%s])([0-9]+)$" % ("".join(DISCARD_INDICATOR)))

SUIT_ORDER = 'mpsz'
RANKS = [
    '新人',
    '9級',
    '8級',
    '7級',
    '6級',
    '5級',
    '4級',
    '3級',
    '2級',
    '1級',
    '初段',
    '二段',
    '三段',
    '四段',
    '五段',
    '六段',
    '七段',
    '八段',
    '九段',
    '十段',
    '天鳳位'
]
DRAWN_TYPES = {
    "kaze4": "四風連打",
    "yao9": "九種九牌",
    "ron3": "三家和了",
    "reach4": "四家立直",
    "kan4": "四槓散了",
    "nm": "流局滿貫"
}

SCORE_PATTERN = [
    # // 一飜
    "門前清自摸和",
    "立直",
    "一発",
    "槍槓",
    "嶺上開花",
    "海底摸月",
    "河底撈魚",
    "平和",
    "断幺九",
    "一盃口",
    "自風 東",
    "自風 南",
    "自風 西",
    "自風 北",
    "場風 東",
    "場風 南",
    "場風 西",
    "場風 北",
    "役牌 白",
    "役牌 發",
    "役牌 中",

    # // 二飜
    "両立直",
    "七対子",
    "混全帯幺九",
    "一気通貫",
    "三色同順",
    "三色同刻",
    "三槓子",
    "対々和",
    "三暗刻",
    "小三元",
    "混老頭",

    # //  三飜
    "二盃口",
    "純全帯幺九",
    "混一色",

    # //  六飜
    "清一色",

    # //  満貫
    "人和",

    # //  役満
    "天和",
    "地和",
    "大三元",
    "四暗刻",
    "四暗刻単騎",
    "字一色",
    "緑一色",
    "清老頭",
    "九蓮宝燈",
    "純正九蓮宝燈",
    "国士無双",
    "国士無双１３面",
    "大四喜",
    "小四喜",
    "四槓子",

    "ドラ",
    "裏ドラ",
    "赤ドラ",
]
DRAW_REGEX = [re.compile(r"^%s([0-9]+)" % draw) for draw in DRAW_INDICATOR]
DISCARD_REGEX = [re.compile(r"^%s([0-9]+)" % draw) for draw in DISCARD_INDICATOR]
API_URL_TEMPLATE = 'http://e.mjv.jp/0/log/?{0}'
TENHOU_TILE_CATEGORY = MixedCategory([SubCategory(9, 4)] * 3 + [SubCategory(7, 4)])
