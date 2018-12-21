from collections import Counter, defaultdict
from time import perf_counter

from container.distribution import TileDistribution, StaticWall
from container.pattern.win import NormalTypeWin
from container.set import TileSet
from container.utils import tile_set_from_string

import numpy as np
from numpy import linalg as LA

if __name__ == '__main__':
    input_hand = tile_set_from_string(input('Input hand:'))
    remain_tiles = TileSet(TileDistribution.ALL_TILES * 4) - input_hand

    remain_tile_distribution = StaticWall(remain_tiles)

    possible_discard = {tile: input_hand - TileSet([tile]) for tile in input_hand}

    remain_draw_count = int(input('Remain times for drawing tiles:'))

    win_counter = Counter()

    condition_win_counter = defaultdict(Counter)

    try_count = input('Experiment times (default 1000):')

    try_count = 1000 if try_count.strip() == '' else int(try_count)

    normal_win = NormalTypeWin()

    seven_pair = NormalTypeWin(melds=0, pairs=7)

    win_patterns = [normal_win, seven_pair]

    elapsed_time = 0

    start = perf_counter()
    task_start_time = start

    for i in range(try_count):
        sample_wall = TileSet(remain_tile_distribution.sample(remain_draw_count))

        possible_win_set = set()

        for tile, hand in possible_discard.items():
            total_hand = hand + sample_wall
            for win_pattern in win_patterns:
                if win_pattern.match(total_hand):
                    win_counter.update([tile])
                    possible_win_set.add(tile)
                    break

        for possible_win_tile in possible_win_set:
            condition_win_counter[possible_win_tile].update((possible_win_set - {possible_win_tile}))

        interval = perf_counter() - start
        if interval > 1:
            start = perf_counter()
            elapsed_time = start - task_start_time
            done = i + 1
            eta = elapsed_time / done * try_count - elapsed_time
            print("Experiments %d/%d with %.1fs, ETA %.1fs" % (done, try_count, elapsed_time, eta))

    solution_count = len(possible_discard)

    print("Done in %.1fs!" % (perf_counter() - task_start_time))

    solution_tiles = list(possible_discard.keys())

    min_rate = 1 / try_count

    condition_matrix = np.full((solution_count, solution_count), min_rate, dtype=np.double)

    for transfer_index, transfer_tile in enumerate(solution_tiles):
        for condition_index, condition_tile in enumerate(solution_tiles):
            transfer_count = condition_win_counter[condition_tile][transfer_tile]
            condition_count = win_counter[condition_tile]
            if transfer_count > 0 and condition_count > 0:
                condition_matrix[transfer_index][condition_index] = transfer_count / condition_count

    # FIXME: add regularization of Markov possibilities matrix (row sum equals 1).

    # FIXME: define proper self retain possibilities.

    condition_matrix = np.matrix(condition_matrix)

    unbiased_distribution = np.full((solution_count,), 1 / solution_count)

    rough_pick = condition_matrix * (unbiased_distribution.reshape(1, -1).transpose())

    rough_pick = np.array(rough_pick).reshape(-1)

    eigenvalues, eigenvectors = LA.eig(condition_matrix)

    nearest_one_index = abs(eigenvalues - 1).argmin()

    infinite_pick = eigenvectors[:, nearest_one_index]

    infinite_pick = np.array(infinite_pick).reshape(-1)

    infinite_pick /= sum(infinite_pick)

    pick_rank_map = {tile: (rough, infinite) for tile, rough, infinite in
                     zip(solution_tiles, rough_pick, infinite_pick)}

    results = sorted(win_counter.items(), key=lambda tup: tup[1], reverse=True)
    print("for input hand <%s>, remain %d draws:" % (input_hand, remain_draw_count))
    for tile, win_count in results:
        rough, infinite = pick_rank_map[tile]
        print("discard %s: %.2f%% win rate (%d/%d), %.2f%% rough pick rate, %.2f%% accurate pick rate" %
              (tile,
               win_count * 100 / try_count,
               win_count, try_count
               , rough * 100, infinite * 100))