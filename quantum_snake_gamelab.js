// Quantum Snake for Code.org GameLab
// Copy-paste this entire file into https://code.org/educate/gamelab (one file only).
// The game blends classic Snake with quantum ideas: superposition and measurement.
// States: Menu -> Tutorial (step-by-step) or Free Play.

// ------------------ CONFIG ------------------
var cellSize = 20;            // Grid cell size
var cols = 20;                // Grid width
var rows = 20;                // Grid height
var moveDelay = 8;            // Frames between moves
var slowDelay = 12;           // Tutorial slowdown
var startLength = 3;          // Starting snake length
var proximityMeasure = 30;    // Distance that triggers measurement
var fading = 120;             // Frames clone remains after measurement

// ------------------ STATE ------------------
var gameState = "menu";       // menu, tutorial, free
var tutorialStep = 0;
var frameCounter = 0;
var snake = [];
var dir = {x: 1, y: 0};
var pendingDir = {x: 1, y: 0};
var apples = [];
var score = 0;
var tutorialMessages = [
  "Welcome! In quantum computing, particles can be in SUPERPOSITION.",
  "We'll model a superposed apple: it appears in two spots at once!",
  "Get close to MEASURE. Measurement forces a single outcome.",
  "Use arrow keys to move. Eat apples to grow.",
  "In this game, the apple has a real version and a ghost clone.",
  "When you're near, the universe 'decides' which apple is real.",
  "Ghost fades away. Real apple feeds your snake.",
  "Ready? Practice once, then try Free Play!"
];

// ------------------ SETUP ------------------
function setup() {
  createCanvas(cols * cellSize, rows * cellSize + 80);
  textAlign(LEFT, CENTER);
  resetSnake();
  spawnSuperposedApple();
}

// ------------------ MAIN LOOP ------------------
function draw() {
  background(18, 18, 28);
  if (gameState === "menu") {
    drawMenu();
    return;
  }
  drawGrid();
  if (gameState === "tutorial") {
    drawTutorial();
  } else if (gameState === "free") {
    drawGame(false);
  }
}

// ------------------ MENU ------------------
function drawMenu() {
  fill(255);
  textSize(28);
  text("Quantum Snake", 30, 60);
  textSize(16);
  text("Classic Snake + Quantum ideas (Superposition & Measurement)", 30, 90);
  drawButton(60, 140, 220, 40, "Tutorial", function () {
    gameState = "tutorial";
    tutorialStep = 0;
    resetSnake(true);
  });
  drawButton(60, 200, 220, 40, "Free Play", function () {
    gameState = "free";
    resetSnake();
  });
  textSize(12);
  text("Use mouse to select. Keyboard controls during play.", 30, 260);
}

function drawButton(x, y, w, h, label, onClick) {
  var hover = mouseX > x && mouseX < x + w && mouseY > y && mouseY < y + h;
  fill(hover ? color(70, 130, 200) : color(40, 80, 140));
  rect(x, y, w, h, 8);
  fill(255);
  textSize(18);
  text(label, x + 10, y + h / 2);
  if (mouseIsPressed && hover) {
    onClick();
  }
}

// ------------------ TUTORIAL ------------------
function drawTutorial() {
  drawGame(true);
  drawTutorialOverlay();
}

function drawTutorialOverlay() {
  fill(0, 150);
  rect(0, rows * cellSize, width, 80);
  fill(255);
  textSize(14);
  text("Step " + (tutorialStep + 1) + " of " + tutorialMessages.length + ": " + tutorialMessages[tutorialStep], 10, rows * cellSize + 20, width - 20, 60);
  text("Press SPACE to advance", 10, rows * cellSize + 60);
}

function keyPressed() {
  if (gameState === "tutorial" && keyCode === 32) { // Space
    tutorialStep++;
    if (tutorialStep >= tutorialMessages.length) {
      gameState = "free";
      resetSnake();
    } else {
      resetSnake(true);
    }
  }
}

// ------------------ GAMEPLAY ------------------
function drawGame(isTutorial) {
  handleInput();
  frameCounter++;
  var delay = isTutorial ? slowDelay : moveDelay;
  if (frameCounter % delay === 0) {
    stepSnake();
    checkCollisions();
  }
  drawApples();
  drawSnake();
  drawHUD(isTutorial);
}

function resetSnake(isTutorial) {
  snake = [];
  var startX = floor(cols / 2);
  var startY = floor(rows / 2);
  for (var i = 0; i < startLength; i++) {
    snake.unshift({ x: startX - i, y: startY });
  }
  dir = { x: 1, y: 0 };
  pendingDir = { x: 1, y: 0 };
  score = 0;
  apples = [];
  spawnSuperposedApple();
  frameCounter = 0;
}

