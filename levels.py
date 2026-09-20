import random

FIXED_LEVELS = [
    # 第 1 关
    [
        ['R', 0, 0, 'U'],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        ['D', 0, 0, 'L'],
    ],
    # 第 2 关
    [
        ['R', 0, 'U', 0],
        [0, 0, 0, 0],
        ['D', 0, 0, 'L'],
        [0, 'R', 0, 'U'],
    ],
    # 第 3 关
    [
        ['R', 0, 0, 'D'],
        [0, 'U', 0, 0],
        [0, 0, 'L', 0],
        ['D', 0, 0, 'R'],
    ],
    # 第 4 关：5x5
    [
        ['R', 0, 0, 0, 'D'],
        [0, 0, 'U', 0, 0],
        [0, 'D', 'R', 'U', 0],
        [0, 0, 'L', 0, 0],
        ['U', 0, 0, 0, 'R'],
    ],
    # 第 5 关：6x6
    [
        ['U', 0, 'R', 0, 'D', 0],
        [0, 'U', 0, 'D', 0, 'L'],
        ['D', 0, 0, 0, 'R', 0],
        [0, 'D', 0, 'R', 0, 'R'],
        [0, 0, 'D', 0, 0, 'U'],
        ['R', 0, 0, 'D', 0, 'R'],
    ],
]


def _has_opposite_in_line(board, rows, cols, r, c, d):
    """检查在 (r,c) 放方向 d 后，是否和同行/同列已有箭头面对面"""
    opposite = {'U': 'D', 'D': 'U', 'L': 'R', 'R': 'L'}[d]
    # 同行检查：往左找有没有 R（朝右），往右找有没有 L（朝左）
    if d in ('L', 'R'):
        if d == 'R':
            # 右边不能有 L（面对面）
            for cc in range(c + 1, cols):
                if board[r][cc] == 'L':
                    return True
        else:
            for cc in range(0, c):
                if board[r][cc] == 'R':
                    return True
    # 同列检查：往上找有没有 D，往下找有没有 U
    if d in ('U', 'D'):
        if d == 'U':
            for rr in range(0, r):
                if board[rr][c] == 'D':
                    return True
        else:
            for rr in range(r + 1, rows):
                if board[rr][c] == 'U':
                    return True
    return False


def gen_timed_level(rows=7, cols=7, density=0.5):
    """生成第 6 关：7x7 随机箭头，避免面对面，保证有解"""
    board = [[0] * cols for _ in range(rows)]
    candidates = []
    for r in range(rows):
        for c in range(cols):
            if random.random() > density:
                continue
            # 边缘的箭头强制朝外
            if r == 0:
                d = 'U'
            elif r == rows - 1:
                d = 'D'
            elif c == 0:
                d = 'L'
            elif c == cols - 1:
                d = 'R'
            else:
                d = random.choice(['U', 'D', 'L', 'R'])
            candidates.append((r, c, d))

    random.shuffle(candidates)
    for r, c, d in candidates:
        if board[r][c] != 0:
            continue
        if _has_opposite_in_line(board, rows, cols, r, c, d):
            continue
        board[r][c] = d
    return board


LEVELS = FIXED_LEVELS + [gen_timed_level()]