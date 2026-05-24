"""Test suite for tictactoe.py — covers Section 8 of SPEC.md."""
from __future__ import annotations

import random

import pytest

from tictactoe import (
    ai_move,
    available_moves,
    check_winner,
    make_move,
    minimax,
    new_board,
    parse_human_input,
    render,
)


# ---------------------------------------------------------------------------
# new_board / available_moves
# ---------------------------------------------------------------------------

def test_new_board_is_nine_single_spaces():
    b = new_board()
    assert isinstance(b, list)
    assert len(b) == 9
    assert all(c == " " for c in b)


def test_available_moves_on_empty_board():
    assert available_moves(new_board()) == [0, 1, 2, 3, 4, 5, 6, 7, 8]


def test_available_moves_excludes_played_indices():
    b = new_board()
    b = make_move(b, 0, "X")
    b = make_move(b, 4, "O")
    assert available_moves(b) == [1, 2, 3, 5, 6, 7, 8]


# ---------------------------------------------------------------------------
# make_move
# ---------------------------------------------------------------------------

def test_make_move_places_mark():
    b = new_board()
    nb = make_move(b, 3, "X")
    assert nb[3] == "X"
    assert nb[0] == " "
    assert nb[8] == " "


def test_make_move_does_not_mutate_input():
    b = new_board()
    original = list(b)
    nb = make_move(b, 5, "O")
    assert b == original
    assert nb is not b


def test_make_move_on_occupied_cell_raises():
    b = make_move(new_board(), 0, "X")
    with pytest.raises(ValueError):
        make_move(b, 0, "O")


@pytest.mark.parametrize("bad_pos", [-1, 9, 100])
def test_make_move_out_of_range_raises(bad_pos):
    with pytest.raises(ValueError):
        make_move(new_board(), bad_pos, "X")


@pytest.mark.parametrize("bad_player", ["Z", "", "x", "o", "XO"])
def test_make_move_invalid_player_raises(bad_player):
    with pytest.raises(ValueError):
        make_move(new_board(), 0, bad_player)


# ---------------------------------------------------------------------------
# check_winner — all 8 winning lines for X and O
# ---------------------------------------------------------------------------

WINNING_LINES = [
    (0, 1, 2),  # top row
    (3, 4, 5),  # middle row
    (6, 7, 8),  # bottom row
    (0, 3, 6),  # left col
    (1, 4, 7),  # middle col
    (2, 5, 8),  # right col
    (0, 4, 8),  # main diag
    (2, 4, 6),  # anti-diag
]


def _board_with_line(line, player):
    """Build a board with `player` on `line` and other cells empty."""
    b = new_board()
    for i in line:
        b[i] = player
    return b


@pytest.mark.parametrize("line", WINNING_LINES)
def test_check_winner_x_wins_each_line(line):
    assert check_winner(_board_with_line(line, "X")) == "X"


@pytest.mark.parametrize("line", WINNING_LINES)
def test_check_winner_o_wins_each_line(line):
    assert check_winner(_board_with_line(line, "O")) == "O"


def test_check_winner_draw():
    # X O X
    # X O O
    # O X X
    b = ["X", "O", "X",
         "X", "O", "O",
         "O", "X", "X"]
    assert check_winner(b) == "draw"


def test_check_winner_empty_board_is_none():
    assert check_winner(new_board()) is None


def test_check_winner_partial_no_winner_is_none():
    b = new_board()
    b = make_move(b, 0, "X")
    b = make_move(b, 4, "O")
    b = make_move(b, 1, "X")
    assert check_winner(b) is None


# ---------------------------------------------------------------------------
# parse_human_input
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw,expected", [
    ("1", 0), ("2", 1), ("3", 2),
    ("4", 3), ("5", 4), ("6", 5),
    ("7", 6), ("8", 7), ("9", 8),
])
def test_parse_human_input_valid(raw, expected):
    assert parse_human_input(raw, new_board()) == expected


@pytest.mark.parametrize("raw", ["0", "10", "-1", "99"])
def test_parse_human_input_out_of_range_raises(raw):
    with pytest.raises(ValueError):
        parse_human_input(raw, new_board())


