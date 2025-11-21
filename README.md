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

## Quantum-powered rules
- Each apple spawns in **superposition**: two translucent ghost clones appear on the grid.
- When your snake head comes near, a **measurement** randomly collapses the apple—one clone becomes the real apple, and the other vanishes.
- Eat the measured apple to grow and score. Hitting walls or yourself ends the run.

## Tutorial first
The game starts with a guided tutorial overlay explaining controls and the quantum twists. Approach the ghost apples to see collapse in action, then press **Enter** to start the full game.
