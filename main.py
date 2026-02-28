from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import traceback
import sys
import io

app = FastAPI()

# Required for GA3
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

        result = sys.stdout.getvalue()
        sys.stdout = old_stdout

        return {
            "result": result,
            "error": []
        }

    except Exception:
        sys.stdout = old_stdout

        tb = traceback.extract_tb(sys.exc_info()[2])

        error_lines = [t.lineno for t in tb]

        return {
            "result": "",
            "error": error_lines
        }