import curses
import random
import time
from pathlib import Path

SCORES_FILE = Path(__file__).resolve().parent / "scores_joueurs" / "arcade_shooter_scores.txt"


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
        self.high_scores = load_scores()
        self.state = "menu"
        self.menu_index = 0
        self.menu_options = ["Démarrer", "Quitter"]
        self.running = True
        self.player_name = "Joueur"
        self.reset_game()

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
        elif key in (ord(" "), ord("a"), ord("A"), ord("x"), ord("X")):
            self.fire()
        elif key in (ord("q"), ord("Q")):
            self.state = "menu"

        self.player_x = int(max(2, min(self.player_x, self.width - 3)))
        self.player_y = int(max(2, min(self.player_y, self.height - 3)))

    def set_held_false(self):
        self.held = {"left": False, "right": False, "up": False, "down": False, "shoot": False}

    def move_player(self, dt):
        return

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

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            spawn_count = 1 + (self.score // 120)
            for _ in range(min(3, max(1, spawn_count))):
                self.spawn_enemy()
            self.spawn_timer = max(0.18, 0.9 - self.score / 800)

        self.enemy_speed = 1.2 + min(7.0, self.score / 180)

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

            if not self.high_scores:
                self.stdscr.addstr(7, 6, "Aucun score pour le moment.")
            else:
                for index, (pseudo, score) in enumerate(self.high_scores):
                    self.stdscr.addstr(7 + index * 2, 6, f"{index + 1}. {pseudo} - {score}")

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
            self.stdscr.addstr(0, 0, f"Score : {self.score}   Vies : {self.lives}")

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

            if self.state == "menu":
                if key != -1:
                    self.handle_menu_input(key)
                self.render_menu()
            elif self.state == "playing":
                if key != -1:
                    self.handle_playing_input(key)
                self.update_game()
                self.render_game()
            elif self.state == "game_over":
                if key != -1:
                    self.handle_game_over_input(key)
                self.render_game_over()

            time.sleep(0.016)


def main(stdscr):
    game = TouhouShooter(stdscr)
    game.run()


if __name__ == "__main__":
    curses.wrapper(main)
