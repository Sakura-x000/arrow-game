import pygame
import sys
import math
import json
import os
import random
from levels import LEVELS, FIXED_LEVELS, gen_timed_level

pygame.init()

CELL = 65
TOP_H = 190
MARGIN = 140

SELECT_W = 620
SELECT_H = 700

COLS = 4
ROWS = 4
BOARD_W = CELL * COLS
BOARD_H = CELL * ROWS
BOARD_X = MARGIN
BOARD_Y = TOP_H + 30
WIDTH = BOARD_W + MARGIN * 2
HEIGHT = BOARD_Y + BOARD_H + MARGIN

SAVE_FILE = "save.json"

TIMED_LEVEL_INDEX = 5
TIMED_TOTAL_MS = 30000

BG_TOP = (30, 40, 70)
BG_BOTTOM = (45, 55, 95)
CARD_BG = (50, 62, 105)
CARD_LIGHT = (65, 80, 130)
CARD_SOFT = (75, 92, 145)
WHITE = (255, 255, 255)
BLACK = (20, 25, 40)
DARK = (220, 230, 245)
GRID_LINE = (80, 95, 140)
GRAY = (120, 135, 170)
DARK_GRAY = (90, 105, 140)
BLUE = (90, 150, 230)
LIGHT_BLUE = (120, 175, 245)
DEEP_BLUE = (60, 110, 200)
RED = (240, 100, 100)
LIGHT_RED = (250, 130, 130)
GREEN = (80, 200, 140)
LIGHT_GREEN = (110, 220, 165)
YELLOW = (255, 210, 70)
PURPLE = (160, 120, 230)
LIGHT_PURPLE = (190, 150, 250)
ORANGE = (250, 170, 80)
LIGHT_ORANGE = (255, 200, 130)

ARROW_COLORS = [
    (240, 110, 110),
    (100, 160, 245),
    (80, 210, 150),
    (255, 190, 70),
    (180, 140, 240),
    (250, 140, 190),
]

FONT = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 22)
BIG_FONT = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 40)
HUGE_FONT = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 46)
SMALL_FONT = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 18)
TINY_FONT = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 15)

screen = None
clock = pygame.time.Clock()

DIRS = {
    'U': (-1, 0),
    'D': (1, 0),
    'L': (0, -1),
    'R': (0, 1),
}

STATE_SELECT = "select"
STATE_PLAY = "play"
STATE_WIN = "win"
STATE_LOSE = "lose"
STATE_PAUSE = "pause"
STATE_CONFIRM = "confirm"
STATE_INTRO = "intro"

state = STATE_SELECT
level_index = 0
board = []
mistakes = 0
MAX_MISTAKES = 3
animating = []
shake = None
unlocked = 1
level_stars = [0, 0, 0, 0, 0, 0]
level_times = [0, 0, 0, 0, 0, 0]

level_start_ticks = 0
elapsed_before_pause = 0
pause_start_ticks = 0
is_paused = False
final_time_ms = 0
final_score = 0

timed_remaining_ms = TIMED_TOTAL_MS
score = 0
combo = 0
best_scores = [0, 0, 0, 0, 0, 0]
last_tick_ms = 0

MAX_UNDO = 3
undo_left = MAX_UNDO
undo_stack = []

MAX_HINT = 3
hint_left = MAX_HINT
hint_cell = None
hint_timer = 0

mouse_pos = (0, 0)
pending_level = 0

level_btns = []
pause_btn = None
undo_btn = None
hint_btn = None
restart_btn = None
back_btn_play = None

resume_btn = None
save_quit_btn = None
back_select_btn = None

next_btn = None
back_btn_win = None
retry_btn = None
back_btn_lose = None

continue_btn = None
restart_btn2 = None


