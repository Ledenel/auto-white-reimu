from ..constant import TENHOU_TILE_CATEGORY, SUIT_ORDER
from mahjong.tile.definition import Tile


def tile_from_tenhou(index):
    """
    tenhou index is numbered as [1m,1m,1m,1m,2m,2m,...,9m,1p,...,9p,1s,...,9s,1z,...,7z,7z,7z,7z]
    numbered first 5m,5s,5p is considered as aka dora.
    """
    color, number, _ = TENHOU_TILE_CATEGORY.category(index)
    return Tile(number + 1, SUIT_ORDER[color])


def tile_to_tenhou_range(tile: Tile):
    color = SUIT_ORDER.index(tile.color)
    number = tile.number - 1
    start_tile, end_tile = (TENHOU_TILE_CATEGORY.index(t) for t in [(color, number, 0), (color, number, 3)])
    return range(start_tile, end_tile + 1)