@pytest.mark.parametrize("raw", ["a", "", "1.5", "abc", " ", "X"])
def test_parse_human_input_non_numeric_raises(raw):
    with pytest.raises(ValueError):
        parse_human_input(raw, new_board())


def test_parse_human_input_occupied_cell_raises():
    b = make_move(new_board(), 0, "X")  # cell 1 occupied
    with pytest.raises(ValueError):
        parse_human_input("1", b)


# ---------------------------------------------------------------------------
# ai_move / minimax
# ---------------------------------------------------------------------------

def test_ai_move_empty_board_returns_valid_index():
    move = ai_move(new_board(), "O")
    assert 0 <= move <= 8


def test_ai_takes_immediate_winning_move():
    # O has two-in-a-row at 0,1; should play 2 to win.
    b = [
        "O", "O", " ",
        "X", "X", " ",
        " ", " ", " ",
    ]
    assert ai_move(b, "O") == 2


def test_ai_blocks_immediate_human_win():
    # X has two-in-a-row at 0,1; AI must play 2 to block.
    b = [
        "X", "X", " ",
        "O", " ", " ",
        " ", " ", " ",
    ]
    assert ai_move(b, "O") == 2


def test_ai_tie_break_after_center_picks_index_zero():
    # Per spec: after X plays center (index 4), AI as 'O' picks lowest-index
    # optimal corner = 0.
    b = new_board()
    b = make_move(b, 4, "X")
    assert ai_move(b, "O") == 0


def test_minimax_terminal_scores():
    # AI ('O') already won.
    won = _board_with_line((0, 1, 2), "O")
    assert minimax(won, "X", "O") == 1
    # AI ('O') already lost.
    lost = _board_with_line((0, 1, 2), "X")
    assert minimax(lost, "O", "O") == -1
    # Draw position
    drawn = ["X", "O", "X",
             "X", "O", "O",
             "O", "X", "X"]
    assert minimax(drawn, "X", "O") == 0


def _simulate_human_random_vs_ai(seed):
    """Human ('X') plays random legal moves, AI ('O') plays optimally.
    Returns the final winner string from check_winner."""
    rng = random.Random(seed)
    board = new_board()
    current = "X"
    while True:
        w = check_winner(board)
        if w is not None:
            return w
        if current == "X":
            move = rng.choice(available_moves(board))
        else:
            move = ai_move(board, "O")
        board = make_move(board, move, current)
        current = "O" if current == "X" else "X"


def test_ai_never_loses_random_sample():
    # ~200 random games. AI must never lose (X never wins).
    losses = []
    for seed in range(200):
        result = _simulate_human_random_vs_ai(seed)
        assert result in ("O", "draw"), (
            f"AI lost (or unexpected result {result!r}) on seed {seed}"
        )
        if result == "X":
            losses.append(seed)
    assert not losses, f"AI lost on seeds: {losses}"


# ---------------------------------------------------------------------------
# render
# ---------------------------------------------------------------------------

def test_render_empty_board_shows_digits_and_separator():
    out = render(new_board())
    for d in "123456789":
        assert d in out
    assert "-----------" in out


def test_render_places_x_and_o_in_corners():
    b = new_board()
    b = make_move(b, 0, "X")
    b = make_move(b, 8, "O")
    out = render(b)
    lines = out.splitlines()
    # First content row contains X (top-left), last content row contains O (bottom-right).
    assert "X" in lines[0]
    assert "1" not in lines[0]  # cell 1 should now show X, not its number
    assert "O" in lines[-1]
    assert "9" not in lines[-1]


def test_render_empty_cell_shows_its_number():
    b = new_board()
    b = make_move(b, 4, "X")  # only center filled
    out = render(b)
    # Number 5 (center, 1-indexed) should NOT appear; X should appear instead.
    # All other digits 1,2,3,4,6,7,8,9 should still appear.
    assert "X" in out
    for d in "12346789":
        assert d in out
    assert "5" not in out
