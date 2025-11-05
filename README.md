# Quantum Pong: Superposition Showdown

Quantum Pong is a playful take on the classic Pong arcade game built with
[pygame](https://www.pygame.org/). The latest version introduces a guided
lesson mode that slows the action down and teaches the fundamentals of quantum
computing step by step.

## Quantum Concepts Inside the Game

- **Superposition** – Once unlocked in the lesson, paddle hits can branch the
  ball into several simultaneous paths. Each ghostly orb represents one
  possible trajectory and its brightness mirrors the probability that the ball
  will collapse to that path.
- **Measurement** – Later in the lesson you can press `M` or allow the ball to
  enter the glowing gate at the centre of the arena to perform a measurement.
  The act of observation collapses the superposition and only one classical
  ball remains.
- **Probability Visualisation** – The probability bar near the bottom of the
  screen shows how the likelihoods of each path evolve over time.

Use these mechanics to keep the AI guessing, or time your measurements to gain
an advantage once the concepts have been introduced.

## Guided Lesson Flow

Every core idea is introduced through a dedicated stage with on-screen
explanations, UI cards, and objectives. Press `Enter` to advance into each
stage when you are ready.

1. **Stage 1 – Classical Rally**: Practise the basic controls with a single,
   predictable ball. Return it three times to continue.
2. **Stage 2 – Superposition**: Experience the ball splitting into simultaneous
   paths and watch the probability bar as the superposition evolves for five
   seconds.
3. **Stage 3 – Measurement**: Learn how observation collapses the system by
   triggering two measurements, either manually or through the measurement gate.
4. **Stage 4 – Sandbox**: Revisit every mechanic with full control and keep
   experimenting in free play.

## Controls

- `W` / `S` or `↑` / `↓` – Move the player's paddle.
- `Enter` – Start the highlighted lesson stage.
- `M` – Measure the quantum state (available from Stage 3 onward).
- `Space` – Pause the action and reflect on what is happening.
- `Esc` – Quit.

## Installation & Running

1. Create and activate a virtual environment (optional but recommended).
2. Install the dependency:

   ```bash
   pip install -r requirements.txt
   ```

3. Launch the game:

   ```bash
   python main.py
   ```

You will need a desktop environment capable of opening a pygame window.

## Requirements

- Python 3.9+
- pygame 2.0+

If pygame fails to initialise because no display is available, set the
`SDL_VIDEODRIVER` environment variable to a supported backend for your platform.
