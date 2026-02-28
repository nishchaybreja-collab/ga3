from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import traceback
import sys
import io

app = FastAPI()

# ---- CORS (required for GA3 tester) ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Request model ----
class CodeInput(BaseModel):
    code: str


@app.get("/")
def root():
    return {"status": "running"}


# ---- Code Interpreter Endpoint ----
@app.post("/code-interpreter")
def run_code(data: CodeInput):
    code = data.code

    # Capture printed output
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    try:
        local_vars = {}
        exec(code, {}, local_vars)

        output = sys.stdout.getvalue()

        sys.stdout = old_stdout

        return {
            "output": output.strip()
        }

    except Exception:
        sys.stdout = old_stdout

        tb = traceback.format_exc()

        return {
            "error": tb
        }