#!/usr/bin/env python3
"""Rebuild Lu.pdf in the preview/ folder whenever a CV source file changes.

Run from any directory with: python3 resume-latex/cv_preview.py
Stop the watcher with Ctrl+C.
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "Lu.tex"
OUTPUT_DIR = HERE / "preview"
WATCHED_SUFFIXES = {".tex", ".cls", ".sty", ".bib"}
POLL_SECONDS = 0.75


def source_signature() -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in HERE.iterdir() if p.suffix in WATCHED_SUFFIXES):
        digest.update(path.name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def build() -> bool:
    latexmk = shutil.which("latexmk")
    if not latexmk:
        print("Error: latexmk was not found. Install MacTeX or TeX Live, then retry.", file=sys.stderr)
        return False

    OUTPUT_DIR.mkdir(exist_ok=True)
    command = [
        latexmk,
        "-pdf",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-file-line-error",
        f"-outdir={OUTPUT_DIR}",
        SOURCE.name,
    ]
    print(f"\nBuilding {OUTPUT_DIR / 'Lu.pdf'} ...", flush=True)
    result = subprocess.run(command, cwd=HERE)
    if result.returncode == 0:
        print(f"Preview ready: {OUTPUT_DIR / 'Lu.pdf'}", flush=True)
        return True

    print("Build failed. Fix the LaTeX error and save a source file to retry.", file=sys.stderr, flush=True)
    return False


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"CV source not found: {SOURCE}")

    previous_signature = None
    print(f"Watching CV sources in {HERE}. Press Ctrl+C to stop.", flush=True)
    try:
        while True:
            current_signature = source_signature()
            if current_signature != previous_signature:
                build()
                previous_signature = current_signature
            time.sleep(POLL_SECONDS)
    except KeyboardInterrupt:
        print("\nStopped CV preview watcher.", flush=True)


if __name__ == "__main__":
    main()
