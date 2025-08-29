# main.py
import os
import re
from typing import Any, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="BFHL API")

# ----- CONFIG (via environment variables) -----
# FULL_NAME can be "John Doe" or "john_doe" — it's normalized to lowercase + underscores.
FULL_NAME = os.getenv("FULL_NAME", "john doe")
DOB = os.getenv("DOB", "17091999")          # ddmmyyyy
EMAIL = os.getenv("EMAIL", "john@xyz.com")
ROLL_NUMBER = os.getenv("ROLL_NUMBER", "ABCD123")


def normalize_full_name(name: str) -> str:
    """Lowercase, replace whitespace with underscores, keep a-z0-9 and underscores only."""
    s = name.strip().lower()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-z0-9_]", "", s)
    return s


USER_ID = f"{normalize_full_name(FULL_NAME)}_{DOB}"


# ----- Pydantic model -----
class InputData(BaseModel):
    data: List[Any]


# ----- Helper logic -----
_digits_re = re.compile(r"^-?\d+$")


def process_payload(data_list: List[Any]):
    even_numbers = []
    odd_numbers = []
    alphabets = []
    special_characters = []
    sum_numbers = 0
    all_alpha_chars = []  # collect individual alphabetic characters in original order

    for item in data_list:
        token = "" if item is None else str(item).strip()

        if token == "":
            # treat empty string as special character token
            special_characters.append(token)
            continue

        # Numeric tokens: integers only (optional leading minus)
        if _digits_re.fullmatch(token):
            n = int(token)
            if abs(n) % 2 == 0:
                even_numbers.append(token)  # keep as string (requirement)
            else:
                odd_numbers.append(token)
            sum_numbers += n

        # Alphabet-only token (letters only)
        elif token.isalpha():
            alphabets.append(token.upper())
            # collect characters preserving original case (we'll alternate caps later)
            all_alpha_chars.extend(list(token))

        else:
            # mixed / contains non-alpha-numeric -> special characters token
            special_characters.append(token)

    # Build concat_string: reverse all_alpha_chars, then alternating caps starting UPPER
    rev = all_alpha_chars[::-1]
    concat_string = "".join(
        (ch.upper() if idx % 2 == 0 else ch.lower()) for idx, ch in enumerate(rev)
    )

    return {
        "odd_numbers": odd_numbers,
        "even_numbers": even_numbers,
        "alphabets": alphabets,
        "special_characters": special_characters,
        "sum": str(sum_numbers),  # sum as string (requirement)
        "concat_string": concat_string,
    }


# ----- Routes -----
@app.post("/bfhl")
def bfhl(payload: InputData):
    if not isinstance(payload.data, list):
        raise HTTPException(status_code=400, detail="`data` must be a list")

    processed = process_payload(payload.data)

    response = {
        "status": 200,
        "is_success": True,
        "user_id": USER_ID,
        "email": EMAIL,
        "roll_number": ROLL_NUMBER,
        "odd_numbers": processed["odd_numbers"],
        "even_numbers": processed["even_numbers"],
        "alphabets": processed["alphabets"],
        "special_characters": processed["special_characters"],
        "sum": processed["sum"],
        "concat_string": processed["concat_string"],
    }

    return response


@app.get("/")
def root():
    return {"message": "BFHL API — POST /bfhl with JSON body { \"data\": [ ... ] }"}

