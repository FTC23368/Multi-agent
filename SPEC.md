# Tic-Tac-Toe with AI Opponent — Specification

## 1. Overview
A single-player command-line tic-tac-toe game where a human plays against an unbeatable AI opponent on a standard 3x3 board. The game runs in the terminal, renders the board after each move, prompts the human for input, and announces the outcome (win, loss, or draw). The AI uses the minimax algorithm so optimal play by the human results in a draw and any human mistake results in a loss.

## 2. Tech Stack
- **Language:** Python 3.10+
- **Form factor:** Single-file CLI script (`tictactoe.py`)
- **Dependencies:** Standard library only (no third-party packages)
- **Test framework:** `pytest`

**Justification:** Python keeps the project dependency-free, makes pure functions easy to unit test, and the single-file layout means the testing agent can import functions directly without packaging overhead.

## 3. Game Rules
- Board is a 3x3 grid with 9 cells.
- Two players: `X` and `O`. `X` always moves first.
- Players alternate turns, placing their mark in any empty cell.
- A player wins by occupying three cells in a row, column, or diagonal (8 possible winning lines).
- If all 9 cells fill without a winner, the game is a draw.
- A move into an occupied cell or off-board is invalid and must be rejected without changing turn.

## 4. AI Behavior
- **Algorithm:** Minimax with full game-tree search (no depth limit needed; ≤ 9 plies).
- **Optimality:** AI plays optimally and is unbeatable. Outcomes against optimal AI: draw (best human result) or AI win.
- **Player assignment:** Human is always `X` (moves first). AI is always `O` (moves second). No difficulty levels in v1.
- **Tie-breaking:** When multiple moves share the best minimax score, the AI picks the lowest-indexed cell (positions 1–9) to make behavior deterministic and testable.
- **Scoring convention:** AI win = `+1`, draw = `0`, AI loss = `-1`. AI maximizes; human is modeled as minimizer.

## 5. User Interface
- **Board representation (display):** 3x3 grid printed with cell numbers 1–9 (top-left to bottom-right, row-major). Empty cells show their number; played cells show `X` or `O`.

Example initial board:
```
 1 | 2 | 3
-----------
 4 | 5 | 6
-----------
 7 | 8 | 9
```

Example mid-game:
```
 X | 2 | O
-----------
 4 | X | 6
-----------
 7 | 8 | O
```

- **Input format:** Human enters a single integer 1–9 at the prompt `Your move (1-9): `.
- **Invalid input handling:** Non-integer input, out-of-range numbers, and already-taken cells produce a one-line error (`Invalid move. Try again.`) and reprompt without consuming the turn.
- **Game flow per turn:**
  1. Print board.
  2. If human turn: prompt and read move.
  3. If AI turn: print `AI plays: <n>`.
  4. Apply move, check terminal state, swap turn.
- **End-of-game output:** Print final board followed by exactly one of: `You win!`, `AI wins!`, or `Draw.`
- **Replay:** After the result, prompt `Play again? (y/n): `. On `y`, start a new game. On any other input, exit.

## 6. Module / Function Structure
All functions live in `tictactoe.py`. Board is represented as a `list[str]` of length 9 with values `'X'`, `'O'`, or `' '` (single space) for empty. Positions are 0-indexed internally (0–8), but user-facing positions are 1–9. Convert at the I/O boundary only.

Required functions and signatures:

- `new_board() -> list[str]`
  Returns a fresh board: a list of 9 single-space strings.

- `render(board: list[str]) -> str`
  Returns the multi-line string representation per Section 5. Empty cells render as their 1-indexed number; filled cells render as `X` or `O`.

- `available_moves(board: list[str]) -> list[int]`
  Returns 0-indexed positions of empty cells, in ascending order.

- `make_move(board: list[str], position: int, player: str) -> list[str]`
  Returns a NEW board (does not mutate input) with `player` placed at 0-indexed `position`. Raises `ValueError` if `position` is out of range 0–8, the cell is occupied, or `player` not in `{'X','O'}`.

- `check_winner(board: list[str]) -> str | None`
  Returns `'X'` if X has three in a line, `'O'` if O has three in a line, `'draw'` if board is full with no winner, otherwise `None` (game ongoing).

