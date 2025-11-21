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
PANEL_BG = (20, 20, 60, 190)
PANEL_BORDER = (90, 90, 160)

MEASUREMENT_DISTANCE = GRID_SIZE * 2
TUTORIAL_FONT_SIZE = 20
PANEL_WIDTH = 260


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

        self.state = "menu"  # menu | tutorial | free_play
        self.tutorial_level = 0
        self.tutorial_ready_to_advance = False
        self.tutorial_target = pygame.Vector2(GRID_WIDTH // 2 + 5, GRID_HEIGHT // 2)
        self.score = 0
        self.game_over = False
        self.reset_game()

    def reset_game(self):
        start_pos = pygame.Vector2(GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.snake = Snake([start_pos], pygame.Vector2(1, 0))
        self.apple: QuantumApple | None = QuantumApple(self.snake.positions)
        self.score = 0
        self.game_over = False

    def start_free_play(self):
        self.state = "free_play"
        self.reset_game()

    def start_tutorial(self):
        self.tutorial_level = 0
        self.state = "tutorial"
        self.prepare_tutorial_level()

    def prepare_tutorial_level(self):
        self.reset_game()
        self.tutorial_ready_to_advance = False
        if self.tutorial_level == 0:
            # Movement basics
            self.apple = None
            self.snake.direction = pygame.Vector2(1, 0)
            self.tutorial_target = pygame.Vector2(GRID_WIDTH // 2 + 6, GRID_HEIGHT // 2)
        elif self.tutorial_level == 1:
            # Superposition collapse
            self.apple = QuantumApple(self.snake.positions)
        elif self.tutorial_level == 2:
            # Measurement and eating
            self.apple = QuantumApple(self.snake.positions)
        else:
            self.start_free_play()

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

    def process_apple_interactions(self, spawn_new_on_eat: bool = True):
        measured_now = False
        ate = False
        if self.apple:
            measured_now = self.apple.check_proximity(self.snake.head())
            if self.apple.measured and self.snake.head() == self.apple.real_position:
                self.snake.grow()
                self.score += 1
                ate = True
                if spawn_new_on_eat:
                    self.apple = QuantumApple(self.snake.positions)
                else:
                    self.apple = None
        return measured_now, ate

    def check_collisions(self):
        if self.snake.hits_boundary() or self.snake.hits_self():
            self.game_over = True

    def update_free_play(self):
        self.handle_input()
        self.snake.move()
        self.process_apple_interactions(spawn_new_on_eat=True)
        self.check_collisions()

    def update_tutorial(self):
        if self.tutorial_level >= 3:
            return
        self.handle_input()
        self.snake.move()

        if self.tutorial_level == 0:
            if self.snake.head() == self.tutorial_target:
                self.tutorial_ready_to_advance = True
        elif self.tutorial_level == 1:
            measured_now, _ = self.process_apple_interactions(spawn_new_on_eat=False)
            if measured_now:
                self.tutorial_ready_to_advance = True
        elif self.tutorial_level == 2:
            measured_now, ate = self.process_apple_interactions(spawn_new_on_eat=False)
            if self.apple is None and ate:
                # apple removed after eating measured one
                self.tutorial_ready_to_advance = True
            elif measured_now:
                # allow player to see collapse even if not yet eaten
                pass
        self.check_collisions()

    def draw_target_tile(self):
        rect = pygame.Rect(self.tutorial_target.x * GRID_SIZE, self.tutorial_target.y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(self.screen, (255, 200, 90), rect, border_radius=6)
        outline = pygame.Rect(rect.x - 2, rect.y - 2, rect.width + 4, rect.height + 4)
        pygame.draw.rect(self.screen, (255, 150, 40), outline, 2, border_radius=6)

    def draw(self):
        self.screen.fill(BACKGROUND)
        if self.state in {"tutorial", "free_play"}:
            self.draw_grid()
            if self.apple:
                self.apple.draw(self.screen)
            if self.state == "tutorial" and self.tutorial_level == 0:
                self.draw_target_tile()
            self.draw_snake()
            self.draw_score()
            if self.state == "tutorial":
                self.draw_tutorial_panel()
            if self.game_over:
                self.draw_game_over()
        elif self.state == "menu":
            self.draw_menu()

    def tutorial_lines(self) -> list[str]:
        if self.tutorial_level == 0:
            return [
                "Level 1: Movement", 
                "Use arrow keys to move.",
                "Reach the highlighted tile to continue.",
            ]
        if self.tutorial_level == 1:
            return [
                "Level 2: Superposition", 
                "Apples start as two ghost positions.",
                "Approach them to trigger a measurement.",
            ]
        return [
            "Level 3: Measurement & Growth", 
            "After collapse, only one apple is real.",
            "Eat the measured apple to grow and score!",
        ]

    def draw_tutorial_panel(self):
        panel = pygame.Surface((PANEL_WIDTH, HEIGHT), pygame.SRCALPHA)
        panel.fill(PANEL_BG)
        border_rect = panel.get_rect()
        pygame.draw.rect(panel, PANEL_BORDER, border_rect, 2)

        padding = 12
        y = padding
        for line in self.tutorial_lines():
            text = self.tutorial_font.render(line, True, TEXT_COLOR)
            panel.blit(text, (padding, y))
            y += TUTORIAL_FONT_SIZE + 6

        if self.tutorial_level == 1:
            detail = "Watch one clone vanish: that's measurement!"
        elif self.tutorial_level == 2:
            detail = "Measured apples stay; eat them to grow."
        else:
            detail = "Grid navigation keeps you alive."
        detail_text = self.tutorial_font.render(detail, True, TEXT_COLOR)
        panel.blit(detail_text, (padding, y + 6))

        if self.tutorial_ready_to_advance and not self.game_over:
            advance_msg = "Press ENTER for next lesson" if self.tutorial_level < 2 else "Press ENTER for Free Play"
        else:
            advance_msg = "Complete the objective to advance"
        advance_text = self.tutorial_font.render(advance_msg, True, TEXT_COLOR)
        panel.blit(advance_text, (padding, HEIGHT - 40))

        self.screen.blit(panel, (WIDTH - PANEL_WIDTH, 0))

    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        title = self.font.render("Game Over", True, TEXT_COLOR)
        prompt = self.font.render("Press R to restart", True, TEXT_COLOR)
        rect = title.get_rect(center=(WIDTH // 2 - PANEL_WIDTH // 2, HEIGHT // 2 - 20))
        self.screen.blit(title, rect)
        rect2 = prompt.get_rect(center=(WIDTH // 2 - PANEL_WIDTH // 2, HEIGHT // 2 + 20))
        self.screen.blit(prompt, rect2)

    def draw_menu(self):
        self.screen.fill(BACKGROUND)
        title = self.font.render("Quantum Snake", True, TEXT_COLOR)
        subtitle = self.tutorial_font.render("Learn quantum ideas through play", True, TEXT_COLOR)
        prompt1 = self.font.render("Press T for Tutorial", True, TEXT_COLOR)
        prompt2 = self.font.render("Press F for Free Play", True, TEXT_COLOR)
        center_x = WIDTH // 2
        self.screen.blit(title, title.get_rect(center=(center_x, HEIGHT // 2 - 80)))
        self.screen.blit(subtitle, subtitle.get_rect(center=(center_x, HEIGHT // 2 - 40)))
        self.screen.blit(prompt1, prompt1.get_rect(center=(center_x, HEIGHT // 2 + 20)))
        self.screen.blit(prompt2, prompt2.get_rect(center=(center_x, HEIGHT // 2 + 60)))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if self.state == "menu":
                        if event.key == pygame.K_t:
                            self.start_tutorial()
                        elif event.key == pygame.K_f:
                            self.start_free_play()
                    elif self.state == "tutorial":
                        if event.key == pygame.K_RETURN and self.tutorial_ready_to_advance and not self.game_over:
                            self.tutorial_level += 1
                            self.prepare_tutorial_level()
                        if event.key == pygame.K_r and self.game_over:
                            self.prepare_tutorial_level()
                    elif self.state == "free_play":
                        if event.key == pygame.K_r and self.game_over:
                            self.start_free_play()

            if self.state == "tutorial" and not self.game_over:
                self.update_tutorial()
            elif self.state == "free_play" and not self.game_over:
                self.update_free_play()

            self.draw()
            pygame.display.flip()
            self.clock.tick(10)


def main():
    Game().run()


if __name__ == "__main__":
    main()
