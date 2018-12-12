from collections import Counter
from time import perf_counter

from distribution import TileDistribution, StaticWall
from pattern.win import NormalTypeWin
from tile.set import TileSet
from tile.utils import tile_set_from_string

if __name__ == '__main__':
    input_hand = tile_set_from_string(input('Input hand:'))
    remain_tiles = TileSet(TileDistribution.ALL_TILES * 4) - input_hand

    remain_tile_distribution = StaticWall(remain_tiles)

    possible_discard = {tile: input_hand - Counter([tile]) for tile in input_hand}

    remain_draw_count = int(input('Remain times for drawing tiles:'))

    win_counter = Counter()

    try_count = input('Experiment times (default 1000):')

    try_count = 1000 if try_count.strip() == '' else int(try_count)

    normal_win = NormalTypeWin()

    seven_pair = NormalTypeWin(melds=0, pairs=7)

    win_patterns = [normal_win, seven_pair]

    elapsed_time = 0

    start = perf_counter()
    task_start_time = start

    for i in range(try_count):
        sample_wall = Counter(remain_tile_distribution.sample(remain_draw_count))

        for tile, hand in possible_discard.items():
            total_hand = hand + sample_wall
            for win_pattern in win_patterns:
                if win_pattern.match(total_hand):
                    win_counter.update([tile])
                    break

        interval = perf_counter() - start
        if interval > 1:
            start = perf_counter()
            elapsed_time = start - task_start_time
            done = i + 1
            eta = elapsed_time / done * try_count - elapsed_time
            print("Experiments %d/%d with %.1fs, ETA %.1fs" % (done, try_count, elapsed_time, eta))

    print("Done in %.1fs!" % (perf_counter() - task_start_time))

    results = sorted(win_counter.items(), key=lambda tup: tup[1], reverse=True)
    print("for input hand <%s>, remain %d draws:" % (input_hand, remain_draw_count))
    for tile, win_count in results:
        print("discard %s: %.2f%% win rate (%d/%d)" % (tile, win_count * 100 / try_count, win_count, try_count))
