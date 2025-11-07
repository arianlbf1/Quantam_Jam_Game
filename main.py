"""Quantum Snake: an educational pygame game introducing quantum superposition and measurement."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Sequence, Tuple

import pygame

# Window and grid configuration
WINDOW_WIDTH, WINDOW_HEIGHT = 960, 720
CELL_SIZE = 24
GRID_WIDTH = WINDOW_WIDTH // CELL_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // CELL_SIZE

# Colours
BACKGROUND = (6, 8, 20)
GRID_COLOR = (20, 24, 40)
SNAKE_HEAD_COLOR = (255, 246, 140)
SNAKE_BODY_COLOR = (120, 220, 160)
FRUIT_COLOR = (255, 80, 110)
SUPERPOSITION_COLOR = (120, 210, 255, 170)
MEASUREMENT_HALO = (170, 80, 255, 200)
UI_PANEL = (12, 16, 40, 220)
UI_TEXT = (230, 240, 255)
HINT_TEXT = (230, 210, 255)

# Timing
MOVE_DELAY = 0.15  # seconds between snake steps
MEASUREMENT_FLASH_DURATION = 0.6
BANNER_DURATION = 3.5

pygame.init()
FONT = pygame.font.Font(None, 32)
SMALL_FONT = pygame.font.Font(None, 24)
TINY_FONT = pygame.font.Font(None, 20)
BIG_FONT = pygame.font.Font(None, 56)

Position = Tuple[int, int]


@dataclass
class LessonStage:
    """Metadata describing a lesson step."""

    title: str
    objective: str
    concept_notes: List[str]
    allow_measurement: bool
    superposition_chance: float
    target_length: int = 0
    target_collapses: int = 0
    target_score: int = 0


STAGES: Sequence[LessonStage] = [
    LessonStage(
        title="Classical Control",
        objective="Collect 5 data bits without crashing.",
        concept_notes=[
            "Snake moves deterministically on a grid.",
            "Eating classical fruit increases length by one.",
            "No quantum effects yet—focus on steering!",
        ],
        allow_measurement=False,
        superposition_chance=0.0,
        target_score=5,
    ),
    LessonStage(
        title="Quantum Superposition",
        objective="Collapse 3 shimmering fruit with the M key.",
        concept_notes=[
            "Quantum fruit exist in multiple positions until measured.",
            "Probabilities (percentages) show the likelihood of each state.",
            "Press M to perform a measurement and collapse the state.",
        ],
        allow_measurement=True,
        superposition_chance=1.0,
        target_collapses=3,
    ),
    LessonStage(
        title="Strategic Measurement",
        objective="Score 7 points while mixing classical and quantum fruit.",
        concept_notes=[
            "Not every fruit is quantum—decide when to measure.",
            "Measuring early guarantees a position but costs time.",
            "Let the superposition evolve as you line up a better shot.",
        ],
        allow_measurement=True,
        superposition_chance=0.6,
        target_score=7,
    ),
    LessonStage(
        title="Free Play Lab",
        objective="Keep experimenting! Try self-imposed challenges.",
        concept_notes=[
            "Combine movement, superposition, and measurement strategies.",
            "Try timing measurements just before contact for surprise collapses.",
            "Can you maintain a long snake while dealing with quantum fruit?",
        ],
        allow_measurement=True,
        superposition_chance=0.75,
    ),
]


class QuantumFruit:
    """Fruit that can exist in classical or superposed states."""

    def __init__(self) -> None:
        self.positions: List[Position] = [(0, 0)]
        self.weights: List[float] = [1.0]
        self.state: str = "classical"
        self.highlight_timer: float = 0.0

    def _available_positions(self, snake: Sequence[Position]) -> List[Position]:
        snake_set = set(snake)
        return [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in snake_set
        ]

    def spawn(self, snake: Sequence[Position], superposition_chance: float) -> None:
        if superposition_chance > 0 and random.random() < superposition_chance:
            self._spawn_superposition(snake)
        else:
            self._spawn_classical(snake)

    def _spawn_classical(self, snake: Sequence[Position]) -> None:
        available = self._available_positions(snake)
        if not available:
            return
        self.positions = [random.choice(available)]
        self.weights = [1.0]
        self.state = "classical"
        self.highlight_timer = 0.0

    def _spawn_superposition(self, snake: Sequence[Position]) -> None:
        available = self._available_positions(snake)
        if not available:
            self._spawn_classical(snake)
            return
        random.shuffle(available)
        desired_states = 2 if len(available) < 3 else random.choice([2, 2, 3])
        desired_states = min(desired_states, len(available))
        self.positions = available[:desired_states]
        raw_weights = [random.uniform(0.4, 1.2) for _ in self.positions]
        total = sum(raw_weights) or 1.0
        self.weights = [w / total for w in raw_weights]
        self.state = "superposition"
        self.highlight_timer = 0.0

    def measure(self) -> bool:
        if self.state != "superposition":
            return False
        indices = list(range(len(self.positions)))
        chosen_index = random.choices(indices, weights=self.weights)[0]
        chosen_position = self.positions[chosen_index]
        self.positions = [chosen_position]
        self.weights = [1.0]
        self.state = "collapsed"
        self.highlight_timer = MEASUREMENT_FLASH_DURATION
        return True

    def update(self, dt: float) -> None:
        if self.highlight_timer > 0:
            self.highlight_timer = max(0.0, self.highlight_timer - dt)

    def draw(self, surface: pygame.Surface) -> None:
        if self.state == "superposition":
            for idx, (x, y) in enumerate(self.positions):
                center = (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2)
                overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                pygame.draw.circle(
                    overlay,
                    SUPERPOSITION_COLOR,
                    (CELL_SIZE // 2, CELL_SIZE // 2),
                    CELL_SIZE // 2 - 2,
                )
                surface.blit(overlay, (center[0] - CELL_SIZE // 2, center[1] - CELL_SIZE // 2))
                probability = int(round(self.weights[idx] * 100))
                label = TINY_FONT.render(f"{probability}%", True, (10, 18, 44))
                label_rect = label.get_rect(center=center)
                surface.blit(label, label_rect)
        else:
            x, y = self.positions[0]
            center = (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2)
            pygame.draw.circle(
                surface,
                FRUIT_COLOR,
                center,
                CELL_SIZE // 2 - 2,
            )
            if self.highlight_timer > 0:
                alpha = int(255 * (self.highlight_timer / MEASUREMENT_FLASH_DURATION))
                halo_surface = pygame.Surface((CELL_SIZE * 2, CELL_SIZE * 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    halo_surface,
                    (*MEASUREMENT_HALO[:3], alpha),
                    (CELL_SIZE, CELL_SIZE),
                    CELL_SIZE,
                    width=3,
                )
                surface.blit(halo_surface, (center[0] - CELL_SIZE, center[1] - CELL_SIZE))


class QuantumSnakeGame:
    """Encapsulates gameplay, rendering, and lesson progression."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.snake: List[Position] = []
        self.direction: Position = (1, 0)
        self.next_direction: Position = (1, 0)
        self.pending_growth = 0
        self.elapsed_move = 0.0

        self.stage_index = 0
        self.stage_points = 0
        self.stage_collapses = 0
        self.total_points = 0
        self.total_collapses = 0

        self.measurement_flash_timer = 0.0
        self.measurement_hint_timer = 0.0
        self.banner_timer = 0.0
        self.banner_text = ""

        self.fruit = QuantumFruit()
        self.start_stage(initial=True)

    def start_stage(self, initial: bool = False, message: str | None = None) -> None:
        self.snake = [(GRID_WIDTH // 2 - i, GRID_HEIGHT // 2) for i in range(3)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.pending_growth = 0
        self.elapsed_move = 0.0
        self.stage_points = 0
        self.stage_collapses = 0
        self.measurement_flash_timer = 0.0
        self.measurement_hint_timer = 0.0

        stage = STAGES[self.stage_index]
        self.fruit.spawn(self.snake, stage.superposition_chance)

        if message:
            self.banner_text = message
        else:
            self.banner_text = f"Stage {self.stage_index + 1}: {stage.title} — {stage.objective}"
        self.banner_timer = BANNER_DURATION if (initial or message) else BANNER_DURATION

    def fail_stage(self, reason: str) -> None:
        stage = STAGES[self.stage_index]
        fail_message = f"Stage reset: {reason}"
        if not stage.allow_measurement:
            fail_message += " (Tip: arrow keys steer!)"
        self.start_stage(message=fail_message)

    def handle_direction_change(self, key: int) -> None:
        if key in (pygame.K_UP, pygame.K_w):
            new_direction = (0, -1)
        elif key in (pygame.K_DOWN, pygame.K_s):
            new_direction = (0, 1)
        elif key in (pygame.K_LEFT, pygame.K_a):
            new_direction = (-1, 0)
        elif key in (pygame.K_RIGHT, pygame.K_d):
            new_direction = (1, 0)
        else:
            return

        # Prevent reversing directly into yourself
        if len(self.snake) > 1 and (
            new_direction[0] == -self.direction[0] and new_direction[1] == -self.direction[1]
        ):
            return
        self.next_direction = new_direction

    def attempt_measurement(self) -> None:
        stage = STAGES[self.stage_index]
        if not stage.allow_measurement:
            self.measurement_hint_timer = 1.5
            return
        if self.fruit.measure():
            self.stage_collapses += 1
            self.total_collapses += 1
            self.measurement_flash_timer = MEASUREMENT_FLASH_DURATION
        else:
            self.measurement_hint_timer = 1.2

    def move_snake(self) -> None:
        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])

        if not (0 <= new_head[0] < GRID_WIDTH) or not (0 <= new_head[1] < GRID_HEIGHT):
            self.fail_stage("You hit the wall")
            return
        if new_head in self.snake:
            self.fail_stage("The snake intersected itself")
            return

        self.snake.insert(0, new_head)

        ate_fruit = False
        if self.fruit.state == "superposition" and new_head in self.fruit.positions:
            self.measurement_hint_timer = 1.5
        elif self.fruit.state != "superposition" and new_head == self.fruit.positions[0]:
            ate_fruit = True

        if ate_fruit:
            self.pending_growth += 1
            self.total_points += 1
            self.stage_points += 1
            stage = STAGES[self.stage_index]
            self.fruit.spawn(self.snake, stage.superposition_chance)
        if self.pending_growth > 0:
            self.pending_growth -= 1
        else:
            self.snake.pop()

    def check_progression(self) -> None:
        if self.stage_index >= len(STAGES) - 1:
            return
        stage = STAGES[self.stage_index]
        if stage.target_length and len(self.snake) >= stage.target_length:
            self.advance_stage()
        elif stage.target_collapses and self.stage_collapses >= stage.target_collapses:
            self.advance_stage()
        elif stage.target_score and self.stage_points >= stage.target_score:
            self.advance_stage()

    def advance_stage(self) -> None:
        if self.stage_index < len(STAGES) - 1:
            self.stage_index += 1
            self.start_stage()

    def update(self, dt: float) -> None:
        self.elapsed_move += dt
        if self.measurement_flash_timer > 0:
            self.measurement_flash_timer = max(0.0, self.measurement_flash_timer - dt)
        if self.measurement_hint_timer > 0:
            self.measurement_hint_timer = max(0.0, self.measurement_hint_timer - dt)
        if self.banner_timer > 0:
            self.banner_timer = max(0.0, self.banner_timer - dt)

        self.fruit.update(dt)

        if self.elapsed_move >= MOVE_DELAY:
            self.elapsed_move -= MOVE_DELAY
            self.move_snake()
            self.check_progression()

    def draw_grid(self) -> None:
        for x in range(GRID_WIDTH):
            pygame.draw.line(
                self.screen,
                GRID_COLOR,
                (x * CELL_SIZE, 0),
                (x * CELL_SIZE, WINDOW_HEIGHT),
                1,
            )
        for y in range(GRID_HEIGHT):
            pygame.draw.line(
                self.screen,
                GRID_COLOR,
                (0, y * CELL_SIZE),
                (WINDOW_WIDTH, y * CELL_SIZE),
                1,
            )

    def draw_snake(self) -> None:
        for index, (x, y) in enumerate(self.snake):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if index == 0:
                pygame.draw.rect(self.screen, SNAKE_HEAD_COLOR, rect, border_radius=6)
            else:
                body_color = (
                    SNAKE_BODY_COLOR[0],
                    int(SNAKE_BODY_COLOR[1] * (0.9 + 0.1 * (index % 2))),
                    SNAKE_BODY_COLOR[2],
                )
                pygame.draw.rect(self.screen, body_color, rect, border_radius=4)

    def draw_panel(self) -> None:
        stage = STAGES[self.stage_index]
        panel = pygame.Surface((WINDOW_WIDTH, 150), pygame.SRCALPHA)
        panel.fill(UI_PANEL)
        self.screen.blit(panel, (0, 0))

        title_text = FONT.render(stage.title, True, UI_TEXT)
        self.screen.blit(title_text, (24, 12))

        objective_text = SMALL_FONT.render(stage.objective, True, UI_TEXT)
        self.screen.blit(objective_text, (24, 52))

        stats = (
            f"Stage points: {self.stage_points}    "
            f"Snake length: {len(self.snake)}    "
            f"Collapses: {self.stage_collapses}"
        )
        stats_text = SMALL_FONT.render(stats, True, UI_TEXT)
        self.screen.blit(stats_text, (24, 86))

        total_stats = SMALL_FONT.render(
            f"Total points: {self.total_points}   Total collapses: {self.total_collapses}",
            True,
            UI_TEXT,
        )
        self.screen.blit(total_stats, (24, 118))

        concept_x = WINDOW_WIDTH - 360
        concept_y = 18
        concept_heading = SMALL_FONT.render("Concept focus:", True, UI_TEXT)
        self.screen.blit(concept_heading, (concept_x, concept_y))
        for idx, note in enumerate(stage.concept_notes):
            bullet = TINY_FONT.render(f"• {note}", True, UI_TEXT)
            self.screen.blit(bullet, (concept_x, concept_y + 28 + idx * 22))

    def draw_overlay_texts(self) -> None:
        if self.banner_timer > 0 and self.banner_text:
            banner_surface = pygame.Surface((WINDOW_WIDTH, 80), pygame.SRCALPHA)
            banner_surface.fill((12, 0, 48, int(160 * (self.banner_timer / BANNER_DURATION + 0.2))))
            self.screen.blit(banner_surface, (0, WINDOW_HEIGHT // 2 - 120))
            text = BIG_FONT.render(self.banner_text, True, HINT_TEXT)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 80))
            self.screen.blit(text, text_rect)

        if self.measurement_flash_timer > 0:
            alpha = int(120 * (self.measurement_flash_timer / MEASUREMENT_FLASH_DURATION))
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((80, 0, 120, alpha))
            self.screen.blit(overlay, (0, 0))

        control_hint = SMALL_FONT.render("Controls: Arrow keys/WASD move • M measures superpositions", True, HINT_TEXT)
        hint_rect = control_hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 24))
        self.screen.blit(control_hint, hint_rect)

        if self.measurement_hint_timer > 0:
            hint = "Measure first! Press M to collapse the quantum fruit."
            text = FONT.render(hint, True, HINT_TEXT)
            rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 64))
            self.screen.blit(text, rect)

    def draw(self) -> None:
        self.screen.fill(BACKGROUND)
        self.draw_grid()
        self.draw_snake()
        self.fruit.draw(self.screen)
        self.draw_panel()
        self.draw_overlay_texts()

    def run(self) -> None:
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_m:
                        self.attempt_measurement()
                    else:
                        self.handle_direction_change(event.key)

            self.update(dt)
            self.draw()
            pygame.display.flip()

        pygame.quit()


def main() -> None:
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Quantum Snake: Superposition and Measurement")
    game = QuantumSnakeGame(screen)
    game.run()


if __name__ == "__main__":
    main()
