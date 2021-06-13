"""
    先手(黒): 1, 後手（白）: -1
    どちらかが合法手無くなると終了。その時点で石の多い方が勝利
    よって合法手の無い側が勝つこともある
"""
import functools
import copy
import json
import random

import numpy as np


N_COLS = N_ROWS = 6

ACTION_SPACE = N_ROWS * N_COLS


def xy_to_idx(row, col):
    return N_ROWS * row + col


def idx_to_xy(i):
    x, y = i // N_ROWS, i % N_ROWS
    return x, y


def encode_state(state: list, current_player: int):
    """ NN入力用の整形処理
    """
    state = np.array(state).reshape(N_ROWS, N_COLS)
    player = (state == current_player)
    opponent = (state == -current_player)
    x = np.stack([player, opponent], axis=2).astype(np.float32)

    return x


def get_initial_state():

    state = [0] * (N_ROWS * N_COLS)

    state[xy_to_idx(N_ROWS // 2 - 1, N_COLS // 2 - 1)] = 1
    state[xy_to_idx(N_ROWS // 2, N_COLS // 2)] = 1
    state[xy_to_idx(N_ROWS // 2 - 1, N_COLS // 2)] = -1
    state[xy_to_idx(N_ROWS // 2, N_COLS // 2 - 1)] = -1

    return state


@functools.lru_cache(maxsize=2048)
def get_directions(i):

    _, col = idx_to_xy(i)

    up = list(range(i, -1, -N_COLS))[1:]
    down = list(range(i, N_ROWS*N_COLS, N_COLS))[1:]

    left = list(reversed(range(i-col, i, 1)))
    right = list(range(i+1, i + N_COLS - col))

    ul = list(range(i, -1, -N_COLS-1))[1:col+1]
    ur = list(range(i, -1, -N_COLS+1))[1:N_COLS - col]

    ll = list(range(i, N_ROWS * N_COLS, N_COLS-1))[1:col+1]
    lr = list(range(i, N_ROWS * N_COLS, N_COLS+1))[1:N_COLS - col]

    return [up, down, left, right, ul, ur, ll, lr]


def is_valid_action(state: list, action: int, player: int):

    #: すでに石がある
    if state[action] != 0:
        return False

    directions = get_directions(action)

    for direction in directions:
        stones = [state[i] for i in direction]
        if player in stones and -player in stones:
            stones = stones[:stones.index(player)]
            if stones and all(i == -player for i in stones):
                return True

    return False


@functools.lru_cache(maxsize=2048)
def _get_valid_actions(state_str: list, player: int):

    state = json.loads(state_str)

    valid_actions = [action for action in range(N_ROWS * N_COLS)
                     if is_valid_action(state, action, player)]

    return valid_actions


def get_valid_actions(state: list, player: int):
    state_str = json.dumps(state)
    return _get_valid_actions(state_str, player)


def step(state: list, action: int, player: int):

    #assert is_valid_action(state, action, player)

    next_state = copy.deepcopy(state)

    directions = get_directions(action)

    for direction in directions:
        stones = [state[i] for i in direction]
        if player in stones and -player in stones:
            idx = stones.index(player)
            stones = stones[:idx]
            if stones and all(i == -player for i in stones):
                for i in direction[:idx]:
                    next_state[i] = player

    next_state[action] = player

    #: 相手に合法手なしで終了
    valid_actions = get_valid_actions(next_state, -player)

    done = False if valid_actions else True

    return next_state, done


def is_done(state, player):

    valid_actions = get_valid_actions(state, player)

    done = False if valid_actions else True

    return done


def get_result(state: list):

    black_stones = sum([1 for i in state if i == 1])
    white_stones = sum([1 for i in state if i == -1])

    if black_stones > white_stones:
        return 1, -1
    elif white_stones > black_stones:
        return -1, 1
    elif black_stones == white_stones:
        return 0, 0
    else:
        raise Exception("Unexpected error")


def greedy_action(state: list, player: int, epsilon=0.):

    valid_actions = get_valid_actions(state, player)

    if random.random() > epsilon:
        best_action = None
        best_score = 0
        for action in valid_actions:
            next_state, done = step(state, action, player)
            _, score = count_stone(next_state)
            if score > best_score:
                best_score = score
                best_action = action

        return best_action

    else:
        action = random.choice(valid_actions)
        return action


def count_stone(state: list):
    first = sum([1 for i in state if i == 1])
    second = sum([1 for i in state if i == -1])
    return (first, second)