# Quantum Pong: Superposition Showdown

Quantum Pong is a playful take on the classic Pong arcade game built with
[pygame](https://www.pygame.org/) that introduces fundamental ideas from
quantum computing.

## Quantum Concepts Inside the Game

- **Superposition** – When the ball hits a paddle it splits into several
  simultaneous paths. Each ghostly orb represents one possible trajectory and
  its brightness mirrors the probability that the ball will collapse to that
  path.
- **Measurement** – Press `M` or allow the ball to enter the glowing gate at the
  centre of the arena to perform a measurement. The act of observation collapses
  the superposition and only one classical ball remains.
- **Probability Visualisation** – The probability bar near the bottom of the
  screen shows how the likelihoods of each path evolve over time.

Use these mechanics to keep the AI guessing, or time your measurements to gain
an advantage!

## Controls

- `W` / `S` or `↑` / `↓` – Move the player's paddle.
- `M` – Measure the quantum state and collapse the ball to one trajectory.
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
