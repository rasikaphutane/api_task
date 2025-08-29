import os
import re
from typing import Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import json


app = FastAPI(title="BFHL API")

# ---- User Details (env fallback) ----
FULL_NAME = os.getenv("FULL_NAME", "Rasika Phutane")
DOB = os.getenv("DOB", "18092004")          # ddmmyyyy
EMAIL = os.getenv("EMAIL", "rasikaphuxxx@gmail.com")
ROLL_NUMBER = os.getenv("ROLL_NUMBER", "22BCE1322")

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

@app.get("/bfhl", response_class=HTMLResponse)
def bfhl_ui():
    """Simple HTML UI for testing the API."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <title>BFHL API Tester</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #2c3e50; }
            input, button { padding: 8px; margin: 5px 0; }
            #response { margin-top: 20px; padding: 10px; border: 1px solid #ddd; background: #f9f9f9; }
            textarea { width: 100%; height: 200px; }
        </style>
    </head>
    <body>
        <h1>🚀 BFHL API Tester</h1>
        <p>Enter comma-separated values (e.g., <code>1, 2, abc, XYZ, #$%</code>)</p>
        
        <input type="text" id="dataInput" size="50" placeholder="Enter values here" />
        <br>
        <button onclick="sendRequest()">Send to API</button>
        
        <h2>Response:</h2>
        <div id="response"><i>No request made yet.</i></div>
        
        <script>
            async function sendRequest() {
                const input = document.getElementById("dataInput").value;
                const dataArray = input.split(",").map(x => x.trim());
                
                const responseDiv = document.getElementById("response");
                responseDiv.innerHTML = "<i>Loading...</i>";
                
                try {
                    const res = await fetch("/bfhl", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ data: dataArray })
                    });
                    const json = await res.json();
                    responseDiv.innerHTML = "<textarea readonly>" + JSON.stringify(json, null, 2) + "</textarea>";
                } catch (err) {
                    responseDiv.innerHTML = "<b style='color:red'>Error:</b> " + err;
                }
            }
        </script>
    </body>
    </html>
    """

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
