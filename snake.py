import curses
import random
import json
import os
import time

SCORE_FILE = os.path.join(os.path.dirname(__file__), "scores.json")

def load_high_score():
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE) as f:
            data = json.load(f)
            return data.get("high_score", 0)
    return 0

def save_high_score(score):
    high = load_high_score()
    if score > high:
        with open(SCORE_FILE, "w") as f:
            json.dump({"high_score": score}, f)
        return True
    return False

def draw_border(win, h, w):
    win.attron(curses.color_pair(3))
    win.border()
    win.attroff(curses.color_pair(3))

def place_food(snake, h, w, obstacles=()):
    while True:
        food = (random.randint(1, h - 2), random.randint(1, w - 2))
        if food not in snake and food not in obstacles:
            return food

def place_obstacles(snake, food, h, w, count):
    obstacles = []
    attempts = 0
    while len(obstacles) < count and attempts < 1000:
        attempts += 1
        pos = (random.randint(2, h - 3), random.randint(2, w - 3))
        head = snake[0]
        # keep a safe zone around the snake's head
        if (abs(pos[0] - head[0]) < 4 and abs(pos[1] - head[1]) < 4):
            continue
        if pos not in snake and pos != food and pos not in obstacles:
            obstacles.append(pos)
    return obstacles

def game(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)   # snake
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)     # food
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)    # border
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # UI text
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)   # normal text

    h, w = stdscr.getmaxyx()

    while True:
        result = run_game(stdscr, h, w)
        if not show_end_screen(stdscr, h, w, result):
            break

def run_game(stdscr, h, w):
    stdscr.clear()

    snake = [(h // 2, w // 2), (h // 2, w // 2 - 1), (h // 2, w // 2 - 2)]
    direction = curses.KEY_RIGHT
    food = place_food(snake, h, w)
    score = 0
    high_score = load_high_score()
    base_speed = 75  # ms (2x faster than before)
    obstacles = []

    stdscr.nodelay(True)
    stdscr.timeout(base_speed)

    while True:
        stdscr.clear()
        draw_border(stdscr, h, w)

        # HUD
        level = score // 5 + 1
        speed_label = f" 레벨: {level}  점수: {score}  최고기록: {high_score}  장애물: {len(obstacles)} "
        keys_label = " 방향키: 이동 | Q: 종료 "
        stdscr.attron(curses.color_pair(4))
        stdscr.addstr(0, max(1, (w - len(speed_label)) // 2), speed_label)
        stdscr.addstr(h - 1, max(1, (w - len(keys_label)) // 2), keys_label)
        stdscr.attroff(curses.color_pair(4))

        # obstacles
        for obs in obstacles:
            try:
                stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
                stdscr.addch(obs[0], obs[1], "▪")
                stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)
            except curses.error:
                pass

        # food
        try:
            stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
            stdscr.addch(food[0], food[1], "●")
            stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
        except curses.error:
            pass

        # snake
        for i, seg in enumerate(snake):
            try:
                if i == 0:
                    stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
                    stdscr.addch(seg[0], seg[1], "■")
                    stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
                else:
                    stdscr.attron(curses.color_pair(1))
                    stdscr.addch(seg[0], seg[1], "□")
                    stdscr.attroff(curses.color_pair(1))
            except curses.error:
                pass

        stdscr.refresh()

        key = stdscr.getch()
        if key == ord("q") or key == ord("Q"):
            return {"score": score, "quit": True}

        # direction (no 180° reversal)
        opposites = {
            curses.KEY_UP: curses.KEY_DOWN,
            curses.KEY_DOWN: curses.KEY_UP,
            curses.KEY_LEFT: curses.KEY_RIGHT,
            curses.KEY_RIGHT: curses.KEY_LEFT,
        }
        if key in opposites and key != opposites.get(direction):
            direction = key

        head = snake[0]
        if direction == curses.KEY_UP:
            new_head = (head[0] - 1, head[1])
        elif direction == curses.KEY_DOWN:
            new_head = (head[0] + 1, head[1])
        elif direction == curses.KEY_LEFT:
            new_head = (head[0], head[1] - 1)
        else:
            new_head = (head[0], head[1] + 1)

        # wall, self, or obstacle collision
        if (new_head[0] <= 0 or new_head[0] >= h - 1 or
                new_head[1] <= 0 or new_head[1] >= w - 1 or
                new_head in snake or new_head in obstacles):
            return {"score": score, "quit": False}

        snake.insert(0, new_head)

        if new_head == food:
            score += 1
            if score > high_score:
                high_score = score
            # add obstacle every 5 points (max 20)
            new_level = score // 5 + 1
            target_obstacles = min((new_level - 1) * 2, 20)
            if len(obstacles) < target_obstacles:
                obstacles = place_obstacles(snake, food, h, w, target_obstacles)
            food = place_food(snake, h, w, obstacles)
            # speed up every 5 points (min 35ms)
            new_speed = max(35, base_speed - (score // 5) * 8)
            stdscr.timeout(new_speed)
        else:
            snake.pop()

def show_end_screen(stdscr, h, w, result):
    new_record = save_high_score(result["score"])
    high_score = load_high_score()

    stdscr.clear()
    draw_border(stdscr, h, w)

    lines = []
    if result.get("quit"):
        lines.append(("게임 종료", curses.color_pair(4) | curses.A_BOLD))
    else:
        lines.append(("💥 게임 오버!", curses.color_pair(2) | curses.A_BOLD))

    lines.append(("", curses.color_pair(5)))
    lines.append((f"점수: {result['score']}", curses.color_pair(4) | curses.A_BOLD))

    if new_record and result["score"] > 0:
        lines.append(("🏆 새 최고기록!", curses.color_pair(2) | curses.A_BOLD))
    else:
        lines.append((f"최고기록: {high_score}", curses.color_pair(5)))

    lines.append(("", curses.color_pair(5)))
    lines.append(("R  다시 시작", curses.color_pair(1)))
    lines.append(("Q  나가기", curses.color_pair(3)))

    start_y = h // 2 - len(lines) // 2
    for i, (text, attr) in enumerate(lines):
        x = max(1, (w - len(text)) // 2)
        try:
            stdscr.attron(attr)
            stdscr.addstr(start_y + i, x, text)
            stdscr.attroff(attr)
        except curses.error:
            pass

    stdscr.nodelay(False)
    while True:
        key = stdscr.getch()
        if key in (ord("r"), ord("R")):
            return True
        if key in (ord("q"), ord("Q")):
            return False

if __name__ == "__main__":
    curses.wrapper(game)
