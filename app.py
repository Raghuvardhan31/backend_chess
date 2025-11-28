import asyncpg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ---------------------------
# Replace this with your actual database URL
# Format: postgresql://username:password@host:port/dbname
DATABASE_URL = "postgresql://postgres:Gav051031_@db.dkarbwwnjyttgdmdjydq.supabase.co:5432/postgres"


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
# Database helper
# ---------------------------
async def get_connection():
    # Use SSL if needed (common for cloud DBs like Supabase)
    return await asyncpg.connect(DATABASE_URL, ssl="require")

# ---------------------------
# Root endpoint
# ---------------------------
@app.get("/")
def home():
    return {"message": "FastAPI Chess API is running!"}

# ---------------------------
# GET all checkmates
# ---------------------------
@app.get("/checkmates")
async def get_all_checkmates():
    conn = await get_connection()
    rows = await conn.fetch("SELECT * FROM chess.checkmate ORDER BY id")
    await conn.close()
    return [dict(row) for row in rows]

# ---------------------------
# GET checkmate by ID
# ---------------------------
@app.get("/checkmates/{checkmate_id}")
async def get_checkmate(checkmate_id: int):
    conn = await get_connection()
    row = await conn.fetchrow("SELECT * FROM chess.checkmate WHERE id = $1", checkmate_id)
    await conn.close()
    if row:
        return dict(row)
    raise HTTPException(status_code=404, detail="Checkmate not found")

# ---------------------------
# POST create new checkmate
# ---------------------------
@app.post("/checkmates")
async def create_checkmate(checkmate: Checkmate):
    conn = await get_connection()
    query = """
        INSERT INTO chess.checkmate(fen, type, difficulty_level, solution_moves)
        VALUES ($1, $2, $3, $4)
        RETURNING *
    """
    row = await conn.fetchrow(query, checkmate.fen, checkmate.type, checkmate.difficulty_level, checkmate.solution_moves)
    await conn.close()
    return dict(row)

# ---------------------------
# PUT update checkmate
# ---------------------------
@app.put("/checkmates/{checkmate_id}")
async def update_checkmate(checkmate_id: int, checkmate: Checkmate):
    conn = await get_connection()
    query = """
        UPDATE chess.checkmate
        SET fen = $1, type = $2, difficulty_level = $3, solution_moves = $4
        WHERE id = $5
        RETURNING *
    """
    row = await conn.fetchrow(query, checkmate.fen, checkmate.type, checkmate.difficulty_level, checkmate.solution_moves, checkmate_id)
    await conn.close()
    if row:
        return dict(row)
    raise HTTPException(status_code=404, detail="Checkmate not found")

# ---------------------------
# DELETE checkmate
# ---------------------------
@app.delete("/checkmates/{checkmate_id}")
async def delete_checkmate(checkmate_id: int):
    conn = await get_connection()
    row = await conn.fetchrow("DELETE FROM chess.checkmate WHERE id = $1 RETURNING *", checkmate_id)
    await conn.close()
    if row:
        return {"message": f"Checkmate with id {checkmate_id} deleted"}
    raise HTTPException(status_code=404, detail="Checkmate not found")
