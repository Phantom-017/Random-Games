import curses
import random
import time
from pathlib import Path

SCORES_FILE = Path(__file__).resolve().parent / "scores_joueurs" / "arcade_shooter_scores.txt"
RANK_NAMES = ("Bronze", "Argent", "Or", "Platine", "Jade", "Améthyste", "Diamant")


def load_scores():
    path = SCORES_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        return []

    scores = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            if ":" in line:
                pseudo, raw = line.rsplit(":", 1)
                pseudo = pseudo.strip()
                raw = raw.strip()
                if pseudo and raw.isdigit():
                    scores.append((pseudo, int(raw)))
            elif line.isdigit():
                scores.append(("Joueur", int(line)))
    except Exception:
        return []
    return sorted(scores, key=lambda item: item[1], reverse=True)[:3]


def save_scores(scores):
    path = SCORES_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"{pseudo}:{score}" for pseudo, score in scores[:3]), encoding="utf-8")


class TouhouShooter:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.stdscr.nodelay(True)
        self.stdscr.keypad(True)
        curses.curs_set(0)
        self.rank_color_pairs = {}
        italic = getattr(curses, "A_ITALIC", 0)
        self.rank_text_styles = {
            1: curses.A_DIM,
            2: italic,
            3: curses.A_BOLD,
            4: curses.A_BOLD | italic,
            5: curses.A_BLINK,
            6: curses.A_BOLD | curses.A_BLINK,
            7: curses.A_BOLD | italic | curses.A_BLINK,
        }
        self.setup_rank_colors()
        self.high_scores = load_scores()
        self.state = "menu"
        self.menu_index = 0
        self.menu_options = ["Démarrer", "Quitter"]
        self.running = True
        self.player_name = "Joueur"
        self.reset_game()

    def setup_rank_colors(self):
        try:
            if not curses.has_colors():
                return
            curses.start_color()
            background = 0
            try:
                curses.use_default_colors()
                background = -1
            except curses.error:
                pass
            if curses.COLORS >= 256:
                colors = {
                    1: 130,
                    2: 250,
                    3: 220,
                    4: 87,
                    5: 35,
                    6: 135,
                    7: 39,
                }
            else:
                colors = {
                    1: curses.COLOR_RED,
                    2: curses.COLOR_WHITE,
                    3: curses.COLOR_YELLOW,
                    4: curses.COLOR_CYAN,
                    5: curses.COLOR_GREEN,
                    6: curses.COLOR_MAGENTA,
                    7: curses.COLOR_BLUE,
                }
            for rank, color in colors.items():
                curses.init_pair(rank, color, background)
                self.rank_color_pairs[rank] = curses.color_pair(rank)
        except curses.error:
            self.rank_color_pairs = {}

    def reset_game(self):
        self.height, self.width = self.stdscr.getmaxyx()
        self.player_x = max(2, min(self.width // 2, self.width - 3))
        self.player_y = max(2, min(self.height - 3, self.height - 3))
        self.bullets = []
        self.enemies = []
        self.score = 0
        self.lives = 5
        self.game_over = False
        self.spawn_timer = 0
        self.fire_cooldown = 0.0
        self.auto_fire = False
        self.enemy_speed = 2
        self.held = {"left": False, "right": False, "up": False, "down": False, "shoot": False}

    def start_game(self):
        self.reset_game()
        self.state = "playing"

    def add_score(self):
        self.high_scores.append((self.player_name, self.score))
        self.high_scores = sorted(self.high_scores, key=lambda item: item[1], reverse=True)[:3]
        save_scores(self.high_scores)

    def handle_menu_input(self, key):
        if key in (ord("q"), ord("Q"), 27):
            self.running = False
            return
        if key in (curses.KEY_UP, ord("z"), ord("Z"), ord("w"), ord("W")):
            self.menu_index = (self.menu_index - 1) % len(self.menu_options)
        elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
            self.menu_index = (self.menu_index + 1) % len(self.menu_options)
        elif key in (10, 13, 32):
            selected = self.menu_options[self.menu_index]
            if selected == "Démarrer":
                self.ask_pseudo()
            elif selected == "Quitter":
                self.running = False

    def ask_pseudo(self):
        curses.echo()
        curses.curs_set(1)
        self.stdscr.nodelay(False)
        self.stdscr.erase()
        self.stdscr.addstr(5, 5, "Pseudo : ")
        self.stdscr.refresh()
        try:
            pseudo = self.stdscr.getstr(5, 15, 12).decode("utf-8", "ignore").strip()
        except Exception:
            pseudo = "Joueur"
        finally:
            curses.noecho()
            curses.curs_set(0)
            self.stdscr.nodelay(True)

        self.player_name = pseudo if pseudo else "Joueur"
        self.start_game()

    def handle_game_over_input(self, key):
        if key in (ord("r"), ord("R")):
            self.start_game()
        elif key in (ord("m"), ord("M")):
            self.state = "menu"
        elif key in (ord("q"), ord("Q"), 27):
            self.running = False

    def handle_playing_input(self, key):
        if key in (curses.KEY_LEFT, ord("h"), ord("H")):
            self.player_x -= 3
        elif key in (curses.KEY_RIGHT, ord("l"), ord("L"), ord("d"), ord("D")):
            self.player_x += 3
        elif key in (curses.KEY_UP, ord("k"), ord("K"), ord("z"), ord("Z"), ord("w"), ord("W")):
            self.player_y -= 3
        elif key in (curses.KEY_DOWN, ord("j"), ord("J"), ord("s"), ord("S")):
            self.player_y += 3
        elif key == ord(" "):
            self.auto_fire = not self.auto_fire
        elif key in (ord("a"), ord("A"), ord("x"), ord("X")):
            self.fire()
        elif key in (ord("q"), ord("Q")):
            self.state = "menu"

        self.player_x = int(max(2, min(self.player_x, self.width - 3)))
        self.player_y = int(max(2, min(self.player_y, self.height - 3)))

    def set_held_false(self):
        self.held = {"left": False, "right": False, "up": False, "down": False, "shoot": False}
        self.auto_fire = False

    def move_player(self, dt):
        return

    def get_difficulty(self):
        if self.score >= 600:
            return 7, "Difficulté secrète"
        if self.score >= 500:
            return 6, "Difficulté secrète"
        level = min(5, (self.score // 100) + 1)
        labels = {
            1: "Niveau 1",
            2: "Niveau 2",
            3: "Niveau 3",
            4: "Niveau 4",
            5: "Niveau 5",
        }
        return level, labels.get(level, "Niveau 5")

    def get_rank(self, score=None):
        score = self.score if score is None else score
        rank = min(len(RANK_NAMES), (score // 100) + 1)
        return rank, RANK_NAMES[rank - 1]

    def get_rank_style(self, score=None):
        rank, name = self.get_rank(score)
        style = self.rank_color_pairs.get(rank, curses.A_NORMAL)
        style |= self.rank_text_styles.get(rank, curses.A_NORMAL)
        return rank, name, style

    def get_difficulty_stats(self):
        level, label = self.get_difficulty()

        if level >= 6:
            return {
                "label": label,
                "spawn_count": 3 + (self.score // 180),
                "spawn_delay": max(0.08, 0.55 - (self.score / 2500)),
                "enemy_speed": 2.4 + (self.score / 150) + ((level - 6) * 0.5),
            }

        base = {
            1: {"spawn_count": 1, "spawn_delay": 0.95, "enemy_speed": 1.1},
            2: {"spawn_count": 1, "spawn_delay": 0.8, "enemy_speed": 1.5},
            3: {"spawn_count": 2, "spawn_delay": 0.68, "enemy_speed": 1.9},
            4: {"spawn_count": 2, "spawn_delay": 0.56, "enemy_speed": 2.4},
            5: {"spawn_count": 2, "spawn_delay": 0.45, "enemy_speed": 2.9},
        }
        stats = base[level]
        return {
            "label": label,
            "spawn_count": stats["spawn_count"],
            "spawn_delay": max(0.32, stats["spawn_delay"] - (self.score / 12000)),
            "enemy_speed": stats["enemy_speed"] + min(1.0, self.score / 700),
        }

    def fire(self):
        if self.fire_cooldown > 0:
            return
        self.bullets.append([int(self.player_x), int(self.player_y - 1)])
        self.fire_cooldown = 0.12

    def spawn_enemy(self):
        x = random.randint(2, self.width - 3)
        self.enemies.append([int(x), 1])

    def update_game(self):
        dt = 0.05
        self.move_player(dt)

        self.fire_cooldown = max(0, self.fire_cooldown - dt)
        
        if self.auto_fire:
            self.fire()

        difficulty = self.get_difficulty_stats()

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            for _ in range(max(1, min(6, difficulty["spawn_count"]))):
                self.spawn_enemy()
            self.spawn_timer = difficulty["spawn_delay"]

        self.enemy_speed = difficulty["enemy_speed"]

        for bullet in self.bullets[:]:
            bullet[1] = int(bullet[1] - 2)
            if bullet[1] < 0:
                self.bullets.remove(bullet)

        for enemy in self.enemies[:]:
            enemy[1] = int(enemy[1] + self.enemy_speed)
            if enemy[1] >= self.height + 2:
                self.enemies.remove(enemy)
                continue

            if int(enemy[1]) >= int(self.player_y) and abs(int(enemy[0]) - int(self.player_x)) <= 2:
                self.enemies.remove(enemy)
                self.lives -= 1
                if self.lives <= 0:
                    self.state = "game_over"
                    self.add_score()
                    self.set_held_false()
                    return

        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if abs(int(bullet[0]) - int(enemy[0])) <= 1 and abs(int(bullet[1]) - int(enemy[1])) <= 1:
                    self.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.score += 10
                    break

    def render_menu(self):
        try:
            self.stdscr.erase()
            title = "Arcade Shooter"
            self.stdscr.addstr(2, max(0, self.width // 2 - len(title) // 2), title, curses.A_BOLD)
            self.stdscr.addstr(5, 4, "Top 3 :")
            self.stdscr.addstr(13, 4, "Chaque tranche de 100 points augmente la difficulté")

            if not self.high_scores:
                self.stdscr.addstr(7, 6, "Aucun score pour le moment.")
            else:
                for index, (pseudo, score) in enumerate(self.high_scores):
                    _, rank_name, rank_style = self.get_rank_style(score)
                    line = f"{index + 1}. [{rank_name}] {pseudo} - {score}"
                    self.stdscr.addstr(7 + index * 2, 6, line, rank_style)

            for index, option in enumerate(self.menu_options):
                prefix = ">" if index == self.menu_index else " "
                line = 15 + index * 3
                self.stdscr.addstr(line, 8, f"{prefix} {option}", curses.A_REVERSE if index == self.menu_index else curses.A_NORMAL)

            self.stdscr.addstr(self.height - 2, 2, "Flèches ou Z/S pour naviguer • Entrée pour valider • Q pour quitter")
            self.stdscr.refresh()
        except curses.error:
            pass

    def render_game(self):
        try:
            self.stdscr.erase()
            difficulty, label = self.get_difficulty()
            _, rank_name, rank_style = self.get_rank_style()
            self.stdscr.addstr(0, 0, f"Score : {self.score}   Vies : {self.lives}   Niveau : {label} ({rank_name})", rank_style)

            if difficulty == 6:
                self.stdscr.addstr(1, 0, "Mode secret : quasi impossible !", curses.A_BOLD)

            for bullet_x, bullet_y in self.bullets:
                if 0 <= bullet_y < self.height and 0 <= bullet_x < self.width:
                    self.stdscr.addch(bullet_y, bullet_x, ord("|"))

            for enemy_x, enemy_y in self.enemies:
                if 0 <= enemy_y < self.height and 0 <= enemy_x < self.width:
                    self.stdscr.addch(enemy_y, enemy_x, ord("V"))

            self.stdscr.addstr(self.player_y, self.player_x, "A")
            self.stdscr.refresh()
        except curses.error:
            pass

    def render_game_over(self):
        try:
            self.stdscr.erase()
            title = "Game Over"
            self.stdscr.addstr(2, max(0, self.width // 2 - len(title) // 2), title, curses.A_BOLD)
            self.stdscr.addstr(5, 6, f"Score final : {self.score}")
            self.stdscr.addstr(8, 6, "R : rejouer")
            self.stdscr.addstr(10, 6, "M : menu")
            self.stdscr.addstr(12, 6, "Q : quitter")
            self.stdscr.refresh()
        except curses.error:
            pass

    def run(self):
        while self.running:
            key = self.stdscr.getch()

            while key != -1:
                if self.state == "menu":
                    self.handle_menu_input(key)
                elif self.state == "playing":
                    self.handle_playing_input(key)
                elif self.state == "game_over":
                    self.handle_game_over_input(key)

                key = self.stdscr.getch()

            if self.state == "menu":
                self.render_menu()
            elif self.state == "playing":
                self.update_game()
                self.render_game()
            elif self.state == "game_over":
                self.render_game_over()

            time.sleep(0.016)


def main(stdscr):
    game = TouhouShooter(stdscr)
    game.run()


if __name__ == "__main__":
    curses.wrapper(main)