"""Run the AskLedo Python API (matching cron included) on :8000."""

import os
from pathlib import Path

import uvicorn

PYTHON_API_ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    os.chdir(PYTHON_API_ROOT)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
