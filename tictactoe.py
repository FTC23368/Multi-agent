from __future__ import annotations

EMPTY = " "
PLAYERS = {"X", "O"}
WINNING_LINES = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


def new_board() -> list[str]:
    return [EMPTY] * 9


def render(board: list[str]) -> str:
    def cell(i: int) -> str:
        return board[i] if board[i] != EMPTY else str(i + 1)

    rows = []
    for r in range(3):
        a, b, c = cell(3 * r), cell(3 * r + 1), cell(3 * r + 2)
        rows.append(f" {a} | {b} | {c}")
    return "\n-----------\n".join(rows)


def available_moves(board: list[str]) -> list[int]:
    return [i for i, v in enumerate(board) if v == EMPTY]


def make_move(board: list[str], position: int, player: str) -> list[str]:
    if player not in PLAYERS:
        raise ValueError(f"Invalid player: {player!r}")
    if not isinstance(position, int) or isinstance(position, bool):
        raise ValueError(f"Position must be an integer, got {position!r}")
    if position < 0 or position > 8:
        raise ValueError(f"Position out of range 0-8: {position}")
    if board[position] != EMPTY:
        raise ValueError(f"Cell {position} is already occupied")
    new = list(board)
    new[position] = player
    return new


def check_winner(board: list[str]) -> str | None:
    for a, b, c in WINNING_LINES:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a]
    if EMPTY not in board:
        return "draw"
    return None


def minimax(board: list[str], current_player: str, ai_player: str) -> int:
    result = check_winner(board)
    if result is not None:
        if result == ai_player:
            return 1
        if result == "draw":
            return 0
        return -1

    other = "O" if current_player == "X" else "X"
    if current_player == ai_player:
        best = -2
        for pos in available_moves(board):
            score = minimax(make_move(board, pos, current_player), other, ai_player)
            if score > best:
                best = score
            if best == 1:
                break
        return best
    else:
        best = 2
        for pos in available_moves(board):
            score = minimax(make_move(board, pos, current_player), other, ai_player)
            if score < best:
                best = score
            if best == -1:
                break
        return best


def ai_move(board: list[str], ai_player: str) -> int:
    if ai_player not in PLAYERS:
        raise ValueError(f"Invalid player: {ai_player!r}")
    if check_winner(board) is not None:
        raise ValueError("Board is terminal; no move available")
    moves = available_moves(board)
    if not moves:
        raise ValueError("Board is full; no move available")
    other = "O" if ai_player == "X" else "X"
    best_score = -2
    best_pos = moves[0]
    for pos in moves:
        score = minimax(make_move(board, pos, ai_player), other, ai_player)
        if score > best_score:
            best_score = score
            best_pos = pos
    return best_pos


def parse_human_input(raw: str, board: list[str]) -> int:
    if not isinstance(raw, str):
        raise ValueError("Input must be a string")
    s = raw.strip()
    if not s:
        raise ValueError("Empty input")
    if not (s.lstrip("+-").isdigit() and s.lstrip("+-") != ""):
        raise ValueError(f"Not an integer: {raw!r}")
    try:
        n = int(s)
    except ValueError as e:
        raise ValueError(f"Not an integer: {raw!r}") from e
    if n < 1 or n > 9:
        raise ValueError(f"Out of range 1-9: {n}")
    pos = n - 1
    if board[pos] != EMPTY:
        raise ValueError(f"Cell {n} is already occupied")
    return pos


def play_game() -> None:
    board = new_board()
    human, ai = "X", "O"
    current = "X"
    while True:
        print(render(board))
        winner = check_winner(board)
        if winner is not None:
            break
        if current == human:
            raw = input("Your move (1-9): ")
            try:
                pos = parse_human_input(raw, board)
            except ValueError:
                print("Invalid move. Try again.")
                continue
            board = make_move(board, pos, human)
        else:
            pos = ai_move(board, ai)
            print(f"AI plays: {pos + 1}")
            board = make_move(board, pos, ai)
        current = "O" if current == "X" else "X"

    if winner == human:
        print("You win!")
    elif winner == ai:
        print("AI wins!")
    else:
        print("Draw.")


def main() -> None:
    while True:
        play_game()
        again = input("Play again? (y/n): ").strip().lower()
        if again != "y":
            break


if __name__ == "__main__":
    main()
