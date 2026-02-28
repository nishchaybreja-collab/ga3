from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import sys
from io import StringIO
import traceback
import os

from google import genai
from google.genai import types

app = FastAPI()

# -------- Request model --------
class CodeInput(BaseModel):
    code: str


# -------- Execute Python --------
def execute_python_code(code: str):
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        exec(code)
        output = sys.stdout.getvalue()
        return True, output

    except Exception:
        output = traceback.format_exc()
        return False, output

    finally:
        sys.stdout = old_stdout


# -------- AI Schema --------
class ErrorAnalysis(BaseModel):
    error_lines: List[int]


# -------- AI function --------
def analyze_error_with_ai(code: str, tb: str):

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = f"""
Analyze this Python code and traceback.
Return only the line numbers where the error occurred.

CODE:
{code}

TRACEBACK:
{tb}
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "error_lines": types.Schema(
                        type=types.Type.ARRAY,
                        items=types.Schema(type=types.Type.INTEGER)
                    )
                },
                required=["error_lines"]
            )
        )
    )

    result = ErrorAnalysis.model_validate_json(response.text)
    return result.error_lines


# -------- Endpoint --------
@app.post("/code-interpreter")
def run_code(data: CodeInput):

    success, output = execute_python_code(data.code)

    if success:
        return {
            "error": [],
            "result": output
        }

    lines = analyze_error_with_ai(data.code, output)

    return {
        "error": lines,
        "result": output
    }