import os
import re
from typing import Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="BFHL API")

# ---- User Details (env fallback) ----
FULL_NAME = os.getenv("FULL_NAME", "John Doe")
DOB = os.getenv("DOB", "17091999")          # ddmmyyyy
EMAIL = os.getenv("EMAIL", "john@xyz.com")
ROLL_NUMBER = os.getenv("ROLL_NUMBER", "ABCD123")

def normalize_full_name(name: str) -> str:
    """Normalize a name: lowercase, replace spaces with underscores, strip invalid chars."""
    s = name.strip().lower()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-z0-9_]", "", s)
    return s

USER_ID = f"{normalize_full_name(FULL_NAME)}_{DOB}"

# ---- Models ----
class InputData(BaseModel):
    data: List[Any]

_digits_re = re.compile(r"^-?\d+$")  # integer regex (handles negatives)

# ---- Logic ----
def process_payload(data_list: List[Any]):
    even_numbers = []
    odd_numbers = []
    alphabets = []
    special_characters = []
    sum_numbers = 0
    all_alpha_chars = []

    for item in data_list:
        token = "" if item is None else str(item).strip()

        if token == "":
            special_characters.append(token)
            continue

        if _digits_re.fullmatch(token):   # numbers
            n = int(token)
            if abs(n) % 2 == 0:
                even_numbers.append(token)
            else:
                odd_numbers.append(token)
            sum_numbers += n

        elif token.isalpha():             # alphabets
            alphabets.append(token.upper())
            all_alpha_chars.extend(list(token))

        else:                             # special chars
            special_characters.append(token)

    rev = all_alpha_chars[::-1]
    concat_string = "".join(
        ch.upper() if idx % 2 == 0 else ch.lower()
        for idx, ch in enumerate(rev)
    )

    return {
        "odd_numbers": odd_numbers,
        "even_numbers": even_numbers,
        "alphabets": alphabets,
        "special_characters": special_characters,
        "sum": str(sum_numbers),
        "concat_string": concat_string,
    }

# ---- Routes ----
@app.post("/bfhl")
def bfhl_post(payload: InputData):
    """POST: classify tokens + return metadata"""
    if not isinstance(payload.data, list):
        raise HTTPException(status_code=400, detail="`data` must be a list")

    processed = process_payload(payload.data)

    return {
        "status": 200,
        "is_success": True,
        "user_id": USER_ID,
        "email": EMAIL,
        "roll_number": ROLL_NUMBER,
        **processed,
    }

@app.get("/bfhl")
def bfhl_get():
    """GET: For browser testing & submission link"""
    return {
        "status": 200,
        "message": "BFHL API is live 🚀. Use POST /bfhl with JSON body { \"data\": [ ... ] }",
        "example": {
            "data": ["1", "2", "abc", "XYZ", "#$%"]
        },
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/")
def root():
    return {
        "status": 200,
        "message": "BFHL API is running 🚀. Go to /docs to test",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health():
    return {"status": 200, "message": "OK"}
