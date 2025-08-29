import os
import re
from typing import Any, List
from fastapi import FastAPI, HTTPException

from pydantic import BaseModel

app = FastAPI(title="BFHL API")

<<<<<<< HEAD
# ----- CONFIG (via environment variables) -----
# FULL_NAME can be "John Doe" or "john_doe" — it's normalized to lowercase + underscores.
FULL_NAME = os.getenv("FULL_NAME", "John Doe")
=======
FULL_NAME = os.getenv("FULL_NAME", "john doe")
>>>>>>> 96758b646040c93b295a04b32ce9474aa55c364a
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

class InputData(BaseModel):
    data: List[Any]

<<<<<<< HEAD

# ----- Helper logic -----
_digits_re = re.compile(r"^-?\d+$")  # integer regex (handles negatives)
=======
_digits_re = re.compile(r"^-?\d+$")
>>>>>>> 96758b646040c93b295a04b32ce9474aa55c364a


def process_payload(data_list: List[Any]):
    """Classify tokens into categories and compute extra fields."""
    even_numbers = []
    odd_numbers = []
    alphabets = []
    special_characters = []
    sum_numbers = 0
    all_alpha_chars = []  # collect characters from all alphabetic tokens

    for item in data_list:
        token = "" if item is None else str(item).strip()

        if token == "":
            special_characters.append(token)
            continue

        # Numeric tokens (integers only)
        if _digits_re.fullmatch(token):
            n = int(token)
            if abs(n) % 2 == 0:
                even_numbers.append(token)  # keep as string (requirement)
            else:
                odd_numbers.append(token)
            sum_numbers += n

        # Alphabet tokens
        elif token.isalpha():
            alphabets.append(token.upper())
            all_alpha_chars.extend(list(token))

        # Special/mixed tokens
        else:
            special_characters.append(token)

    # Build concat_string: reverse collected characters + alternating caps
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


# ----- Routes -----
@app.post("/bfhl")
def bfhl(payload: InputData):
    """Main endpoint: accepts JSON with 'data' list, returns classification + metadata."""
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


@app.get("/")
def root():
    """Root endpoint with instructions."""
    return {
        "status": 200,
        "message": "BFHL API is running 🚀. POST JSON to /bfhl with { \"data\": [ ... ] }",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health():
    """Health check for Render/Vercel uptime monitoring."""
    return {"status": 200, "message": "OK"}
