import random
import sys
from dataclasses import dataclass

import pygame


# Window and grid settings
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

BACKGROUND = (12, 10, 24)
GRID_COLOR = (40, 40, 70)
SNAKE_COLOR = (80, 220, 120)
APPLE_COLOR = (230, 76, 102)
APPLE_CLONE_COLOR = (180, 120, 255)
TEXT_COLOR = (240, 240, 255)

MEASUREMENT_DISTANCE = GRID_SIZE * 2
TUTORIAL_FONT_SIZE = 22


@dataclass
class Snake:
    positions: list
    direction: pygame.Vector2
    growing: int = 0

    def head(self) -> pygame.Vector2:
        return self.positions[0]

    def turn(self, new_direction: pygame.Vector2) -> None:
        if self.positions and (self.direction + new_direction) != pygame.Vector2(0, 0):
            self.direction = new_direction

    def move(self) -> None:
        new_head = self.head() + self.direction
        self.positions.insert(0, new_head)
        if self.growing > 0:
            self.growing -= 1
        else:
            self.positions.pop()

    def grow(self, amount: int = 1) -> None:
        self.growing += amount

    def hits_boundary(self) -> bool:
        head = self.head()
        return head.x < 0 or head.x >= GRID_WIDTH or head.y < 0 or head.y >= GRID_HEIGHT

    def hits_self(self) -> bool:
        return self.head() in self.positions[1:]


class QuantumApple:
    """Represents an apple in superposition until measured."""

    def __init__(self, snake_positions: list[pygame.Vector2]):
        self.measured = False
        self.real_position: pygame.Vector2 | None = None
        self.positions = self._spawn_positions(snake_positions)

    def _spawn_positions(self, snake_positions: list[pygame.Vector2]):
        available = [
            pygame.Vector2(x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if pygame.Vector2(x, y) not in snake_positions
        ]
        pos1 = random.choice(available)
        available.remove(pos1)
        pos2 = random.choice(available)
        return [pos1, pos2]

    def measure(self):
        if not self.measured:
            self.real_position = random.choice(self.positions)
            self.measured = True

    def check_proximity(self, snake_head: pygame.Vector2):
        if self.measured:
            return False
        for pos in self.positions:
            distance = snake_head.distance_to(pos)
            if distance * GRID_SIZE <= MEASUREMENT_DISTANCE:
                self.measure()
                return True
        return False

    def draw(self, surface: pygame.Surface):
        if not self.measured:
            for pos in self.positions:
                rect = pygame.Rect(pos.x * GRID_SIZE, pos.y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(surface, APPLE_CLONE_COLOR, rect, border_radius=6)
        else:
            pos = self.real_position
            rect = pygame.Rect(pos.x * GRID_SIZE, pos.y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, APPLE_COLOR, rect, border_radius=6)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Quantum Snake")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 24)
        self.tutorial_font = pygame.font.SysFont("arial", TUTORIAL_FONT_SIZE)

        self.reset_game()
        self.mode = "tutorial"
        self.tutorial_measurement_done = False

    def reset_game(self):
        start_pos = pygame.Vector2(GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.snake = Snake([start_pos], pygame.Vector2(1, 0))
        self.apple = QuantumApple(self.snake.positions)
        self.score = 0
        self.game_over = False

    def draw_grid(self):
        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (WIDTH, y))

    def draw_snake(self):
        for pos in self.snake.positions:
            rect = pygame.Rect(pos.x * GRID_SIZE, pos.y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(self.screen, SNAKE_COLOR, rect, border_radius=4)

    def draw_score(self):
        text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(text, (10, 10))

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.snake.turn(pygame.Vector2(0, -1))
        elif keys[pygame.K_DOWN]:
            self.snake.turn(pygame.Vector2(0, 1))
        elif keys[pygame.K_LEFT]:
            self.snake.turn(pygame.Vector2(-1, 0))
        elif keys[pygame.K_RIGHT]:
            self.snake.turn(pygame.Vector2(1, 0))

    def update(self):
        self.handle_input()
        self.snake.move()
        measured_now = self.apple.check_proximity(self.snake.head())
        if measured_now and self.mode == "tutorial":
            self.tutorial_measurement_done = True

        if self.apple.measured and self.snake.head() == self.apple.real_position:
            self.snake.grow()
            self.score += 1
            self.apple = QuantumApple(self.snake.positions)
            self.tutorial_measurement_done = False

        if self.snake.hits_boundary() or self.snake.hits_self():
            self.game_over = True

    def draw(self):
        self.screen.fill(BACKGROUND)
        self.draw_grid()
        self.apple.draw(self.screen)
        self.draw_snake()
        self.draw_score()

    def tutorial_text(self) -> list[str]:
        return [
            "Welcome to Quantum Snake!",
            "1. Arrows move the snake on the grid.",
            "2. Apples start in SUPERPOSITION (two ghost clones).",
            "3. Measurement happens when you get close: one apple stays, the clone vanishes.",
            "4. Eat the measured apple to grow and score.",
            "Move near the ghost apples to perform a measurement.",
        ]

    def draw_tutorial_overlay(self):
        box_rect = pygame.Rect(40, 40, WIDTH - 80, 180)
        pygame.draw.rect(self.screen, (20, 20, 60), box_rect, border_radius=8)
        pygame.draw.rect(self.screen, (70, 70, 130), box_rect, 2, border_radius=8)

        lines = self.tutorial_text()
        for i, line in enumerate(lines):
            text = self.tutorial_font.render(line, True, TEXT_COLOR)
            self.screen.blit(text, (60, 60 + i * 26))

        bottom_msg = "After you measure once, press ENTER for the full game." if self.tutorial_measurement_done else "Try getting close to trigger a measurement."
        bottom_text = self.tutorial_font.render(bottom_msg, True, TEXT_COLOR)
        self.screen.blit(bottom_text, (60, box_rect.bottom - 36))

    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        title = self.font.render("Game Over", True, TEXT_COLOR)
        prompt = self.font.render("Press R to restart", True, TEXT_COLOR)
        rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        self.screen.blit(title, rect)
        rect2 = prompt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        self.screen.blit(prompt, rect2)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if self.mode == "tutorial" and event.key == pygame.K_RETURN and self.tutorial_measurement_done:
                        self.mode = "game"
                        self.reset_game()
                    if event.key == pygame.K_r and self.game_over:
                        self.reset_game()
                        self.mode = "game"
                        self.game_over = False

            if not self.game_over:
                self.update()

            self.draw()

            if self.mode == "tutorial":
                self.draw_tutorial_overlay()
            if self.game_over:
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(10)


def main():
    Game().run()


if __name__ == "__main__":
    main()
