from collections import Counter, defaultdict
from time import perf_counter

from mahjong.container.distribution import TileDistribution, StaticWall
from mahjong.container.pattern.win import NormalTypeWin, UniquePairs
from mahjong.container.set import TileSet
from mahjong.container.utils import tile_set_from_string

import numpy as np
from numpy import linalg as LA


def main():
    input_hand = tile_set_from_string(input('Input hand:'))
    while len(input_hand) != 14:
        print("Input hand should be 14 tiles, e.g. 123m067p9s1234567z. " +
              "You have input %s legal tiles" % len(input_hand))
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
    seven_pair = UniquePairs()
    win_patterns = [normal_win, seven_pair]
    avg_win_counter = Counter()
    total_win_count = 0
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
                    total_win_count += 1
                    possible_win_set.add(tile)
                    break

        for tile in possible_win_set:
            avg_win_counter[tile] += 1 / len(possible_win_set)

        for no_win_tile in set(possible_discard.keys()) - possible_win_set:
            for tile in possible_win_set:
                condition_win_counter[no_win_tile][tile] += 1 / len(possible_win_set)

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
    for condition_index, condition_tile in enumerate(solution_tiles):
        self_transfer_rate = avg_win_counter[condition_tile] / total_win_count
        # self_transfer_rate = 0
        for transfer_index, transfer_tile in enumerate(solution_tiles):
            transfer_count = condition_win_counter[condition_tile][transfer_tile]
            condition_count = win_counter[transfer_tile]
            if transfer_count > 0 and condition_count > 0:
                condition_matrix[transfer_index][condition_index] = transfer_count
        condition_matrix[:, condition_index] *= ((1 - self_transfer_rate) / sum(condition_matrix[:, condition_index]))
        condition_matrix[condition_index][condition_index] = self_transfer_rate
    # FIXME: add regularization of Markov possibilities matrix (column sum equals 1).
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
    # results = sorted(win_counter.items(), key=lambda tup: tup[1], reverse=True)
    results = sorted(pick_rank_map.items(), key=lambda tup: tup[1][1], reverse=True)
    print("for input hand <%s>, remain %d draws:" % (input_hand, remain_draw_count))
    for tile, (rough, infinite) in results:
        # rough, infinite = pick_rank_map[tile]
        win_count = win_counter[tile]
        print("discard %s: %.2f%% win rate (%d/%d), %.2f%% rough pick rate, %.2f%% accurate pick rate" %
              (tile,
               win_count * 100 / try_count,
               win_count, try_count
               , rough * 100, infinite * 100))


if __name__ == '__main__':
    main()
