# Quantum Snake: Superposition Lab

Quantum Snake reimagines the classic Snake arcade challenge as a hands-on
introduction to the core ideas of quantum computing. Built with
[pygame](https://www.pygame.org/), the game walks players through
superposition and measurement concepts before letting them experiment freely in
a sandbox "lab" stage.

## Why Snake?

Snake already demonstrates deterministic, classical behaviour—the perfect
baseline for showing how quantum rules differ. By layering in shimmering fruit
that occupy multiple states and giving players control over when to measure the
system, Quantum Snake turns abstract ideas into playful, memorable actions.

## Lesson Structure

The experience is paced across four guided stages. Each stage unlocks new UI
notes, objectives, and mechanics so the learning curve stays approachable.

1. **Stage 1 – Classical Control**  
   Practise steering, collect five classical data bits, and build a feel for the
   deterministic movement loop.
2. **Stage 2 – Quantum Superposition**  
   Fruit now spawn in two or three simultaneous positions. Percent labels above
   each state visualise the probability that a measurement will collapse to that
   spot. Press `M` to perform three measurements and progress.
3. **Stage 3 – Strategic Measurement**  
   Classical and quantum fruit mix together. Decide when to measure to reach
   seven points without crashing. Purple flashes highlight each successful
   observation.
4. **Stage 4 – Free Play Lab**  
   With every mechanic unlocked you can keep experimenting, design your own
   challenges, and try to manage an ever-longer snake amid quantum uncertainty.

## Quantum Concepts in Play

- **Superposition** – Shimmering fruit markers show every probable location a
  qubit-like data bit could collapse to. Their transparency and probability
  labels reinforce that the fruit is not committed to a single tile yet.
- **Measurement** – Press `M` to collapse a superposition into a single
  classical fruit. A brief violet halo and screen tint visualise the act of
  observation and help players connect the action with the theory.
- **Probability Visualisation** – Percentages update every time a new
  superposition is spawned, prompting players to reason about likelihood before
  choosing when to measure.
- **Classical vs Quantum Contrast** – Stage stats and concept notes highlight
  the differences between deterministic motion and probabilistic outcomes.

## Controls

- `←`, `→`, `↑`, `↓` or `A`, `D`, `W`, `S` – Steer the snake.
- `M` – Perform a measurement (available once quantum fruit appear).
- `Esc` – Quit the game.

Hints for facilitators and curious players appear directly in the UI so you can
pause between rounds and discuss what happened.

## Installation & Running

1. (Optional) Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Launch the lesson:

   ```bash
   python main.py
   ```

A desktop environment capable of opening a pygame window is required.

## Requirements

- Python 3.9+
- pygame 2.0+

If pygame reports that it cannot open a display, configure the `SDL_VIDEODRIVER`
environment variable for your operating system before launching the game.