function handleInput() {
  if (keyWentDown("up") && dir.y !== 1) pendingDir = { x: 0, y: -1 };
  if (keyWentDown("down") && dir.y !== -1) pendingDir = { x: 0, y: 1 };
  if (keyWentDown("left") && dir.x !== 1) pendingDir = { x: -1, y: 0 };
  if (keyWentDown("right") && dir.x !== -1) pendingDir = { x: 1, y: 0 };
}

function stepSnake() {
  dir = pendingDir;
  var newHead = { x: snake[0].x + dir.x, y: snake[0].y + dir.y };
  snake.unshift(newHead);
  if (!eatCheck(newHead)) {
    snake.pop();
  }
}

function drawSnake() {
  for (var i = 0; i < snake.length; i++) {
    var seg = snake[i];
    fill(i === 0 ? color(80, 230, 140) : color(30, 180, 100));
    rect(seg.x * cellSize, seg.y * cellSize, cellSize, cellSize, 4);
  }
}

function drawGrid() {
  stroke(40);
  for (var i = 0; i <= cols; i++) {
    line(i * cellSize, 0, i * cellSize, rows * cellSize);
  }
  for (var j = 0; j <= rows; j++) {
    line(0, j * cellSize, cols * cellSize, j * cellSize);
  }
  noStroke();
}

// ------------------ QUANTUM APPLES ------------------
function spawnSuperposedApple() {
  var posA = randomOpenCell();
  var posB = randomOpenCell();
  apples = [{
    real: random([0, 1]), // index of real apple (0 or 1)
    options: [posA, posB],
    measured: false,
    ghostFade: 0
  }];
}

function randomOpenCell() {
  var good = false;
  var p;
  while (!good) {
    p = { x: floor(random(cols)), y: floor(random(rows)) };
    good = !occupiesSnake(p);
  }
  return p;
}

function occupiesSnake(p) {
  for (var i = 0; i < snake.length; i++) {
    if (snake[i].x === p.x && snake[i].y === p.y) return true;
  }
  return false;
}

function drawApples() {
  for (var i = 0; i < apples.length; i++) {
    var apple = apples[i];
    var realIndex = apple.real;
    var cloneIndex = 1 - realIndex;
    var realPos = apple.options[realIndex];
    var clonePos = apple.options[cloneIndex];

    // Show both positions before measurement: superposition visual
    fill(apple.measured ? color(255, 80, 100) : color(255, 160, 220, 200));
    rect(realPos.x * cellSize, realPos.y * cellSize, cellSize, cellSize, 6);

    // Ghost apple (clone)
    if (!apple.measured || apple.ghostFade > 0) {
      var alpha = apple.measured ? map(apple.ghostFade, 0, fading, 150, 0) : 120;
      fill(120, 200, 255, alpha);
      rect(clonePos.x * cellSize, clonePos.y * cellSize, cellSize, cellSize, 6);
      if (apple.measured) apple.ghostFade--;
    }

    // Trigger measurement if snake is near either apple
    var head = snake[0];
    if (!apple.measured) {
      var distReal = dist(head.x * cellSize, head.y * cellSize, realPos.x * cellSize, realPos.y * cellSize);
      var distClone = dist(head.x * cellSize, head.y * cellSize, clonePos.x * cellSize, clonePos.y * cellSize);
      if (distReal < proximityMeasure || distClone < proximityMeasure) {
        apple.measured = true;
        apple.ghostFade = fading;
        // Measurement could collapse to either; random outcome!
        if (random() < 0.5) {
          apple.real = realIndex;
        } else {
          apple.real = cloneIndex;
        }
      }
    }
  }
}

function eatCheck(head) {
  for (var i = 0; i < apples.length; i++) {
    var apple = apples[i];
    var realPos = apple.options[apple.real];
    if (head.x === realPos.x && head.y === realPos.y) {
      score++;
      spawnSuperposedApple();
      return true;
    }
  }
  return false;
}

function checkCollisions() {
  var head = snake[0];
  if (head.x < 0 || head.y < 0 || head.x >= cols || head.y >= rows) {
    resetSnake(gameState === "tutorial");
  }
  for (var i = 1; i < snake.length; i++) {
    if (snake[i].x === head.x && snake[i].y === head.y) {
      resetSnake(gameState === "tutorial");
    }
  }
}

// ------------------ HUD ------------------
function drawHUD(isTutorial) {
  fill(0, 150);
  rect(0, rows * cellSize, width, 80);
  fill(255);
  textSize(14);
  if (isTutorial) {
    text("Tutorial Mode | Grow to practice measurement.", 10, rows * cellSize + 20);
  } else {
    text("Free Play | Score: " + score, 10, rows * cellSize + 20);
  }
  text("Arrow Keys: move | Space: advance tutorial | Apples appear in superposition.", 10, rows * cellSize + 45);
  text("Get close to measure; real apple feeds you, ghost fades.", 10, rows * cellSize + 65);
}
