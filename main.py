from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import traceback
import sys
import io

app = FastAPI()

# CORS (required)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeInput(BaseModel):
    code: str


@app.get("/")
def root():
    return {"status": "running"}


@app.post("/code-interpreter")
def run_code(data: CodeInput):

    code = data.code

    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    try:
        exec(code, {})

        output = sys.stdout.getvalue().strip()
        sys.stdout = old_stdout

        return {
            "output": output,
            "error": []
        }

    except Exception:
        sys.stdout = old_stdout

        tb = traceback.extract_tb(sys.exc_info()[2])

        error_lines = []
        for t in tb:
            error_lines.append(t.lineno)

        return {
            "output": "",
            "error": error_lines
        }