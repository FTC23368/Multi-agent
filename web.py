"""Web UI for tic-tac-toe.

Run:  python3 web.py   then open http://localhost:8000

Stdlib only. Reuses game logic from tictactoe.py.
"""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from tictactoe import (
    EMPTY,
    ai_move,
    available_moves,
    check_winner,
    make_move,
    new_board,
)

HOST = "127.0.0.1"
PORT = 8000

INDEX_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Tic-Tac-Toe</title>
<style>
  :root {
    --bg: #0f172a;
    --panel: #1e293b;
    --ink: #e2e8f0;
    --muted: #94a3b8;
    --accent: #38bdf8;
    --x: #f87171;
    --o: #34d399;
    --line: #334155;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    min-height: 100vh;
    display: grid;
    place-items: center;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: radial-gradient(circle at top, #1e293b, var(--bg));
    color: var(--ink);
  }
  main {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 28px 32px 24px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.4);
    width: min(360px, 92vw);
  }
  h1 {
    margin: 0 0 4px;
    font-size: 22px;
    letter-spacing: 0.02em;
  }
  p.sub {
    margin: 0 0 18px;
    color: var(--muted);
    font-size: 13px;
  }
  #status {
    text-align: center;
    font-size: 15px;
    min-height: 22px;
    margin-bottom: 14px;
    color: var(--accent);
  }
  @keyframes blink-result {
    0%, 100% { opacity: 1; }
    50%      { opacity: 0; }
  }
  #status.blink {
    animation: blink-result 0.45s ease-in-out 3;
  }
  #board {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    aspect-ratio: 1;
  }
  .cell {
    background: #0f172a;
    border: 1px solid var(--line);
    border-radius: 10px;
    font-size: 44px;
    font-weight: 600;
    display: grid;
    place-items: center;
    cursor: pointer;
    transition: background 0.15s, transform 0.05s;
    user-select: none;
  }
  .cell:hover:not(.played):not(.locked) { background: #1e2a44; }
  .cell:active:not(.played):not(.locked) { transform: scale(0.97); }
  .cell.played { cursor: default; }
  .cell.locked { cursor: not-allowed; }
  .cell.x { color: var(--x); }
  .cell.o { color: var(--o); }
  .cell .num {
    color: #475569;
    font-size: 16px;
    font-weight: 400;
  }
  button.reset {
    margin-top: 16px;
    width: 100%;
    padding: 10px;
    background: var(--accent);
    color: #0f172a;
    border: 0;
    border-radius: 10px;
    font-weight: 600;
    font-size: 14px;
    cursor: pointer;
  }
  button.reset:hover { filter: brightness(1.1); }
</style>
</head>
<body>
<main>
  <h1>Tic-Tac-Toe</h1>
  <p class="sub">You are <strong style="color:var(--x)">X</strong>. The AI is <strong style="color:var(--o)">O</strong> and never loses.</p>
  <div id="status">Your move.</div>
  <div id="board"></div>
  <button class="reset" onclick="reset()">New game</button>
</main>

<script>
let board = Array(9).fill(" ");
let locked = false;

const boardEl = document.getElementById("board");
const statusEl = document.getElementById("status");

function setStatus(text, blink = false) {
  // Remove class first and force a reflow so the animation can re-trigger.
  statusEl.classList.remove("blink");
  void statusEl.offsetWidth;
  statusEl.textContent = text;
  if (blink) statusEl.classList.add("blink");
}

function render() {
  boardEl.innerHTML = "";
  board.forEach((v, i) => {
    const cell = document.createElement("div");
    cell.className = "cell";
    if (v === "X") { cell.classList.add("played", "x"); cell.textContent = "X"; }
    else if (v === "O") { cell.classList.add("played", "o"); cell.textContent = "O"; }
    else {
      const n = document.createElement("span");
      n.className = "num";
      n.textContent = i + 1;
      cell.appendChild(n);
      cell.onclick = () => play(i);
    }
    if (locked) cell.classList.add("locked");
    boardEl.appendChild(cell);
  });
}

async function play(i) {
  if (locked || board[i] !== " ") return;
  locked = true;
  setStatus("AI is thinking...");
  try {
    const res = await fetch("/api/move", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ board, position: i }),
    });
    const data = await res.json();
    if (!res.ok) {
      setStatus(data.error || "Error");
      locked = false;
      render();
      return;
    }
    board = data.board;
    render();
    if (data.winner === "X") { setStatus("You win! \u{1F389}", true); }
    else if (data.winner === "O") { setStatus("AI wins.", true); }
    else if (data.winner === "draw") { setStatus("Draw.", true); }
    else { setStatus("Your move."); locked = false; }
  } catch (e) {
    setStatus("Network error.");
    locked = false;
    render();
  }
}

function reset() {
  board = Array(9).fill(" ");
  locked = false;
  setStatus("Your move.");
  render();
}

render();
</script>
</body>
</html>
"""


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _validate_board(b) -> list[str]:
    if not isinstance(b, list) or len(b) != 9:
        raise ValueError("board must be a list of length 9")
    for v in b:
        if v not in ("X", "O", EMPTY):
            raise ValueError(f"board contains invalid value: {v!r}")
    return list(b)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:  # quieter logs
        return

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            body = INDEX_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_error(404, "Not Found")

    def do_POST(self) -> None:
        if self.path != "/api/move":
            self.send_error(404, "Not Found")
            return

        length = int(self.headers.get("Content-Length", "0"))
        try:
            raw = self.rfile.read(length).decode("utf-8") if length else "{}"
            data = json.loads(raw)
            board = _validate_board(data.get("board", new_board()))
            position = data.get("position")
            if not isinstance(position, int) or isinstance(position, bool):
                raise ValueError("position must be an integer 0-8")
        except (json.JSONDecodeError, ValueError) as e:
            _json_response(self, 400, {"error": str(e)})
            return

        # State must be human-to-move: count of X equals count of O.
        x_count = sum(1 for v in board if v == "X")
        o_count = sum(1 for v in board if v == "O")
        if x_count != o_count:
            _json_response(self, 400, {"error": "It is not the human's turn"})
            return

        winner = check_winner(board)
        if winner is not None:
            _json_response(self, 400, {"error": "Game is already over"})
            return

        try:
            board = make_move(board, position, "X")
        except ValueError as e:
            _json_response(self, 400, {"error": str(e)})
            return

        winner = check_winner(board)
        ai_pos = None
        if winner is None:
            ai_pos = ai_move(board, "O")
            board = make_move(board, ai_pos, "O")
            winner = check_winner(board)

        _json_response(self, 200, {"board": board, "aiMove": ai_pos, "winner": winner})


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Tic-Tac-Toe web UI running at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
