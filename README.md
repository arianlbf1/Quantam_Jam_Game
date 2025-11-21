# Quantum Snake

A pygame twist on classic Snake that teaches quantum computing ideas like **superposition** and **measurement** through playful mechanics.

## How to run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the game:
   ```bash
   python main.py
   ```

> Tip: If you're on a headless machine, set `SDL_VIDEODRIVER=dummy` before running so pygame can create a windowless surface.

## Game modes
- **Tutorial**: Three short lessons introduce movement, superposition, and measurement/growth one at a time. Progress with **Enter** after finishing each objective.
- **Free Play**: The full game loop with scoring, superposition apples, and restarts.

The start screen lets you choose Tutorial (**T**) or Free Play (**F**).

## Quantum-powered rules
- Each apple spawns in **superposition**: two translucent ghost clones appear on the grid.
- When your snake head comes near, a **measurement** randomly collapses the apple—one clone becomes the real apple, and the other vanishes.
- Eat the measured apple to grow and score. Hitting walls or yourself ends the run.