- `minimax(board: list[str], current_player: str, ai_player: str) -> int`
  Returns the minimax score for `current_player` to move, from the perspective of `ai_player` (AI win = +1, draw = 0, AI loss = -1). Pure recursive function; no I/O.

- `ai_move(board: list[str], ai_player: str) -> int`
  Returns the 0-indexed best move for `ai_player`. Tie-breaks by lowest index. Assumes at least one move is available; raises `ValueError` if board is full or terminal.

- `parse_human_input(raw: str, board: list[str]) -> int`
  Parses user input string and returns a 0-indexed valid position. Raises `ValueError` with a descriptive message for non-integer input, out-of-range values, or occupied cells.

- `play_game() -> None`
  Runs one full game loop (board printing, input, AI moves, end-of-game message). Uses `input()` and `print()`.

- `main() -> None`
  Entry point. Runs `play_game()` in a loop until the user declines to replay. Guarded by `if __name__ == "__main__":`.

## 7. File Layout
```
/Users/jahangiriqbal/Projects/Multi-agent/
├── SPEC.md           # this document
├── tictactoe.py      # all game code (functions listed in Section 6)
└── test_tictactoe.py # pytest test suite (Section 8)
```

No additional configuration files are required. No package structure, no `__init__.py`.

## 8. Test Plan
The testing agent must create `test_tictactoe.py` covering at least the following scenarios. All tests import directly from `tictactoe`.

### `new_board` and `available_moves`
- `new_board()` returns a list of length 9, all single spaces.
- `available_moves(new_board())` returns `[0,1,2,3,4,5,6,7,8]`.
- After two moves, `available_moves` excludes those indices.

### `make_move`
- Placing on empty cell returns new board with correct mark.
- Original board is not mutated.
- Placing on occupied cell raises `ValueError`.
- Out-of-range position (-1, 9, 100) raises `ValueError`.
- Invalid player (`'Z'`, `''`) raises `ValueError`.

### `check_winner`
- Each of 3 row wins for X and O detected.
- Each of 3 column wins for X and O detected.
- Both diagonal wins for X and O detected.
- Full board with no line returns `'draw'`.
- Empty and partial boards with no winner return `None`.

### `parse_human_input`
- Valid `'1'`–`'9'` on empty board returns 0–8 respectively.
- `'0'`, `'10'`, `'-1'` raise `ValueError`.
- Non-numeric input (`'a'`, `''`, `'1.5'`) raises `ValueError`.
- Input pointing to an occupied cell raises `ValueError`.

### `ai_move` and `minimax`
- On empty board, AI playing `'O'` returns a valid index 0–8.
- AI takes an immediate winning move when one exists (set up board with O two-in-a-row and one empty completing cell; assert `ai_move` returns that cell).
- AI blocks an immediate human win (X has two-in-a-row, one open completing cell; AI must play that cell).
- Tie-breaking determinism: from the empty board, AI as `'O'` after X plays center (index 4) picks the lowest-index optimal corner (index 0). (Spec the expected move so the test is concrete.)
- **AI never loses:** run a simulation where human plays every legal sequence to depth 9 (or a representative random sample of 200 games with random human moves) and assert `check_winner` final result is never `'X'`.

### `render`
- Empty board render contains digits `1` through `9` and the separator line `-----------`.
- A board with `X` at index 0 and `O` at index 8 renders `X` in the top-left position and `O` in the bottom-right.

### Integration (optional, recommended)
- A scripted game where human input is fed via monkeypatched `input()` produces a deterministic end-state and prints either `You win!`, `AI wins!`, or `Draw.` exactly once.

## 9. Acceptance Criteria
- [ ] `python tictactoe.py` launches a playable game from the terminal.
- [ ] Human plays as `X` and moves first; AI plays as `O`.
- [ ] Board renders per Section 5 (cell numbers shown for empty cells).
- [ ] Invalid input is rejected with a clear message and does not consume the turn.
- [ ] AI never loses across the full test simulation in Section 8.
- [ ] All functions in Section 6 exist with the exact names and signatures specified.
- [ ] `pytest test_tictactoe.py` passes with zero failures.
- [ ] No third-party runtime dependencies; only Python 3.10+ standard library.
- [ ] Code lives in `tictactoe.py`; tests in `test_tictactoe.py`; both in the working directory.
- [ ] Replay prompt works: `y` starts a new game, anything else exits cleanly.
