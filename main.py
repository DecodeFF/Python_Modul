from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from enum import Enum
from typing import List

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class NameMapping(Enum):
    PAWN = 'P'
    KNIGHT = 'N'
    BISHOP = 'B'
    ROOK = 'R'
    QUEEN = 'Q'
    KING = 'K'

class Move(BaseModel):
    player: str
    position_from: str
    position_to: str

class Piece(BaseModel):
    color: str
    position: tuple
    name: str

class King(Piece):
    name: str = NameMapping.KING.value

class Rook(Piece):
    name: str = NameMapping.ROOK.value

class Knight(Piece):
    name: str = NameMapping.KNIGHT.value

class Bishop(Piece):
    name: str = NameMapping.BISHOP.value

class Queen(Piece):
    name: str = NameMapping.QUEEN.value

class Pawn(Piece):
    name: str = NameMapping.PAWN.value

class Board(BaseModel):
    pieces: List[List[str]]

class Game:
    def __init__(self):
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
        if self.valid_move(from_row, from_col, to_row, to_col):
            piece = self.board[from_row][from_col]
            self.board[to_row][to_col] = piece
            self.board[from_row][from_col] = ""
            self.toggle_player()
        else:
            raise HTTPException(status_code=400, detail="Invalid move")

    def toggle_player(self):
        self.current_player = "black" if self.current_player == "white" else "white"

    def valid_move(self, from_row, from_col, to_row, to_col):
        # Add actual chess move logic here
        return True

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
    if board_state is None or not all(board_state):
        return "No active game or board is uninitialized. Please start a game first."
    return templates.TemplateResponse("board.html", {"request": request, "board_state": {"pieces": board_state}})

@app.get("/")
def root():
    return {"message": "Welcome to Chess API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
