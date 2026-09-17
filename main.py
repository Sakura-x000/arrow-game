import pygame
import sys
import math
from levels import LEVELS

pygame.init()

# ============ 尺寸 ============
CELL = 90
COLS = 4
ROWS = 4
BOARD_W = CELL * COLS
BOARD_H = CELL * ROWS
TOP_H = 130
MARGIN = 100

BOARD_X = MARGIN
BOARD_Y = TOP_H + 30

WIDTH = BOARD_W + MARGIN * 2
HEIGHT = BOARD_Y + BOARD_H + MARGIN

# ============ 颜色（深蓝主题） ============
BG_TOP = (30, 40, 70)         # 深蓝
BG_BOTTOM = (45, 55, 95)      # 稍浅的蓝紫
CARD_BG = (50, 62, 105)       # 卡片底色
CARD_LIGHT = (65, 80, 130)    # 浅一点
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
ORANGE = (250, 160, 80)

ARROW_COLORS = [
    (240, 110, 110),   # 红
    (100, 160, 245),   # 蓝
    (80, 210, 150),    # 绿
    (255, 190, 70),    # 黄
    (180, 140, 240),   # 紫
    (250, 140, 190),   # 粉
]

FONT = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 22)
BIG_FONT = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 42)
HUGE_FONT = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 50)
SMALL_FONT = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 18)
TINY_FONT = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 15)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("一箭又一箭")
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

state = STATE_SELECT
level_index = 0
board = []
mistakes = 0
MAX_MISTAKES = 3
animating = []
shake = None
unlocked = 1
level_stars = [0, 0, 0]

mouse_pos = (0, 0)

level_btns = []
for i in range(len(LEVELS)):
    r = i // 2
    c = i % 2
    bx = WIDTH // 2 - 140 + c * 150
    by = 280 + r * 130
    level_btns.append(pygame.Rect(bx, by, 130, 100))

restart_btn = pygame.Rect(WIDTH - 160, 40, 130, 42)
back_btn_play = pygame.Rect(WIDTH - 160, 88, 130, 38)

