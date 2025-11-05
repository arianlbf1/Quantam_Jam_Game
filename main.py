"""Quantum Pong: A pygame-based educational game demonstrating quantum concepts.

The game layers the basics of classical Pong with two quantum computing concepts:
    * Superposition: the ball can travel in multiple probable paths simultaneously.
    * Measurement: observing the quantum ball collapses it to a single classical path.

Players can experiment with when to measure to collapse the ball, or allow the
superposition to evolve to confuse the opponent's paddle.

Run with: python main.py
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import List

import pygame

WIDTH, HEIGHT = 960, 540
PADDLE_WIDTH, PADDLE_HEIGHT = 16, 96
BALL_RADIUS = 10
PADDLE_SPEED = 260
BALL_SPEED = 230
SPLIT_ANGLE = math.radians(11)
MAX_STATES = 4
MEASUREMENT_STRIP_X = WIDTH // 2
MEASUREMENT_STRIP_WIDTH = 12

pygame.init()
FONT = pygame.font.SysFont("Fira Code", 20)
SMALL_FONT = pygame.font.SysFont("Fira Code", 16)
TITLE_FONT = pygame.font.SysFont("Fira Code", 28, bold=True)


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


@dataclass
class Paddle:
    x: float
    y: float
    is_player: bool = False

    def move(self, direction: float, dt: float) -> None:
        self.y += direction * PADDLE_SPEED * dt
        self.y = clamp(self.y, 0, HEIGHT - PADDLE_HEIGHT)

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), PADDLE_WIDTH, PADDLE_HEIGHT)


@dataclass
class QuantumState:
    x: float
    y: float
    vx: float
    vy: float
    probability: float
    color: pygame.Color = field(default_factory=lambda: pygame.Color(120, 200, 255))

    def copy(self) -> "QuantumState":
        return QuantumState(self.x, self.y, self.vx, self.vy, self.probability, self.color)


@dataclass
class LessonStage:
    title: str
    summary: List[str]
    objective: str
    allow_superposition: bool = False
    allow_measurement: bool = False
    required_rallies: int = 0
    required_superposition_time: float = 0.0
    measurement_goal: int = 0


class QuantumBall:
    def __init__(self) -> None:
        self.states: List[QuantumState] = []
        self.collapse_timer = 0.0
        self.reset(direction=1)

    def reset(self, direction: int) -> None:
        self.states = [
            QuantumState(WIDTH / 2, HEIGHT / 2, direction * BALL_SPEED, random.uniform(-140, 140), 1.0,
                         pygame.Color(255, 255, 255)),
        ]
        self.collapse_timer = 0.0

    def ensure_normalised(self) -> None:
        total = sum(state.probability for state in self.states)
        if total == 0:
            equal_prob = 1.0 / len(self.states)
            for state in self.states:
                state.probability = equal_prob
            return
        for state in self.states:
            state.probability /= total

    def update(self, dt: float) -> None:
        self.collapse_timer += dt
        for state in self.states:
            state.x += state.vx * dt
            state.y += state.vy * dt

            if state.y - BALL_RADIUS < 0:
                state.y = BALL_RADIUS
                state.vy = abs(state.vy)
            elif state.y + BALL_RADIUS > HEIGHT:
                state.y = HEIGHT - BALL_RADIUS
                state.vy = -abs(state.vy)

        self.ensure_normalised()

    def draw(self, surface: pygame.Surface) -> None:
        for state in self.states:
            alpha = clamp(int(120 + state.probability * 120), 80, 255)
            overlay = pygame.Surface((BALL_RADIUS * 2, BALL_RADIUS * 2), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 0))
            pygame.draw.circle(overlay, (*state.color[:3], alpha), (BALL_RADIUS, BALL_RADIUS), BALL_RADIUS)
            surface.blit(overlay, (state.x - BALL_RADIUS, state.y - BALL_RADIUS))

    def measure(self) -> None:
        probabilities = [state.probability for state in self.states]
        cumulative = []
        total = 0.0
        for prob in probabilities:
            total += prob
            cumulative.append(total)
        collapse_value = random.random() * total
        chosen_index = 0
        for idx, boundary in enumerate(cumulative):
            if collapse_value <= boundary:
                chosen_index = idx
                break
        chosen_state = self.states[chosen_index]
        chosen_state.probability = 1.0
        chosen_state.color = pygame.Color(255, 230, 120)
        self.states = [chosen_state]
        self.collapse_timer = 0.0

    def split(self, angle_sign: int) -> None:
        if len(self.states) >= MAX_STATES:
            return
        new_states: List[QuantumState] = []
        for state in self.states:
            base = state.copy()
            rotated = state.copy()
            # Slightly rotate velocity to create a new path
            speed = math.hypot(state.vx, state.vy)
            angle = math.atan2(state.vy, state.vx)
            rotated_angle = angle + angle_sign * SPLIT_ANGLE
            rotated.vx = math.cos(rotated_angle) * speed
            rotated.vy = math.sin(rotated_angle) * speed
            rotated.color = pygame.Color(180, 255, 180)
            base.color = pygame.Color(200, 160, 255)
            new_states.extend([base, rotated])
        equal_prob = 1.0 / len(new_states)
        for state in new_states:
            state.probability = equal_prob
        self.states = new_states
        self.collapse_timer = 0.0

    def average_position(self) -> tuple[float, float]:
        avg_x = sum(state.x * state.probability for state in self.states)
        avg_y = sum(state.y * state.probability for state in self.states)
        return avg_x, avg_y

    def any_state_offscreen(self) -> int | None:
        for state in self.states:
            if state.x + BALL_RADIUS < 0:
                return -1
            if state.x - BALL_RADIUS > WIDTH:
                return 1
        return None

    def collide_with_paddle(self, paddle: Paddle, allow_superposition: bool) -> bool:
        collided = False
        for state in self.states:
            if paddle.rect.collidepoint(state.x, state.y):
                collided = True
                state.x = (
                    paddle.rect.right + BALL_RADIUS
                    if paddle.x < WIDTH / 2
                    else paddle.rect.left - BALL_RADIUS
                )
                state.vx *= -1
                offset = ((state.y - paddle.y) / PADDLE_HEIGHT) - 0.5
                state.vy = offset * BALL_SPEED * 1.4
        if collided and allow_superposition:
            self.split(angle_sign=-1 if paddle.x < WIDTH / 2 else 1)
        self.ensure_normalised()
        return collided


class QuantumPong:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Quantum Pong: Superposition Showdown")
        self.clock = pygame.time.Clock()
        self.ball = QuantumBall()
        self.player = Paddle(32, HEIGHT / 2 - PADDLE_HEIGHT / 2, is_player=True)
        self.opponent = Paddle(WIDTH - 48, HEIGHT / 2 - PADDLE_HEIGHT / 2)
        self.player_score = 0
        self.opponent_score = 0
        self.running = True
        self.paused = False
        self.measure_hint_timer = 0.0
        self.lesson_stages: List[LessonStage] = [
            LessonStage(
                title="Stage 1 · Classical Rally",
                summary=[
                    "This warm-up mirrors classic Pong.",
                    "Track the white ball and meet it with your paddle.",
                    "Feel how predictable classical motion can be.",
                ],
                objective="Return the ball 3 times using your paddle.",
                required_rallies=3,
            ),
            LessonStage(
                title="Stage 2 · Superposition",
                summary=[
                    "Now the ball can branch into several probable paths.",
                    "Each colored copy shows where the quantum ball might be.",
                    "Let the probabilities evolve before you make a decision.",
                ],
                objective="Keep the rally going while superposed paths persist for 5 seconds.",
                allow_superposition=True,
                required_superposition_time=5.0,
            ),
            LessonStage(
                title="Stage 3 · Measurement",
                summary=[
                    "Observing the system collapses it to one outcome.",
                    "Press M to actively measure, or guide the ball through the purple gate.",
                    "Notice how the quantum spread disappears after measuring.",
                ],
                objective="Trigger 2 measurements to collapse the ball.",
                allow_superposition=True,
                allow_measurement=True,
                measurement_goal=2,
            ),
            LessonStage(
                title="Stage 4 · Sandbox",
                summary=[
                    "Combine all the ideas at your own pace.",
                    "Experiment with delaying or hastening measurement.",
                    "Can you predict the opponent while managing uncertainty?",
                ],
                objective="Free play — explore superposition and measurement together.",
                allow_superposition=True,
                allow_measurement=True,
            ),
        ]
        self.stage_index = 0
        self.stage_intro_active = True
        self.stage_timer = 0.0
        self.superposition_timer = 0.0
        self.measurements_made = 0
        self.player_rallies = 0
        self.lesson_complete = False

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(60) / 1000
            self.handle_events()
            if not self.paused and not self.stage_intro_active:
                self.update(dt)
            self.draw()
        pygame.quit()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE and not self.stage_intro_active:
                    self.paused = not self.paused
                elif event.key == pygame.K_RETURN and self.stage_intro_active:
                    self.start_stage_play()
                elif (
                    event.key == pygame.K_m
                    and not self.paused
                    and not self.stage_intro_active
                    and self.current_stage.allow_measurement
                ):
                    self.register_measurement(manual=True)

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        direction = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            direction -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            direction += 1
        self.player.move(direction, dt)

        avg_x, avg_y = self.ball.average_position()
        if avg_y < self.opponent.y + PADDLE_HEIGHT / 2:
            self.opponent.move(-0.6, dt)
        else:
            self.opponent.move(0.6, dt)

        self.ball.update(dt)
        if self.ball.collide_with_paddle(self.player, self.current_stage.allow_superposition):
            self.player_rallies += 1
        self.ball.collide_with_paddle(self.opponent, self.current_stage.allow_superposition)

        if self.current_stage.allow_measurement and self.should_measure_strip():
            self.register_measurement(manual=False)

        score_direction = self.ball.any_state_offscreen()
        if score_direction == -1:
            self.opponent_score += 1
            self.ball.reset(direction=1)
        elif score_direction == 1:
            self.player_score += 1
            self.ball.reset(direction=-1)

        self.measure_hint_timer += dt
        self.stage_timer += dt
        if len(self.ball.states) > 1:
            self.superposition_timer += dt

    def should_measure_strip(self) -> bool:
        for state in self.ball.states:
            if MEASUREMENT_STRIP_X <= state.x <= MEASUREMENT_STRIP_X + MEASUREMENT_STRIP_WIDTH:
                if self.ball.collapse_timer > 0.8:
                    return True
        return False

    def register_measurement(self, manual: bool) -> None:
        self.ball.measure()
        self.measure_hint_timer = 0.0
        self.measurements_made += 1
        if manual:
            self.ball.collapse_timer = 0.0

    def draw_probability_bar(self) -> None:
        bar_width = 220
        bar_height = 14
        x = WIDTH // 2 - bar_width // 2
        y = HEIGHT - 60
        pygame.draw.rect(self.screen, (26, 26, 36), (x, y, bar_width, bar_height), border_radius=6)
        offset = x
        for state in self.ball.states:
            width = bar_width * state.probability
            pygame.draw.rect(
                self.screen,
                state.color,
                (offset, y, width, bar_height),
                border_radius=6,
            )
            offset += width
        caption = SMALL_FONT.render("Probability distribution of the ball", True, (230, 230, 230))
        self.screen.blit(caption, (x, y - 22))

    def draw_measurement_strip(self) -> None:
        if not self.current_stage.allow_measurement:
            return
        strip_rect = pygame.Rect(MEASUREMENT_STRIP_X, 0, MEASUREMENT_STRIP_WIDTH, HEIGHT)
        pygame.draw.rect(self.screen, (90, 40, 150), strip_rect, border_radius=8)
        text = SMALL_FONT.render("Measurement Gate", True, (210, 200, 255))
        self.screen.blit(text, (MEASUREMENT_STRIP_X - text.get_width() // 2, 20))

    def draw_ui(self) -> None:
        top_panel = pygame.Rect(0, 0, WIDTH, 72)
        pygame.draw.rect(self.screen, (18, 18, 28), top_panel)
        pygame.draw.line(self.screen, (60, 60, 90), (0, 72), (WIDTH, 72), 2)

        score_text = FONT.render(
            f"Player {self.player_score} : {self.opponent_score} Opponent",
            True,
            (240, 240, 240),
        )
        self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 16))

        instructions = [
            "W/S or Up/Down: move paddle",
            "Space: pause the simulation",
        ]
        if self.current_stage.allow_measurement:
            instructions.insert(1, "M: measure now (collapse superposition)")
        for idx, line in enumerate(instructions):
            text = SMALL_FONT.render(line, True, (200, 200, 200))
            self.screen.blit(text, (20, 16 + idx * 20))

        self.draw_stage_tracker()

        if (
            self.measure_hint_timer > 10
            and len(self.ball.states) > 1
            and self.current_stage.allow_measurement
        ):
            hint = SMALL_FONT.render(
                "Try measuring! Press M to observe the system.",
                True,
                (255, 210, 180),
            )
            self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 90))

    def draw_stage_tracker(self) -> None:
        tracker_rect = pygame.Rect(WIDTH - 280, 8, 260, 56)
        pygame.draw.rect(self.screen, (26, 26, 42), tracker_rect, border_radius=12)
        pygame.draw.rect(self.screen, (70, 70, 120), tracker_rect, 2, border_radius=12)
        stage_text = SMALL_FONT.render(
            f"{self.current_stage.title}", True, (255, 210, 140)
        )
        self.screen.blit(stage_text, (tracker_rect.x + 12, tracker_rect.y + 8))
        objective_text = SMALL_FONT.render(
            self.current_stage.objective, True, (210, 210, 220)
        )
        self.screen.blit(objective_text, (tracker_rect.x + 12, tracker_rect.y + 30))
        if self.lesson_complete:
            completed = SMALL_FONT.render(
                "Lesson complete! Enjoy the sandbox.", True, (180, 255, 180)
            )
            self.screen.blit(completed, (tracker_rect.x - 60, tracker_rect.y + 72))

    @property
    def current_stage(self) -> LessonStage:
        return self.lesson_stages[self.stage_index]

    def start_stage_play(self) -> None:
        self.stage_intro_active = False
        self.paused = False
        self.stage_timer = 0.0
        self.superposition_timer = 0.0
        self.measure_hint_timer = 0.0
        self.player_rallies = 0
        self.measurements_made = 0
        if self.stage_index == len(self.lesson_stages) - 1:
            self.lesson_complete = True
        self.ball.reset(direction=random.choice([-1, 1]))

    def complete_current_stage(self) -> None:
        if self.stage_index == len(self.lesson_stages) - 1:
            self.lesson_complete = True
            return
        self.stage_index += 1
        self.stage_intro_active = True
        self.paused = True
        self.player_rallies = 0
        self.measurements_made = 0
        self.superposition_timer = 0.0
        self.stage_timer = 0.0
        self.ball.reset(direction=random.choice([-1, 1]))

    def check_stage_objectives(self) -> None:
        stage = self.current_stage
        if stage.required_rallies and self.player_rallies >= stage.required_rallies:
            self.complete_current_stage()
        elif (
            stage.required_superposition_time
            and self.superposition_timer >= stage.required_superposition_time
        ):
            self.complete_current_stage()
        elif stage.measurement_goal and self.measurements_made >= stage.measurement_goal:
            self.complete_current_stage()

    def draw(self) -> None:
        self.screen.fill((8, 8, 16))
        self.draw_measurement_strip()
        pygame.draw.rect(self.screen, (200, 200, 255), self.player.rect)
        pygame.draw.rect(self.screen, (255, 120, 120), self.opponent.rect)
        self.ball.draw(self.screen)
        self.draw_probability_bar()
        self.draw_ui()

        if self.stage_intro_active:
            self.draw_stage_intro()
        elif self.paused:
            self.draw_pause_overlay()

        if not self.lesson_complete:
            self.check_stage_objectives()

        pygame.display.flip()

    def draw_stage_intro(self) -> None:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 30, 230))
        self.screen.blit(overlay, (0, 0))
        stage = self.current_stage
        box = pygame.Rect(0, 0, WIDTH - 200, HEIGHT - 220)
        box.center = (WIDTH // 2, HEIGHT // 2)
        pygame.draw.rect(self.screen, (24, 24, 44), box, border_radius=16)
        pygame.draw.rect(self.screen, (90, 90, 160), box, 3, border_radius=16)
        title = TITLE_FONT.render(stage.title, True, (255, 215, 160))
        self.screen.blit(title, (box.centerx - title.get_width() // 2, box.y + 30))
        for idx, line in enumerate(stage.summary):
            text = SMALL_FONT.render(line, True, (220, 220, 230))
            self.screen.blit(text, (box.x + 40, box.y + 100 + idx * 26))
        objective_label = FONT.render("Objective", True, (180, 220, 255))
        self.screen.blit(objective_label, (box.x + 40, box.y + 220))
        objective_text = SMALL_FONT.render(stage.objective, True, (200, 240, 255))
        self.screen.blit(objective_text, (box.x + 40, box.y + 250))
        prompt = SMALL_FONT.render("Press Enter to begin this stage", True, (255, 255, 255))
        self.screen.blit(prompt, (box.centerx - prompt.get_width() // 2, box.bottom - 60))

    def draw_pause_overlay(self) -> None:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 40, 180))
        self.screen.blit(overlay, (0, 0))
        pause_text = TITLE_FONT.render("Paused", True, (255, 255, 255))
        self.screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 60))
        info_lines = [
            "While paused, consider how probabilities evolve over time.",
            "What advantage does waiting before measuring give you?",
        ]
        for idx, line in enumerate(info_lines):
            text = SMALL_FONT.render(line, True, (230, 230, 230))
            self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + idx * 20))
        if self.lesson_complete:
            congrats = SMALL_FONT.render(
                "Lesson complete! Keep experimenting.", True, (180, 255, 180)
            )
            self.screen.blit(congrats, (WIDTH // 2 - congrats.get_width() // 2, HEIGHT // 2 + 80))


def main() -> None:
    game = QuantumPong()
    game.run()


if __name__ == "__main__":
    main()
