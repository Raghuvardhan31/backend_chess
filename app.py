import asyncpg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

# ---------------------------
# Get database URL from Render environment
# ---------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables")

app = FastAPI(title="Chess Checkmate API")

# ---------------------------
# Pydantic model for request
# ---------------------------
class Checkmate(BaseModel):
    fen: str
    type: str
    difficulty_level: str
    solution_moves: str

# ---------------------------
# Create connection pool for asyncpg
# ---------------------------
@app.on_event("startup")
async def startup():
    app.state.db_pool = await asyncpg.create_pool(DATABASE_URL)

@app.on_event("shutdown")
async def shutdown():
    await app.state.db_pool.close()

# ---------------------------
# Helper to get a connection from pool
# ---------------------------
async def get_connection():
    return app.state.db_pool.acquire()

# ---------------------------
# Root endpoint
# ---------------------------
@app.get("/")
async def home():
    return {"message": "FastAPI Chess API is running!"}

# ---------------------------
# GET all checkmates
# ---------------------------
@app.get("/checkmates")
async def get_all_checkmates():
    async with app.state.db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM chess.checkmate ORDER BY id")
    return [dict(row) for row in rows]

# ---------------------------
# GET checkmate by ID
# ---------------------------
@app.get("/checkmates/{checkmate_id}")
async def get_checkmate(checkmate_id: int):
    async with app.state.db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM chess.checkmate WHERE id = $1", checkmate_id)
    if row:
        return dict(row)
    raise HTTPException(status_code=404, detail="Checkmate not found")

# ---------------------------
# POST create new checkmate
# ---------------------------
@app.post("/checkmates")
async def create_checkmate(checkmate: Checkmate):
    async with app.state.db_pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO chess.checkmate(fen, type, difficulty_level, solution_moves)
            VALUES ($1, $2, $3, $4)
            RETURNING *
            """,
            checkmate.fen, checkmate.type, checkmate.difficulty_level, checkmate.solution_moves
        )
    return dict(row)

# ---------------------------
# PUT update checkmate
# ---------------------------
@app.put("/checkmates/{checkmate_id}")
async def update_checkmate(checkmate_id: int, checkmate: Checkmate):
    async with app.state.db_pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            UPDATE chess.checkmate
            SET fen = $1, type = $2, difficulty_level = $3, solution_moves = $4
            WHERE id = $5
            RETURNING *
            """,
            checkmate.fen, checkmate.type, checkmate.difficulty_level, checkmate.solution_moves, checkmate_id
        )
    if row:
        return dict(row)
    raise HTTPException(status_code=404, detail="Checkmate not found")

# ---------------------------
# DELETE checkmate
# ---------------------------
@app.delete("/checkmates/{checkmate_id}")
async def delete_checkmate(checkmate_id: int):
    async with app.state.db_pool.acquire() as conn:
        row = await conn.fetchrow("DELETE FROM chess.checkmate WHERE id = $1 RETURNING *", checkmate_id)
    if row:
        return {"message": f"Checkmate with id {checkmate_id} deleted"}
    raise HTTPException(status_code=404, detail="Checkmate not found")