next_btn = pygame.Rect(WIDTH // 2 - 145, 430, 130, 48)
back_btn_win = pygame.Rect(WIDTH // 2 + 15, 430, 130, 48)
retry_btn = pygame.Rect(WIDTH // 2 - 145, 430, 130, 48)
back_btn_lose = pygame.Rect(WIDTH // 2 + 15, 430, 130, 48)


def draw_bg():
    """深蓝渐变 + 装饰圆点"""
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(BG_TOP[0] * (1 - ratio) + BG_BOTTOM[0] * ratio)
        g = int(BG_TOP[1] * (1 - ratio) + BG_BOTTOM[1] * ratio)
        b = int(BG_TOP[2] * (1 - ratio) + BG_BOTTOM[2] * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

    # 装饰圆点
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


def load_level(idx):
    global board, mistakes, animating, shake
    data = LEVELS[idx]
    board = [[cell for cell in row] for row in data]
    mistakes = 0
    animating = []
    shake = None


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
                font=None, radius=12):
    hover = rect.collidepoint(mouse_pos)
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


def draw_select():
    draw_bg()

    # 标题卡片
    title_card = pygame.Rect(WIDTH // 2 - 180, 50, 360, 110)
    draw_card(screen, title_card, CARD_BG, radius=20)

    title = HUGE_FONT.render("一箭又一箭", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 65))

    # 彩色装饰箭头
    draw_arrow(screen, 60, 200, 'R', ARROW_COLORS[0], 0.6)
    draw_arrow(screen, WIDTH - 60, 200, 'L', ARROW_COLORS[1], 0.6)
    draw_arrow(screen, WIDTH // 2, 210, 'U', ARROW_COLORS[2], 0.6)

    sub = FONT.render("选择关卡", True, DARK)
    screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 230))

    for i, btn in enumerate(level_btns):
        unlocked_flag = i < unlocked

        shadow_rect = btn.move(3, 3)
        sh = pygame.Surface((shadow_rect.width, shadow_rect.height),
                            pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, 50), sh.get_rect(), border_radius=16)
        screen.blit(sh, shadow_rect.topleft)

        if unlocked_flag:
            hover_flag = btn.collidepoint(mouse_pos)
            color = LIGHT_BLUE if hover_flag else BLUE
            text_color = WHITE
        else:
            color = (65, 80, 130)
            text_color = (130, 145, 180)

        pygame.draw.rect(screen, color, btn, border_radius=16)

        num = FONT.render(f"第 {i + 1} 关", True, text_color)
        screen.blit(num, (btn.x + btn.width // 2 - num.get_width() // 2,
                          btn.y + 16))

        stars = level_stars[i]
        star_y = btn.y + 58
        for s in range(3):
            sx = btn.x + 30 + s * 32
            draw_star(screen, sx, star_y, 12, s < stars)

        if not unlocked_flag:
            lock = TINY_FONT.render("未解锁", True, text_color)
            screen.blit(lock, (btn.x + btn.width // 2 - lock.get_width() // 2,
                               btn.y + 78))

    tip = SMALL_FONT.render("通关后解锁下一关", True, (130, 145, 180))
    screen.blit(tip, (WIDTH // 2 - tip.get_width() // 2, HEIGHT - 45))


def draw_play():
    draw_bg()

    # 顶部卡片
    card = pygame.Rect(20, 18, WIDTH - 40, TOP_H - 36)
    draw_card(screen, card, CARD_BG, radius=18)

    info1 = BIG_FONT.render(f"第 {level_index + 1} 关", True, WHITE)
    screen.blit(info1, (40, 30))

    info2 = FONT.render(f"剩余  {remaining_arrows()}", True, DARK)
    info3 = FONT.render(f"失误  {mistakes}/{MAX_MISTAKES}", True,
                        RED if mistakes >= MAX_MISTAKES else DARK)
    screen.blit(info2, (40, 82))
    screen.blit(info3, (160, 82))

    draw_button(screen, restart_btn, "重新开始", BLUE, LIGHT_BLUE, WHITE,
                SMALL_FONT, 12)
    draw_button(screen, back_btn_play, "返回选关", GRAY, DARK_GRAY, WHITE,
                SMALL_FONT, 10)

    # 棋盘卡片
    board_card = pygame.Rect(BOARD_X - 10, BOARD_Y - 10,
                             BOARD_W + 20, BOARD_H + 20)
    draw_card(screen, board_card, CARD_LIGHT, radius=18)

    for r in range(ROWS):
        for c in range(COLS):
            x = BOARD_X + c * CELL
            y = BOARD_Y + r * CELL
            pygame.draw.rect(screen, GRID_LINE, (x, y, CELL, CELL), 1)
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
    pygame.draw.rect(screen, CARD_BG, popup, border_radius=24)
    # 弹窗装饰
    for i in range(4):
        angle = math.pi / 4 + i * math.pi / 2
        px = WIDTH // 2 + int(150 * math.cos(angle))
        py = 110 + int(150 * math.sin(angle))
        if popup.collidepoint(px, py):
            pygame.draw.circle(screen, (70, 85, 140), (px, py), 4)
    return popup


def draw_win():
    draw_bg()
    popup = draw_popup(420, 380)

    title = BIG_FONT.render("太棒了！", True, GREEN)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, popup.y + 40))

    stars = MAX_MISTAKES - mistakes
    if stars < 1:
        stars = 1
    for i in range(3):
        sx = WIDTH // 2 - 60 + i * 60
        draw_star(screen, sx, popup.y + 140, 26, i < stars)

    if level_index < len(LEVELS) - 1:
        draw_button(screen, next_btn, "下一关", BLUE, LIGHT_BLUE, WHITE,
                    FONT, 14)
    draw_button(screen, back_btn_win, "返回选关", GRAY, DARK_GRAY, WHITE,
                FONT, 14)


def draw_lose():
    draw_bg()
    popup = draw_popup(420, 380)

    title = BIG_FONT.render("再试一次吧！", True, RED)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, popup.y + 50))

    draw_arrow(screen, WIDTH // 2, popup.y + 170, 'D', RED, 1.4)

    draw_button(screen, retry_btn, "重来", RED, LIGHT_RED, WHITE, FONT, 14)
    draw_button(screen, back_btn_lose, "返回选关", GRAY, DARK_GRAY, WHITE,
                FONT, 14)


def handle_click(pos):
    global mistakes, state, shake, level_index, unlocked, level_stars

    if state == STATE_SELECT:
        for i, btn in enumerate(level_btns):
            if i < unlocked and btn.collidepoint(pos):
                level_index = i
                load_level(i)
                state = STATE_PLAY
                return

    elif state == STATE_PLAY:
        if restart_btn.collidepoint(pos):
            load_level(level_index)
            return
        if back_btn_play.collidepoint(pos):
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

        if is_blocked(r, c, cell):
            mistakes += 1
            shake = {"r": r, "c": c, "dx": 8, "timer": 12}
            if mistakes >= MAX_MISTAKES:
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
            if remaining_arrows() == 0:
                stars = MAX_MISTAKES - mistakes
                if stars < 1:
                    stars = 1
                if stars > level_stars[level_index]:
                    level_stars[level_index] = stars
                if level_index + 1 < len(LEVELS) and unlocked < level_index + 2:
                    unlocked = level_index + 2
                state = STATE_WIN

    elif state == STATE_WIN:
        if level_index < len(LEVELS) - 1 and next_btn.collidepoint(pos):
            level_index += 1
            load_level(level_index)
            state = STATE_PLAY
            return
        if back_btn_win.collidepoint(pos):
            state = STATE_SELECT
            return

    elif state == STATE_LOSE:
        if retry_btn.collidepoint(pos):
            load_level(level_index)
            state = STATE_PLAY
            return
        if back_btn_lose.collidepoint(pos):
            state = STATE_SELECT
            return


def update_animation():
    global shake, animating
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
                    if state in (STATE_PLAY, STATE_WIN, STATE_LOSE):
                        state = STATE_SELECT

        if state == STATE_SELECT:
            draw_select()
        elif state == STATE_PLAY:
            update_animation()
            draw_play()
        elif state == STATE_WIN:
            draw_win()
        elif state == STATE_LOSE:
            draw_lose()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()