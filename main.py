from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from enum import Enum
from typing import List

app = FastAPI()
templates = Jinja2Templates(directory="templates")  # Ensure this directory is correctly specified

class NameMapping(Enum):
    pawn = 1
    knight = 2
    bishop = 3
    rook = 4
    queen = 5
    king = 6

class Move(BaseModel):
    player: str
    position_from: str
    position_to: str

class Piece(BaseModel):
    color: str
    position: tuple

class King(Piece):
    pass

class Rook(Piece):
    pass

class Knight(Piece):
    pass

class Bishop(Piece):
    pass

class Queen(Piece):
    pass

class Pawn(Piece):
    def __init__(self, color: str, position: tuple):
        super().__init__(color=color, position=position)

class Board(BaseModel):
    pieces: List[List[str]]

class Game:
    def __init__(self):
        # Initialize with an empty board to prevent NoneType errors.
        self.board = [[""] * 8 for _ in range(8)]
        self.current_player = "white"

    def start_game(self):
        self.board = [
            ["R", "N", "B", "Q", "K", "B", "N", "R"],
            ["P"] * 8,
            [""] * 8,
            [""] * 8,
            [""] * 8,
            [""] * 8,
            ["p"] * 8,
            ["r", "n", "b", "q", "k", "b", "n", "r"]
        ]

    def move(self, move: Move):
        from_row, from_col = self.convert_position(move.position_from)
        to_row, to_col = self.convert_position(move.position_to)
        piece = self.board[from_row][from_col]
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = ""
        self.current_player = "black" if self.current_player == "white" else "white"

    def get_board(self):
        return self.board

    def convert_position(self, position):
        columns = 'abcdefgh'
        row = int(position[1]) - 1
        col = columns.index(position[0].lower())
        return row, col

game = Game()

@app.post("/start_game")
def api_start_game():
    game.start_game()
    return {"message": "Game started"}

@app.post("/move")
def api_move(move: Move):
    game.move(move)
    return {"message": "Move successful"}

@app.get("/display_board", response_class=HTMLResponse)
def display_board(request: Request):
    board_state = game.get_board()
    if board_state is None or not all(board_state):  # Check if board_state is None or contains empty rows
        return "No active game or board is uninitialized. Please start a game first."
    return templates.TemplateResponse("board.html", {"request": request, "board_state": {"pieces": board_state}})

@app.get("/")
def root():
    return {"message": "Welcome to Chess API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