def _build_play_buttons(rows, cols, w, h):
    global pause_btn, undo_btn, hint_btn, restart_btn, back_btn_play
    global resume_btn, save_quit_btn, back_select_btn
    global next_btn, back_btn_win, retry_btn, back_btn_lose

    pad = 20
    btn_w = 95
    btn_h = 34
    gap = 8
    row1_y = 88
    row2_y = 128

    back_btn_play = pygame.Rect(w - pad - btn_w, row2_y, btn_w, btn_h)
    restart_btn = pygame.Rect(w - pad - btn_w * 2 - gap, row2_y, btn_w, btn_h)

    hint_btn = pygame.Rect(w - pad - btn_w, row1_y, btn_w, btn_h)
    undo_btn = pygame.Rect(w - pad - btn_w * 2 - gap, row1_y, btn_w, btn_h)
    pause_btn = pygame.Rect(w - pad - btn_w * 3 - gap * 2, row1_y, btn_w, btn_h)

    resume_btn = pygame.Rect(w // 2 - 150, 320, 300, 50)
    save_quit_btn = pygame.Rect(w // 2 - 150, 390, 300, 50)
    back_select_btn = pygame.Rect(w // 2 - 150, 460, 300, 50)

    next_btn = pygame.Rect(w // 2 + 15, 450, 130, 48)
    back_btn_win = pygame.Rect(w // 2 - 145, 450, 130, 48)
    retry_btn = pygame.Rect(w // 2 - 145, 450, 130, 48)
    back_btn_lose = pygame.Rect(w // 2 + 15, 450, 130, 48)


def _build_select_buttons(w):
    global level_btns, continue_btn, restart_btn2
    level_btns = []

    btn_w = 160
    btn_h = 130
    gap_x = 30
    gap_y = 40

    cols = 3
    total_w = btn_w * cols + gap_x * (cols - 1)
    start_x = w // 2 - total_w // 2
    start_y = 260

    for i in range(len(LEVELS)):
        r = i // cols
        c = i % cols
        bx = start_x + c * (btn_w + gap_x)
        by = start_y + r * (btn_h + gap_y)
        level_btns.append(pygame.Rect(bx, by, btn_w, btn_h))

    continue_btn = pygame.Rect(w // 2 - 160, 380, 150, 50)
    restart_btn2 = pygame.Rect(w // 2 + 10, 380, 150, 50)


def apply_level_size(rows, cols):
    global COLS, ROWS, BOARD_W, BOARD_H, BOARD_X, BOARD_Y
    global WIDTH, HEIGHT, screen

    COLS = cols
    ROWS = rows
    BOARD_W = CELL * COLS
    BOARD_H = CELL * ROWS
    BOARD_X = MARGIN
    BOARD_Y = TOP_H + 30
    WIDTH = BOARD_W + MARGIN * 2
    HEIGHT = BOARD_Y + BOARD_H + MARGIN

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    _build_play_buttons(rows, cols, WIDTH, HEIGHT)


def apply_select_size():
    global WIDTH, HEIGHT, screen, COLS, ROWS
    COLS = 0
    ROWS = 0
    WIDTH = SELECT_W
    HEIGHT = SELECT_H
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    _build_select_buttons(WIDTH)


apply_level_size(4, 4)


def has_save():
    return os.path.exists(SAVE_FILE)


def read_save():
    if not has_save():
        return None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def write_save():
    data = {
        "level_index": level_index,
        "board": board,
        "mistakes": mistakes,
        "elapsed_ms": get_elapsed_ms(),
        "level_stars": level_stars,
        "level_times": level_times,
        "unlocked": unlocked,
        "undo_left": undo_left,
        "undo_stack": undo_stack,
        "hint_left": hint_left,
        "best_scores": best_scores,
        "timed_remaining_ms": timed_remaining_ms,
        "score": score,
        "combo": combo,
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def delete_save():
    if has_save():
        try:
            os.remove(SAVE_FILE)
        except Exception:
            pass


def get_elapsed_ms():
    if is_paused:
        return elapsed_before_pause
    return elapsed_before_pause + (pygame.time.get_ticks() - level_start_ticks)


def format_time(ms):
    total = ms // 1000
    return f"{total} 秒"


def start_timer(initial_ms=0):
    global level_start_ticks, elapsed_before_pause, is_paused
    level_start_ticks = pygame.time.get_ticks()
    elapsed_before_pause = initial_ms
    is_paused = False


def pause_timer():
    global elapsed_before_pause, is_paused, pause_start_ticks
    if not is_paused:
        elapsed_before_pause += pygame.time.get_ticks() - level_start_ticks
        pause_start_ticks = pygame.time.get_ticks()
        is_paused = True


def resume_timer():
    global level_start_ticks, is_paused
    if is_paused:
        level_start_ticks = pygame.time.get_ticks()
        is_paused = False


def set_timer(ms):
    global level_start_ticks, elapsed_before_pause, is_paused
    level_start_ticks = pygame.time.get_ticks()
    elapsed_before_pause = ms
    is_paused = False


def load_level(idx, saved=None):
    global board, mistakes, animating, shake, level_stars, level_times, unlocked
    global undo_left, undo_stack, hint_left, hint_cell, hint_timer
    global timed_remaining_ms, score, combo, last_tick_ms
    global final_time_ms, final_score

    if saved is not None:
        data_board = saved["board"]
        rows = len(data_board)
        cols = len(data_board[0])
        apply_level_size(rows, cols)
        board = [[cell for cell in row] for row in data_board]
        mistakes = saved["mistakes"]
        start_timer(saved.get("elapsed_ms", 0))
        if "level_stars" in saved:
            level_stars = saved["level_stars"]
        if "level_times" in saved:
            level_times = saved["level_times"]
        if "unlocked" in saved:
            unlocked = saved["unlocked"]
        undo_left = saved.get("undo_left", MAX_UNDO)
        undo_stack = saved.get("undo_stack", [])
        hint_left = saved.get("hint_left", MAX_HINT)
        if "best_scores" in saved:
            best_scores = saved["best_scores"]
        if "timed_remaining_ms" in saved:
            timed_remaining_ms = saved["timed_remaining_ms"]
        if "score" in saved:
            score = saved["score"]
        if "combo" in saved:
            combo = saved["combo"]
    else:
        data = LEVELS[idx]
        rows = len(data)
        cols = len(data[0])
        apply_level_size(rows, cols)
        board = [[cell for cell in row] for row in data]
        mistakes = 0
        start_timer(0)
        undo_left = MAX_UNDO
        undo_stack = []
        hint_left = MAX_HINT
        if idx == TIMED_LEVEL_INDEX:
            timed_remaining_ms = TIMED_TOTAL_MS
            score = 0
            combo = 0
    animating = []
    shake = None
    hint_cell = None
    hint_timer = 0
    last_tick_ms = 0


def push_undo():
    undo_stack.append({
        "board": [[cell for cell in row] for row in board],
        "mistakes": mistakes,
        "elapsed_ms": get_elapsed_ms(),
    })
    if len(undo_stack) > 50:
        undo_stack.pop(0)


def do_undo():
    global board, mistakes, undo_left
    if undo_left <= 0 or not undo_stack:
        return
    state_data = undo_stack.pop()
    board = [[cell for cell in row] for row in state_data["board"]]
    mistakes = state_data["mistakes"]
    set_timer(state_data["elapsed_ms"])
    undo_left -= 1


def find_free_arrows():
    result = []
    for r in range(ROWS):
        for c in range(COLS):
            cell = board[r][c]
            if cell != 0 and not is_blocked(r, c, cell):
                result.append((r, c))
    return result


def do_hint():
    global hint_left, hint_cell, hint_timer
    if hint_left <= 0:
        return
    free = find_free_arrows()
    if not free:
        return
    hint_cell = random.choice(free)
    hint_timer = 72
    hint_left -= 1


def remaining_arrows():
    return sum(1 for row in board for cell in row if cell != 0)


def is_blocked(r, c, direction):
    dr, dc = DIRS[direction]
    nr, nc = r + dr, c + dc
    while 0 <= nr < ROWS and 0 <= nc < COLS:
        if board[nr][nc] != 0:
            return True
        nr += dr
        nc += dc
    return False


def arrow_color(r, c, direction):
    idx = (r * 7 + c * 3 + ord(direction)) % len(ARROW_COLORS)
    return ARROW_COLORS[idx]


def draw_arrow(surface, cx, cy, direction, color, scale=1.0, alpha=255):
    s = scale
    half_shaft = 5 * s
    half_head = 13 * s
    back = -26 * s
    neck = 4 * s
    tip = 32 * s

    if direction == 'R':
        shaft = [(cx + back, cy - half_shaft), (cx + neck, cy - half_shaft),
                 (cx + neck, cy + half_shaft), (cx + back, cy + half_shaft)]
        head = [(cx + neck, cy - half_head), (cx + tip, cy),
                (cx + neck, cy + half_head)]
    elif direction == 'L':
        shaft = [(cx - back, cy - half_shaft), (cx - neck, cy - half_shaft),
                 (cx - neck, cy + half_shaft), (cx - back, cy + half_shaft)]
        head = [(cx - neck, cy - half_head), (cx - tip, cy),
                (cx - neck, cy + half_head)]
    elif direction == 'U':
        shaft = [(cx - half_shaft, cy - back), (cx - half_shaft, cy - neck),
                 (cx + half_shaft, cy - neck), (cx + half_shaft, cy - back)]
        head = [(cx - half_head, cy - neck), (cx, cy - tip),
                (cx + half_head, cy - neck)]
    else:
        shaft = [(cx - half_shaft, cy + back), (cx - half_shaft, cy + neck),
                 (cx + half_shaft, cy + neck), (cx + half_shaft, cy + back)]
        head = [(cx - half_head, cy + neck), (cx, cy + tip),
                (cx + half_head, cy + neck)]

    if alpha < 255:
        temp = pygame.Surface((CELL * 3, CELL * 3), pygame.SRCALPHA)
        offset = CELL * 1.5
        s_pts = [(p[0] - cx + offset, p[1] - cy + offset) for p in shaft]
        h_pts = [(p[0] - cx + offset, p[1] - cy + offset) for p in head]
        c = (*color, alpha)
        pygame.draw.polygon(temp, c, s_pts)
        pygame.draw.polygon(temp, c, h_pts)
        surface.blit(temp, (cx - offset, cy - offset))
    else:
        pygame.draw.polygon(surface, color, shaft)
        pygame.draw.polygon(surface, color, head)


def draw_star(surface, cx, cy, size, filled, color=YELLOW):
    pts = []
    for i in range(10):
        angle = math.radians(-90 + i * 36)
        r = size if i % 2 == 0 else size * 0.45
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    if filled:
        pygame.draw.polygon(surface, color, pts)
    else:
        pygame.draw.polygon(surface, (100, 115, 155), pts)


def draw_button(surface, rect, text, base_color, hover_color, text_color=WHITE,
                font=None, radius=12, disabled=False):
    hover = rect.collidepoint(mouse_pos) and not disabled
    if disabled:
        color = (70, 80, 115)
    else:
        color = hover_color if hover else base_color
    shadow_rect = rect.move(2, 2)
    sh = pygame.Surface((shadow_rect.width, shadow_rect.height),
                        pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 60), sh.get_rect(), border_radius=radius)
    surface.blit(sh, shadow_rect.topleft)
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if font is None:
        font = FONT
    txt = font.render(text, True, text_color)
    surface.blit(txt, (rect.x + rect.width // 2 - txt.get_width() // 2,
                       rect.y + rect.height // 2 - txt.get_height() // 2))


def draw_bg():
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(BG_TOP[0] * (1 - ratio) + BG_BOTTOM[0] * ratio)
        g = int(BG_TOP[1] * (1 - ratio) + BG_BOTTOM[1] * ratio)
        b = int(BG_TOP[2] * (1 - ratio) + BG_BOTTOM[2] * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
    for i in range(12):
        angle = i * math.pi / 6
        px = WIDTH // 2 + int(260 * math.cos(angle))
        py = HEIGHT // 2 + int(260 * math.sin(angle))
        if 0 < px < WIDTH and 0 < py < HEIGHT:
            pygame.draw.circle(screen, (60, 75, 120), (px, py), 3)


def draw_card(surface, rect, color, radius=16, shadow=True):
    if shadow:
        shadow_rect = rect.move(3, 3)
        s = pygame.Surface((shadow_rect.width, shadow_rect.height),
                           pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, 50), s.get_rect(), border_radius=radius)
        surface.blit(s, shadow_rect.topleft)
    pygame.draw.rect(surface, color, rect, border_radius=radius)


def get_intro_rects():
    pw, ph = 480, 420
    popup = pygame.Rect(WIDTH // 2 - pw // 2, HEIGHT // 2 - ph // 2,
                        pw, ph)
    btn_w, btn_h = 150, 48
    gap = 20
    total_w = btn_w * 2 + gap
    bx = popup.centerx - total_w // 2
    by = popup.bottom - btn_h - 30
    back_rect = pygame.Rect(bx, by, btn_w, btn_h)
    start_rect = pygame.Rect(bx + btn_w + gap, by, btn_w, btn_h)
    return start_rect, back_rect


def get_timed_result_rects():
    pw, ph = 460, 400
    popup = pygame.Rect(WIDTH // 2 - pw // 2, HEIGHT // 2 - ph // 2,
                        pw, ph)
    btn_w, btn_h = 150, 48
    gap = 20
    total_w = btn_w * 2 + gap
    bx = popup.centerx - total_w // 2
    by = popup.bottom - btn_h - 25
    back_rect = pygame.Rect(bx, by, btn_w, btn_h)
    retry_rect = pygame.Rect(bx + btn_w + gap, by, btn_w, btn_h)
    return retry_rect, back_rect
def draw_select():
    if WIDTH != SELECT_W or HEIGHT != SELECT_H:
        apply_select_size()

    draw_bg()

    title_card = pygame.Rect(WIDTH // 2 - 200, 40, 400, 100)
    draw_card(screen, title_card, CARD_BG, radius=20)
    title = HUGE_FONT.render("一箭又一箭", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 55))

    sub = FONT.render("选择关卡", True, DARK)
    screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 175))

    save_data = read_save()

    for i, btn in enumerate(level_btns):
        unlocked_flag = i < unlocked

        shadow_rect = btn.move(3, 3)
        sh = pygame.Surface((shadow_rect.width, shadow_rect.height),
                            pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, 50), sh.get_rect(), border_radius=18)
        screen.blit(sh, shadow_rect.topleft)

        if unlocked_flag:
            hover_flag = btn.collidepoint(mouse_pos)
            color = LIGHT_BLUE if hover_flag else BLUE
            text_color = WHITE
        else:
            color = (65, 80, 130)
            text_color = (130, 145, 180)
        pygame.draw.rect(screen, color, btn, border_radius=18)

        if i == TIMED_LEVEL_INDEX:
            label = "限时模式"
        else:
            label = f"第 {i + 1} 关"
        num = FONT.render(label, True, text_color)
        screen.blit(num, (btn.centerx - num.get_width() // 2, btn.y + 12))

        if i == TIMED_LEVEL_INDEX:
            if i < len(best_scores) and best_scores[i] > 0:
                t = TINY_FONT.render(f"最高 {best_scores[i]} 分", True,
                                     (200, 215, 240))
                screen.blit(t, (btn.centerx - t.get_width() // 2,
                                btn.y + 55))
            elif not unlocked_flag:
                lock = TINY_FONT.render("未解锁", True, text_color)
                screen.blit(lock, (btn.centerx - lock.get_width() // 2,
                                   btn.y + 70))
        else:
            stars = level_stars[i] if i < len(level_stars) else 0
            star_y = btn.y + 60
            total_stars_w = 3 * 30
            sx0 = btn.centerx - total_stars_w // 2 + 15
            for s in range(3):
                draw_star(screen, sx0 + s * 30, star_y, 11, s < stars)

            if i < len(level_times) and level_times[i] > 0:
                t = TINY_FONT.render(format_time(level_times[i]), True,
                                     (200, 215, 240))
                screen.blit(t, (btn.centerx - t.get_width() // 2,
                                btn.y + 88))
            elif save_data and save_data.get("level_index") == i:
                tag = TINY_FONT.render("有存档", True, YELLOW)
                screen.blit(tag, (btn.centerx - tag.get_width() // 2,
                                  btn.y + 88))
            elif not unlocked_flag:
                lock = TINY_FONT.render("未解锁", True, text_color)
                screen.blit(lock, (btn.centerx - lock.get_width() // 2,
                                   btn.y + 88))

    tip = SMALL_FONT.render("通关后解锁下一关", True, (130, 145, 180))
    screen.blit(tip, (WIDTH // 2 - tip.get_width() // 2, HEIGHT - 40))


def draw_play():
    draw_bg()
    card = pygame.Rect(20, 18, WIDTH - 40, TOP_H - 36)
    draw_card(screen, card, CARD_BG, radius=18)

    # 第一行信息：动态排布
    parts = []
    parts.append(BIG_FONT.render(f"第 {level_index + 1} 关", True, WHITE))

    if level_index == TIMED_LEVEL_INDEX:
        parts.append(FONT.render(f"得分 {score}", True, DARK))
        parts.append(FONT.render(f"连击 {combo}", True, YELLOW))
        remain = max(0, timed_remaining_ms) // 1000
        parts.append(FONT.render(f"剩余 {remain} 秒", True,
                                 RED if remain <= 10 else YELLOW))
    else:
        parts.append(FONT.render(f"剩余 {remaining_arrows()}", True, DARK))
        parts.append(FONT.render(f"失误 {mistakes}/{MAX_MISTAKES}", True,
                                 RED if mistakes >= MAX_MISTAKES else DARK))
        parts.append(FONT.render(f"用时 {format_time(get_elapsed_ms())}",
                                 True, YELLOW))

    x = 40
    y = 30
    gap = 20
    for p in parts:
        screen.blit(p, (x, y + (BIG_FONT.get_height() - p.get_height()) // 2))
        x += p.get_width() + gap

    # 两行按钮
    draw_button(screen, pause_btn, "暂停", GRAY, DARK_GRAY, WHITE,
                SMALL_FONT, 10)
    undo_disabled = (undo_left <= 0 or not undo_stack)
    draw_button(screen, undo_btn, f"撤销 {undo_left}", PURPLE, LIGHT_PURPLE,
                WHITE, SMALL_FONT, 10, disabled=undo_disabled)
    hint_disabled = (hint_left <= 0)
    draw_button(screen, hint_btn, f"提示 {hint_left}", ORANGE, LIGHT_ORANGE,
                WHITE, SMALL_FONT, 10, disabled=hint_disabled)
    draw_button(screen, restart_btn, "重新开始", BLUE, LIGHT_BLUE, WHITE,
                SMALL_FONT, 10)
    draw_button(screen, back_btn_play, "返回", GRAY, DARK_GRAY, WHITE,
                SMALL_FONT, 10)

    # 棋盘
    board_card = pygame.Rect(BOARD_X - 10, BOARD_Y - 10,
                             BOARD_W + 20, BOARD_H + 20)
    draw_card(screen, board_card, CARD_LIGHT, radius=18)

    highlight_on = False
    if hint_cell and hint_timer > 0:
        phase = (hint_timer // 12) % 2
        highlight_on = (phase == 1)

    for r in range(ROWS):
        for c in range(COLS):
            x = BOARD_X + c * CELL
            y = BOARD_Y + r * CELL
            pygame.draw.rect(screen, GRID_LINE, (x, y, CELL, CELL), 1)

            if highlight_on and hint_cell == (r, c):
                hl = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
                hl.fill((255, 220, 80, 110))
                screen.blit(hl, (x, y))
                pygame.draw.rect(screen, YELLOW, (x, y, CELL, CELL), 3,
                                 border_radius=6)

            cell = board[r][c]
            if cell != 0:
                cx = x + CELL // 2
                cy = y + CELL // 2
                color = arrow_color(r, c, cell)
                dx, dy = 0, 0
                if shake and shake["r"] == r and shake["c"] == c:
                    dx = shake["dx"]
                    color = RED
                draw_arrow(screen, cx + dx, cy + dy, cell, color)

    for a in animating:
        x = BOARD_X + a["c"] * CELL
        y = BOARD_Y + a["r"] * CELL
        cx = x + CELL // 2 + a["ox"]
        cy = y + CELL // 2 + a["oy"]
        alpha = max(0, 255 - a["fade"])
        color = arrow_color(a["r"], a["c"], a["dir"])
        draw_arrow(screen, cx, cy, a["dir"], color, 1.0, alpha)


def draw_popup(width, height):
    popup = pygame.Rect(WIDTH // 2 - width // 2, 110, width, height)
    shadow = popup.move(5, 5)
    sh = pygame.Surface((shadow.width, shadow.height), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 80), sh.get_rect(), border_radius=24)
    screen.blit(sh, shadow.topleft)
    pygame.draw.rect(screen, CARD_SOFT, popup, border_radius=24)
    return popup


def draw_pause():
    mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 150))
    screen.blit(mask, (0, 0))
    popup = draw_popup(420, 420)
    title = BIG_FONT.render("暂停中", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, popup.y + 40))
    t = FONT.render(f"已用时 {format_time(elapsed_before_pause)}",
                    True, YELLOW)
    screen.blit(t, (WIDTH // 2 - t.get_width() // 2, popup.y + 110))
    draw_button(screen, resume_btn, "继续", BLUE, LIGHT_BLUE, WHITE, FONT, 14)
    draw_button(screen, save_quit_btn, "保存并退出", GREEN, LIGHT_GREEN,
                WHITE, FONT, 14)
    draw_button(screen, back_select_btn, "返回选关", GRAY, DARK_GRAY, WHITE,
                FONT, 14)


def draw_confirm():
    draw_bg()
    popup = draw_popup(440, 280)
    title = FONT.render(f"第 {pending_level + 1} 关有存档", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, popup.y + 40))
    sub = SMALL_FONT.render("是否继续上次进度？", True, DARK)
    screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, popup.y + 90))
    draw_button(screen, continue_btn, "继续", BLUE, LIGHT_BLUE, WHITE,
                FONT, 14)
    draw_button(screen, restart_btn2, "重新开始", RED, LIGHT_RED, WHITE,
                FONT, 14)


def draw_intro():
    draw_bg()

    mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 160))
    screen.blit(mask, (0, 0))

    pw, ph = 480, 420
    popup = pygame.Rect(WIDTH // 2 - pw // 2, HEIGHT // 2 - ph // 2,
                        pw, ph)

    shadow = popup.move(5, 5)
    sh = pygame.Surface((shadow.width, shadow.height), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 90), sh.get_rect(), border_radius=26)
    screen.blit(sh, shadow.topleft)

    pygame.draw.rect(screen, CARD_SOFT, popup, border_radius=26)

    title = BIG_FONT.render("限时模式", True, YELLOW)
    screen.blit(title, (popup.centerx - title.get_width() // 2,
                        popup.y + 30))

    pygame.draw.line(screen, (100, 120, 170),
                     (popup.x + 40, popup.y + 95),
                     (popup.right - 40, popup.y + 95), 2)

    lines = [
        "每关地图随机生成",
        "30 秒内点击箭头得分",
        "点掉一个箭头 +1 分",
        "连续 3 连击 +2 秒",
        "点到被挡的箭头 -2 秒",
        "分数 = 箭头数 + 剩余秒数 ÷ 2",
    ]
    for i, line in enumerate(lines):
        t = SMALL_FONT.render(line, True, DARK)
        screen.blit(t, (popup.centerx - t.get_width() // 2,
                        popup.y + 115 + i * 30))

    start_rect, back_rect = get_intro_rects()
    draw_button(screen, back_rect, "返回选关", GRAY, DARK_GRAY, WHITE,
                FONT, 14)
    draw_button(screen, start_rect, "开始挑战", YELLOW,
                (255, 230, 130), BLACK, FONT, 14)


def draw_win():
    draw_bg()
    popup = draw_popup(420, 400)
    title = BIG_FONT.render("太棒了！", True, GREEN)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, popup.y + 30))

    stars = MAX_MISTAKES - mistakes
    if stars < 1:
        stars = 1
    for i in range(3):
        sx = WIDTH // 2 - 60 + i * 60
        draw_star(screen, sx, popup.y + 120, 26, i < stars)

    t = FONT.render(f"用时 {format_time(final_time_ms)}", True, YELLOW)
    screen.blit(t, (WIDTH // 2 - t.get_width() // 2, popup.y + 190))

    if level_index < len(LEVELS) - 1:
        draw_button(screen, next_btn, "下一关", BLUE, LIGHT_BLUE, WHITE,
                    FONT, 14)
    draw_button(screen, back_btn_win, "返回选关", GRAY, DARK_GRAY, WHITE,
                FONT, 14)


def draw_timed_result():
    draw_bg()
    pw, ph = 460, 400
    popup = pygame.Rect(WIDTH // 2 - pw // 2, HEIGHT // 2 - ph // 2,
                        pw, ph)

    shadow = popup.move(5, 5)
    sh = pygame.Surface((shadow.width, shadow.height), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 90), sh.get_rect(), border_radius=26)
    screen.blit(sh, shadow.topleft)
    pygame.draw.rect(screen, CARD_SOFT, popup, border_radius=26)

    title = BIG_FONT.render("通关！", True, GREEN)
    screen.blit(title, (popup.centerx - title.get_width() // 2,
                        popup.y + 30))

    pygame.draw.line(screen, (100, 120, 170),
                     (popup.x + 40, popup.y + 95),
                     (popup.right - 40, popup.y + 95), 2)

    lines = [
        f"连击  {combo}",
        f"用时  {format_time(final_time_ms)}",
        f"分数  {final_score}",
    ]
    for i, line in enumerate(lines):
        t = FONT.render(line, True, WHITE)
        screen.blit(t, (popup.centerx - t.get_width() // 2,
                        popup.y + 120 + i * 40))

    bs = SMALL_FONT.render(f"最高分  {best_scores[TIMED_LEVEL_INDEX]}",
                           True, YELLOW)
    screen.blit(bs, (popup.centerx - bs.get_width() // 2, popup.y + 260))

    retry_rect, back_rect = get_timed_result_rects()
    draw_button(screen, back_rect, "返回选关", GRAY, DARK_GRAY, WHITE,
                FONT, 14)
    draw_button(screen, retry_rect, "再来一局", YELLOW,
                (255, 230, 130), BLACK, FONT, 14)


def draw_lose():
    draw_bg()
    popup = draw_popup(420, 400)
    title = BIG_FONT.render("再试一次吧！", True, RED)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, popup.y + 40))

    t = SMALL_FONT.render(f"用时 {format_time(final_time_ms)}", True, DARK)
    screen.blit(t, (WIDTH // 2 - t.get_width() // 2, popup.y + 130))

    draw_arrow(screen, WIDTH // 2, popup.y + 200, 'D', RED, 1.4)
    draw_button(screen, retry_btn, "重来", RED, LIGHT_RED, WHITE, FONT, 14)
    draw_button(screen, back_btn_lose, "返回选关", GRAY, DARK_GRAY, WHITE,
                FONT, 14)


def handle_click(pos):
    global mistakes, state, shake, level_index, unlocked, level_stars
    global pending_level, final_time_ms, level_times, undo_left
    global hint_cell, hint_timer, score, combo, timed_remaining_ms
    global final_score

    if state == STATE_SELECT:
        save_data = read_save()
        for i, btn in enumerate(level_btns):
            if i < unlocked and btn.collidepoint(pos):
                if save_data and save_data.get("level_index") == i:
                    pending_level = i
                    state = STATE_CONFIRM
                elif i == TIMED_LEVEL_INDEX:
                    pending_level = i
                    state = STATE_INTRO
                else:
                    level_index = i
                    load_level(i)
                    state = STATE_PLAY
                return

    elif state == STATE_CONFIRM:
        save_data = read_save()
        if continue_btn.collidepoint(pos):
            if save_data and save_data.get("level_index") == pending_level:
                level_index = pending_level
                load_level(pending_level, saved=save_data)
            else:
                level_index = pending_level
                load_level(pending_level)
            state = STATE_PLAY
        elif restart_btn2.collidepoint(pos):
            delete_save()
            level_index = pending_level
            load_level(pending_level)
            state = STATE_PLAY

    elif state == STATE_INTRO:
        start_rect, back_rect = get_intro_rects()
        if start_rect.collidepoint(pos):
            if pending_level == TIMED_LEVEL_INDEX:
                LEVELS[pending_level] = gen_timed_level()
            level_index = pending_level
            load_level(pending_level)
            state = STATE_PLAY
        elif back_rect.collidepoint(pos):
            state = STATE_SELECT

    elif state == STATE_PLAY:
        if pause_btn.collidepoint(pos):
            pause_timer()
            state = STATE_PAUSE
            return
        if undo_btn.collidepoint(pos):
            do_undo()
            return
        if hint_btn.collidepoint(pos):
            do_hint()
            return
        if restart_btn.collidepoint(pos):
            delete_save()
            if level_index == TIMED_LEVEL_INDEX:
                LEVELS[level_index] = gen_timed_level()
            load_level(level_index)
            return
        if back_btn_play.collidepoint(pos):
            delete_save()
            state = STATE_SELECT
            return

        x, y = pos
        if not (BOARD_X <= x < BOARD_X + BOARD_W and
                BOARD_Y <= y < BOARD_Y + BOARD_H):
            return
        c = (x - BOARD_X) // CELL
        r = (y - BOARD_Y) // CELL
        if not (0 <= r < ROWS and 0 <= c < COLS):
            return
        cell = board[r][c]
        if cell == 0:
            return

        hint_cell = None
        hint_timer = 0

        push_undo()

        if is_blocked(r, c, cell):
            if level_index == TIMED_LEVEL_INDEX:
                timed_remaining_ms -= 2000
                if timed_remaining_ms < 0:
                    timed_remaining_ms = 0
                combo = 0
                shake = {"r": r, "c": c, "dx": 8, "timer": 12}
            else:
                mistakes += 1
                shake = {"r": r, "c": c, "dx": 8, "timer": 12}
                if mistakes >= MAX_MISTAKES:
                    final_time_ms = get_elapsed_ms()
                    delete_save()
                    state = STATE_LOSE
        else:
            dr, dc = DIRS[cell]
            animating.append({
                "r": r, "c": c, "dir": cell,
                "ox": 0, "oy": 0,
                "vx": dc * 22, "vy": dr * 22,
                "fade": 0
            })
            board[r][c] = 0
            if level_index == TIMED_LEVEL_INDEX:
                score += 1
                combo += 1
                if combo % 3 == 0:
                    timed_remaining_ms += 2000
                    if timed_remaining_ms > TIMED_TOTAL_MS:
                        timed_remaining_ms = TIMED_TOTAL_MS
                if remaining_arrows() == 0:
                    final_time_ms = get_elapsed_ms()
                    total = score + (max(0, timed_remaining_ms) // 1000) // 2
                    final_score = total
                    if total > best_scores[TIMED_LEVEL_INDEX]:
                        best_scores[TIMED_LEVEL_INDEX] = total
                    delete_save()
                    state = STATE_LOSE
            else:
                if remaining_arrows() == 0:
                    final_time_ms = get_elapsed_ms()
                    stars = MAX_MISTAKES - mistakes
                    if stars < 1:
                        stars = 1
                    if stars > level_stars[level_index]:
                        level_stars[level_index] = stars
                    t = final_time_ms
                    if level_times[level_index] == 0 or t < level_times[level_index]:
                        level_times[level_index] = t
                    if level_index + 1 < len(LEVELS) and unlocked < level_index + 2:
                        unlocked = level_index + 2
                    delete_save()
                    state = STATE_WIN

    elif state == STATE_PAUSE:
        if resume_btn.collidepoint(pos):
            resume_timer()
            state = STATE_PLAY
        elif save_quit_btn.collidepoint(pos):
            write_save()
            state = STATE_SELECT
        elif back_select_btn.collidepoint(pos):
            delete_save()
            state = STATE_SELECT

    elif state == STATE_WIN:
        if level_index < len(LEVELS) - 1 and next_btn.collidepoint(pos):
            level_index += 1
            if level_index == TIMED_LEVEL_INDEX:
                pending_level = level_index
                state = STATE_INTRO
            else:
                load_level(level_index)
                state = STATE_PLAY
            return
        if back_btn_win.collidepoint(pos):
            state = STATE_SELECT
            return

    elif state == STATE_LOSE:
        if level_index == TIMED_LEVEL_INDEX:
            retry_rect, back_rect = get_timed_result_rects()
            if retry_rect.collidepoint(pos):
                LEVELS[level_index] = gen_timed_level()
                load_level(level_index)
                state = STATE_PLAY
                return
            if back_rect.collidepoint(pos):
                state = STATE_SELECT
                return
        else:
            if retry_btn.collidepoint(pos):
                load_level(level_index)
                state = STATE_PLAY
                return
            if back_btn_lose.collidepoint(pos):
                state = STATE_SELECT
                return


def update_animation():
    global shake, animating, hint_timer, hint_cell
    global timed_remaining_ms, last_tick_ms, state, final_time_ms
    global best_scores, final_score

    new_anim = []
    for a in animating:
        a["ox"] += a["vx"]
        a["oy"] += a["vy"]
        a["fade"] += 8
        if (-300 < a["ox"] < WIDTH + 300 and
                -300 < a["oy"] < HEIGHT + 300 and a["fade"] < 255):
            new_anim.append(a)
    animating = new_anim

    if shake:
        shake["timer"] -= 1
        shake["dx"] = -shake["dx"]
        if shake["timer"] <= 0:
            shake = None

    if hint_timer > 0:
        hint_timer -= 1
        if hint_timer <= 0:
            hint_cell = None

    if (level_index == TIMED_LEVEL_INDEX and state == STATE_PLAY
            and not is_paused):
        now = pygame.time.get_ticks()
        if last_tick_ms == 0:
            last_tick_ms = now
        else:
            dt = now - last_tick_ms
            last_tick_ms = now
            timed_remaining_ms -= dt
            if timed_remaining_ms <= 0:
                timed_remaining_ms = 0
                final_time_ms = get_elapsed_ms()
                total = score + (max(0, timed_remaining_ms) // 1000) // 2
                final_score = total
                if total > best_scores[TIMED_LEVEL_INDEX]:
                    best_scores[TIMED_LEVEL_INDEX] = total
                delete_save()
                state = STATE_LOSE


def main():
    global state, level_index, mouse_pos
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state == STATE_PLAY:
                        pause_timer()
                        state = STATE_PAUSE
                    elif state == STATE_PAUSE:
                        resume_timer()
                        state = STATE_PLAY
                    elif state in (STATE_WIN, STATE_LOSE):
                        state = STATE_SELECT
                elif event.key == pygame.K_z:
                    if state == STATE_PLAY:
                        do_undo()

        if state == STATE_SELECT:
            draw_select()
        elif state == STATE_PLAY:
            update_animation()
            draw_play()
        elif state == STATE_PAUSE:
            draw_play()
            draw_pause()
        elif state == STATE_CONFIRM:
            draw_confirm()
        elif state == STATE_INTRO:
            draw_intro()
        elif state == STATE_WIN:
            draw_win()
        elif state == STATE_LOSE:
            if level_index == TIMED_LEVEL_INDEX:
                draw_timed_result()
            else:
                draw_lose()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()